"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { readJsonResponse } from "@/lib/client-response";

/** Compact admin toggle for member seller-search permission. */
export function SearchAccessToggle({
  memberId,
  searchEnabled,
}: {
  memberId: number | string;
  searchEnabled: boolean;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [enabled, setEnabled] = useState(searchEnabled);

  async function toggle() {
    const next = !enabled;
    if (
      !confirm(
        next
          ? "Enable seller search for this member?"
          : "Disable seller search for this member? They will see a message instead of search results.",
      )
    ) {
      return;
    }
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/admin/member-access", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          memberId,
          action: "search",
          enabled: next,
        }),
      });
      const data = await readJsonResponse<{ error?: string }>(response);
      if (!response.ok) throw new Error(data.error || "Unable to update search access.");
      setEnabled(next);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to update search access.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="w-full space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2 rounded-[12px] border border-slate-200 bg-slate-50 px-3 py-2.5">
        <div className="min-w-0">
          <p className="flex items-center gap-1.5 text-[12px] font-semibold text-slate-900">
            <Search className="size-3.5 text-[#15388c]" />
            Seller search
          </p>
          <p className="mt-0.5 text-[11px] text-slate-500">
            Currently {enabled ? "enabled" : "disabled"}
          </p>
        </div>
        <button
          type="button"
          disabled={busy}
          onClick={toggle}
          className={`inline-flex h-9 shrink-0 items-center rounded-[12px] px-3 text-[12px] font-semibold transition disabled:opacity-50 ${
            enabled
              ? "border border-rose-200 bg-white text-rose-700 hover:bg-rose-50"
              : "bg-emerald-700 text-white hover:bg-emerald-800"
          }`}
        >
          {busy ? "Saving…" : enabled ? "Disable" : "Enable"}
        </button>
      </div>
      {error && (
        <p className="text-[12px] font-medium text-rose-700">{error}</p>
      )}
    </div>
  );
}
