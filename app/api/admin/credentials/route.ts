import { readJsonBody } from "@/lib/request-body";
import { NextResponse } from "next/server";
import { env } from "@/lib/runtime-env";
import { getChatGPTUser } from "@/app/chatgpt-auth";
import { isConfiguredAdmin, memberFromRow, parseMemberId } from "@/lib/member-data";
import { reportDb } from "@/lib/report-store";
import { hashPassword, randomSecret } from "@/lib/passwords";
import { notifyMember } from "@/lib/notifications";
import { isOriginValid } from "@/lib/origin-check";
export async function POST(request: Request) {
  const reply = (data: object,status=200) => NextResponse.json(data,{status,headers:{"Cache-Control":"no-store"}});
  if(!isOriginValid(request)) return reply({error:"Invalid request origin."},403);
  const user = await getChatGPTUser();
  if(!user || !isConfiguredAdmin(user.email)) return reply({error:"Administrator access required."},403);
  try {
    const memberId=parseMemberId((await readJsonBody(request) as Record<string, unknown>).memberId);
    if(memberId==null) return reply({error:"Invalid member."},400);
    const db=reportDb();const member=memberFromRow(await db.prepare("SELECT * FROM members WHERE id=? LIMIT 1").bind(memberId).first());
    if(!member || !["pending","approved"].includes(member.status)) return reply({error:"Only pending or approved members can receive credentials."},409);
    if(process.env.PORTAL_MODE==="combined")return reply({error:"Use Approve & create account on the signup request, or Edit access for existing users."},409);
    const loginId=member.loginId ?? (typeof member.id==="number"?`MEM${String(member.id).padStart(6,"0")}`:`MEM${String(member.id).slice(-6).toUpperCase()}`);
    const temporaryPassword=randomSecret();
    const now=Date.now(),updated=await db.prepare("UPDATE members SET login_id=?,password_hash=?,must_change_password=1,failed_logins=0,locked_until=NULL,status='approved',reviewed_by=?,reviewed_at=?,updated_at=? WHERE id=? AND credential_version=? AND status=?").bind(loginId,hashPassword(temporaryPassword),user.userId,now,now,member.id,member.credentialVersion,member.status).run();
    if(!updated.meta.changes) return reply({error:"This member changed. Refresh and try again."},409);
    await db.prepare("INSERT INTO audit_logs(actor_user_id,action,target_member_id,created_at) VALUES(?,?,?,?)").bind(user.userId,member.status === "pending" ? "member.approved_credentials_issued" : "member.credentials_reset",member.id,now).run();
    await env.DB?.prepare("UPDATE password_reset_requests SET status='completed',reviewed_by=?,reviewed_at=? WHERE member_id=? AND status='pending'").bind(user.userId,Date.now(),member.id).run();
    await notifyMember(member.id,{type:member.status==="pending"?"membership_approved":"password_reset",title:member.status==="pending"?"Membership approved":"Password reset",message:member.status==="pending"?"Your company membership was approved and credentials were issued. Use the credentials shared by the administrator to sign in.":"Your password was reset by the administrator. Use the newly shared temporary password to sign in.",href:"/login"});
    return reply({loginId,temporaryPassword});
  } catch { return reply({error:"Unable to issue credentials. Refresh before trying again."},500); }
}
