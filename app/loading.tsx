import { Building2, FileSearch, Scale, Lock } from "lucide-react";

export default function Loading() {
  return (
    <main className="min-h-screen bg-[#f5f7fb]">
      {/* Hero skeleton */}
      <div className="gradient-mesh relative h-[420px] overflow-hidden">
        <div className="pointer-events-none absolute -right-20 top-10 size-72 rounded-full bg-blue-400/20 blur-3xl animate-pulse" />
        <div className="relative z-10 mx-auto max-w-6xl px-5 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="size-11 animate-pulse rounded-xl bg-white/15" />
              <div className="h-5 w-48 animate-pulse rounded bg-white/15" />
            </div>
            <div className="flex gap-2">
              <div className="h-9 w-24 animate-pulse rounded-lg bg-white/15" />
              <div className="h-9 w-20 animate-pulse rounded-lg bg-white/15" />
            </div>
          </div>
        </div>
        <div className="relative z-10 mx-auto max-w-6xl px-5 pt-16">
          <div className="h-7 w-72 animate-pulse rounded-full bg-white/15" />
          <div className="mt-6 h-12 w-full max-w-2xl animate-pulse rounded-xl bg-white/15" />
          <div className="mt-3 h-12 w-3/4 max-w-xl animate-pulse rounded-xl bg-white/15" />
          <div className="mt-6 h-5 w-full max-w-xl animate-pulse rounded bg-white/10" />
          <div className="mt-3 h-5 w-2/3 max-w-md animate-pulse rounded bg-white/10" />
          <div className="mt-8 flex gap-4">
            <div className="h-12 w-44 animate-pulse rounded-xl bg-white/25" />
            <div className="h-12 w-36 animate-pulse rounded-xl bg-white/15" />
          </div>
        </div>
      </div>

      {/* Features skeleton */}
      <div className="mx-auto max-w-6xl px-5 py-16">
        <div className="mx-auto max-w-2xl text-center">
          <div className="mx-auto h-4 w-24 animate-pulse rounded bg-slate-200" />
          <div className="mx-auto mt-3 h-9 w-3/4 animate-pulse rounded-xl bg-slate-200" />
          <div className="mx-auto mt-4 h-4 w-full animate-pulse rounded bg-slate-100" />
        </div>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[Building2, FileSearch, Scale, Lock].map((Icon, i) => (
            <div key={i} className="rounded-2xl border border-slate-200 bg-white p-6">
              <div className="grid size-12 place-items-center rounded-xl bg-[#15388c]/5 text-[#15388c]/30">
                <Icon className="size-6" />
              </div>
              <div className="mt-4 h-5 w-3/4 animate-pulse rounded bg-slate-200" />
              <div className="mt-2 h-3 w-full animate-pulse rounded bg-slate-100" />
              <div className="mt-1 h-3 w-5/6 animate-pulse rounded bg-slate-100" />
            </div>
          ))}
        </div>
      </div>

      {/* CTA skeleton */}
      <div className="mx-auto max-w-6xl px-5 pb-20">
        <div className="h-48 animate-pulse rounded-3xl bg-slate-200" />
      </div>
    </main>
  );
}
