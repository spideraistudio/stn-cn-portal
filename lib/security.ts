import { createHmac } from "node:crypto";
import { env } from "@/lib/runtime-env";
import { mongoDb } from "./sql-mongo";
import { reportDb } from "./report-store";
import { notifyAdmin } from "./notifications";

function secret(){if(!env.IDENTIFIER_LOOKUP_KEY)throw new Error("IDENTIFIER_LOOKUP_KEY is required");return env.IDENTIFIER_LOOKUP_KEY;}
function hash(value:string){return createHmac("sha256",secret()).update(value).digest("hex");}
export function networkHash(request:Request){const raw=request.headers.get("cf-connecting-ip")||"unknown";return hash(`network:${raw}`);}
export async function consumeLimit(request:Request,action:string,identity:string,max:number,windowMs:number){
  const now=Date.now(),cutoff=now-windowMs,key=hash(`${action}:${identity}`);
  const col=(await mongoDb()).collection("security_rate_limits");
  const row=await col.findOneAndUpdate(
    {key},
    [{ $set:{
      key,
      action,
      count:{$cond:[{$lte:[{$ifNull:["$window_start",0]},cutoff]},1,{$add:[{$ifNull:["$count",0]},1]}]},
      window_start:{$cond:[{$lte:[{$ifNull:["$window_start",0]},cutoff]},now,"$window_start"]},
    }}],
    {upsert:true,returnDocument:"after"}
  );
  const count=Number(row?.count||1);
  const windowStart=Number(row?.window_start||now);
  return {allowed:count<=max,count,retryAfterSeconds:Math.max(1,Math.ceil(((windowStart+windowMs)-now)/1000))};
}
export async function recordSecurityEvent(request:Request,eventType:string,memberId:number|string|null,details:string,severity="warning"){await reportDb().prepare("INSERT INTO security_events(id,event_type,member_id,network_hash,details,severity,created_at) VALUES(?,?,?,?,?,?,?)").bind(crypto.randomUUID(),eventType,memberId,networkHash(request),details.slice(0,500),severity,Date.now()).run();if(severity==="warning")await notifyAdmin({type:"security_warning",title:"Unusual activity detected",message:details,href:"/admin/audit?q=security"});}
export async function flagRepeatedUpload(request:Request,memberId:number|string,reason:string){const result=await consumeLimit(request,"invalid_upload",`member:${memberId}`,3,30*60*1000);if(result.count===4)await recordSecurityEvent(request,"repeated_invalid_upload",memberId,reason);}
