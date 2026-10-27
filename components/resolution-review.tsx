"use client";

import { useState } from "react";
import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import { Button } from "./ui/button";
import { readJsonResponse } from "@/lib/client-response";

export function ResolutionReview({ id }: { id: string }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  return (
    <form
      className="space-y-3"
      onSubmit={async event => {
        event.preventDefault();
        const status = (event.nativeEvent as SubmitEvent).submitter?.getAttribute("value");
        if (
          !status ||
          !window.confirm(
            `${status === "approved" ? "Approve" : "Reject"} this resolution request?`,
          )
        ) {
          return;
        }
        setBusy(true);
        setError("");
        try {
          const response = await fetch("/api/resolution-review", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              id,
              status,
              notes: new FormData(event.currentTarget).get("notes"),
            }),
          });
          const data = await readJsonResponse<{ error?: string }>(response);
          if (!response.ok) throw new Error(data.error || "Review failed.");
          window.location.reload();
        } catch (cause) {
          setError(cause instanceof Error ? cause.message : "Review failed.");
          setBusy(false);
        }
      }}
    >
      <label className="block text-[13px] font-medium text-slate-700">
        Review reason <span className="text-rose-600">*</span>
        <textarea
          name="notes"
          required
          minLength={2}
          maxLength={1000}
          rows={3}
          placeholder="Explain why you are approving or rejecting this request…"
          className="mt-1.5 w-full rounded-[12px] border border-slate-200 bg-white px-3 py-2.5 text-[13px] text-slate-800 outline-none transition focus:border-[#15388c] focus:ring-2 focus:ring-[#15388c]/15"
        />
      </label>

      <div className="flex flex-wrap gap-2">
        <Button
          disabled={busy}
          type="submit"
          value="approved"
          className="h-10 rounded-[12px] bg-emerald-700 px-4 text-[13px] font-semibold text-white hover:bg-emerald-800"
        >
          {busy ? <Loader2 className="size-4 animate-spin" /> : <CheckCircle2 className="size-4" />}
          Approve resolution
        </Button>
        <Button
          disabled={busy}
          type="submit"
          value="rejected"
          variant="outline"
          className="h-10 rounded-[12px] border-rose-200 px-4 text-[13px] font-semibold text-rose-700 hover:bg-rose-50"
        >
          {busy ? <Loader2 className="size-4 animate-spin" /> : <XCircle className="size-4" />}
          Reject request
        </Button>
      </div>

      {error ? (
        <p role="alert" className="rounded-[10px] border border-rose-200 bg-rose-50 px-3 py-2 text-[13px] text-rose-800">
          {error}
        </p>
      ) : null}
    </form>
  );
}
