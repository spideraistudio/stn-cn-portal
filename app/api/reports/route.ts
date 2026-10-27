import { updatedCaseNumbers } from "@/lib/case-numbers";
import { readFormBody } from "@/lib/request-body";
import { NextResponse } from "next/server";
import { env } from "@/lib/runtime-env";
import { reportInput,amountPaise,redactIdentifiers } from "@/lib/report-validation";
import { reportDb,reportMember,identifierKey } from "@/lib/report-store";
import { flagRepeatedUpload,recordSecurityEvent } from "@/lib/security";
import { notifyAdmin } from "@/lib/notifications";
import { validateIndianLocation } from "@/lib/india-locations";
import { isOriginValid } from "@/lib/origin-check";
const reply=(data:object,status=200)=>NextResponse.json(data,{status,headers:{"Cache-Control":"no-store"}});
export async function POST(request:Request) {
 if(!isOriginValid(request)) return reply({error:"Invalid request origin."},403);
 let member;try{member=await reportMember();}catch{return reply({error:"Member verification is temporarily unavailable. Please refresh and retry."},503);}if(!member) return reply({error:"An approved membership and assigned category are required."},403);
 const uploaded:string[]=[];
 let submittedId: string | null = null;
 try {
  if(Number(request.headers.get("content-length")||0)>6*1024*1024){await flagRepeatedUpload(request,member.id,"Repeated oversized seller-report uploads");return reply({error:"Upload at most three files of 1.5 MB each."},413);}
  const form=await readFormBody(request);
  let raw: unknown;
  try { raw = JSON.parse(String(form.get("report")||"{}")); }
  catch { return reply({ error: "Invalid report payload." }, 400); }
  const parsed = reportInput.safeParse(raw);
  if (!parsed.success) {
    const message = parsed.error.issues[0]?.message || "Check required fields.";
    return reply({ error: message }, 400);
  }
  const v = parsed.data;
  const db=reportDb();submittedId=v.requestId;
  const previous=await db.prepare("SELECT id FROM seller_reports WHERE id=? AND member_id=?").bind(v.requestId,member.id).first();
  if(previous) return reply({id:v.requestId});
  const gstKey=identifierKey(member.category,"gst",v.gstin);const duplicate=await db.prepare("SELECT r.id FROM seller_reports r JOIN sellers s ON s.id=r.seller_id WHERE r.member_id=? AND r.category=? AND s.gst_lookup=? AND r.status IN ('pending','approved') LIMIT 1").bind(member.id,member.category,gstKey).first();if(duplicate){await recordSecurityEvent(request,"duplicate_seller_submission",member.id,`Blocked duplicate report for seller ending ${v.gstin.slice(-4)}`,"info");return reply({error:"You already submitted a report about this seller. Open My Reports to edit it or request changes."},409);}
  const established=await db.prepare("SELECT r.firm_name,r.taluka,r.district,r.state,r.pincode FROM seller_reports r JOIN sellers s ON s.id=r.seller_id JOIN members m ON m.id=r.member_id WHERE r.category=? AND s.gst_lookup=? AND r.status='approved' AND m.is_pilot=? ORDER BY COALESCE(r.reviewed_at,r.created_at) DESC LIMIT 1").bind(member.category,gstKey,Number(member.isPilot)).first<{firm_name:string;taluka:string;district:string;state:string;pincode:string}>();
  const submittedLocation=validateIndianLocation(v.state,v.district,v.pincode);
  if(!established||v.requestSellerCorrection){if(!submittedLocation.valid)return reply({error:submittedLocation.error},400);}
  const now=Date.now();
  let caseDetails;try{caseDetails=updatedCaseNumbers({...v,caseNumber:redactIdentifiers(v.caseNumber)},undefined,now);}catch(error){return reply({error:error instanceof Error?error.message:"Check case number type."},400);}
  const files=form.getAll("documents").filter((v):v is File=>v instanceof File && v.size>0);
  if(files.length>3 || files.some(f=>f.size>1.5*1024*1024)){await flagRepeatedUpload(request,member.id,"Repeated oversized or excessive seller-report uploads");return reply({error:"Upload at most three files of 1.5 MB each."},400);}
  if(files.length && !env.REPORT_FILES) return reply({error:"Document storage is not configured yet."},503);
  const docs=[];
  for(const file of files) {
   const bytes=new Uint8Array(await file.slice(0,12).arrayBuffer());
   const mime=bytes[0]===0x25&&bytes[1]===0x50&&bytes[2]===0x44&&bytes[3]===0x46&&bytes[4]===0x2d ? "application/pdf" : bytes[0]===0xff&&bytes[1]===0xd8&&bytes[2]===0xff ? "image/jpeg" : bytes.slice(0,8).join(',')==='137,80,78,71,13,10,26,10' ? "image/png" : null;
   if(!mime){await flagRepeatedUpload(request,member.id,"Repeated invalid seller-report file types");return reply({error:"Only PDF, JPG and PNG documents are accepted."},400);}
   docs.push({file,mime,id:crypto.randomUUID()});
  }
  const identity=established&&!v.requestSellerCorrection?{firmName:established.firm_name,taluka:established.taluka,district:established.district,state:established.state,pincode:established.pincode||""}:v;const newSellerId=crypto.randomUUID();
  const identityValues=[identity.firmName,"",identity.taluka,identity.district,identity.state,identity.pincode||""].map(value=>redactIdentifiers(String(value??"")));
  const statements=[db.prepare("INSERT INTO sellers(id,category,gst_lookup,gst_last4) VALUES(?,?,?,?) ON CONFLICT (category,gst_lookup) DO NOTHING").bind(newSellerId,member.category,gstKey,v.gstin.slice(-4)),
   db.prepare(`INSERT INTO seller_reports(id,seller_id,member_id,category,firm_name,person_name,taluka,district,state,pincode,rating,dispute,amount_paise,dispute_type,dispute_other,dispute_start_month,dispute_end_month,dispute_ongoing,legal,case_number,case_number_type,case_number_history,summary,status,created_at)
    SELECT ?,id,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'pending',? FROM sellers WHERE category=? AND gst_lookup=?`).bind(v.requestId,member.id,member.category,...identityValues,v.rating,Number(v.dispute),v.dispute?amountPaise(v.amount,v.unit):null,v.dispute?v.disputeType:null,v.dispute&&v.disputeType==='other'?redactIdentifiers(v.disputeOther):null,v.dispute?v.disputeStartMonth:null,v.dispute&&!v.disputeOngoing?v.disputeEndMonth:null,Number(v.dispute&&v.disputeOngoing),Number(v.legal),caseDetails.number,caseDetails.type,caseDetails.history,redactIdentifiers(v.summary),now,member.category,gstKey)];
  for(const doc of docs){const key=`reports/${v.requestId}/${doc.id}`;await env.REPORT_FILES.put(key,doc.file.stream(),{httpMetadata:{contentType:doc.mime}});uploaded.push(key);statements.push(db.prepare("INSERT INTO report_documents(id,report_id,object_key,name,mime,size) VALUES(?,?,?,?,?,?)").bind(doc.id,v.requestId,key,redactIdentifiers(doc.file.name).slice(0,150),doc.mime,doc.file.size));}
  statements.push(db.prepare("INSERT INTO report_audit(id,report_id,actor,action,created_at) VALUES(?,?,?,?,?)").bind(crypto.randomUUID(),v.requestId,`member:${member.id}`,"submitted",now));
  await db.batch(statements);
  void notifyAdmin({type:established&&v.requestSellerCorrection?"seller_correction":"report_submission",title:established&&v.requestSellerCorrection?"Seller-detail correction request":"New seller report",message:`${v.firmName} was submitted for administrator review.`,href:"/admin/reports"});
  return reply({id:v.requestId},201);
 }catch(error){
  // A lost database response may follow a successful commit. Reconcile before deleting files.
  console.error("[api/reports]", error);
  if(submittedId){try{const saved=await reportDb().prepare("SELECT id FROM seller_reports WHERE id=? AND member_id=?").bind(submittedId,member.id).first();if(saved)return reply({id:submittedId});}catch{return reply({error:"Submission status is uncertain. Check My reports before retrying."},503);}}
  if(uploaded.length) await env.REPORT_FILES.delete(uploaded).catch(()=>{});
  const guardFailed = error instanceof Error && (error as { code?: string }).code === "GUARD_FAILED";
  return reply({
    error: guardFailed
      ? "You already submitted a report about this seller. Open My Reports to edit it or request changes."
      : "Unable to submit. Your form is preserved; please retry.",
  }, 400);
 }
}
