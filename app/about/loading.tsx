export default function Loading() {
  return (
    <main className="min-h-screen bg-[#f5f7fb]">
      {/* Hero skeleton */}
      <div className="gradient-mesh relative h-72 overflow-hidden">
        <div className="relative z-10 mx-auto max-w-5xl px-5 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="size-11 animate-pulse rounded-xl bg-white/15" />
              <div className="h-5 w-52 animate-pulse rounded bg-white/15" />
            </div>
            <div className="h-9 w-20 animate-pulse rounded-lg bg-white/15" />
          </div>
        </div>
        <div className="relative z-10 mx-auto max-w-5xl px-5 pt-8">
          <div className="h-6 w-52 animate-pulse rounded-full bg-white/15" />
          <div className="mt-5 h-12 w-full max-w-2xl animate-pulse rounded-xl bg-white/15" />
          <div className="mt-3 h-12 w-3/4 max-w-xl animate-pulse rounded-xl bg-white/15" />
          <div className="mt-5 h-5 w-full max-w-xl animate-pulse rounded bg-white/10" />
        </div>
      </div>

      {/* Content skeleton */}
      <div className="mx-auto max-w-5xl px-5 py-16">
        <div className="grid gap-10 lg:grid-cols-[1.2fr_.8fr]">
          <div className="space-y-4">
            <div className="h-4 w-28 animate-pulse rounded bg-slate-200" />
            <div className="h-9 w-3/4 animate-pulse rounded-xl bg-slate-200" />
            <div className="h-4 w-full animate-pulse rounded bg-slate-100" />
            <div className="h-4 w-full animate-pulse rounded bg-slate-100" />
            <div className="h-4 w-5/6 animate-pulse rounded bg-slate-100" />
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-6">
            <div className="h-5 w-40 animate-pulse rounded bg-slate-200" />
            <div className="mt-4 space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <div className="h-4 w-20 animate-pulse rounded bg-slate-100" />
                  <div className="h-4 w-32 animate-pulse rounded bg-slate-200" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
