"use client";
import { useState } from "react";
import { CheckCircle2, Loader2, Mail, User } from "lucide-react";
import { readJsonResponse } from "@/lib/client-response";

export function ForgotPasswordForm() {
  const [busy, setBusy] = useState(false), [done, setDone] = useState(false), [error, setError] = useState("");

  if (done) {
    return (
      <div className="mt-6 animate-fade-in flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-5">
        <CheckCircle2 className="mt-0.5 size-6 shrink-0 text-emerald-600" />
        <div>
          <p className="font-semibold text-emerald-900">Request received</p>
          <p className="mt-1 text-sm text-emerald-800">
            If the details match an account, the administrator will prepare a
            temporary password and contact your company manually.
          </p>
        </div>
      </div>
    );
  }

  return (
    <form className="mt-6 space-y-5" onSubmit={async e => {
      e.preventDefault(); setBusy(true); setError("");
      try {
        const f = new FormData(e.currentTarget),
          response = await fetch("/api/password-reset-request", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify(Object.fromEntries(f)),
          }),
          data = await readJsonResponse<{ error?: string }>(response);
        if (!response.ok) throw new Error(data.error || "Unable to send request.");
        setDone(true);
      } catch (c) {
        setError(c instanceof Error ? c.message : "Unable to send request.");
        setBusy(false);
      }
    }}>
      <label className="block text-sm font-medium text-slate-700">Member ID
        <div className="relative mt-2">
          <User className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-slate-400" />
          <input
            name="loginId"
            required
            pattern="MEM[0-9A-F]{6,}"
            placeholder="MEM000001"
            className="h-12 w-full rounded-xl border border-slate-200 bg-white pl-11 pr-4 font-mono uppercase outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10"
          />
        </div>
      </label>
      <label className="block text-sm font-medium text-slate-700">Registered email
        <div className="relative mt-2">
          <Mail className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-slate-400" />
          <input
            name="email"
            required
            type="email"
            maxLength={160}
            placeholder="business@example.com"
            className="h-12 w-full rounded-xl border border-slate-200 bg-white pl-11 pr-4 outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10"
          />
        </div>
      </label>
      {error && (
        <div role="alert" className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
          {error}
        </div>
      )}
      <button
        disabled={busy}
        className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-[#15388c] font-semibold text-white shadow-lg shadow-[#15388c]/20 transition hover:bg-[#1d46a8] hover:shadow-xl disabled:opacity-50"
      >
        {busy && <Loader2 className="size-5 animate-spin" />}
        {busy ? "Sending…" : "Request password reset"}
      </button>
    </form>
  );
}
