import { reportDb,safeReportColumns,maskReport,identifierKey } from "./report-store";
import { mongoDb } from "./sql-mongo";
import type { ReportView } from "@/components/report-cards";
import { syncApprovedResolutionsToReports } from "@/lib/sync-approved-resolutions";

function asKey(value:unknown){
  if(value==null)return "";
  if(typeof value==="object" && typeof (value as {toHexString?:()=>string}).toHexString==="function")return (value as {toHexString:()=>string}).toHexString();
  return String(value);
}
function pendingStatus(){return {$or:[{status:"pending"},{status:null},{status:""},{status:{$exists:false}}]};}

export type OverviewReport={
  id:string;firmName:string;status:string;category:string;companyName:string;loginId:string|null;
  rating:number;createdAt:number|null;gstLast4:string|null;
};

export async function listOverviewReports(limit=20):Promise<OverviewReport[]>{
  const db=await mongoDb();
  const [reports,members,sellers]=await Promise.all([
    db.collection("seller_reports").find({}).sort({created_at:-1,_id:-1}).limit(limit).toArray(),
    db.collection("members").find({}).project({company_name:1,login_id:1}).toArray(),
    db.collection("sellers").find({}).project({gst_last4:1}).toArray(),
  ]);
  const membersById=new Map(members.map(m=>[asKey(m._id),m]));
  const sellersById=new Map(sellers.map(s=>[asKey(s._id??s.id),s]));
  return reports.map(report=>{
    const member=membersById.get(asKey(report.member_id));
    const seller=sellersById.get(asKey(report.seller_id))||sellersById.get(asKey(report._id));
    return {
      id:asKey(report._id??report.id),
      firmName:String(report.firm_name||"—"),
      status:String(report.status||"pending"),
      category:report.category==="other"?"other":"agriculture",
      companyName:String(member?.company_name||"—"),
      loginId:member?.login_id?String(member.login_id):null,
      rating:Number(report.rating)||0,
      createdAt:typeof report.created_at==="number"?report.created_at:null,
      gstLast4:seller?.gst_last4?String(seller.gst_last4):null,
    };
  });
}

export async function reportList(member:{id:number|string;category:string}|null,before:number,search=""){
 await syncApprovedResolutionsToReports();
 const query=search.trim().toLowerCase(),filter=member&&query?" AND (lower(r.firm_name) LIKE ? OR lower(r.summary) LIKE ? OR lower(COALESCE(r.dispute_type,'')) LIKE ?)":"",args:(string|number)[]=member?[before,member.id,member.category,member.category]:[before];if(filter){const like=`%${query}%`;args.push(like,like,like);}
 const db=reportDb();const result=await db.prepare(`SELECT ${safeReportColumns}${member?",(SELECT q.status FROM dispute_resolution_requests q WHERE q.report_id=r.id ORDER BY q.created_at DESC LIMIT 1) latest_resolution_status,(SELECT q.admin_notes FROM dispute_resolution_requests q WHERE q.report_id=r.id ORDER BY q.created_at DESC LIMIT 1) latest_resolution_notes":',m.login_id reporter_login_id,m.company_name reporter_company,m.mobile_number reporter_mobile'} FROM seller_reports r JOIN sellers s ON s.id=r.seller_id ${member?'':'JOIN members m ON m.id=r.member_id'} WHERE r.created_at < ? ${member?'AND r.member_id=? AND r.category=? AND s.category=?':"AND r.status='pending'"}${filter} ORDER BY r.created_at DESC LIMIT 51`).bind(...args).all<Record<string,unknown>>();
 const rows=result.results.slice(0,50);const reports=[];
 for(const row of rows){const documents=await db.prepare("SELECT id,name FROM report_documents WHERE report_id=?").bind(row.id).all<{id:string;name:string}>();const resolutionRequests=[];if(member){const requests=await db.prepare("SELECT id,resolved_on,resolved_amount_paise,description,status,admin_notes,created_at FROM dispute_resolution_requests WHERE report_id=? AND member_id=? ORDER BY created_at DESC LIMIT 20").bind(row.id,member.id).all<{id:string;resolved_on:string;resolved_amount_paise:number;description:string;status:string;admin_notes:string|null;created_at:number}>();for(const request of requests.results){const evidence=await db.prepare("SELECT id,name FROM dispute_resolution_documents WHERE request_id=?").bind(request.id).all<{id:string;name:string}>();resolutionRequests.push({...request,documents:evidence.results});}}reports.push({...maskReport(row),documents:documents.results,resolution_requests:resolutionRequests} as ReportView);}
 return {reports,next:result.results.length>50 ? Number(rows[rows.length-1].created_at):null};
}

export type AdminReportFilters={q?:string;status?:string;category?:string;from?:number;to?:number;memberId?:number|string;disputeStatus?:string};

export type AdminReportListResult={
  reports:ReportView[];
  total:number;
  page:number;
  pageSize:number;
  totalPages:number;
  /** @deprecated cursor pagination — prefer page */
  next:number|null;
};

function escapeRegex(value:string){
  return value.replace(/[.*+?^${}()|[\]\\]/g,"\\$&");
}

export async function adminReportList(
  filters:AdminReportFilters,
  opts:number|{page?:number;pageSize?:number;before?:number}={}
):Promise<AdminReportListResult>{
  // Back-compat: second arg used to be `before` cursor timestamp
  const options=typeof opts==="number"?{before:opts,page:1,pageSize:10}:opts;
  const page=Math.max(1,Number(options.page)||1);
  const pageSize=Math.min(50,Math.max(1,Number(options.pageSize)||10));
  const before=typeof options.before==="number"&&options.before>0?options.before:undefined;

  const db=await mongoDb();
  const and:Record<string,unknown>[]=[];
  if(before!=null)and.push({$or:[{created_at:{$lt:before}},{created_at:null},{created_at:{$exists:false}}]});
  const statusRaw = String(filters.status || "pending");
  const status = ["pending", "approved", "rejected", "superseded", "all"].includes(statusRaw)
    ? statusRaw
    : "pending";
  if (status !== "all") {
    and.push(status === "pending" ? pendingStatus() : { status });
  }  if(["agriculture","other"].includes(filters.category||""))and.push({category:filters.category});
  if(filters.memberId)and.push({$or:[{member_id:filters.memberId},{member_id:String(filters.memberId)}]});
  if(filters.disputeStatus==="reported")and.push({dispute:{$in:[1,true,"1"]}});
  if(filters.disputeStatus==="resolved")and.push({dispute:{$in:[1,true,"1"]},dispute_resolved:{$in:[1,true,"1"]}});
  if(filters.from)and.push({created_at:{$gte:filters.from}});
  if(filters.to)and.push({created_at:{$lte:filters.to}});

  const [members,sellers,pendingResolutions]=await Promise.all([
    db.collection("members").find({}).project({company_name:1,login_id:1,mobile_number:1}).toArray(),
    db.collection("sellers").find({}).toArray(),
    db.collection("dispute_resolution_requests").find({status:"pending"}).project({report_id:1}).toArray(),
  ]);
  const membersById=new Map(members.map(m=>[asKey(m._id),m]));
  const sellersById=new Map(sellers.map(s=>[asKey(s._id??s.id),s]));
  const pendingByReport=new Set(pendingResolutions.map(r=>asKey(r.report_id)));

  if(filters.q){
    const query=filters.q.trim().toUpperCase();
    if(/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/.test(query)){
      const keys=new Set([identifierKey("agriculture","gst",query),identifierKey("other","gst",query)]);
      const sellerIds=[...sellersById.entries()].filter(([,s])=>keys.has(String(s.gst_lookup||""))).map(([id])=>id);
      and.push({$or:[{seller_id:{$in:sellerIds}},{_id:{$in:sellerIds}}]});
    }else{
      const like=escapeRegex(filters.q.trim());
      const memberIds=members.filter(m=>`${m.company_name||""} ${m.login_id||""}`.toLowerCase().includes(filters.q!.trim().toLowerCase())).map(m=>asKey(m._id));
      and.push({$or:[
        {firm_name:{$regex:like,$options:"i"}},
        {member_id:{$in:memberIds}},
      ]});
    }
  }

  const match=and.length?{$and:and}:{};
  const total=await db.collection("seller_reports").countDocuments(match);
  const totalPages=Math.max(1,Math.ceil(total/pageSize));
  const safePage=Math.min(page,totalPages);
  const docs=await db.collection("seller_reports").find(match).sort({created_at:-1,_id:-1}).skip((safePage-1)*pageSize).limit(pageSize).toArray();

  const reports:ReportView[]=[];
  for(const row of docs){
    const member=membersById.get(asKey(row.member_id))||membersById.get(asKey(row.person_name));
    const seller=sellersById.get(asKey(row.seller_id))||sellersById.get(asKey(row._id));
    const documents=await db.collection("report_documents").find({report_id:asKey(row._id??row.id)}).project({id:1,name:1,_id:1}).toArray();
    reports.push(maskReport({
      ...row,
      id:asKey(row._id??row.id),
      status:["pending","approved","rejected","superseded"].includes(String(row.status))?String(row.status):"pending",
      category:row.category==="other"?"other":"agriculture",
      firm_name:typeof row.firm_name==="string"&&row.firm_name.trim()?row.firm_name:"—",
      taluka:typeof row.taluka==="string"?row.taluka:"",
      district:typeof row.district==="string"?row.district:"",
      state:typeof row.state==="string"?row.state:"",
      pincode:typeof row.pincode==="string"?row.pincode:"",
      rating:Math.min(10,Math.max(0,Math.round(Number(row.rating))||0)),
      dispute:row.dispute===1||row.dispute===true?1:0,
      legal:row.legal===1||row.legal===true?1:0,
      dispute_ongoing:row.dispute_ongoing===1||row.dispute_ongoing===true?1:0,
      dispute_resolved:row.dispute_resolved===1||row.dispute_resolved===true?1:0,
      amount_paise:typeof row.amount_paise==="number"?row.amount_paise:null,
      dispute_type:typeof row.dispute_type==="string"?row.dispute_type:null,
      dispute_other:typeof row.dispute_other==="string"?row.dispute_other:null,
      dispute_start_month:/^\d{4}-\d{2}$/.test(String(row.dispute_start_month||""))?String(row.dispute_start_month):null,
      dispute_end_month:/^\d{4}-\d{2}$/.test(String(row.dispute_end_month||""))?String(row.dispute_end_month):null,
      summary:typeof row.summary==="string"?row.summary:"",
      created_at:typeof row.created_at==="number"?row.created_at:Date.now(),
      reporter_login_id:member?.login_id||null,
      reporter_company:member?.company_name||null,
      reporter_mobile:member?.mobile_number||null,
      pending_resolution:pendingByReport.has(asKey(row._id??row.id))?1:0,
      gst_last4:seller?.gst_last4||"",
    }) as unknown as ReportView);
    reports[reports.length-1].documents=documents.map(doc=>({id:asKey(doc.id??doc._id),name:String(doc.name||"Document")}));
    reports[reports.length-1].resolution_requests=[];
  }

  const lastCreated=reports.length?Number(reports[reports.length-1].created_at)||null:null;
  return {
    reports,
    total,
    page:safePage,
    pageSize,
    totalPages,
    next:safePage<totalPages&&lastCreated?lastCreated:null,
  };
}
