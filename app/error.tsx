"use client";
import { useEffect } from "react";
import Link from "next/link";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error("[global-error]", error);
  }, [error]);

  return (
    <main className="relative grid min-h-screen place-items-center overflow-hidden bg-[#f5f7fb] p-5">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -right-20 -top-20 size-96 rounded-full bg-rose-200/30 blur-3xl" />
        <div className="absolute -left-20 bottom-0 size-96 rounded-full bg-amber-200/20 blur-3xl" />
      </div>

      <section className="relative z-10 w-full max-w-lg animate-fade-in-up text-center">
        <div className="mx-auto mb-6 grid size-24 place-items-center rounded-3xl bg-gradient-to-br from-rose-500 to-rose-700 shadow-xl shadow-rose-500/20">
          <AlertTriangle className="size-12 text-white" />
        </div>
        <p className="text-sm font-semibold uppercase tracking-wider text-rose-600">Something went wrong</p>
        <h1 className="mt-2 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Unexpected error
        </h1>
        <p className="mx-auto mt-4 max-w-md text-slate-500">
          An unexpected error occurred while loading this page. Please try again,
          or return to the home page. If the problem persists, contact the
          administrator.
        </p>

        {error.digest && (
          <p className="mt-4 rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-mono text-slate-500">
            Error ID: {error.digest}
          </p>
        )}

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <button
            onClick={reset}
            className="inline-flex items-center gap-2 rounded-xl bg-[#15388c] px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-[#15388c]/20 transition hover:bg-[#1d46a8]"
          >
            <RefreshCw className="size-4" />
            Try again
          </button>
          <Link href="/" className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
            <Home className="size-4" />
            Back to home
          </Link>
        </div>

        <p className="mt-10 text-xs text-slate-400">
          © 2026 Meet Patel · Sellers Trust Network
        </p>
      </section>
    </main>
  );
}
