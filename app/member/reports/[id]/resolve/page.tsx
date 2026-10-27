import { notFound, redirect } from "next/navigation";
import { requireApprovedMember } from "@/lib/member-session";
import { reportDb } from "@/lib/report-store";
import { ReportShell } from "@/components/report-shell";
import { ResolutionRequestForm } from "@/components/resolution-request-form";

export const dynamic = "force-dynamic";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const member = await requireApprovedMember();
  const { id } = await params;
  const report = await reportDb()
    .prepare(
      "SELECT id,firm_name,dispute,dispute_resolved,status,amount_paise,resolved_amount_paise FROM seller_reports WHERE id=? AND member_id=?",
    )
    .bind(id, member.id)
    .first<{
      id: string;
      firm_name: string;
      dispute: number;
      dispute_resolved: number;
      status: string;
      amount_paise: number | null;
      resolved_amount_paise: number | null;
    }>();

  if (!report) notFound();
  if (report.status !== "approved" || !report.dispute || report.dispute_resolved) {
    redirect("/member/reports");
  }

  const pending = await reportDb()
    .prepare(
      "SELECT id FROM dispute_resolution_requests WHERE report_id=? AND status='pending'",
    )
    .bind(id)
    .first();
  if (pending) redirect("/member/reports");

  const remainingAmountPaise = Math.max(
    0,
    Number(report.amount_paise || 0) - Number(report.resolved_amount_paise || 0),
  );

  return (
    <ReportShell
      title="Mark dispute resolved"
      description={`Submit the resolution of the dispute reported for ${report.firm_name}. The report remains open until the administrator approves this request.`}
    >
      <ResolutionRequestForm
        reportId={id}
        remainingAmountPaise={remainingAmountPaise}
      />
    </ReportShell>
  );
}
