import { NextResponse } from "next/server";
import { env } from "@/lib/runtime-env";
import { reportAdmin,reportDb } from "@/lib/report-store";
const reply=(body:object,status=200)=>NextResponse.json(body,{status,headers:{"Cache-Control":"no-store"}});
export async function POST(_request:Request){
 const admin=await reportAdmin();if(!admin)return reply({error:"Administrator access required."},403);
 try{const db=reportDb(),cutoff=Date.now()-30*24*60*60*1000;
  const reports=await db.prepare(`SELECT r.id FROM seller_reports r WHERE ((r.status='rejected' AND COALESCE(r.reviewed_at,r.created_at)<?) OR (r.status IN ('pending','rejected') AND EXISTS(SELECT 1 FROM account_deletion_requests q WHERE q.member_id=r.member_id AND q.status='approved' AND q.reviewed_at<?))) AND NOT EXISTS(SELECT 1 FROM legal_holds h WHERE h.target_type='report' AND h.target_id=r.id AND h.released_at IS NULL)`).bind(cutoff,cutoff).all<{id:string}>(),ids=reports.results.map(row=>row.id),documents:string[]=[];
  for(const id of ids){const docs=await db.prepare("SELECT object_key FROM report_documents WHERE report_id=?").bind(id).all<{object_key:string}>();documents.push(...docs.results.map(row=>row.object_key));await db.batch([db.prepare("DELETE FROM report_documents WHERE report_id=?").bind(id),db.prepare("DELETE FROM report_audit WHERE report_id=?").bind(id),db.prepare("DELETE FROM seller_reports WHERE id=?").bind(id)]);}
  if(documents.length&&env.REPORT_FILES)await env.REPORT_FILES.delete(documents);
  const members=await db.prepare(`SELECT id FROM members WHERE status='rejected' AND created_at<? AND NOT EXISTS(SELECT 1 FROM legal_holds h WHERE h.target_type='member' AND h.target_id=members.id AND h.released_at IS NULL) AND NOT EXISTS(SELECT 1 FROM seller_reports r WHERE r.member_id=members.id)`).bind(cutoff).all<{id:number}>();
  for(const row of members.results)await db.batch([db.prepare("DELETE FROM notifications WHERE member_id=?").bind(row.id),db.prepare("DELETE FROM member_sessions WHERE member_id=?").bind(row.id),db.prepare("UPDATE audit_logs SET target_member_id=NULL,details=CONCAT(COALESCE(details,''),?) WHERE target_member_id=?").bind(` [deleted member ${row.id}]`,row.id),db.prepare("DELETE FROM members WHERE id=? AND status='rejected'").bind(row.id)]);
  return reply({ok:true,reportsDeleted:ids.length,membersDeleted:members.results.length});
 }catch(error){console.error("[cleanup]",error);return reply({error:"Cleanup could not be completed."},500);}
}
