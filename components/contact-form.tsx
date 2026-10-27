"use client";
import { useState, type FormEvent } from "react";
import { Loader2, CheckCircle2, Send, User, Mail, Tag, FileText } from "lucide-react";

const TOPICS = [
  { value: "general", label: "General enquiry" },
  { value: "membership", label: "Membership / registration" },
  { value: "grievance", label: "Grievance or complaint" },
  { value: "seller_correction", label: "Seller correction request" },
  { value: "account", label: "Account access / deletion" },
  { value: "security", label: "Security report" },
] as const;

export function ContactForm() {
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const form = new FormData(e.currentTarget);
      const name = String(form.get("name") || "").trim();
      const email = String(form.get("email") || "").trim();
      const topic = String(form.get("topic") || "general");
      const message = String(form.get("message") || "").trim();
      if (name.length < 2) throw new Error("Please enter your name.");
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error("Please enter a valid email address.");
      if (message.length < 10) throw new Error("Please provide a message of at least 10 characters.");
      if (message.length > 2000) throw new Error("Message is too long (2000 character maximum).");

      // No email backend exists; compose a mailto link so the user's email
      // client opens with a pre-filled message addressed to the grievance officer.
      const subject = encodeURIComponent(`[STN:${topic}] From ${name}`);
      const body = encodeURIComponent(`Name: ${name}\nEmail: ${email}\nTopic: ${topic}\n\n${message}`);
      window.location.href = `mailto:meetpatel.hmt@gmail.com?subject=${subject}&body=${body}`;
      // Give the browser a moment to open the mail client, then show success.
      setTimeout(() => setDone(true), 600);
    } catch (c) {
      setError(c instanceof Error ? c.message : "Unable to send message.");
      setBusy(false);
    }
  }

  if (done) {
    return (
      <div className="animate-fade-in flex flex-col items-center py-6 text-center">
        <div className="grid size-16 place-items-center rounded-full bg-emerald-50">
          <CheckCircle2 className="size-9 text-emerald-600" />
        </div>
        <h3 className="mt-4 text-xl font-bold text-slate-900">Message ready</h3>
        <p className="mt-2 max-w-sm text-sm text-slate-500">
          Your email client should have opened with a pre-filled message. If it
          didn&apos;t, please email <a href="mailto:meetpatel.hmt@gmail.com" className="font-medium text-[#15388c] underline">meetpatel.hmt@gmail.com</a> directly.
        </p>
        <button
          onClick={() => { setDone(false); setBusy(false); }}
          className="mt-5 rounded-xl border border-slate-200 px-5 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
        >
          Send another
        </button>
      </div>
    );
  }

  const inputClass = "h-12 w-full rounded-xl border border-slate-200 bg-white pl-11 pr-4 text-base outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10";

  return (
    <form onSubmit={submit} className="space-y-5">
      {/* Honeypot */}
      <input name="website" tabIndex={-1} autoComplete="off" className="hidden" aria-hidden="true" />

      <label className="block text-sm font-medium text-slate-700">Your name *
        <div className="relative mt-2">
          <User className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-slate-400" />
          <input name="name" required maxLength={120} placeholder="Full name" className={inputClass} />
        </div>
      </label>

      <label className="block text-sm font-medium text-slate-700">Email address *
        <div className="relative mt-2">
          <Mail className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-slate-400" />
          <input name="email" required type="email" maxLength={160} placeholder="you@example.com" className={inputClass} />
        </div>
      </label>

      <label className="block text-sm font-medium text-slate-700">Topic *
        <div className="relative mt-2">
          <Tag className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-slate-400" />
          <select name="topic" defaultValue="general" className={`${inputClass} appearance-none pr-10`}>
            {TOPICS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
      </label>

      <label className="block text-sm font-medium text-slate-700">Message *
        <div className="relative mt-2">
          <FileText className="pointer-events-none absolute left-3 top-4 size-5 text-slate-400" />
          <textarea
            name="message"
            required
            minLength={10}
            maxLength={2000}
            rows={5}
            placeholder="Describe your enquiry, grievance, or request…"
            className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-11 pr-4 text-base outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10"
          />
        </div>
        <span className="mt-1.5 block text-xs text-slate-400">10–2000 characters</span>
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
        {busy ? <Loader2 className="size-5 animate-spin" /> : <Send className="size-5" />}
        {busy ? "Preparing…" : "Send message"}
      </button>

      <p className="text-center text-xs text-slate-400">
        Opens your email client pre-filled to the grievance officer
      </p>
    </form>
  );
}
