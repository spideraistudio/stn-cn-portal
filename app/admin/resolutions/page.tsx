import { redirect } from "next/navigation";
import { requireChatGPTUser } from "@/app/chatgpt-auth";
import { isConfiguredAdmin } from "@/lib/member-data";
import { reportDb } from "@/lib/report-store";
import { syncResolvedDisputesFromApprovals } from "@/lib/sync-resolved-disputes";
import { ReportShell } from "@/components/report-shell";
import {
  AdminResolutionsPanel,
  type ResolutionListItem,
} from "@/components/admin-resolutions-panel";

export const dynamic = "force-dynamic";

type Row = {
  id: string;
  report_id: string;
  resolved_on: string;
  resolved_amount_paise: number;
  description: string;
  status: string;
  admin_notes: string | null;
  created_at: number;
  reviewed_at: number | null;
  firm_name: string;
  category: string;
  company_name: string;
  login_id: string | null;
  mobile_number: string;
};

export default async function Page() {
  const user = await requireChatGPTUser("/admin/resolutions");
  if (!isConfiguredAdmin(user.email)) redirect("/join");

  await syncResolvedDisputesFromApprovals();

  const db = reportDb();
  const result = await db
    .prepare(
      "SELECT q.id,q.report_id,q.resolved_on,q.resolved_amount_paise,q.description,q.status,q.admin_notes,q.created_at,q.reviewed_at,r.firm_name,r.category,m.company_name,m.login_id,m.mobile_number FROM dispute_resolution_requests q JOIN seller_reports r ON r.id=q.report_id JOIN members m ON m.id=q.member_id ORDER BY CASE q.status WHEN 'pending' THEN 0 ELSE 1 END,q.created_at DESC LIMIT 100",
    )
    .all<Row>();

  const rows: ResolutionListItem[] = [];
  for (const row of result.results) {
    const documents = await db
      .prepare("SELECT id,name FROM dispute_resolution_documents WHERE request_id=?")
      .bind(row.id)
      .all<{ id: string; name: string }>();
    rows.push({
      ...row,
      resolved_amount_paise: Number(row.resolved_amount_paise || 0),
      documents: documents.results,
    });
  }

  const pending = rows.filter(r => r.status === "pending").length;

  return (
    <ReportShell
      admin
      title="Dispute resolutions"
      description={
        pending
          ? `${pending} request${pending === 1 ? "" : "s"} waiting for approve or reject.`
          : "Review member dispute resolution requests. Pending items appear first."
      }
    >
      <AdminResolutionsPanel rows={rows} />
    </ReportShell>
  );
}
