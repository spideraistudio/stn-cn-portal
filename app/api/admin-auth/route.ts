import { combinedPortal } from "@/lib/portal-session";
import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { ADMIN_SESSION_COOKIE, getChatGPTUser } from "@/app/chatgpt-auth";
import { digest, randomSecret, verifyPassword, hashPassword } from "@/lib/passwords";
import { currentAdminCredential } from "@/lib/admin-credentials";
import { reportDb } from "@/lib/report-store";
import { consumeLimit, networkHash, recordSecurityEvent } from "@/lib/security";
import { readJsonBody, RequestBodyError } from "@/lib/request-body";
import { operationGuard } from "@/lib/operation-guard";
const reply=(body:object,status=200)=>NextResponse.json(body,{status,headers:{"Cache-Control":"no-store"}});
const cookieOptions={httpOnly:true,secure:process.env.NODE_ENV==="production",sameSite:"strict" as const,path:"/",maxAge:8*60*60};
export async function POST(request:Request){if(combinedPortal())return NextResponse.json({error:"Use the common portal for login, logout and password changes.",redirect:"/portal"},{status:409});
 try {
  const body=await readJsonBody(request),jar=await cookies(),db=reportDb();
  if(body.action==="logout"){
   const token=jar.get(ADMIN_SESSION_COOKIE)?.value;
   if(token)await db.prepare("DELETE FROM admin_sessions WHERE token_hash=?").bind(digest(token)).run();
   jar.delete(ADMIN_SESSION_COOKIE);return reply({redirect:"/admin-login"});
  }
  const changing=body.action==="password",user=changing?await getChatGPTUser():null;
  if(changing&&!user)return reply({error:"Administrator authentication required."},403);
  const limit=await consumeLimit(request,changing?"admin_password":"admin_login",changing?user!.userId:networkHash(request),10,15*60*1000);
  if(!limit.allowed){
   if(limit.count===11)await recordSecurityEvent(request,"admin_auth_rate_limited",null,"Repeated administrator authentication attempts blocked for 15 minutes");
   return NextResponse.json({error:"Too many attempts. Please wait 15 minutes."},{status:429,headers:{"Cache-Control":"no-store","Retry-After":String(limit.retryAfterSeconds)}});
  }
  const credential=await currentAdminCredential();
  if(!credential)return reply({error:"Administrator credentials are not configured."},503);
  const loginId=typeof body.loginId==="string"?body.loginId.trim().toUpperCase():"",password=changing?body.currentPassword:body.password;
  if((!changing&&loginId!==credential.login_id)||typeof password!=="string"||!verifyPassword(password,credential.password_hash))return reply({error:changing?"Current password is incorrect.":"Invalid administrator ID or password."},401);
  const token=randomSecret(),now=Date.now();
  const guard=operationGuard(credential.version===0?"NOT EXISTS(SELECT 1 FROM admin_credentials WHERE login_id=?)":"EXISTS(SELECT 1 FROM admin_credentials WHERE login_id=? AND version=?)",credential.version===0?[credential.login_id]:[credential.login_id,credential.version]);
  if(changing){
   if(typeof body.password!=="string"||body.password.length<12||body.password.length>128||body.password!==body.confirmPassword||body.password===password)return reply({error:"Choose a different password of 12–128 characters and enter it identically twice."},400);
   const nextHash=hashPassword(body.password),nextVersion=credential.version+1;
   await db.batch([guard.check,db.prepare("INSERT INTO admin_credentials(login_id,password_hash,version,updated_at) VALUES(?,?,?,?) ON CONFLICT (login_id) DO UPDATE SET password_hash=EXCLUDED.password_hash,version=EXCLUDED.version,updated_at=EXCLUDED.updated_at").bind(credential.login_id,nextHash,nextVersion,now),db.prepare("DELETE FROM admin_sessions WHERE login_id=?").bind(credential.login_id),db.prepare("INSERT INTO admin_sessions(token_hash,login_id,version,expires_at,created_at) VALUES(?,?,?,?,?)").bind(digest(token),credential.login_id,nextVersion,now+8*60*60*1000,now),db.prepare("INSERT INTO audit_logs(actor_user_id,action,created_at) VALUES(?,?,?)").bind(user!.userId,"admin.password_changed",now),guard.release]);
   jar.set(ADMIN_SESSION_COOKIE,token,cookieOptions);return reply({ok:true});
  }
  await db.batch([guard.check,db.prepare("DELETE FROM admin_sessions WHERE expires_at<=?").bind(now),db.prepare("INSERT INTO admin_sessions(token_hash,login_id,version,expires_at,created_at) VALUES(?,?,?,?,?)").bind(digest(token),credential.login_id,credential.version,now+8*60*60*1000,now),guard.release]);
  jar.set(ADMIN_SESSION_COOKIE,token,cookieOptions);return reply({redirect:credential.version===0?"/admin/security":"/admin"});
 }catch(error){
  console.error("admin-auth", error);
  if(error instanceof RequestBodyError)return reply({error:error.message},error.status);
  const code=error && typeof error==="object" && "code" in error ? String((error as {code?:unknown}).code) : "";
  const name=error instanceof Error ? error.name : "";
  if(code==="GUARD_FAILED")return reply({error:"Unable to complete the request. Refresh and try again."},409);
  if(["ECONNREFUSED","ETIMEDOUT","ENOTFOUND","28P01","3D000","08001","08006","MongoNetworkError","MongoServerSelectionError","SELF_SIGNED_CERT_IN_CHAIN"].includes(code)
    || ["MongoNetworkError","MongoServerSelectionError"].includes(name)){
   return reply({error:"Database is unavailable. Check MONGODB_URI and Atlas Network Access (IP whitelist)."},503);
  }
  return reply({error:"Unable to complete the request. Refresh and try again."},500);
 }
}
