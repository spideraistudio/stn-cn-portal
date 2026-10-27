import { readJsonBody } from "@/lib/request-body";
import { NextResponse } from "next/server";
import { reportAdmin, reportDb } from "@/lib/report-store";
import { redactIdentifiers } from "@/lib/report-validation";
import { notifyMember } from "@/lib/notifications";
import { operationGuard } from "@/lib/operation-guard";

const reply = (data: object, status = 200) =>
  NextResponse.json(data, { status, headers: { "Cache-Control": "no-store" } });

function asPaise(value: unknown) {
  const n = Number(value);
  return Number.isFinite(n) ? Math.max(0, Math.trunc(n)) : 0;
}

export async function POST(request: Request) {
  const admin = await reportAdmin();
  if (!admin) return reply({ error: "Administrator access required." }, 403);

  try {
    const { id, status, notes } = (await readJsonBody(request)) as Record<string, unknown>;
    if (
      typeof id !== "string" ||
      !["approved", "rejected"].includes(String(status)) ||
      typeof notes !== "string" ||
      notes.trim().length < 2 ||
      notes.length > 1000
    ) {
      return reply({ error: "Choose a decision and enter a review reason." }, 400);
    }

    const db = reportDb();
    const row = await db
      .prepare(
        "SELECT q.id,q.report_id,q.member_id,q.resolved_on,q.resolved_amount_paise,q.description,r.firm_name,r.amount_paise,r.resolved_amount_paise AS report_resolved_amount_paise,r.dispute,r.dispute_resolved,r.status AS report_status FROM dispute_resolution_requests q JOIN seller_reports r ON r.id=q.report_id WHERE q.id=? AND q.status='pending'",
      )
      .bind(id)
      .first<{
        id: string;
        report_id: string;
        member_id: number;
        resolved_on: string;
        resolved_amount_paise: number;
        description: string;
        firm_name: string;
        amount_paise: number;
        report_resolved_amount_paise: number;
        dispute: number;
        dispute_resolved: number;
        report_status: string;
      }>();

    if (!row) return reply({ error: "This request was already reviewed. Refresh the page." }, 409);

    const requestAmount = asPaise(row.resolved_amount_paise);
    const reportAmount = asPaise(row.amount_paise);
    const alreadyResolved = asPaise(row.report_resolved_amount_paise);
    const remaining = Math.max(0, reportAmount - alreadyResolved);

    if (status === "approved") {
      if (row.report_status !== "approved" || !Number(row.dispute) || Number(row.dispute_resolved)) {
        return reply({ error: "The original dispute is no longer eligible for resolution." }, 409);
      }
      if (requestAmount <= 0 || requestAmount > remaining) {
        return reply({ error: "Resolved amount is no longer valid for this dispute." }, 409);
      }
    }

    const nextResolvedAmount = Math.min(
      reportAmount > 0 ? reportAmount : alreadyResolved + requestAmount,
      alreadyResolved + requestAmount,
    );
    // Admin approval closes the dispute on the report. Amount is still tracked for money stats.
    const nextDisputeResolved = 1;

    const guard = operationGuard(
      "EXISTS(SELECT 1 FROM dispute_resolution_requests q JOIN seller_reports r ON r.id=q.report_id WHERE q.id=? AND q.status='pending' AND (?='rejected' OR (r.status='approved' AND r.dispute=1 AND r.dispute_resolved=0 AND q.resolved_amount_paise>0 AND q.resolved_amount_paise<=COALESCE(r.amount_paise,0)-COALESCE(r.resolved_amount_paise,0))))",
      [id, String(status)],
    );

    const now = Date.now();
    const cleanNotes = redactIdentifiers(notes.trim());
    const statements = [guard.check];

    if (status === "approved") {
      statements.push(
        db
          .prepare(
            "UPDATE seller_reports SET resolved_amount_paise=?,dispute_resolved=?,resolved_on=?,resolution_summary=? WHERE id=? AND status='approved'",
          )
          .bind(nextResolvedAmount, nextDisputeResolved, row.resolved_on, row.description, row.report_id),
      );
    }

    statements.push(
      db
        .prepare(
          "UPDATE dispute_resolution_requests SET status=?,admin_notes=?,reviewer=?,reviewed_at=? WHERE id=? AND status='pending'",
        )
        .bind(status, cleanNotes, admin.userId, now, id),
    );
    statements.push(
      db
        .prepare("INSERT INTO report_audit(id,report_id,actor,action,created_at) VALUES(?,?,?,?,?)")
        .bind(crypto.randomUUID(), row.report_id, admin.userId, `resolution_${status}`, now),
    );
    statements.push(guard.release);

    const result = await db.batch(statements);
    if (status === "approved" && !result[1].meta.changes) {
      return reply({ error: "The original dispute is no longer eligible for resolution." }, 409);
    }

    await notifyMember(row.member_id, {
      type: `resolution_${status}`,
      title: `Resolution request ${status}`,
      message: `${row.firm_name}: ${cleanNotes}`,
      href: "/member/reports",
    });

    return reply({ ok: true, disputeResolved: status === "approved" ? nextDisputeResolved === 1 : false });
  } catch {
    return reply({ error: "Unable to save resolution review." }, 500);
  }
}
