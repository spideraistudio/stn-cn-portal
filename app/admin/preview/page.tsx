import { redirect } from "next/navigation";
import { getChatGPTUser, chatGPTSignInPath } from "@/app/chatgpt-auth";
import { isConfiguredAdmin } from "@/lib/member-data";
import { MemberDashboard } from "@/components/member-dashboard";

export const dynamic = "force-dynamic";
export default async function MemberPreview() {
  const user = await getChatGPTUser();
  if (!user) redirect(chatGPTSignInPath("/admin/preview"));
  if (!isConfiguredAdmin(user.email)) redirect("/join");
  return <MemberDashboard preview profile={{ companyName: "Sample Agriculture Company", gstin: "DEMO — not a real GSTIN", address: "Sample office address", taluka: "Himatnagar", district: "Sabar Kantha", state: "Gujarat", pincode: "383001", responsiblePersonName: "Sample Member", mobileNumber: "Not provided (demo)", email: "member@example.com", approvedOn: "Preview only", categoryLabel: "Agriculture", requestedCategory: null }} />;
}
