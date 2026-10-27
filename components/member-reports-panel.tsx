"use client";
import {CaseNumberInfo} from "./case-number-info";

import { useMemo, useState, type ReactNode } from "react";
import {
  ArrowLeft,
  Eye,
  FilePenLine,
  FileText,
  MoreHorizontal,
  Scale,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { DetailSection, ListFrame } from "@/components/list-frame";
import type { ReportView } from "@/components/report-cards";

function statusClass(status: string) {
  if (status === "approved") return "bg-emerald-50 text-emerald-700";
  if (status === "pending") return "bg-amber-50 text-amber-800";
  if (status === "rejected") return "bg-rose-50 text-rose-700";
  return "bg-slate-100 text-slate-600";
}

function initials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "SR";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
}

function money(paise: number | null | undefined) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format((Number(paise) || 0) / 100);
}

function monthLabel(value: string) {
  const match = String(value || "").match(/^(\d{4})-(\d{2})$/);
  if (!match) return "Not provided";
  const date = new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, 1));
  if (Number.isNaN(date.valueOf())) return "Not provided";
  return new Intl.DateTimeFormat("en-IN", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(date);
}

function safeDate(value: string | number | Date | null | undefined) {
  if (value == null || value === "") return "—";
  const date =
    value instanceof Date
      ? value
      : typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value)
        ? new Date(`${value}T00:00:00`)
        : new Date(value);
  if (Number.isNaN(date.valueOf())) return "—";
  return date.toLocaleDateString("en-IN", { timeZone: "Asia/Kolkata" });
}

function Row({
  label,
  value,
  strong = false,
}: {
  label: string;
  value: ReactNode;
  strong?: boolean;
}) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-50 py-2.5 last:border-0">
      <span className="text-[13px] text-slate-500">{label}</span>
      <span
        className={`max-w-[65%] text-right text-[13px] ${
          strong ? "font-semibold text-slate-900" : "font-medium text-slate-800"
        }`}
      >
        {value || "—"}
      </span>
    </div>
  );
}

function actionButtons(report: ReportView) {
  const canEdit =
    ["pending", "approved"].includes(report.status) &&
    (report.status === "pending" || !report.pending_resolution);
  const canResolve =
    report.status === "approved" &&
    !!report.dispute &&
    !report.dispute_resolved &&
    !report.pending_resolution;

  return (
    <div className="flex flex-wrap gap-2">
      {canEdit && (
        <a
          href={`/member/reports/${report.id}/edit`}
          className="inline-flex h-9 items-center gap-1.5 rounded-[12px] border border-slate-200 bg-white px-3 text-[12px] font-semibold text-[#15388c] transition hover:bg-slate-50"
        >
          <FilePenLine className="size-3.5" />
          {report.status === "approved" ? "Request changes" : "Edit pending"}
        </a>
      )}
      {canResolve && (
        <a
          href={`/member/reports/${report.id}/resolve`}
          className="inline-flex h-9 items-center gap-1.5 rounded-[12px] bg-[#15388c] px-3 text-[12px] font-semibold text-white transition hover:bg-[#102d74]"
        >
          <Scale className="size-3.5" />
          Mark dispute resolved
        </a>
      )}
      {!!report.pending_resolution && (
        <span className="inline-flex h-9 items-center rounded-[12px] bg-amber-50 px-3 text-[12px] font-semibold text-amber-800">
          Resolution awaiting review
        </span>
      )}
      {!canEdit && !canResolve && !report.pending_resolution && (
        <span className="text-[12px] text-slate-500">No actions available</span>
      )}
    </div>
  );
}

export function MemberReportsPanel({
  reports,
  total,
  pagination,
  emptySearch = false,
}: {
  reports: ReportView[];
  total: number;
  pagination?: ReactNode;
  emptySearch?: boolean;
}) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = useMemo(
    () => reports.find(r => r.id === selectedId) ?? null,
    [reports, selectedId],
  );

  if (selected) {
    return (
      <ListFrame
        tone="detail"
        header={
          <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
            <div className="flex min-w-0 flex-wrap items-center gap-2.5">
              <button
                type="button"
                onClick={() => setSelectedId(null)}
                className="inline-flex size-9 items-center justify-center rounded-[12px] border border-slate-200 text-slate-700 transition hover:bg-slate-50"
                aria-label="Back to list"
              >
                <ArrowLeft className="size-4" />
              </button>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="truncate text-[16px] font-semibold text-slate-900">
                    Report details
                  </h2>
                  <span className="rounded-[12px] bg-slate-100 px-2 py-0.5 font-mono text-[11px] text-slate-600">
                    #{selected.id.slice(0, 8)}
                  </span>
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-[12px] px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${statusClass(selected.status)}`}
                  >
                    <span className="size-1.5 rounded-full bg-current opacity-80" />
                    {selected.status}
                  </span>
                </div>
                <p className="mt-0.5 truncate text-[12px] text-slate-500">
                  {selected.firm_name}
                </p>
              </div>
            </div>
            <div className="hidden sm:block">{actionButtons(selected)}</div>
          </div>
        }
      >
        <div className="grid gap-3 p-3 lg:grid-cols-[1.55fr_1fr]">
          <div className="space-y-3">
            <DetailSection title="Seller">
              <div className="mb-3 flex items-center gap-3">
                <span className="grid size-11 place-items-center rounded-[12px] bg-[#ece8f8] text-[13px] font-bold text-[#5b4b8a]">
                  {initials(selected.firm_name)}
                </span>
                <div className="min-w-0">
                  <p className="truncate text-[15px] font-semibold text-slate-900">
                    {selected.firm_name}
                  </p>
                  <p className="truncate text-[12px] text-slate-500">
                    {selected.taluka}, {selected.district}, {selected.state}
                    {selected.pincode ? ` · PIN ${selected.pincode}` : ""}
                  </p>
                </div>
              </div>
              <Row
                label="GSTIN"
                value={<span className="font-mono">{selected.gstin}</span>}
              />
              <Row label="Rating" value={`${selected.rating}/10`} strong />
              <Row label="Submitted" value={safeDate(selected.created_at)} />
            </DetailSection>

            <DetailSection title="Experience summary">
              <p className="whitespace-pre-wrap break-words text-[13px] leading-6 text-slate-700">
                {selected.summary}
              </p>
            </DetailSection>

            {!!Number(selected.dispute) && (
              <DetailSection title="Commercial dispute">
                <Row
                  label="Status"
                  value={
                    selected.dispute_resolved ||
                    ((Number(selected.amount_paise) || 0) > 0 &&
                      (Number(selected.resolved_amount_paise) || 0) >=
                        (Number(selected.amount_paise) || 0))
                      ? "Resolved"
                      : (Number(selected.resolved_amount_paise) || 0) > 0
                        ? "Partially resolved"
                        : "Open"
                  }
                  strong
                />
                <Row
                  label="Type"
                  value={`${selected.dispute_type?.replaceAll("_", " ") || "—"}${
                    selected.dispute_other ? ` — ${selected.dispute_other}` : ""
                  }`}
                />
                <Row label="Amount" value={money(selected.amount_paise)} strong />
                <Row
                  label="Period"
                  value={
                    selected.dispute_start_month
                      ? `${monthLabel(selected.dispute_start_month)} – ${
                          selected.dispute_ongoing
                            ? "Ongoing"
                            : selected.dispute_end_month
                              ? monthLabel(selected.dispute_end_month)
                              : "Not provided"
                        }`
                      : "Not provided"
                  }
                />
                {selected.resolved_amount_paise ? (
                  <Row
                    label="Resolved amount"
                    value={money(selected.resolved_amount_paise)}
                  />
                ) : null}
                {selected.dispute_resolved && selected.resolved_on ? (
                  <>
                    <Row label="Resolved on" value={safeDate(selected.resolved_on)} />
                    {selected.resolution_summary ? (
                      <p className="mt-2 whitespace-pre-wrap text-[13px] text-slate-600">
                        {selected.resolution_summary}
                      </p>
                    ) : null}
                  </>
                ) : null}
              </DetailSection>
            )}

            {!!Number(selected.legal) && (
              <DetailSection title="Legal proceedings">
                <CaseNumberInfo report={selected}/>
              </DetailSection>
            )}
          </div>

          <div className="space-y-3">
            <DetailSection title="Actions">
              {actionButtons(selected)}
              {selected.latest_resolution_status === "rejected" && (
                <p className="mt-3 rounded-[12px] border border-rose-200 bg-rose-50 px-3 py-2 text-[12px] text-rose-800">
                  Resolution request rejected
                  {selected.latest_resolution_notes
                    ? `: ${selected.latest_resolution_notes}`
                    : "."}
                </p>
              )}
            </DetailSection>

            <DetailSection title="Review">
              <div className="flex flex-wrap gap-2">
                {selected.report_reviewed ? (
                  <span className="rounded-[12px] bg-blue-50 px-3 py-1 text-[11px] font-semibold text-blue-800">
                    Admin reviewed
                  </span>
                ) : null}
                {selected.identity_checked ? (
                  <span className="rounded-[12px] bg-emerald-50 px-3 py-1 text-[11px] font-semibold text-emerald-800">
                    Identity checked
                  </span>
                ) : null}
                {selected.evidence_reviewed ? (
                  <span className="rounded-[12px] bg-amber-50 px-3 py-1 text-[11px] font-semibold text-amber-800">
                    Evidence reviewed
                  </span>
                ) : null}
                {!selected.report_reviewed &&
                  !selected.identity_checked &&
                  !selected.evidence_reviewed && (
                    <span className="text-[13px] text-slate-500">Awaiting admin review</span>
                  )}
              </div>
              {selected.review_notes ? (
                <p className="mt-3 text-[13px] text-slate-600">
                  Review note: {selected.review_notes}
                </p>
              ) : null}
            </DetailSection>

            {selected.documents?.length ? (
              <DetailSection title="Documents">
                <div className="flex flex-col gap-2">
                  {selected.documents.map(document => (
                    <a
                      key={document.id}
                      href={`/api/report-document/${document.id}`}
                      className="break-all text-[13px] font-medium text-[#15388c] underline"
                    >
                      {document.name}
                    </a>
                  ))}
                </div>
              </DetailSection>
            ) : null}

            {selected.resolution_requests?.length ? (
              <DetailSection
                title={`Resolution history (${selected.resolution_requests.length})`}
              >
                <div className="space-y-3">
                  {selected.resolution_requests.map(request => (
                    <div
                      key={request.id}
                      className="rounded-[12px] border border-slate-100 bg-slate-50 px-3 py-2.5"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="text-[12px] font-semibold text-slate-800">
                          {safeDate(request.resolved_on)}
                        </p>
                        <span className="text-[11px] font-semibold capitalize text-slate-600">
                          {request.status}
                        </span>
                      </div>
                      {request.resolved_amount_paise ? (
                        <p className="mt-1 text-[12px] text-slate-700">
                          {money(request.resolved_amount_paise)}
                        </p>
                      ) : null}
                      <p className="mt-1 whitespace-pre-wrap text-[12px] text-slate-600">
                        {request.description}
                      </p>
                      {request.admin_notes && (
                        <p className="mt-1 text-[12px] text-slate-500">
                          Admin: {request.admin_notes}
                        </p>
                      )}
                      {request.documents.map(document => (
                        <a
                          key={document.id}
                          href={`/api/resolution-document/${document.id}`}
                          className="mt-1 block break-all text-[12px] font-medium text-[#15388c] underline"
                        >
                          {document.name}
                        </a>
                      ))}
                    </div>
                  ))}
                </div>
              </DetailSection>
            ) : null}
          </div>
        </div>
      </ListFrame>
    );
  }

  return (
    <ListFrame
      header={
        <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
          <span className="rounded-[12px] border border-slate-200 bg-slate-50 px-3 py-1 text-[12px] text-slate-600">
            {total === 0
              ? "No reports"
              : `${total} report${total === 1 ? "" : "s"}`}
          </span>
        </div>
      }
      footer={pagination}
    >
      {reports.length === 0 ? (
        <div className="grid place-items-center px-4 py-16 text-center">
          <span className="grid size-11 place-items-center rounded-[12px] bg-slate-100 text-slate-500">
            <FileText className="size-5" />
          </span>
          <p className="mt-3 text-[14px] font-semibold text-slate-900">
            {emptySearch ? "No matching reports" : "No reports yet"}
          </p>
          <p className="mt-1 max-w-sm text-[12px] text-slate-500">
            {emptySearch
              ? "Try a different search, or clear filters."
              : "Submit a business experience report to see it here."}
          </p>
          {!emptySearch && (
            <a
              href="/member/submit-report"
              className="mt-4 inline-flex h-9 items-center rounded-[12px] bg-[#15388c] px-3.5 text-[12px] font-semibold text-white hover:bg-[#102d74]"
            >
              Submit report
            </a>
          )}
        </div>
      ) : (
        <table className="w-full min-w-[760px] table-fixed text-left">
          <thead className="sticky top-0 z-10">
            <tr className="border-b border-slate-100 bg-[#fafbfc] text-[11px] font-semibold uppercase tracking-[0.12em] text-[#15388c]">
              <th className="w-[34%] px-4 py-3">Seller</th>
              <th className="w-[12%] px-3 py-3">Rating</th>
              <th className="w-[14%] px-3 py-3">Status</th>
              <th className="w-[14%] px-3 py-3">Dispute</th>
              <th className="w-[14%] px-3 py-3">Submitted</th>
              <th className="w-[12%] px-3 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {reports.map(report => (
              <tr
                key={report.id}
                className="cursor-pointer border-b border-slate-100 last:border-0 transition hover:bg-slate-50/80"
                onClick={() => setSelectedId(report.id)}
              >
                <td className="px-4 py-3">
                  <div className="flex w-full items-center gap-3 text-left">
                    <span className="grid size-9 shrink-0 place-items-center rounded-[12px] bg-[#ece8f8] text-[11px] font-bold text-[#5b4b8a]">
                      {initials(report.firm_name)}
                    </span>
                    <span className="min-w-0">
                      <span className="block truncate text-[13px] font-semibold text-slate-900">
                        {report.firm_name}
                      </span>
                      <span className="mt-0.5 block truncate font-mono text-[12px] text-slate-500">
                        {report.gstin || "—"}
                      </span>
                    </span>
                  </div>
                </td>
                <td className="px-3 py-3 text-[13px] font-semibold text-slate-800">
                  {report.rating}/10
                </td>
                <td className="px-3 py-3">
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-[12px] px-2 py-1 text-[11px] font-semibold capitalize ${statusClass(report.status)}`}
                  >
                    <span className="size-1.5 rounded-full bg-current opacity-70" />
                    {report.status}
                  </span>
                </td>
                <td className="px-3 py-3 text-[12px] text-slate-600">
                  {!Number(report.dispute)
                    ? "—"
                    : report.dispute_resolved ||
                        ((Number(report.amount_paise) || 0) > 0 &&
                          (Number(report.resolved_amount_paise) || 0) >=
                            (Number(report.amount_paise) || 0))
                      ? "Resolved"
                      : report.pending_resolution
                        ? "Pending"
                        : (Number(report.resolved_amount_paise) || 0) > 0
                          ? "Partial"
                          : "Open"}
                </td>
                <td className="whitespace-nowrap px-3 py-3 text-[13px] text-slate-600">
                  {safeDate(report.created_at)}
                </td>
                <td
                  className="px-3 py-3 text-right"
                  onClick={event => event.stopPropagation()}
                >
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <button
                        type="button"
                        className="inline-flex size-8 items-center justify-center rounded-[12px] text-slate-500 transition hover:bg-slate-100 hover:text-slate-800"
                        aria-label={`Actions for ${report.firm_name}`}
                      >
                        <MoreHorizontal className="size-5" />
                      </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48 rounded-[12px]">
                      <DropdownMenuItem
                        className="gap-2"
                        onSelect={() => setSelectedId(report.id)}
                      >
                        <Eye className="size-4" />
                        View details
                      </DropdownMenuItem>
                      {["pending", "approved"].includes(report.status) &&
                        (report.status === "pending" || !report.pending_resolution) && (
                          <DropdownMenuItem
                            className="gap-2"
                            onSelect={() => {
                              window.location.href = `/member/reports/${report.id}/edit`;
                            }}
                          >
                            <FilePenLine className="size-4" />
                            {report.status === "approved"
                              ? "Request changes"
                              : "Edit pending"}
                          </DropdownMenuItem>
                        )}
                      {report.status === "approved" &&
                        !!report.dispute &&
                        !report.dispute_resolved &&
                        !report.pending_resolution && (
                          <DropdownMenuItem
                            className="gap-2"
                            onSelect={() => {
                              window.location.href = `/member/reports/${report.id}/resolve`;
                            }}
                          >
                            <Scale className="size-4" />
                            Resolve dispute
                          </DropdownMenuItem>
                        )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </ListFrame>
  );
}
