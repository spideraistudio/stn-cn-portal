/* Inline-SQL row types are loosely typed (any) for brevity on dense query pages. */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { requireApprovedMember } from "@/lib/member-session";
import { reportDb } from "@/lib/report-store";
import { ReportShell } from "@/components/report-shell";
import { PilotIssueForm } from "@/components/pilot-issue-form";

export const dynamic = "force-dynamic";

export default async function Page() {
  const member = await requireApprovedMember();
  const result = await reportDb()
    .prepare(
      "SELECT id,issue_type,page_url,description,status,admin_notes,created_at,screenshot_name FROM pilot_issues WHERE member_id=? ORDER BY created_at DESC LIMIT 50",
    )
    .bind(member.id)
    .all<any>();

  return (
    <ReportShell
      title="Report a problem"
      description="Send a problem to the administrator and follow its testing status."
    >
      <PilotIssueForm issues={result.results} />
    </ReportShell>
  );
}
