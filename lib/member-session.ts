import { combinedPortal, portalIdentity } from "./portal-session";
import { redirect } from "next/navigation";import { cookies } from "next/headers";import { digest } from "./passwords";import { reportDb } from "./report-store";import { memberFromRow } from "./member-data";
export const SESSION_COOKIE="stn_member_session";
export async function currentMember(){
if(combinedPortal()){
 const identity=await portalIdentity();
 if(!identity?.modules.stn||!identity.stn_member_id)return null;
 const member=memberFromRow(await reportDb().prepare("SELECT * FROM members WHERE id=? AND status='approved' LIMIT 1").bind(identity.stn_member_id).first());
 return member?{...member,mustChangePassword:false,portalUserId:identity.id}:null;
}
const token=(await cookies()).get(SESSION_COOKIE)?.value;if(!token)return null;const row=await reportDb().prepare("SELECT m.* FROM member_sessions s JOIN members m ON m.id=s.member_id AND m.credential_version=s.version WHERE s.token_hash=? AND s.expires_at>? AND m.status='approved' LIMIT 1").bind(digest(token),Date.now()).first();return memberFromRow(row);}
export async function requireApprovedMember(){const member=await currentMember();if(!member)redirect("/login");if(member.mustChangePassword)redirect("/member/password");return member;}
