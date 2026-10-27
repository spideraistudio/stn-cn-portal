import Link from "next/link";
import { Home, Search, ShieldAlert } from "lucide-react";

export default function NotFound() {
  return (
    <main className="relative grid min-h-screen place-items-center overflow-hidden bg-[#f5f7fb] p-5">
      {/* Decorative background */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -right-20 -top-20 size-96 rounded-full bg-[#15388c]/5 blur-3xl" />
        <div className="absolute -left-20 bottom-0 size-96 rounded-full bg-[#a57c10]/5 blur-3xl" />
      </div>

      <section className="relative z-10 w-full max-w-lg animate-fade-in-up text-center">
        {/* 404 illustration */}
        <div className="mx-auto mb-6 grid size-24 place-items-center rounded-3xl bg-gradient-to-br from-[#15388c] to-[#2852a4] shadow-xl shadow-[#15388c]/20">
          <ShieldAlert className="size-12 text-white" />
        </div>

        <p className="text-sm font-semibold uppercase tracking-wider text-[#a57c10]">Error 404</p>
        <h1 className="mt-2 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Page not found
        </h1>
        <p className="mx-auto mt-4 max-w-md text-slate-500">
          The page you&apos;re looking for doesn&apos;t exist or may have been moved.
          Use the links below to find your way back.
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link href="/" className="inline-flex items-center gap-2 rounded-xl bg-[#15388c] px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-[#15388c]/20 transition hover:bg-[#1d46a8]">
            <Home className="size-4" />
            Back to home
          </Link>
          <Link href="/login" className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
            <Search className="size-4" />
            Member login
          </Link>
        </div>

        <p className="mt-10 text-xs text-slate-400">
          © 2026 Meet Patel · Sellers Trust Network
        </p>
      </section>
    </main>
  );
}
