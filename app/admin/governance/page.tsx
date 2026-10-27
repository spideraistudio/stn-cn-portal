// Server component (force-dynamic): Date.now() is evaluated per-request on the
// server, which is correct for retention-window calculations. The
// react-hooks/purity rule targets client render purity and is a false positive
// here. Row types come from inline SQL and are loosely typed for brevity.
/* eslint-disable react-hooks/purity, @typescript-eslint/no-explicit-any */
import { redirect } from "next/navigation";
import { requireChatGPTUser } from "@/app/chatgpt-auth";
import { isConfiguredAdmin } from "@/lib/member-data";
import { reportDb } from "@/lib/report-store";
import { ReportShell } from "@/components/report-shell";
import { GovernanceConsole } from "@/components/governance-console";
export const dynamic="force-dynamic";
export default async function Page(){
 const user=await requireChatGPTUser("/admin/governance");if(!isConfiguredAdmin(user.email))redirect("/join");const db=reportDb(),warning=Date.now()-23*24*60*60*1000;
 const [corrections,deletions,rejectedReports,rejectedMembers,holds]=await Promise.all([
  db.prepare("SELECT c.*,COALESCE((SELECT firm_name FROM seller_reports r WHERE r.seller_id=c.seller_id AND r.status='approved' ORDER BY COALESCE(r.reviewed_at,r.created_at) DESC LIMIT 1),'Seller') firm_name FROM seller_correction_requests c ORDER BY c.created_at DESC LIMIT 100").all<any>(),
  db.prepare("SELECT q.*,m.company_name FROM account_deletion_requests q JOIN members m ON m.id=q.member_id ORDER BY q.created_at DESC LIMIT 100").all<any>(),
  db.prepare("SELECT r.id,r.firm_name,COALESCE(r.reviewed_at,r.created_at) base,EXISTS(SELECT 1 FROM legal_holds h WHERE h.target_type='report' AND h.target_id=r.id AND h.released_at IS NULL) held FROM seller_reports r WHERE r.status='rejected' AND COALESCE(r.reviewed_at,r.created_at)<?").bind(warning).all<any>(),
  db.prepare("SELECT m.id,m.company_name,m.created_at base,EXISTS(SELECT 1 FROM legal_holds h WHERE h.target_type='member' AND h.target_id=m.id AND h.released_at IS NULL) held FROM members m WHERE m.status='rejected' AND m.created_at<?").bind(warning).all<any>(),
  db.prepare("SELECT id,target_type,target_id,reason,created_at FROM legal_holds WHERE released_at IS NULL ORDER BY created_at DESC").all<any>(),
 ]);
 const scheduled=[...rejectedReports.results.map(row=>({type:"report" as const,id:String(row.id),label:`Rejected report: ${row.firm_name}`,delete_on:Number(row.base)+30*24*60*60*1000,held:Boolean(row.held)})),...rejectedMembers.results.map(row=>({type:"member" as const,id:String(row.id),label:`Rejected application: ${row.company_name}`,delete_on:Number(row.base)+30*24*60*60*1000,held:Boolean(row.held)}))];
 return <ReportShell admin title="Data governance" description="Review correction, account-deletion, retention and legal-hold actions."><GovernanceConsole corrections={corrections.results} deletions={deletions.results} scheduled={scheduled} holds={holds.results}/></ReportShell>;
}
