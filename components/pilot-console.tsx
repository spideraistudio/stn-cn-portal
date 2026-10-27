/* Inline-SQL row types are loosely typed (any) for brevity on dense query pages. */
/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useMemo, useState } from "react";
import { ArrowRight, Database, FileWarning, FlaskConical, HardDrive } from "lucide-react";
import { readJsonResponse } from "@/lib/client-response";
import { DetailSection, ListFrame } from "@/components/list-frame";

type Issue = {
  id: string;
  company_name: string;
  login_id: string | null;
  issue_type: string;
  page_url: string;
  description: string;
  status: string;
  admin_notes: string | null;
  created_at: number;
  screenshot_name: string | null;
};
type Check = {
  id: string;
  check_key: string;
  label: string;
  area: string;
  status: string;
  notes: string | null;
};
type PilotMember = {
  id: number;
  company_name: string;
  login_id: string | null;
  is_pilot: number;
  report_count: number;
};

const tabs = [
  { id: "companies", label: "Pilot companies" },
  { id: "checklist", label: "Checklist" },
  { id: "issues", label: "Problem reports" },
] as const;

type TabId = (typeof tabs)[number]["id"];

function statusClass(status: string) {
  if (status === "pass" || status === "closed") return "bg-emerald-50 text-emerald-700";
  if (status === "fail" || status === "open") return "bg-rose-50 text-rose-700";
  if (status === "blocked" || status === "in_progress") return "bg-amber-50 text-amber-800";
  if (status === "ready_for_retest") return "bg-blue-50 text-blue-800";
  return "bg-slate-100 text-slate-600";
}

const control =
  "h-10 w-full rounded-[12px] border border-slate-200 bg-white px-3 text-[13px] text-slate-800 outline-none focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/12";

export function PilotConsole({
  issues,
  checks,
  members,
  health,
}: {
  issues: Issue[];
  checks: Check[];
  members: PilotMember[];
  health: {
    database: boolean;
    fileStorage: boolean;
    openIssues: number;
    pilotReports: number;
    pendingWork: number;
  };
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<TabId>("companies");
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);
  const [preview, setPreview] = useState<{
    members: number;
    reports: number;
    documents: number;
    issues: number;
  } | null>(null);

  const selectedIssue = useMemo(
    () => issues.find(issue => issue.id === selectedIssueId) ?? null,
    [issues, selectedIssueId],
  );

  const pilotCount = members.filter(m => m.is_pilot).length;
  const openIssues = issues.filter(i => i.status !== "closed").length;

  async function send(body: object) {
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/admin/pilot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await readJsonResponse<any>(response);
      if (!response.ok) throw new Error(data.error || "Unable to update pilot testing.");
      if (data.preview) {
        setPreview(data.preview);
        setBusy(false);
      } else window.location.reload();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to update pilot testing.");
      setBusy(false);
    }
  }

  const healthCards = [
    {
      label: "Database",
      value: health.database ? "Available" : "Down",
      icon: Database,
      tone: health.database ? "text-emerald-800" : "text-rose-700",
    },
    {
      label: "File storage",
      value: health.fileStorage ? "Available" : "Down",
      icon: HardDrive,
      tone: health.fileStorage ? "text-emerald-800" : "text-rose-700",
    },
    {
      label: "Open issues",
      value: String(health.openIssues),
      icon: FileWarning,
      tone: "text-amber-800",
    },
    {
      label: "Pilot reports",
      value: String(health.pilotReports),
      icon: FlaskConical,
      tone: "text-[#15388c]",
    },
    {
      label: "Pending work",
      value: String(health.pendingWork),
      icon: FileWarning,
      tone: "text-slate-800",
    },
  ];

  if (selectedIssue) {
    return (
      <ListFrame
        tone="detail"
        header={
          <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
            <div className="flex min-w-0 items-center gap-2.5">
              <button
                type="button"
                onClick={() => setSelectedIssueId(null)}
                className="inline-flex h-9 items-center rounded-[12px] border border-slate-200 px-3 text-[13px] font-semibold text-slate-700 hover:bg-slate-50"
              >
                ← Back
              </button>
              <div className="min-w-0">
                <h2 className="truncate text-[15px] font-semibold text-slate-900">
                  {selectedIssue.company_name}
                </h2>
                <p className="text-[12px] text-slate-500">
                  Ticket {selectedIssue.id.slice(0, 8).toUpperCase()} ·{" "}
                  {selectedIssue.issue_type.replaceAll("_", " ")}
                </p>
              </div>
            </div>
            <span
              className={`rounded-[12px] px-2.5 py-1 text-[11px] font-semibold capitalize ${statusClass(selectedIssue.status)}`}
            >
              {selectedIssue.status.replaceAll("_", " ")}
            </span>
          </div>
        }
      >
        <div className="grid gap-3 p-3 lg:grid-cols-[1.4fr_1fr]">
          <DetailSection title="Problem details">
            <p className="text-[12px] text-slate-500">{selectedIssue.page_url}</p>
            <p className="mt-3 whitespace-pre-wrap text-[13px] leading-6 text-slate-700">
              {selectedIssue.description}
            </p>
            {selectedIssue.screenshot_name ? (
              <a
                href={`/api/pilot-screenshot/${selectedIssue.id}`}
                target="_blank"
                className="mt-3 inline-flex items-center gap-1 text-[13px] font-semibold text-[#15388c]"
              >
                View screenshot
                <ArrowRight className="size-3.5" />
              </a>
            ) : null}
          </DetailSection>
          <DetailSection title="Actions">
            <form
              className="space-y-3"
              onSubmit={event => {
                event.preventDefault();
                const values = Object.fromEntries(new FormData(event.currentTarget));
                send({ action: "issue", id: selectedIssue.id, ...values });
              }}
            >
              <label className="block text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                Status
                <select name="status" defaultValue={selectedIssue.status} className={`mt-1.5 ${control}`}>
                  <option value="open">Open</option>
                  <option value="in_progress">In progress</option>
                  <option value="ready_for_retest">Ready for retest</option>
                  <option value="closed">Closed</option>
                </select>
              </label>
              <label className="block text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                Admin note
                <input
                  name="notes"
                  defaultValue={selectedIssue.admin_notes || ""}
                  placeholder="Member-visible note"
                  className={`mt-1.5 ${control}`}
                />
              </label>
              <button
                disabled={busy}
                className="inline-flex h-10 w-full items-center justify-center rounded-[12px] bg-[#15388c] text-[13px] font-semibold text-white hover:bg-[#102d74] disabled:opacity-50"
              >
                Update ticket
              </button>
            </form>
          </DetailSection>
        </div>
      </ListFrame>
    );
  }

  return (
    <ListFrame
      header={
        <div className="space-y-3 px-4 py-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-[12px] border border-amber-200 bg-amber-50 px-3 py-1 text-[12px] font-semibold text-amber-800">
              {openIssues} open issues
            </span>
            <span className="rounded-[12px] border border-slate-200 bg-slate-50 px-3 py-1 text-[12px] text-slate-600">
              {pilotCount} pilot companies
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {tabs.map(item => (
              <button
                key={item.id}
                type="button"
                onClick={() => setTab(item.id)}
                className={`inline-flex h-9 items-center rounded-[12px] px-3 text-[12px] font-semibold transition ${
                  tab === item.id
                    ? "bg-[#15388c] text-white"
                    : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      }
    >
      {error ? (
        <p role="alert" className="m-3 rounded-[12px] bg-rose-50 p-3 text-[13px] text-rose-700">
          {error}
        </p>
      ) : null}

      <div className="grid grid-cols-2 gap-2 border-b border-slate-100 p-3 sm:grid-cols-3 lg:grid-cols-5">
        {healthCards.map(card => {
          const Icon = card.icon;
          return (
            <div
              key={card.label}
              className="rounded-[12px] border border-slate-200 bg-[#fafbfc] px-3 py-2.5"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-[11px] text-slate-500">{card.label}</p>
                <Icon className="size-3.5 text-slate-400" />
              </div>
              <p className={`mt-1 text-[15px] font-semibold ${card.tone}`}>{card.value}</p>
            </div>
          );
        })}
      </div>

      {tab === "companies" ? (
        members.length === 0 ? (
          <p className="p-10 text-center text-[13px] text-slate-500">No approved companies yet.</p>
        ) : (
          <table className="w-full min-w-[720px] table-fixed text-left">
            <thead className="sticky top-0 z-10">
              <tr className="border-b border-slate-100 bg-[#fafbfc] text-[11px] font-semibold uppercase tracking-[0.12em] text-[#15388c]">
                <th className="w-[40%] px-4 py-3">Company</th>
                <th className="w-[18%] px-3 py-3">Member ID</th>
                <th className="w-[14%] px-3 py-3">Reports</th>
                <th className="w-[14%] px-3 py-3">Status</th>
                <th className="w-[14%] px-3 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {members.map(member => (
                <tr key={member.id} className="border-b border-slate-100 last:border-0">
                  <td className="px-4 py-3 text-[13px] font-semibold text-slate-900">
                    {member.company_name}
                  </td>
                  <td className="px-3 py-3 font-mono text-[12px] text-slate-600">
                    {member.login_id || "—"}
                  </td>
                  <td className="px-3 py-3 text-[13px] text-slate-700">{member.report_count}</td>
                  <td className="px-3 py-3">
                    <span
                      className={`inline-flex rounded-[12px] px-2 py-1 text-[11px] font-semibold ${
                        member.is_pilot
                          ? "bg-amber-50 text-amber-800"
                          : "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {member.is_pilot ? "Pilot" : "Live"}
                    </span>
                  </td>
                  <td className="px-3 py-3 text-right">
                    <button
                      type="button"
                      disabled={busy}
                      onClick={() =>
                        send({ action: "member", memberId: member.id, isPilot: !member.is_pilot })
                      }
                      className="inline-flex h-8 items-center gap-1 rounded-[12px] border border-slate-200 px-2.5 text-[12px] font-semibold text-[#15388c] hover:bg-slate-50 disabled:opacity-50"
                    >
                      {member.is_pilot ? "Remove" : "Mark pilot"}
                      <ArrowRight className="size-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      ) : null}

      {tab === "checklist" ? (
        <div className="divide-y divide-slate-100">
          {checks.map(check => (
            <form
              key={check.id}
              className="grid gap-2 px-4 py-3 md:grid-cols-[1.3fr_0.7fr_1fr_auto] md:items-center"
              onSubmit={event => {
                event.preventDefault();
                const values = Object.fromEntries(new FormData(event.currentTarget));
                send({ action: "check", id: check.id, ...values });
              }}
            >
              <div className="min-w-0">
                <p className="text-[13px] font-semibold text-slate-900">{check.label}</p>
                <p className="text-[12px] text-slate-500">{check.area}</p>
              </div>
              <select name="status" defaultValue={check.status} className={control}>
                <option value="not_tested">Not tested</option>
                <option value="pass">Pass</option>
                <option value="fail">Fail</option>
                <option value="blocked">Blocked</option>
              </select>
              <input
                name="notes"
                defaultValue={check.notes || ""}
                placeholder="Test note"
                className={control}
              />
              <button
                disabled={busy}
                className="inline-flex h-10 items-center justify-center gap-1 rounded-[12px] bg-[#15388c] px-3 text-[12px] font-semibold text-white hover:bg-[#102d74] disabled:opacity-50"
              >
                Save
                <ArrowRight className="size-3.5" />
              </button>
            </form>
          ))}
        </div>
      ) : null}

      {tab === "issues" ? (
        <>
          {issues.length === 0 ? (
            <p className="p-10 text-center text-[13px] text-slate-500">No problems reported.</p>
          ) : (
            <table className="w-full min-w-[860px] table-fixed text-left">
              <thead className="sticky top-0 z-10">
                <tr className="border-b border-slate-100 bg-[#fafbfc] text-[11px] font-semibold uppercase tracking-[0.12em] text-[#15388c]">
                  <th className="w-[28%] px-4 py-3">Company</th>
                  <th className="w-[18%] px-3 py-3">Type</th>
                  <th className="w-[28%] px-3 py-3">Summary</th>
                  <th className="w-[14%] px-3 py-3">Status</th>
                  <th className="w-[12%] px-3 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {issues.map(issue => (
                  <tr
                    key={issue.id}
                    className="cursor-pointer border-b border-slate-100 last:border-0 transition hover:bg-slate-50/80"
                    onClick={() => setSelectedIssueId(issue.id)}
                  >
                    <td className="px-4 py-3">
                      <p className="truncate text-[13px] font-semibold text-slate-900">
                        {issue.company_name}
                      </p>
                      <p className="mt-0.5 text-[11px] text-slate-500">
                        {issue.id.slice(0, 8).toUpperCase()}
                      </p>
                    </td>
                    <td className="px-3 py-3 text-[13px] capitalize text-slate-700">
                      {issue.issue_type.replaceAll("_", " ")}
                    </td>
                    <td className="px-3 py-3 text-[13px] text-slate-600">
                      <span className="line-clamp-2">{issue.description}</span>
                    </td>
                    <td className="px-3 py-3">
                      <span
                        className={`inline-flex rounded-[12px] px-2 py-1 text-[11px] font-semibold capitalize ${statusClass(issue.status)}`}
                      >
                        {issue.status.replaceAll("_", " ")}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-right">
                      <span className="inline-flex items-center gap-1 text-[12px] font-semibold text-[#15388c]">
                        Open
                        <ArrowRight className="size-3.5" />
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div className="border-t border-rose-100 bg-rose-50/60 p-4">
            <div className="rounded-[12px] border border-rose-200 bg-white p-4">
              <h3 className="text-[14px] font-semibold text-rose-900">Remove pilot data</h3>
              <p className="mt-1 text-[12px] text-rose-800">
                Preview first. Removes only pilot-marked memberships, reports, documents and tickets.
              </p>
              <button
                type="button"
                disabled={busy}
                onClick={() => send({ action: "purge_preview" })}
                className="mt-3 inline-flex h-9 items-center gap-1 rounded-[12px] border border-rose-300 bg-white px-3 text-[12px] font-semibold text-rose-800 hover:bg-rose-50 disabled:opacity-50"
              >
                Preview removal
                <ArrowRight className="size-3.5" />
              </button>
              {preview ? (
                <div className="mt-3 rounded-[12px] border border-rose-200 bg-rose-50 p-3">
                  <p className="text-[12px] font-semibold text-rose-900">
                    Preview: {preview.members} members, {preview.reports} reports,{" "}
                    {preview.documents} documents, {preview.issues} tickets.
                  </p>
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => {
                      if (confirm("Permanently remove only the pilot data shown in this preview?")) {
                        send({ action: "purge", confirm: "REMOVE PILOT DATA" });
                      }
                    }}
                    className="mt-2 inline-flex h-9 items-center rounded-[12px] bg-rose-700 px-3 text-[12px] font-semibold text-white hover:bg-rose-800 disabled:opacity-50"
                  >
                    Confirm pilot-data removal
                  </button>
                </div>
              ) : null}
            </div>
          </div>
        </>
      ) : null}
    </ListFrame>
  );
}
