import { NextResponse } from "next/server";
import { getChatGPTUser } from "@/app/chatgpt-auth";
import { isConfiguredAdmin } from "@/lib/member-data";
import { currentMember } from "@/lib/member-session";

export const dynamic = "force-dynamic";

/**
 * Brand-logo destination used across every page.
 *
 * Uses a relative Location header so production (often bound to 0.0.0.0 behind
 * a reverse proxy) never sends browsers to http://0.0.0.0:port/.
 */
export async function GET() {
  const path = await homePath();
  return new NextResponse(null, {
    status: 307,
    headers: {
      Location: path,
      "Cache-Control": "private, no-store",
    },
  });
}

async function homePath(): Promise<string> {
  try {
    const admin = await getChatGPTUser();
    if (admin && isConfiguredAdmin(admin.email)) return "/admin";
  } catch {
    // Session lookup failures must never block the logo; fall through.
  }

  try {
    const member = await currentMember();
    if (member) return member.mustChangePassword ? "/member/password" : "/member";
  } catch {
    // Same here — an unreachable database still returns the public home page.
  }

  return process.env.PORTAL_MODE === "combined" ? "/stn" : "/";
}
