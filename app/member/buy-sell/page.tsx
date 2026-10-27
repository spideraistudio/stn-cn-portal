import { ReportShell } from "@/components/report-shell";
import { redirect } from "next/navigation";
import { requireApprovedMember } from "@/lib/member-session";
import { categoryAccess } from "@/lib/category-access";
import { seedNotificationsEnabled } from "@/lib/seed-preferences";
import { SeedRequirementsLanding } from "@/components/seed-requirements-landing";

export const dynamic = "force-dynamic";

export default async function Page() {
  const member = await requireApprovedMember();
  if (categoryAccess(member)?.id !== "agriculture") redirect("/member");
  return <ReportShell title="Buy/Sell Requirements" description="Create buying requirements and quote on eligible requests from other members."><SeedRequirementsLanding initialEnabled={await seedNotificationsEnabled(member.id)} /></ReportShell>;
}
