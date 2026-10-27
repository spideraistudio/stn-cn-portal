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
          <div className="h-5 w-32 animate-pulse rounded-full bg-white/15" />
          <div className="mt-3 h-12 w-2/3 max-w-md animate-pulse rounded-xl bg-white/15" />
          <div className="mt-3 h-5 w-full max-w-xl animate-pulse rounded bg-white/10" />
        </div>
      </div>

      {/* Content skeleton */}
      <section className="mx-auto max-w-5xl px-5 py-12">
        <div className="grid gap-8 lg:grid-cols-[1.3fr_.7fr]">
          {/* Form skeleton */}
          <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-lg">
            <div className="border-b border-slate-100 bg-slate-50 px-6 py-4 sm:px-8">
              <div className="h-5 w-40 animate-pulse rounded bg-slate-200" />
              <div className="mt-1.5 h-4 w-64 animate-pulse rounded bg-slate-100" />
            </div>
            <div className="space-y-5 p-6 sm:p-8">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i}>
                  <div className="h-4 w-28 animate-pulse rounded bg-slate-200" />
                  <div className="mt-2 h-12 w-full animate-pulse rounded-xl border border-slate-200 bg-slate-50" />
                </div>
              ))}
              <div className="h-12 w-full animate-pulse rounded-xl bg-[#15388c]/30" />
            </div>
          </div>
          {/* Sidebar skeleton */}
          <aside className="space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="rounded-2xl border border-slate-200 bg-white p-6">
                <div className="h-5 w-20 animate-pulse rounded bg-slate-200" />
                <div className="mt-2 h-4 w-full animate-pulse rounded bg-slate-100" />
                <div className="mt-1 h-4 w-3/4 animate-pulse rounded bg-slate-100" />
              </div>
            ))}
          </aside>
        </div>
      </section>
    </main>
  );
}
