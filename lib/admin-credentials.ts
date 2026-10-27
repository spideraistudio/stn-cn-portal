import { env } from "@/lib/runtime-env";
import { hashPassword } from "./passwords";

export async function currentAdminCredential() {
  const loginId = env.ADMIN_LOGIN_ID?.trim().toUpperCase();
  if (!loginId || !env.DB) return null;
  const stored = await env.DB.prepare("SELECT login_id,password_hash,version FROM admin_credentials WHERE login_id=?").bind(loginId).first<{login_id:string;password_hash:string;version:number}>();
  // The bootstrap secret stops working permanently once the administrator changes it.
  const bootstrap=env.ADMIN_PASSWORD_HASH||(env.ADMIN_INITIAL_PASSWORD.length>=12?hashPassword(env.ADMIN_INITIAL_PASSWORD):"");
  return stored || (bootstrap ? {login_id:loginId,password_hash:bootstrap,version:0} : null);
}
