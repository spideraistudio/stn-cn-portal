import { readJsonBody } from "@/lib/request-body";
import { NextResponse } from "next/server";
import { reportAdmin, reportDb } from "@/lib/report-store";
import { redactIdentifiers } from "@/lib/report-validation";
import { operationGuard } from "@/lib/operation-guard";
import { notifyMember } from "@/lib/notifications";

export async function POST(request: Request) {
  const reply = (data: object, status = 200) => NextResponse.json(data, { status, headers: { "Cache-Control": "no-store" } });
  
  const admin = await reportAdmin();
  if (!admin) return reply({ error: "Administrator access required." }, 403);
  try {
    const { id, status, notes, identityChecked, reportReviewed, evidenceReviewed, approvedForDisplay } = await readJsonBody(request) as Record<string, unknown>;
    const note=typeof notes==="string"?notes.trim():"";
    if (typeof id !== "string" || !["approved", "rejected"].includes(String(status)) || note.length > 1000 || (status==="rejected"&&note.length<2)) return reply({ error: "A rejection reason is required; approval notes are optional." }, 400);
    if(status==="approved"&&(identityChecked!==true||reportReviewed!==true||approvedForDisplay!==true))return reply({error:"Complete the required verification checks before approval."},400);
    const db = reportDb();
    const report = await db.prepare("SELECT id,revision_of,member_id,firm_name,EXISTS(SELECT 1 FROM seller_reports approved WHERE approved.seller_id=seller_reports.seller_id AND approved.status='approved' AND (approved.firm_name<>seller_reports.firm_name OR approved.taluka<>seller_reports.taluka OR approved.district<>seller_reports.district OR approved.state<>seller_reports.state)) identity_change,EXISTS(SELECT 1 FROM report_documents d WHERE d.report_id=seller_reports.id) has_documents FROM seller_reports WHERE id=? AND status='pending'").bind(id).first<{id:string;revision_of:string|null;member_id:number;firm_name:string;identity_change:number;has_documents:number}>();
    if (!report) return reply({ error: "This report was already reviewed. Refresh the page." }, 409);
    if(status==="approved"&&evidenceReviewed&&!report.has_documents)return reply({error:"Evidence cannot be marked reviewed because no document was supplied."},400);
    const now = Date.now(); const cleanNotes = note?redactIdentifiers(note):"";
    const guard=operationGuard("EXISTS(SELECT 1 FROM seller_reports WHERE id=? AND status='pending') AND (?='rejected' OR ? IS NULL OR EXISTS(SELECT 1 FROM seller_reports WHERE id=? AND status='approved'))",[id,String(status),report.revision_of,report.revision_of]);
    const statements = [guard.check,db.prepare("INSERT INTO report_audit(id,report_id,actor,action,created_at) VALUES(?,?,?,?,?)").bind(crypto.randomUUID(),id,admin.userId,status,now)];
    if (status === "approved" && report.revision_of) {
      statements.push(db.prepare("UPDATE seller_reports SET status='superseded',reviewer=?,reviewed_at=? WHERE id=? AND status='approved'").bind(admin.userId,now,report.revision_of));
    }
    // Use an explicit column list per branch instead of string-replace surgery.
    const identityCheckedVal = Number(status === "approved" && Boolean(identityChecked));
    const reportReviewedVal = Number(status === "approved" && Boolean(reportReviewed));
    const evidenceReviewedVal = Number(status === "approved" && Boolean(evidenceReviewed));
    const approvedForDisplayVal = Number(status === "approved" && Boolean(approvedForDisplay));
    if (status === "approved" && report.revision_of) {
      // Approving a revision: the original approved report must already be superseded
      // (the supersede UPDATE above ran in the same batch). Guard with EXISTS.
      statements.push(db.prepare(
        "UPDATE seller_reports SET status=?,review_notes=?,reviewer=?,reviewed_at=?,identity_checked=?,report_reviewed=?,evidence_reviewed=?,approved_for_display=? WHERE id=? AND status='pending' AND EXISTS (SELECT 1 FROM seller_reports original WHERE original.id=seller_reports.revision_of AND original.status='superseded')"
      ).bind(status, cleanNotes || null, admin.userId, now, identityCheckedVal, reportReviewedVal, evidenceReviewedVal, approvedForDisplayVal, id));
    } else {
      statements.push(db.prepare(
        "UPDATE seller_reports SET status=?,review_notes=?,reviewer=?,reviewed_at=?,identity_checked=?,report_reviewed=?,evidence_reviewed=?,approved_for_display=? WHERE id=? AND status='pending'"
      ).bind(status, cleanNotes || null, admin.userId, now, identityCheckedVal, reportReviewedVal, evidenceReviewedVal, approvedForDisplayVal, id));
    }
    statements.push(guard.release);
    const result = await db.batch(statements);
    if(!result[result.length-2].meta.changes)return reply({ error: "This report was already reviewed. Refresh the page." }, 409);
    const correction=Boolean(report.identity_change);await notifyMember(report.member_id,{type:correction?`seller_correction_${status}`:`report_${status}`,title:correction?`Seller correction ${status}`:`Report ${status}`,message:cleanNotes?`${report.firm_name}: ${cleanNotes}`:`${report.firm_name}: ${status}.`,href:"/member/reports"});return reply({ ok: true });
  } catch (error) {
    console.error("[report-review]", error);
    const code = error && typeof error === "object" && "code" in error ? String((error as { code?: unknown }).code) : "";
    if (code === "GUARD_FAILED") return reply({ error: "This report was already reviewed. Refresh the page." }, 409);
    return reply({ error: "Unable to save review. Please try again." }, 500);
  }
}
