import { readJsonBody } from "@/lib/request-body";
import { NextResponse } from "next/server";
import { currentMember } from "@/lib/member-session";
import { reportAdmin,reportDb } from "@/lib/report-store";
import { listNotifications } from "@/lib/notifications";

export async function GET(request:Request){
 const audience=new URL(request.url).searchParams.get("audience")==="admin"?"admin":"member";
 if(audience==="admin"){
  const admin=await reportAdmin();
  if(!admin)return NextResponse.json({error:"Administrator authentication required."},{status:403});
  return NextResponse.json({items:await listNotifications("admin",null)},{headers:{"Cache-Control":"no-store"}});
 }
 const member=await currentMember();
 if(!member)return NextResponse.json({error:"Member authentication required."},{status:403});
 return NextResponse.json({items:await listNotifications("member",member.id)},{headers:{"Cache-Control":"no-store"}});
}

export async function POST(request:Request){
 const reply=(body:object,status=200)=>NextResponse.json(body,{status,headers:{"Cache-Control":"no-store"}});
 
 try{
  const body=await readJsonBody(request) as Record<string,unknown>;
  const id=typeof body.id==="string"&&body.id.length<100?body.id:null,audience=body.audience==="admin"?"admin":"member";
  if(!id&&body.all!==true)return reply({error:"Invalid notification."},400);
  const db=reportDb(),now=Date.now();
  if(audience==="admin"){
   const admin=await reportAdmin();
   if(!admin)return reply({error:"Administrator authentication required."},403);
   const query=id?db.prepare("UPDATE notifications SET read_at=? WHERE id=? AND audience='admin'").bind(now,id):db.prepare("UPDATE notifications SET read_at=? WHERE audience='admin' AND read_at IS NULL").bind(now);
   await query.run();
   return reply({ok:true});
  }
  const member=await currentMember();
  if(!member)return reply({error:"Member authentication required."},403);
  const query=id?db.prepare("UPDATE notifications SET read_at=? WHERE id=? AND audience='member' AND member_id=?").bind(now,id,member.id):db.prepare("UPDATE notifications SET read_at=? WHERE audience='member' AND member_id=? AND read_at IS NULL").bind(now,member.id);
  await query.run();
  return reply({ok:true});
 }catch{return reply({error:"Unable to update notification."},500);}
}
