"use client";

import { useState } from "react";
import { readJsonResponse } from "@/lib/client-response";
import { DetailSection } from "@/components/list-frame";

const control =
  "h-10 w-full rounded-[12px] border border-slate-200 bg-white px-3 text-[13px] text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10";
const labelClass = "mb-1.5 block text-[12px] font-medium text-slate-700";
const btnGhost =
  "inline-flex h-10 items-center justify-center rounded-[12px] border border-slate-200 bg-white px-4 text-[13px] font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50";
const btnDanger =
  "inline-flex h-10 items-center justify-center rounded-[12px] bg-rose-700 px-4 text-[13px] font-semibold text-white transition hover:bg-rose-800 disabled:opacity-50";

export function AccountDeletionForm({ pending }: { pending: boolean }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function cancel() {
    if (!confirm("Cancel your account-deletion request?")) return;
    await send({ action: "cancel" });
  }

  async function send(body: object) {
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/account-deletion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await readJsonResponse<{ error?: string }>(response);
      if (!response.ok) throw new Error(data.error || "Unable to save request.");
      window.location.reload();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to save request.");
      setBusy(false);
    }
  }

  if (pending) {
    return (
      <DetailSection title="Deletion request">
        <div className="rounded-[12px] border border-amber-200 bg-amber-50 px-3.5 py-3">
          <p className="text-[13px] font-semibold text-amber-950">
            Deletion request pending
          </p>
          <p className="mt-1 text-[12px] leading-5 text-amber-900">
            Your account remains active until the administrator decides. You may
            cancel the request now.
          </p>
          <button
            type="button"
            disabled={busy}
            onClick={cancel}
            className={`${btnGhost} mt-3`}
          >
            {busy ? "Please wait…" : "Cancel request"}
          </button>
          {error && (
            <p className="mt-2 text-[12px] font-medium text-rose-700">{error}</p>
          )}
        </div>
      </DetailSection>
    );
  }

  return (
    <DetailSection title="Request account deletion">
      <form
        className="space-y-3"
        onSubmit={event => {
          event.preventDefault();
          if (!confirm("Send this account-deletion request to the administrator?")) {
            return;
          }
          const form = new FormData(event.currentTarget);
          send({
            action: "request",
            password: form.get("password"),
            reason: form.get("reason"),
          });
        }}
      >
        <p className="text-[12px] leading-5 text-slate-600">
          Approved historical reports may remain, but your company will be shown
          as “Former verified member.” Pending and rejected reports will be
          scheduled for deletion.
        </p>
        <label className="block">
          <span className={labelClass}>Reason *</span>
          <textarea
            name="reason"
            required
            minLength={5}
            maxLength={1000}
            rows={4}
            className="w-full rounded-[12px] border border-slate-200 bg-white px-3 py-2.5 text-[13px] outline-none transition focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10"
          />
        </label>
        <label className="block">
          <span className={labelClass}>Current password *</span>
          <input name="password" required type="password" className={control} />
        </label>
        <label className="flex items-start gap-2.5 text-[12px] leading-5 text-slate-700">
          <input type="checkbox" required className="mt-0.5 size-4 rounded border-slate-300" />
          <span>
            I understand approved historical reports may remain after reporter
            attribution is anonymized.
          </span>
        </label>
        <button type="submit" disabled={busy} className={btnDanger}>
          {busy ? "Sending…" : "Send deletion request"}
        </button>
        {error && (
          <p className="rounded-[12px] border border-rose-200 bg-rose-50 px-3 py-2 text-[12px] font-medium text-rose-700">
            {error}
          </p>
        )}
      </form>
    </DetailSection>
  );
}
