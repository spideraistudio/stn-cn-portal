import { notFound, redirect } from "next/navigation";
import { requireApprovedMember } from "@/lib/member-session";
import { categoryAccess } from "@/lib/category-access";
import { reportDb, maskReport, safeReportColumns } from "@/lib/report-store";
import { ReportForm, type EditableReport } from "@/components/report-form";
import { ReportShell } from "@/components/report-shell";

export const dynamic = "force-dynamic";

export default async function EditReportPage({ params }: { params: Promise<{ id: string }> }) {
  const member = await requireApprovedMember();
  const category = categoryAccess(member);
  if (!category) redirect("/member/reports");
  const { id } = await params;
  const db = reportDb();
  const row = await db.prepare(`SELECT ${safeReportColumns} FROM seller_reports r JOIN sellers s ON s.id=r.seller_id WHERE r.id=? AND r.member_id=? AND r.category=? AND r.status IN ('pending','approved')`).bind(id, member.id, category.id).first<Record<string, unknown>>();
  if (!row) notFound();
  const documents = await db.prepare("SELECT id,name FROM report_documents WHERE report_id=? ORDER BY name").bind(id).all<{ id: string; name: string }>();
  const report = { ...maskReport(row), documents: documents.results } as EditableReport;
  return <ReportShell title={report.status === "approved" ? "Request changes to approved report" : "Edit pending report"} description={report.status === "approved" ? "Your changes will be reviewed by the administrator. The current approved version stays searchable until the revision is approved." : "Update your report and supporting documents before the administrator decides it."}><ReportForm initial={report} /></ReportShell>;
}
