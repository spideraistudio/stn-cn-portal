import { env } from "@/lib/runtime-env";
import { reportAdmin,reportMember,reportDb } from "@/lib/report-store";
export async function GET(request:Request,{params}:{params:Promise<{id:string}>}){
 const {id}=await params;const admin=await reportAdmin();const member=admin?null:await reportMember();
 if(!admin&&!member)return new Response("Access denied",{status:403});
 const row=await reportDb().prepare(`SELECT d.object_key,d.mime FROM report_documents d JOIN seller_reports r ON r.id=d.report_id WHERE d.id=? ${admin?'':'AND r.member_id=? AND r.category=?'}`).bind(...(admin?[id]:[id,member!.id,member!.category])).first<{object_key:string;mime:string}>();
 if(!row)return new Response("Document unavailable",{status:404});
 const object=await env.REPORT_FILES.get(row.object_key);if(!object)return new Response("Document unavailable",{status:404});
 return new Response(object.body,{headers:{"Content-Type":row.mime,"Content-Disposition":`attachment; filename="supporting-document.${row.mime==='application/pdf'?'pdf':row.mime==='image/png'?'png':'jpg'}"`,"Cache-Control":"private, no-store","X-Content-Type-Options":"nosniff","Content-Security-Policy":"sandbox"}});
}
