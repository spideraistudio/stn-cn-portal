import {caseNumberLabel} from "@/lib/case-numbers";
import { NextResponse } from "next/server";
import { reportAdmin,reportDb } from "@/lib/report-store";

function cell(value:unknown){let text=String(value??"").replaceAll('"','""');if(/^[\s\uFEFF]*[=+\-@]|^[\t\r\n]/.test(text))text=`'${text}`;return `"${text}"`;}
function csv(headers:string[],rows:unknown[][]){return `\uFEFF${headers.map(cell).join(",")}\r\n${rows.map(row=>row.map(cell).join(",")).join("\r\n")}`;}
export async function GET(request:Request){
 const admin=await reportAdmin();if(!admin)return NextResponse.json({error:"Administrator access required."},{status:403});
 const type=new URL(request.url).searchParams.get("type"),db=reportDb();let body="",filename="";
 if(type==="members"){
  const result=await db.prepare("SELECT login_id,company_name,address,taluka,district,state,pincode,gstin,responsible_person_name,mobile_number,email,category,other_category,status,created_at FROM members ORDER BY created_at DESC").all<Record<string,unknown>>();
  body=csv(["Member ID","Company","Address","Taluka","District","State","PIN code","GSTIN","Responsible person","Mobile","Email","Category","Other category","Status","Registered"],result.results.map(r=>[r.login_id,r.company_name,r.address,r.taluka,r.district,r.state,r.pincode,r.gstin,r.responsible_person_name,r.mobile_number,r.email,r.category,r.other_category,r.status,new Date(Number(r.created_at)).toISOString()]));filename="member-records.csv";
 }else if(type==="reports"){
  const result=await db.prepare("SELECT r.firm_name,r.taluka,r.district,r.state,r.pincode,r.category,r.rating,r.dispute,r.amount_paise,r.resolved_amount_paise,r.dispute_type,r.legal,r.case_number,r.case_number_type,r.case_number_history,r.summary,r.dispute_resolved,r.resolved_on,r.report_reviewed,r.evidence_reviewed,r.created_at,s.gst_last4,m.login_id,m.company_name FROM seller_reports r JOIN sellers s ON s.id=r.seller_id JOIN members m ON m.id=r.member_id WHERE r.status='approved' ORDER BY r.created_at DESC").all<Record<string,unknown>>();
  body=csv(["Seller firm","Taluka","District","State","PIN code","GSTIN (masked)","Category","Rating","Dispute","Disputed amount INR","Resolved amount INR","Dispute type","Legal proceeding","Case number","Case number type","Previous case numbers (JSON)","Summary","Dispute resolved","Resolved on","Admin reviewed","Evidence reviewed","Submitted by Member ID","Submitting company","Submitted"],result.results.map(r=>[r.firm_name,r.taluka,r.district,r.state,r.pincode,`***********${r.gst_last4}`,r.category,r.rating,Number(r.dispute)?"Yes":"No",r.amount_paise==null?"":Number(r.amount_paise)/100,r.resolved_amount_paise==null?"":Number(r.resolved_amount_paise)/100,r.dispute_type,Number(r.legal)?"Yes":"No",r.case_number,Number(r.legal)?caseNumberLabel(r.case_number_type):"",r.case_number_history||"[]",r.summary,Number(r.dispute_resolved)?"Yes":"No",r.resolved_on,Number(r.report_reviewed)?"Yes":"No",Number(r.evidence_reviewed)?"Yes":"No",r.login_id,r.company_name,new Date(Number(r.created_at)).toISOString()]));filename="approved-seller-reports.csv";
 }else return NextResponse.json({error:"Choose a valid export."},{status:400});
 await db.prepare("INSERT INTO audit_logs(actor_user_id,action,details,created_at) VALUES(?,?,?,?)").bind(admin.userId,`admin.export_${type}`,`${type} CSV downloaded`,Date.now()).run();
 return new NextResponse(body,{headers:{"Content-Type":"text/csv; charset=utf-8","Content-Disposition":`attachment; filename=\"${filename}\"`,"Cache-Control":"no-store"}});
}
