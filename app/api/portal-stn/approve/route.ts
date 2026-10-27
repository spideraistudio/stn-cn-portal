import {NextResponse} from 'next/server';
import {portalIdentity} from '@/lib/portal-session';
import {portalAdminCall} from '@/lib/portal-admin-call';
import {mongoDb} from '@/lib/sql-mongo';
import {ObjectId} from 'mongodb';
import {parseMemberId} from '@/lib/member-data';
import {readJsonBody} from '@/lib/request-body';
import {isOriginValid} from '@/lib/origin-check';
export async function POST(request:Request){
 if(!isOriginValid(request))return NextResponse.json({error:'Invalid origin'},{status:403});
 const actor=await portalIdentity();if(actor?.role!=='superadmin')return NextResponse.json({error:'Platform superadmin required'},{status:403});
 try{
 const body=await readJsonBody(request);const id=parseMemberId(body.member_id);
 if(id==null)return NextResponse.json({error:'Invalid signup request'},{status:400});
 const db=await mongoDb(),key=typeof id==='string'?new ObjectId(id):id;
 const member=await db.collection('members').findOne({_id:key} as never);
 if(!member||!['pending','approved','cn_only'].includes(String(member.status)))return NextResponse.json({error:'Request cannot be approved'},{status:409});
 // Prepare a disabled identity first. A network failure leaves a retryable
 // reservation, never a usable account with half-finished permissions.
 await portalAdminCall('provision',body);
 await db.collection('members').updateOne({_id:key,status:{$in:['pending','approved','cn_only']}} as never,{$set:{status:'approved',stn_module_approved:body.stn===true,reviewed_by:'portal:'+actor.id,reviewed_at:Date.now(),updated_at:Date.now()}});
 const result=await portalAdminCall('activate',{member_id:String(id)});
 await db.collection('audit_logs').insertOne({actor_user_id:'portal:'+actor.id,action:'unified.signup_approved',target_member_id:id,created_at:Date.now()});
 return NextResponse.json(result,{headers:{'Cache-Control':'no-store'}});
 }catch(error){return NextResponse.json({error:error instanceof Error?error.message:'Approval failed. Retry the same request and credentials.'},{status:409});}
}
