"use client";

import { useMemo, useState, type ReactNode } from "react";
import {
  ArrowLeft,
  Eye,
  FileText,
  KeyRound,
  MoreHorizontal,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MemberStatusForm } from "@/components/member-status-form";
import { AdminCredentials } from "@/components/admin-credentials";
import { SearchAccessToggle } from "@/components/search-access-toggle";
import { DetailSection, ListFrame } from "@/components/list-frame";

export type CompanyListItem = {
  id: string;
  companyName: string;
  loginId: string | null;
  gstin: string;
  status: string;
  category: string;
  otherCategory: string | null;
  responsiblePersonName: string;
  mobileNumber: string;
  email: string;
  address: string;
  taluka: string;
  district: string;
  state: string;
  pincode: string;
  createdAt: string;
  reportedDisputes: number;
  resolvedDisputes: number;
  hasCredentials: boolean;
  searchEnabled: boolean;
};

function statusClass(status: string) {
  if (status === "approved") return "bg-emerald-50 text-emerald-700";
  if (status === "pending") return "bg-amber-50 text-amber-800";
  if (status === "rejected") return "bg-rose-50 text-rose-700";
  return "bg-slate-100 text-slate-600";
}

function categoryLabel(item: CompanyListItem) {
  return item.category === "agriculture" ? "Agriculture" : item.otherCategory || "Other";
}

function initials(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "CO";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
}

function formatJoined(iso: string) {
  const d = new Date(iso);
  if (!Number.isFinite(d.valueOf())) return "—";
  return d.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    timeZone: "Asia/Kolkata",
  });
}

function Row({ label, value, strong = false }: { label: string; value: ReactNode; strong?: boolean }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-50 py-2.5 last:border-0">
      <span className="text-[13px] text-slate-500">{label}</span>
      <span
        className={`max-w-[60%] text-right text-[13px] ${strong ? "font-semibold text-slate-900" : "font-medium text-slate-800"}`}
      >
        {value || "—"}
      </span>
    </div>
  );
}

export function AdminCompaniesPanel({
  members,
  pendingCount,
  totalCount,
  pagination,
}: {
  members: CompanyListItem[];
  pendingCount: number;
  totalCount?: number;
  pagination?: ReactNode;
}) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = useMemo(
    () => members.find(m => m.id === selectedId) ?? null,
    [members, selectedId],
  );
  const shownTotal = totalCount ?? members.length;

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
                    Company details
                  </h2>
                  {selected.loginId && (
                    <span className="rounded-[12px] bg-slate-100 px-2 py-0.5 font-mono text-[11px] text-slate-600">
                      #{selected.loginId}
                    </span>
                  )}
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-[12px] px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${statusClass(selected.status)}`}
                  >
                    <span className="size-1.5 rounded-full bg-current opacity-80" />
                    {selected.status}
                  </span>
                </div>
                <p className="mt-0.5 truncate text-[12px] text-slate-500">{selected.companyName}</p>
              </div>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  type="button"
                  className="inline-flex h-9 items-center gap-2 rounded-[12px] border border-slate-200 bg-white px-3 text-[13px] font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Actions
                  <MoreHorizontal className="size-4" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48 rounded-[12px]">
                <DropdownMenuItem asChild className="gap-2">
                  <a href={`/admin/reports?status=approved&memberId=${selected.id}`}>
                    <FileText className="size-4" />
                    Seller reports
                  </a>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        }
      >
        <div className="grid gap-3 p-3 lg:grid-cols-[1.55fr_1fr] lg:gap-3 lg:p-3">
          <div className="space-y-3">
            <DetailSection title="Company summary">
              <div className="mb-3 flex items-center gap-3">
                <span className="grid size-11 place-items-center rounded-[12px] bg-[#ece8f8] text-[13px] font-bold text-[#5b4b8a]">
                  {initials(selected.companyName)}
                </span>
                <div className="min-w-0">
                  <p className="truncate text-[15px] font-semibold text-slate-900">
                    {selected.companyName}
                  </p>
                  <p className="truncate text-[12px] text-slate-500">
                    {selected.responsiblePersonName}
                  </p>
                </div>
              </div>
              <Row label="GSTIN" value={<span className="font-mono">{selected.gstin}</span>} />
              <Row label="Category" value={categoryLabel(selected)} />
              <Row label="Joined" value={formatJoined(selected.createdAt)} />
              <Row
                label="Address"
                value={`${selected.address}, ${selected.taluka}, ${selected.district}, ${selected.state} ${selected.pincode}`}
              />
            </DetailSection>

            <DetailSection title="Contact details">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-[13px]">
                  <thead>
                    <tr className="border-b border-slate-100 text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-500">
                      <th className="pb-2 pr-3">Name</th>
                      <th className="pb-2 pr-3">Email</th>
                      <th className="pb-2">Mobile</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="py-2.5 pr-3 font-semibold text-slate-900">
                        {selected.responsiblePersonName || "—"}
                      </td>
                      <td className="py-2.5 pr-3 text-slate-600">{selected.email || "—"}</td>
                      <td className="py-2.5 text-slate-600">{selected.mobileNumber || "—"}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </DetailSection>
          </div>

          <div className="space-y-3">
            <DetailSection title="Membership">
              <Row label="Status" value={<span className="capitalize">{selected.status}</span>} strong />
              <Row label="Member ID" value={selected.loginId || "Not issued"} />
              <Row label="Credentials" value={selected.hasCredentials ? "Issued" : "Not issued"} />
              <Row
                label="Seller search"
                value={selected.searchEnabled ? "Enabled" : "Disabled"}
                strong
              />
            </DetailSection>

            <DetailSection title="Dispute activity">
              <Row label="Reported" value={String(selected.reportedDisputes)} strong />
              <Row label="Resolved" value={String(selected.resolvedDisputes)} strong />
            </DetailSection>

            <DetailSection title="Actions">
              <div className="space-y-2">
                {selected.status === "approved" && (
                  <SearchAccessToggle
                    memberId={selected.id}
                    searchEnabled={selected.searchEnabled}
                  />
                )}
                <div className="flex flex-wrap items-center gap-2">
                  {["pending", "approved", "deactivated"].includes(selected.status) && (
                    <div className="min-w-0 flex-1">
                      <MemberStatusForm memberId={selected.id} status={selected.status} compact />
                    </div>
                  )}
                  {["pending", "approved"].includes(selected.status) && (
                    <div className="min-w-0 flex-1">
                      <AdminCredentials
                        memberId={selected.id}
                        pending={selected.status === "pending"}
                        hasCredentials={selected.hasCredentials}
                        compact
                      />
                    </div>
                  )}
                  <a
                    href={`/admin/reports?status=approved&memberId=${selected.id}`}
                    className="inline-flex h-10 min-w-0 flex-1 items-center justify-center gap-2 rounded-[12px] border border-slate-200 bg-white px-3 text-[13px] font-semibold text-[#15388c] hover:bg-slate-50"
                  >
                    <FileText className="size-4 shrink-0" />
                    Seller reports
                  </a>
                </div>
              </div>
            </DetailSection>
          </div>
        </div>
      </ListFrame>
    );
  }

  return (
    <ListFrame
      header={
        <div className="flex flex-wrap items-center gap-2 px-4 py-3">
          <span className="rounded-[12px] border border-amber-200 bg-amber-50 px-3 py-1 text-[12px] font-semibold text-amber-800">
            {pendingCount} awaiting review
          </span>
          <span className="rounded-[12px] border border-slate-200 bg-slate-50 px-3 py-1 text-[12px] text-slate-600">
            {shownTotal === 1 ? "1 company" : `${shownTotal} companies`}
          </span>
        </div>
      }
      footer={pagination}
    >
      {members.length === 0 ? (
        <p className="p-12 text-center text-slate-500">No company memberships match these filters.</p>
      ) : (
        <table className="w-full min-w-[900px] table-fixed text-left">
          <thead className="sticky top-0 z-10">
            <tr className="border-b border-slate-100 bg-[#fafbfc] text-[11px] font-semibold uppercase tracking-[0.12em] text-[#15388c]">
              <th className="w-[28%] px-4 py-3">Name</th>
              <th className="w-[14%] px-3 py-3">Mobile number</th>
              <th className="w-[16%] px-3 py-3">GSTIN</th>
              <th className="w-[12%] px-3 py-3">Status</th>
              <th className="w-[12%] px-3 py-3">Category</th>
              <th className="w-[12%] px-3 py-3">Joined</th>
              <th className="w-[6%] px-3 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {members.map(member => (
              <tr
                key={member.id}
                className="cursor-pointer border-b border-slate-100 last:border-0 transition hover:bg-slate-50/80"
                onClick={() => setSelectedId(member.id)}
              >
                <td className="px-4 py-3">
                  <div className="flex w-full items-center gap-3 text-left">
                    <span className="grid size-9 shrink-0 place-items-center rounded-[12px] bg-[#ece8f8] text-[11px] font-bold text-[#5b4b8a]">
                      {initials(member.companyName)}
                    </span>
                    <span className="min-w-0">
                      <span className="block truncate text-[13px] font-semibold text-slate-900">
                        {member.companyName || "—"}
                      </span>
                      <span className="mt-0.5 block truncate text-[12px] text-slate-500">
                        {member.email || member.responsiblePersonName || "—"}
                      </span>
                    </span>
                  </div>
                </td>
                <td className="px-3 py-3 text-[13px] text-slate-700">
                  {member.mobileNumber || "—"}
                </td>
                <td className="px-3 py-3">
                  <span className="inline-flex max-w-full truncate rounded-[12px] bg-slate-100 px-2 py-1 font-mono text-[11px] text-slate-700">
                    {member.gstin || "—"}
                  </span>
                </td>
                <td className="px-3 py-3">
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-[12px] px-2 py-1 text-[11px] font-semibold capitalize ${statusClass(member.status)}`}
                  >
                    <span className="size-1.5 rounded-full bg-current opacity-70" />
                    {member.status}
                  </span>
                </td>
                <td className="px-3 py-3 text-[13px] text-slate-700">{categoryLabel(member)}</td>
                <td className="whitespace-nowrap px-3 py-3 text-[13px] text-slate-600">
                  {formatJoined(member.createdAt)}
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
                        aria-label={`Actions for ${member.companyName}`}
                      >
                        <MoreHorizontal className="size-5" />
                      </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48 rounded-[12px]">
                      <DropdownMenuItem
                        className="gap-2"
                        onSelect={() => setSelectedId(member.id)}
                      >
                        <Eye className="size-4" />
                        View details
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild className="gap-2">
                        <a href={`/admin/reports?status=approved&memberId=${member.id}`}>
                          <FileText className="size-4" />
                          Seller reports
                        </a>
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="gap-2"
                        onSelect={() => setSelectedId(member.id)}
                      >
                        <KeyRound className="size-4" />
                        Manage access
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
