"use client";

import { useState } from "react";
import { Button } from "./ui/button";
import { readJsonResponse } from "@/lib/client-response";
import {
  IndianAmountInput,
  formatIndianAmount,
  parseIndianAmount,
} from "@/components/indian-amount-input";

/** Convert paise to a clean INR string (avoids float noise). */
export function paiseToRupees(paise: number) {
  const safe = Math.max(0, Math.trunc(Number(paise) || 0));
  const whole = Math.floor(safe / 100);
  const frac = safe % 100;
  return frac === 0 ? String(whole) : `${whole}.${String(frac).padStart(2, "0")}`;
}

export function ResolutionRequestForm({
  reportId,
  remainingAmountPaise,
}: {
  reportId: string;
  remainingAmountPaise: number;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const fullAmount = paiseToRupees(remainingAmountPaise);
  const fullLabel = formatIndianAmount(fullAmount);

  return (
    <form
      className="space-y-5 rounded-[12px] border border-slate-200 bg-white p-5 sm:p-6"
      onSubmit={async event => {
        event.preventDefault();
        setBusy(true);
        setError("");
        try {
          const form = new FormData(event.currentTarget);
          form.set("reportId", reportId);
          form.set("resolvedUnit", "rupees");
          const amount = parseIndianAmount(String(form.get("resolvedAmount") || ""));
          if (!/^[0-9]{1,12}(\.[0-9]{1,2})?$/.test(amount) || Number(amount) <= 0) {
            throw new Error("Enter the full resolved amount in INR (e.g. 2,58,205).");
          }
          form.set("resolvedAmount", amount);
          const response = await fetch("/api/resolution-request", {
            method: "POST",
            body: form,
          });
          const data = await readJsonResponse<{ error?: string }>(response);
          if (!response.ok) {
            throw new Error(data.error || "Unable to submit resolution request.");
          }
          window.location.href = "/member/reports";
        } catch (cause) {
          setError(
            cause instanceof Error
              ? cause.message
              : "Unable to submit resolution request.",
          );
          setBusy(false);
        }
      }}
    >
      <label className="block text-[12px] font-medium text-slate-700">
        Resolution date *
        <input
          name="resolvedOn"
          type="date"
          required
          max={new Date().toISOString().slice(0, 10)}
          className="mt-1.5 h-10 w-full rounded-[12px] border border-slate-200 px-3 text-[13px] outline-none focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10"
        />
      </label>
      <IndianAmountInput
        name="resolvedAmount"
        label="Amount resolved in this settlement (INR)"
        required
        defaultValue={fullAmount}
        fullAmount={fullAmount}
        hint={
          fullLabel
            ? `Pre-filled with the remaining disputed amount (₹${fullLabel}). Change it for a partial settlement, or reset to the full amount.`
            : "Enter the amount in rupees. Shown as 2,58,205 for easy reading."
        }
      />
      <label className="block text-[12px] font-medium text-slate-700">
        Factual resolution description *
        <textarea
          name="description"
          required
          minLength={10}
          maxLength={2000}
          rows={5}
          placeholder="Explain how the commercial dispute was resolved."
          className="mt-1.5 w-full rounded-[12px] border border-slate-200 px-3 py-2.5 text-[13px] outline-none focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10"
        />
      </label>
      <label className="block text-[12px] font-medium text-slate-700">
        Supporting document (optional)
        <input
          name="document"
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          className="mt-1.5 w-full rounded-[12px] border border-dashed border-slate-300 px-3 py-3 text-[12px]"
        />
        <span className="mt-1 block text-[11px] font-normal text-slate-500">
          PDF, JPG or PNG, maximum 1.5 MB.
        </span>
      </label>
      {error && (
        <p
          role="alert"
          className="rounded-[12px] border border-rose-200 bg-rose-50 px-3 py-2 text-[12px] text-rose-700"
        >
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-2">
        <Button
          disabled={busy}
          type="submit"
          className="h-10 rounded-[12px] bg-[#15388c] px-4 text-[13px] font-semibold hover:bg-[#102d74]"
        >
          {busy ? "Submitting…" : "Send for admin approval"}
        </Button>
        <a
          href="/member/reports"
          className="inline-flex h-10 items-center rounded-[12px] border border-slate-200 px-4 text-[13px] font-semibold text-slate-700"
        >
          Cancel
        </a>
      </div>
    </form>
  );
}
