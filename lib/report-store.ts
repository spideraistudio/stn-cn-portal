import { env } from "@/lib/runtime-env";
import { createHmac } from "node:crypto";
import { currentMember } from "./member-session";
import { categoryAccess } from "./category-access";
import { getChatGPTUser } from "@/app/chatgpt-auth";
import { isConfiguredAdmin } from "./member-data";
export function reportDb() { if(!env.DB) throw new Error("Storage unavailable"); return env.DB; }
export function identifierKey(category:string,kind:string,value:string) {
 if(!env.IDENTIFIER_LOOKUP_KEY) throw new Error("Identifier search is not configured yet.");
 return createHmac("sha256",env.IDENTIFIER_LOOKUP_KEY).update(`${category}:${kind}:${value}`).digest("hex");
}
export async function reportMember() {
 const member=await currentMember();
 if(!member || member.mustChangePassword) return null;
 const category=categoryAccess(member);return category ? {id:member.id,category:category.id,isPilot:Boolean(member.isPilot),searchEnabled:Boolean(member.searchEnabled)} : null;
}
export async function reportAdmin() { const user=await getChatGPTUser();return user && isConfiguredAdmin(user.email) ? user : null; }
export const safeReportColumns = `r.id,r.seller_id,r.revision_of,r.category,r.firm_name,r.taluka,r.district,r.state,r.pincode,r.rating,r.dispute,r.amount_paise,r.dispute_type,r.dispute_other,r.dispute_start_month,r.dispute_end_month,r.dispute_ongoing,r.legal,r.case_number,r.case_number_type,r.case_number_history,r.summary,r.status,r.review_notes,r.created_at,r.dispute_resolved,r.resolved_on,r.resolution_summary,r.resolved_amount_paise,r.identity_checked,r.report_reviewed,r.evidence_reviewed,r.approved_for_display,r.reviewed_at,EXISTS(SELECT 1 FROM dispute_resolution_requests q WHERE q.report_id=r.id AND q.status='pending') pending_resolution,EXISTS(SELECT 1 FROM seller_reports identity WHERE identity.id=(SELECT latest.id FROM seller_reports latest WHERE latest.seller_id=r.seller_id AND latest.status='approved' AND latest.id<>r.id ORDER BY COALESCE(latest.reviewed_at,latest.created_at) DESC LIMIT 1) AND (identity.firm_name<>r.firm_name OR identity.taluka<>r.taluka OR identity.district<>r.district OR identity.state<>r.state OR identity.pincode<>r.pincode)) identity_change_requested,s.gst_last4`;
export function maskReport(row:Record<string,unknown>) {
 const {gst_last4,...safe}=row;
 return {...safe,gstin:"***********"+gst_last4};
}
