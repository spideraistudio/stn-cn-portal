import { updatedCaseNumbers } from "@/lib/case-numbers";
import { readFormBody } from "@/lib/request-body";
import { NextResponse } from "next/server";
import { env } from "@/lib/runtime-env";
import { reportInput, amountPaise, redactIdentifiers } from "@/lib/report-validation";
import { reportDb, reportMember } from "@/lib/report-store";
import { flagRepeatedUpload } from "@/lib/security";
import { operationGuard } from "@/lib/operation-guard";
import { notifyAdmin } from "@/lib/notifications";

const reply = (data: object, status = 200) => NextResponse.json(data, { status, headers: { "Cache-Control": "no-store" } });

export async function POST(request: Request) {
  
  let member;try{member=await reportMember();}catch{return reply({ error: "Member verification is temporarily unavailable. Please refresh and retry." },503);}
  if (!member) return reply({ error: "Approved membership required." }, 403);
  const uploaded: string[] = [];
  let committed = false;
  try {
    const form = await readFormBody(request);
    const sourceId = String(form.get("sourceId") || "");
    const raw=JSON.parse(String(form.get("report")||"{}")) as Record<string,unknown>;raw.gstin="24AAAAA0000A1Z5";raw.requestSellerCorrection=false;const value=reportInput.parse(raw);
    const keepIds = JSON.parse(String(form.get("keepDocuments") || "[]")) as unknown;
    if (!Array.isArray(keepIds) || keepIds.some(id => typeof id !== "string")) return reply({ error: "Invalid document selection." }, 400);
    const db = reportDb();
    const source = await db.prepare("SELECT * FROM seller_reports WHERE id=? AND member_id=?").bind(sourceId, member.id).first<Record<string, unknown>>();
    if (!source || !["pending", "approved"].includes(String(source.status))) return reply({ error: "This report cannot be edited." }, 409);
    if (source.status === "approved") {
      const resolving = await db.prepare("SELECT id FROM dispute_resolution_requests WHERE report_id=? AND status='pending'").bind(sourceId).first();
      if (resolving) return reply({ error: "Finish the pending resolution review before requesting other changes." }, 409);
      const existing = await db.prepare("SELECT id FROM seller_reports WHERE revision_of=? AND status='pending'").bind(sourceId).first();
      if (existing) return reply({ error: "An edit is already awaiting admin review." }, 409);
    }
    const now=Date.now();
    let caseDetails;try{caseDetails=updatedCaseNumbers({...value,caseNumber:redactIdentifiers(value.caseNumber)},source,now);}catch(error){return reply({error:error instanceof Error?error.message:"Check case number type."},400);}
    const existingDocs = await db.prepare("SELECT id,object_key,name,mime,size FROM report_documents WHERE report_id=?").bind(sourceId).all<Record<string, unknown>>();
    const allowed = new Set(existingDocs.results.map(document => String(document.id)));
    if (keepIds.some(id => !allowed.has(id))) return reply({ error: "Invalid document selection." }, 403);
    const files = form.getAll("documents").filter((item): item is File => item instanceof File && item.size > 0);
    if (keepIds.length + files.length > 3 || files.some(file => file.size > 1.5 * 1024 * 1024)){await flagRepeatedUpload(request,member.id,"Repeated oversized or excessive report-edit uploads");return reply({ error: "Keep or upload at most three files of 1.5 MB each." }, 400);}
    const checked: { file: File; mime: string; id: string; key: string }[] = [];
    for (const file of files) {
      const bytes = new Uint8Array(await file.slice(0, 12).arrayBuffer());
      const mime = bytes[0]===0x25&&bytes[1]===0x50&&bytes[2]===0x44&&bytes[3]===0x46&&bytes[4]===0x2d ? "application/pdf" : bytes[0]===0xff&&bytes[1]===0xd8&&bytes[2]===0xff ? "image/jpeg" : bytes.slice(0,8).join(",")==="137,80,78,71,13,10,26,10" ? "image/png" : "";
      if (!mime){await flagRepeatedUpload(request,member.id,"Repeated invalid report-edit file types");return reply({ error: "Only PDF, JPG and PNG documents are accepted." }, 400);}
      const id = crypto.randomUUID(); checked.push({ file, mime, id, key: `reports/${value.requestId}/${id}` });
    }
    for (const document of checked) { await env.REPORT_FILES.put(document.key, document.file.stream(), { httpMetadata: { contentType: document.mime } }); uploaded.push(document.key); }
    const targetId = source.status === "pending" ? sourceId : value.requestId;
    const common = [member.category,source.firm_name,"",source.taluka,source.district,source.state,source.pincode||"",value.rating,Number(value.dispute),value.dispute?amountPaise(value.amount,value.unit):null,value.dispute?value.disputeType:null,value.dispute&&value.disputeType==="other"?redactIdentifiers(value.disputeOther):null,value.dispute?value.disputeStartMonth:null,value.dispute&&!value.disputeOngoing?value.disputeEndMonth:null,Number(value.dispute&&value.disputeOngoing),Number(value.legal),caseDetails.number,caseDetails.type,caseDetails.history,redactIdentifiers(value.summary)];
    const guard=operationGuard("EXISTS(SELECT 1 FROM seller_reports WHERE id=? AND member_id=? AND status=? AND COALESCE(case_number,'')=? AND COALESCE(case_number_type,'')=? AND COALESCE(case_number_history,'')=?) AND NOT EXISTS(SELECT 1 FROM dispute_resolution_requests WHERE report_id=? AND status='pending') AND NOT EXISTS(SELECT 1 FROM seller_reports WHERE revision_of=? AND status='pending')",[sourceId,member.id,String(source.status),String(source.case_number??""),String(source.case_number_type??""),String(source.case_number_history??""),sourceId,sourceId]);
    const statements = [guard.check];
    if (source.status === "pending") {
      statements.push(db.prepare(`UPDATE seller_reports SET category=?,firm_name=?,person_name=?,taluka=?,district=?,state=?,pincode=?,rating=?,dispute=?,amount_paise=?,dispute_type=?,dispute_other=?,dispute_start_month=?,dispute_end_month=?,dispute_ongoing=?,legal=?,case_number=?,case_number_type=?,case_number_history=?,summary=?,created_at=? WHERE id=? AND member_id=? AND status='pending'`).bind(...common,now,targetId,member.id));
      statements.push(keepIds.length?db.prepare(`DELETE FROM report_documents WHERE report_id=? AND id NOT IN (${keepIds.map(()=>"?").join(",")})`).bind(targetId,...keepIds):db.prepare("DELETE FROM report_documents WHERE report_id=?").bind(targetId));
    } else {
      statements.push(db.prepare(`INSERT INTO seller_reports(id,seller_id,revision_of,member_id,category,firm_name,person_name,taluka,district,state,pincode,rating,dispute,amount_paise,dispute_type,dispute_other,dispute_start_month,dispute_end_month,dispute_ongoing,legal,case_number,case_number_type,case_number_history,summary,dispute_resolved,resolved_on,resolution_summary,resolved_amount_paise,status,created_at) SELECT ?,seller_id,?,member_id,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'pending',? FROM seller_reports WHERE id=? AND member_id=? AND status='approved'`).bind(targetId,sourceId,...common,Number(value.dispute&&Boolean(source.dispute_resolved)),value.dispute?source.resolved_on:null,value.dispute?source.resolution_summary:null,value.dispute?Number(source.resolved_amount_paise||0):0,now,sourceId,member.id));
      for (const old of existingDocs.results.filter(document => keepIds.includes(String(document.id)))) statements.push(db.prepare("INSERT INTO report_documents(id,report_id,object_key,name,mime,size) VALUES(?,?,?,?,?,?)").bind(crypto.randomUUID(),targetId,old.object_key,old.name,old.mime,old.size));
    }
    for (const document of checked) statements.push(db.prepare("INSERT INTO report_documents(id,report_id,object_key,name,mime,size) VALUES(?,?,?,?,?,?)").bind(document.id,targetId,document.key,redactIdentifiers(document.file.name).slice(0,150),document.mime,document.file.size));
    statements.push(db.prepare("INSERT INTO report_audit(id,report_id,actor,action,created_at) VALUES(?,?,?,?,?)").bind(crypto.randomUUID(),targetId,`member:${member.id}`,source.status === "pending" ? "edited" : "revision_requested",now));
    statements.push(guard.release);
    await db.batch(statements);
    committed = true;
    if(source.status==="approved")await notifyAdmin({type:"report_change_request",title:"Report change request",message:`A member requested changes to ${String(source.firm_name)}.`,href:"/admin/reports"});
    if (source.status === "pending") for (const old of existingDocs.results.filter(document => !keepIds.includes(String(document.id)))) { const used = await db.prepare("SELECT count(*) count FROM report_documents WHERE object_key=?").bind(old.object_key).first<{count:number}>(); if (!used?.count) await env.REPORT_FILES.delete(String(old.object_key)); }
    return reply({ id: targetId, revision: source.status === "approved" });
  } catch (cause) {
    if (!committed && uploaded.length) await env.REPORT_FILES.delete(uploaded).catch(()=>{});
    if (cause && typeof cause === "object" && "code" in cause && cause.code === "GUARD_FAILED") return reply({error:"This report changed while you were editing. Refresh it and retry; previous case numbers are preserved."},409);
    return reply({ error: cause instanceof Error && cause.name === "ZodError" ? JSON.parse(cause.message)[0]?.message || "Check required fields." : "Unable to save changes. Please try again." }, 400);
  }
}
