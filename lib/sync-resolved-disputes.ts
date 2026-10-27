import { mongoDb } from "@/lib/sql-mongo";

/**
 * Older approvals could leave dispute_resolved=0 when only part of the amount
 * was paid. Admin approval now always closes the dispute — repair legacy rows.
 */
export async function syncResolvedDisputesFromApprovals() {
  const db = await mongoDb();
  const approved = await db
    .collection("dispute_resolution_requests")
    .find({ status: "approved" })
    .project({ report_id: 1, resolved_on: 1, description: 1, resolved_amount_paise: 1 })
    .toArray();

  if (!approved.length) return 0;

  let fixed = 0;
  for (const request of approved) {
    const reportId = request.report_id;
    if (reportId == null || reportId === "") continue;

    const report = await db.collection("seller_reports").findOne({
      $or: [{ _id: reportId }, { id: reportId }],
    });
    if (!report) continue;

    const already =
      report.dispute_resolved === 1 ||
      report.dispute_resolved === true ||
      report.dispute_resolved === "1";
    if (already) continue;

    const amount = Number(report.amount_paise) || 0;
    const currentResolved = Number(report.resolved_amount_paise) || 0;
    const requestAmount = Number(request.resolved_amount_paise) || 0;
    const nextResolved = Math.max(currentResolved, requestAmount);
    const capped = amount > 0 ? Math.min(amount, nextResolved) : nextResolved;

    await db.collection("seller_reports").updateOne(
      { _id: report._id },
      {
        $set: {
          dispute_resolved: 1,
          resolved_amount_paise: capped,
          resolved_on: report.resolved_on || request.resolved_on || null,
          resolution_summary: report.resolution_summary || request.description || null,
        },
      },
    );
    fixed++;
  }

  return fixed;
}
