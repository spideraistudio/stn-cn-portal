"use client";

import { useMemo, useState, type ReactNode } from "react";
import {
  ArrowLeft,
  Building2,
  Eye,
  FileText,
  MoreHorizontal,
  Paperclip,
  Scale,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { DetailSection, ListFrame } from "@/components/list-frame";
import { ResolutionReview } from "@/components/resolution-review";

export type ResolutionListItem = {
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
  documents: { id: string; name: string }[];
};

function statusClass(status: string) {
  if (status === "approved") return "bg-emerald-50 text-emerald-700";
  if (status === "pending") return "bg-amber-50 text-amber-800";
  if (status === "rejected") return "bg-rose-50 text-rose-700";
  return "bg-slate-100 text-slate-600";
}

function money(paise: number | null | undefined) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format((Number(paise) || 0) / 100);
}

function safeDate(value: string | number | null | undefined) {
  if (value == null || value === "") return "—";
  const date =
    typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value)
      ? new Date(`${value}T00:00:00`)
      : new Date(value);
  if (Number.isNaN(date.valueOf())) return "—";
  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    timeZone: "Asia/Kolkata",
  });
}

function initials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "DR";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
}

function categoryLabel(category: string) {
  return category === "agriculture" ? "Agriculture" : category || "Other";
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

export function AdminResolutionsPanel({ rows }: { rows: ResolutionListItem[] }) {
  const sorted = useMemo(
    () =>
      [...rows].sort((a, b) => {
        if (a.status === "pending" && b.status !== "pending") return -1;
        if (b.status === "pending" && a.status !== "pending") return 1;
        return b.created_at - a.created_at;
      }),
    [rows],
  );

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = useMemo(
    () => sorted.find(r => r.id === selectedId) ?? null,
    [sorted, selectedId],
  );

  const pendingCount = sorted.filter(r => r.status === "pending").length;

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
                    Resolution request
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
                <p className="mt-0.5 truncate text-[12px] text-slate-500">{selected.firm_name}</p>
              </div>
            </div>
          </div>
        }
      >
        <div className="grid gap-3 p-3 lg:grid-cols-[1.55fr_1fr]">
          <div className="space-y-3">
            <DetailSection title="Request summary">
              <div className="mb-3 flex items-center gap-3">
                <span className="grid size-11 place-items-center rounded-[12px] bg-[#ece8f8] text-[13px] font-bold text-[#5b4b8a]">
                  {initials(selected.firm_name)}
                </span>
                <div className="min-w-0">
                  <p className="truncate text-[15px] font-semibold text-slate-900">
                    {selected.firm_name}
                  </p>
                  <p className="truncate text-[12px] text-slate-500">
                    {categoryLabel(selected.category)} · Submitted {safeDate(selected.created_at)}
                  </p>
                </div>
              </div>
              <Row label="Resolution date" value={safeDate(selected.resolved_on)} strong />
              <Row label="Resolved amount" value={money(selected.resolved_amount_paise)} strong />
              <Row label="Submitted" value={safeDate(selected.created_at)} />
              <Row
                label="Reviewed"
                value={selected.reviewed_at ? safeDate(selected.reviewed_at) : "—"}
              />
            </DetailSection>

            <DetailSection title="Member description">
              <p className="whitespace-pre-wrap break-words text-[13px] leading-6 text-slate-700">
                {selected.description}
              </p>
            </DetailSection>

            <DetailSection title="Supporting documents">
              {selected.documents.length ? (
                <div className="flex flex-col gap-2">
                  {selected.documents.map(doc => (
                    <a
                      key={doc.id}
                      href={`/api/resolution-document/${doc.id}`}
                      className="inline-flex max-w-full items-center gap-2 break-all text-[13px] font-medium text-[#15388c] underline"
                    >
                      <Paperclip className="size-3.5 shrink-0" />
                      {doc.name}
                    </a>
                  ))}
                </div>
              ) : (
                <p className="text-[13px] text-slate-500">No supporting document supplied.</p>
              )}
            </DetailSection>
          </div>

          <div className="space-y-3">
            <DetailSection title="Member">
              <Row
                label="Company"
                value={
                  <span className="inline-flex items-center gap-1.5">
                    <Building2 className="size-3.5 text-slate-400" />
                    {selected.company_name}
                  </span>
                }
                strong
              />
              <Row label="Member ID" value={selected.login_id || "Pending"} />
              <Row label="Mobile" value={selected.mobile_number} />
            </DetailSection>

            {selected.admin_notes ? (
              <DetailSection title="Admin note">
                <p className="text-[13px] leading-relaxed text-slate-700">{selected.admin_notes}</p>
              </DetailSection>
            ) : null}

            <DetailSection title="Actions">
              {selected.status === "pending" ? (
                <ResolutionReview id={selected.id} />
              ) : (
                <p className="text-[13px] text-slate-500">
                  This request was {selected.status}
                  {selected.reviewed_at ? ` on ${safeDate(selected.reviewed_at)}` : ""}.
                </p>
              )}
            </DetailSection>
          </div>
        </div>
      </ListFrame>
    );
  }

  return (
    <ListFrame
      header={
        <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-[12px] border border-slate-200 bg-slate-50 px-3 py-1 text-[12px] text-slate-600">
              {sorted.length === 0
                ? "No requests"
                : `${sorted.length} request${sorted.length === 1 ? "" : "s"}`}
            </span>
            {pendingCount > 0 ? (
              <span className="rounded-[12px] border border-amber-200 bg-amber-50 px-3 py-1 text-[12px] font-semibold text-amber-800">
                {pendingCount} pending
              </span>
            ) : null}
          </div>
        </div>
      }
    >
      {sorted.length === 0 ? (
        <div className="grid place-items-center p-12 text-center">
          <div className="mx-auto grid size-12 place-items-center rounded-[12px] bg-[#ece8f8] text-[#15388c]">
            <Scale className="size-5" />
          </div>
          <p className="mt-4 text-[15px] font-semibold text-slate-900">No resolution requests</p>
          <p className="mt-1 max-w-sm text-[13px] text-slate-500">
            When a member marks a dispute resolved, it will appear here for approve or reject.
          </p>
        </div>
      ) : (
        <table className="w-full min-w-[920px] table-fixed text-left">
          <thead className="sticky top-0 z-10">
            <tr className="border-b border-slate-100 bg-[#fafbfc] text-[11px] font-semibold uppercase tracking-[0.12em] text-[#15388c]">
              <th className="w-[24%] px-4 py-3">Seller</th>
              <th className="w-[18%] px-3 py-3">Member</th>
              <th className="w-[12%] px-3 py-3">Amount</th>
              <th className="w-[12%] px-3 py-3">Resolved on</th>
              <th className="w-[12%] px-3 py-3">Status</th>
              <th className="w-[12%] px-3 py-3">Submitted</th>
              <th className="w-[8%] px-3 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map(row => (
              <tr
                key={row.id}
                className="cursor-pointer border-b border-slate-100 last:border-0 transition hover:bg-slate-50/80"
                onClick={() => setSelectedId(row.id)}
              >
                <td className="px-4 py-3">
                  <div className="flex w-full items-center gap-3 text-left">
                    <span className="grid size-9 shrink-0 place-items-center rounded-[12px] bg-[#ece8f8] text-[11px] font-bold text-[#5b4b8a]">
                      {initials(row.firm_name)}
                    </span>
                    <span className="min-w-0">
                      <span className="block truncate text-[13px] font-semibold text-slate-900">
                        {row.firm_name}
                      </span>
                      <span className="mt-0.5 block truncate text-[12px] capitalize text-slate-500">
                        {categoryLabel(row.category)}
                      </span>
                    </span>
                  </div>
                </td>
                <td className="px-3 py-3 text-[13px] text-slate-700">
                  <span className="block truncate font-medium">{row.company_name}</span>
                  <span className="mt-0.5 block truncate text-[12px] text-slate-500">
                    {row.login_id || "ID pending"}
                  </span>
                </td>
                <td className="px-3 py-3 text-[13px] font-semibold text-slate-800">
                  {money(row.resolved_amount_paise)}
                </td>
                <td className="whitespace-nowrap px-3 py-3 text-[13px] text-slate-600">
                  {safeDate(row.resolved_on)}
                </td>
                <td className="px-3 py-3">
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-[12px] px-2 py-1 text-[11px] font-semibold capitalize ${statusClass(row.status)}`}
                  >
                    <span className="size-1.5 rounded-full bg-current opacity-70" />
                    {row.status}
                  </span>
                </td>
                <td className="whitespace-nowrap px-3 py-3 text-[13px] text-slate-600">
                  {safeDate(row.created_at)}
                </td>
                <td className="px-3 py-3 text-right" onClick={event => event.stopPropagation()}>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <button
                        type="button"
                        className="inline-flex size-8 items-center justify-center rounded-[12px] text-slate-500 transition hover:bg-slate-100 hover:text-slate-800"
                        aria-label={`Actions for ${row.firm_name}`}
                      >
                        <MoreHorizontal className="size-5" />
                      </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-44 rounded-[12px]">
                      <DropdownMenuItem className="gap-2" onSelect={() => setSelectedId(row.id)}>
                        <Eye className="size-4" />
                        View details
                      </DropdownMenuItem>
                      <DropdownMenuItem className="gap-2" onSelect={() => setSelectedId(row.id)}>
                        <FileText className="size-4" />
                        Open actions
                      </DropdownMenuItem>
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
