"use client";

import { useState, type FormEvent } from "react";
import { AlertTriangle, Bug } from "lucide-react";
import { readJsonResponse } from "@/lib/client-response";
import { DetailSection, ListFrame } from "@/components/list-frame";

type Issue = {
  id: string;
  issue_type: string;
  page_url: string;
  description: string;
  status: string;
  admin_notes: string | null;
  created_at: number;
  screenshot_name: string | null;
};

const control =
  "h-10 w-full rounded-[12px] border border-slate-200 bg-white px-3 text-[13px] text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10";
const labelClass = "mb-1.5 block text-[12px] font-medium text-slate-700";
const btnPrimary =
  "inline-flex h-10 items-center justify-center rounded-[12px] bg-[#15388c] px-4 text-[13px] font-semibold text-white transition hover:bg-[#102d74] disabled:opacity-50";

function statusClass(status: string) {
  if (status === "resolved" || status === "closed") {
    return "bg-emerald-50 text-emerald-800";
  }
  if (status === "in_progress" || status === "reviewing") {
    return "bg-blue-50 text-blue-800";
  }
  return "bg-amber-50 text-amber-900";
}

export function PilotIssueForm({ issues }: { issues: Issue[] }) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [ok, setOk] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement=event.currentTarget;
    setBusy(true);
    setMessage("");
    setOk(false);
    try {
      const response = await fetch("/api/pilot-issues", {
        method: "POST",
        body: new FormData(formElement),
      });
      const data = await readJsonResponse<{ error?: string }>(response);
      if (!response.ok) throw new Error(data.error || "Unable to send issue.");
      setOk(true);
      setMessage("Problem reported. The administrator can now review it.");
      formElement.reset();
      window.location.reload();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to send issue.");
      setBusy(false);
    }
  }

  return (
    <ListFrame tone="detail">
      <div className="space-y-3 p-4 sm:p-5">
        <DetailSection title="Describe the problem">
          <form onSubmit={submit} className="space-y-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block">
                <span className={labelClass}>Issue type *</span>
                <select name="issueType" required className={control}>
                  <option value="error">Error message</option>
                  <option value="wrong_data">Wrong data</option>
                  <option value="access">Access or permission</option>
                  <option value="document">Document problem</option>
                  <option value="other">Other</option>
                </select>
              </label>
              <label className="block">
                <span className={labelClass}>Page or section *</span>
                <input
                  name="pageUrl"
                  required
                  maxLength={300}
                  placeholder="Example: My Reports"
                  className={control}
                />
              </label>
              <label className="block sm:col-span-2">
                <span className={labelClass}>What happened? *</span>
                <textarea
                  name="description"
                  required
                  minLength={10}
                  maxLength={3000}
                  rows={5}
                  placeholder="Tell us what you clicked, what you expected and what appeared."
                  className="w-full rounded-[12px] border border-slate-200 bg-white px-3 py-2.5 text-[13px] outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10"
                />
              </label>
              <label className="block sm:col-span-2">
                <span className={labelClass}>Screenshot (optional)</span>
                <input
                  name="screenshot"
                  type="file"
                  accept="image/png,image/jpeg"
                  className="w-full rounded-[12px] border border-dashed border-slate-300 bg-white px-3 py-3 text-[12px] text-slate-600"
                />
                <span className="mt-1 block text-[11px] text-slate-500">
                  PNG or JPG, maximum 1.5 MB. Do not include passwords.
                </span>
              </label>
            </div>
            <button type="submit" disabled={busy} className={btnPrimary}>
              {busy ? "Sending…" : "Send problem report"}
            </button>
            {message && (
              <p
                role="status"
                className={`rounded-[12px] border px-3 py-2.5 text-[12px] ${
                  ok
                    ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                    : "border-rose-200 bg-rose-50 text-rose-700"
                }`}
              >
                {message}
              </p>
            )}
          </form>
        </DetailSection>

        <DetailSection
          title="My reported problems"
          action={
            <span className="text-[11px] font-medium text-slate-500">
              {issues.length} ticket{issues.length === 1 ? "" : "s"}
            </span>
          }
        >
          {issues.length === 0 ? (
            <div className="flex flex-col items-center px-4 py-10 text-center">
              <span className="grid size-11 place-items-center rounded-[12px] bg-slate-100 text-slate-500">
                <Bug className="size-5" />
              </span>
              <p className="mt-3 text-[13px] font-semibold text-slate-900">
                No problems reported yet
              </p>
              <p className="mt-1 text-[12px] text-slate-500">
                Use the form above when something looks wrong.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {issues.map(issue => (
                <article key={issue.id} className="py-3.5 first:pt-0 last:pb-0">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="text-[13px] font-semibold capitalize text-slate-900">
                        {issue.issue_type.replaceAll("_", " ")} · {issue.page_url}
                      </p>
                      <p className="mt-0.5 text-[11px] text-slate-500">
                        Ticket {issue.id.slice(0, 8).toUpperCase()} ·{" "}
                        {new Date(issue.created_at).toLocaleString("en-IN", {
                          timeZone: "Asia/Kolkata",
                        })}
                      </p>
                    </div>
                    <span
                      className={`rounded-full px-2.5 py-1 text-[11px] font-semibold capitalize ${statusClass(
                        issue.status,
                      )}`}
                    >
                      {issue.status.replaceAll("_", " ")}
                    </span>
                  </div>
                  <p className="mt-2 whitespace-pre-wrap break-words text-[13px] leading-5 text-slate-700">
                    {issue.description}
                  </p>
                  {issue.admin_notes && (
                    <p className="mt-2 flex gap-2 rounded-[12px] border border-emerald-200 bg-emerald-50 px-3 py-2 text-[12px] text-emerald-900">
                      <AlertTriangle className="mt-0.5 size-3.5 shrink-0" />
                      <span>
                        <strong>Administrator:</strong> {issue.admin_notes}
                      </span>
                    </p>
                  )}
                </article>
              ))}
            </div>
          )}
        </DetailSection>
      </div>
    </ListFrame>
  );
}
