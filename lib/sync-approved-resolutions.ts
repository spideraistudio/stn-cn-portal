import { reportDb } from "@/lib/report-store";

type ApprovedRow = {
  report_id: string;
  resolved_on: string;
  resolved_amount_paise: number;
  description: string;
  amount_paise: number | null;
  report_resolved_paise: number | null;
  dispute_resolved: number | null;
};

/**
 * Apply approved resolution amounts onto seller_reports that were left open
 * (can happen when request status updated but report UPDATE did not stick).
 */
export async function syncApprovedResolutionsToReports() {
  const db = reportDb();
  const result = await db
    .prepare(
      `SELECT q.report_id,q.resolved_on,q.resolved_amount_paise,q.description,
              r.amount_paise,r.resolved_amount_paise AS report_resolved_paise,r.dispute_resolved
       FROM dispute_resolution_requests q
       JOIN seller_reports r ON r.id=q.report_id
       WHERE q.status='approved' AND r.dispute=1 AND r.status='approved' AND COALESCE(r.dispute_resolved,0)=0
       ORDER BY q.reviewed_at ASC, q.created_at ASC`,
    )
    .all<ApprovedRow>();

  if (!result.results.length) return 0;

  const byReport = new Map<
    string,
    {
      amount: number;
      currentResolved: number;
      totalApproved: number;
      resolvedOn: string;
      summary: string;
    }
  >();

  for (const row of result.results) {
    const amount = Math.max(0, Number(row.amount_paise) || 0);
    const currentResolved = Math.max(0, Number(row.report_resolved_paise) || 0);
    const add = Math.max(0, Number(row.resolved_amount_paise) || 0);
    const existing = byReport.get(row.report_id);
    if (!existing) {
      byReport.set(row.report_id, {
        amount,
        currentResolved,
        totalApproved: add,
        resolvedOn: row.resolved_on,
        summary: row.description,
      });
    } else {
      existing.totalApproved += add;
      existing.resolvedOn = row.resolved_on || existing.resolvedOn;
      existing.summary = row.description || existing.summary;
    }
  }

  let fixed = 0;
  for (const [reportId, info] of byReport) {
    const nextResolved = Math.min(
      info.amount,
      Math.max(info.currentResolved, info.totalApproved),
    );
    if (nextResolved <= info.currentResolved && nextResolved < info.amount) {
      continue;
    }
    const fullyResolved = info.amount > 0 && nextResolved >= info.amount ? 1 : 0;
    const update = fullyResolved
      ? await db
          .prepare(
            `UPDATE seller_reports
             SET resolved_amount_paise=?,
                 dispute_resolved=1,
                 resolved_on=?,
                 resolution_summary=?,
                 dispute_ongoing=0
             WHERE id=? AND status='approved' AND dispute=1 AND COALESCE(dispute_resolved,0)=0`,
          )
          .bind(nextResolved, info.resolvedOn, info.summary, reportId)
          .run()
      : await db
          .prepare(
            `UPDATE seller_reports
             SET resolved_amount_paise=?,
                 dispute_resolved=0,
                 resolved_on=?,
                 resolution_summary=?
             WHERE id=? AND status='approved' AND dispute=1 AND COALESCE(dispute_resolved,0)=0`,
          )
          .bind(nextResolved, info.resolvedOn, info.summary, reportId)
          .run();
    if (update.meta.changes) fixed += 1;
  }
  return fixed;
}
