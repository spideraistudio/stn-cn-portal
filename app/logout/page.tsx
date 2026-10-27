"use client";
import { useEffect, useRef, useState } from "react";
import { Loader2, AlertCircle, LogOut, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { BrandLogo } from "@/components/brand-logo";

export default function Logout() {
  const [error, setError] = useState(false);
  const started = useRef(false);

  async function doLogout() {
    try {
      const r = await fetch("/api/member-auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "logout" }),
      });
      if (!r.ok) throw new Error();
      window.location.assign("/login");
    } catch {
      setError(true);
    }
  }

  // Fire-once on mount. setState only happens inside the async resolution.
  useEffect(() => {
    if (started.current) return;
    started.current = true;
    void doLogout();
  }, []);

  return (
    <main className="grid min-h-screen place-items-center bg-gradient-to-br from-slate-50 via-[#f5f7fb] to-blue-50 p-5">
      <div className="flex w-full max-w-sm flex-col items-center rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        {/* Logo */}
        {/* Signing out, so the mark points at the public home rather than /home. */}
        <Link href="/" className="mb-5 flex items-center gap-2">
          <span className="grid size-10 place-items-center rounded-xl bg-[#15388c]">
            <BrandLogo compact className="size-9" />
          </span>
          <span className="font-semibold text-slate-900">Sellers Trust Network</span>
        </Link>

        {error ? (
          <>
            <div className="grid size-12 place-items-center rounded-full bg-rose-50">
              <AlertCircle className="size-6 text-rose-600" />
            </div>
            <h1 className="mt-4 text-lg font-semibold text-slate-900">Sign-out incomplete</h1>
            <p className="mt-2 text-sm text-slate-500">The sign-out request did not finish. Please try again.</p>
            <button
              onClick={doLogout}
              className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg bg-[#15388c] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#1d46a8]"
            >
              <LogOut className="size-4" />
              Retry sign out
            </button>
            <Link href="/login" className="mt-3 flex items-center justify-center gap-1.5 text-xs font-semibold text-slate-500 transition hover:text-[#15388c]">
              <ArrowLeft className="size-3" />
              Back to login
            </Link>
          </>
        ) : (
          <>
            <Loader2 className="size-8 animate-spin text-[#15388c]" />
            <h1 className="mt-4 text-lg font-semibold text-slate-900">Signing out…</h1>
            <p className="mt-2 text-sm text-slate-500">Closing your member session.</p>
          </>
        )}
      </div>
    </main>
  );
}
