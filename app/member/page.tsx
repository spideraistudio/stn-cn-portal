import { requireApprovedMember } from "@/lib/member-session";
import { dashboardProfile } from "@/lib/dashboard-profile";
import { MemberDashboard } from "@/components/member-dashboard";
import { unreadNotifications } from "@/lib/notifications";

export const dynamic = "force-dynamic";
export default async function MemberPage() {
  const member = await requireApprovedMember();
  const notificationCount=await unreadNotifications("member",member.id);
  return <MemberDashboard profile={dashboardProfile(member)} notificationCount={notificationCount} />;
}
