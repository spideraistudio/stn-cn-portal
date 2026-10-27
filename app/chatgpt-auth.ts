import { combinedPortal, portalIdentity } from "@/lib/portal-session";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { env } from "@/lib/runtime-env";
import { digest } from "@/lib/passwords";
import { currentAdminCredential } from "@/lib/admin-credentials";

export type ChatGPTUser = {
  userId: string;
  displayName: string;
  email: string;
  fullName: string | null;
};

export const ADMIN_SESSION_COOKIE = "stn_admin_session";

export async function getChatGPTUser(): Promise<ChatGPTUser | null> {
  if(combinedPortal()){
    const identity=await portalIdentity();
    if(identity?.role!=="superadmin"||!identity.modules.stn)return null;
    const email=(env.ADMIN_EMAILS??"").split(",")[0]?.trim().toLowerCase();
    if(!email)return null;
    return {userId:`portal:${identity.id}`,displayName:identity.username,email,fullName:identity.username};
  }
  const token = (await cookies()).get(ADMIN_SESSION_COOKIE)?.value;
  if (!token) return null;
  try {
    if(!env.DB)return null;
    const row = await env.DB.prepare("SELECT login_id,version FROM admin_sessions WHERE token_hash=? AND expires_at>?").bind(digest(token), Date.now()).first<{login_id:string;version:number}>();
    const credential = row ? await currentAdminCredential() : null;
    if (!row || !credential || row.login_id!==credential.login_id || row.version!==credential.version) return null;
    const email = (env.ADMIN_EMAILS ?? "").split(",")[0]?.trim().toLowerCase() || "admin@sellerstrustnetwork.com";
    return { userId: `admin:${row.login_id}`, displayName: "Administrator", email, fullName: "Administrator" };
  } catch { return null; }
}

export async function requireChatGPTUser(
  returnTo: string,
): Promise<ChatGPTUser> {
  const user = await getChatGPTUser();
  if (user) return user;

  redirect(chatGPTSignInPath(returnTo));
}

export function chatGPTSignInPath(returnTo: string): string {
  const safeReturnTo = safeRelativeReturnPath(returnTo);
  return `/admin-login?returnTo=${encodeURIComponent(safeReturnTo)}`;
}

export function chatGPTSignOutPath(): string {
  return "/admin-logout";
}

function safeRelativeReturnPath(value: string): string {
  if (!value.startsWith("/") || value.startsWith("//")) return "/";

  let url: URL;
  try {
    url = new URL(value, "https://app.local");
  } catch {
    return "/";
  }
  if (url.origin !== "https://app.local") return "/";
  if (url.pathname === "/admin-login" || url.pathname === "/admin-logout") return "/admin";

  return `${url.pathname}${url.search}${url.hash}`;
}
