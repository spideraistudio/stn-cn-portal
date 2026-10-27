export default function Loading() {
  return (
    <main className="min-h-screen bg-[#f5f7fb]">
      {/* Hero skeleton */}
      <div className="gradient-mesh relative h-64 overflow-hidden">
        <div className="relative z-10 mx-auto max-w-5xl px-5 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="size-11 animate-pulse rounded-xl bg-white/15" />
              <div className="h-5 w-52 animate-pulse rounded bg-white/15" />
            </div>
            <div className="h-9 w-20 animate-pulse rounded-lg bg-white/15" />
          </div>
        </div>
        <div className="relative z-10 mx-auto max-w-5xl px-5 pt-4">
          <div className="h-5 w-28 animate-pulse rounded-full bg-white/15" />
          <div className="mt-3 h-12 w-2/3 max-w-md animate-pulse rounded-xl bg-white/15" />
          <div className="mt-3 h-5 w-full max-w-xl animate-pulse rounded bg-white/10" />
        </div>
      </div>

      {/* Plans grid skeleton */}
      <section className="mx-auto max-w-6xl px-5 py-12">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="size-11 animate-pulse rounded-xl bg-slate-200" />
                <div className="h-6 w-20 animate-pulse rounded bg-slate-200" />
              </div>
              <div className="mt-4 h-8 w-24 animate-pulse rounded-xl bg-slate-200" />
              <div className="mt-2 h-4 w-full animate-pulse rounded bg-slate-100" />
              <div className="mt-5 space-y-2.5">
                {Array.from({ length: 5 }).map((_, j) => (
                  <div key={j} className="flex items-center gap-2">
                    <div className="size-4 animate-pulse rounded bg-slate-200" />
                    <div className="h-4 flex-1 animate-pulse rounded bg-slate-100" />
                  </div>
                ))}
              </div>
              <div className="mt-6 h-12 w-full animate-pulse rounded-xl bg-[#15388c]/20" />
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
