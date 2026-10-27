import { redirect } from "next/navigation";
import { getChatGPTUser } from "./chatgpt-auth";
import { isConfiguredAdmin } from "@/lib/member-data";
import { currentMember } from "@/lib/member-session";
import { LandingPage } from "@/components/landing-page";

export const dynamic = "force-dynamic";
export default async function Home() {
  const user = await getChatGPTUser();
  if(user&&isConfiguredAdmin(user.email))redirect("/admin");
  const member=await currentMember();
  if(member)redirect(member.mustChangePassword?"/member/password":"/member");
  // Anonymous visitor: show the public landing page.
  return <LandingPage/>;
}
