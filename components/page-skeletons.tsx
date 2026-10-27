import { Building2 } from "lucide-react";

function Bone({ className = "" }: { className?: string }) {
  return <div className={`skeleton-shimmer rounded-[12px] ${className}`} aria-hidden />;
}

/**
 * Content-area skeleton for admin/member loading.tsx.
 * Matches WorkspaceShell padding + ListFrame (flush table + sticky footer).
 */
export function WorkspaceSkeleton({ rows = 8 }: { rows?: number }) {
  return (
    <div
      className="-m-4 flex h-[calc(100%+2rem)] min-h-0 flex-col overflow-hidden bg-white sm:-m-5 sm:h-[calc(100%+2.5rem)] lg:-m-6 lg:h-[calc(100%+3rem)]"
      role="status"
      aria-label="Loading"
    >
      <div className="flex shrink-0 flex-wrap items-center gap-2 border-b border-slate-100 px-4 py-3">
        <Bone className="h-7 w-36" />
        <Bone className="h-7 w-28" />
      </div>

      <div className="flex shrink-0 items-center gap-3 border-b border-slate-100 bg-[#fafbfc] px-4 py-3">
        <Bone className="h-3 w-[22%]" />
        <Bone className="h-3 w-[12%]" />
        <Bone className="h-3 w-[14%]" />
        <Bone className="h-3 w-[10%]" />
        <Bone className="hidden h-3 w-[10%] sm:block" />
        <Bone className="hidden h-3 w-[10%] md:block" />
        <Bone className="ml-auto h-3 w-8" />
      </div>

      <div className="min-h-0 flex-1 overflow-hidden">
        {Array.from({ length: rows }).map((_, i) => (
          <div
            key={i}
            className="flex items-center gap-3 border-b border-slate-100 px-4 py-3.5"
            style={{ animationDelay: `${i * 40}ms` }}
          >
            <Bone className="size-9 shrink-0" />
            <div className="min-w-0 flex-1 space-y-2">
              <Bone className="h-3.5 w-2/5 max-w-[180px]" />
              <Bone className="h-3 w-1/3 max-w-[140px]" />
            </div>
            <Bone className="hidden h-3.5 w-24 sm:block" />
            <Bone className="hidden h-6 w-28 md:block" />
            <Bone className="hidden h-6 w-20 lg:block" />
            <Bone className="size-8 shrink-0" />
          </div>
        ))}
      </div>

      <div className="flex shrink-0 items-center justify-between gap-3 border-t border-slate-100 px-4 py-3">
        <Bone className="h-3.5 w-44" />
        <div className="flex items-center gap-1.5">
          <Bone className="size-8 !rounded-full" />
          <Bone className="size-8 !rounded-full" />
          <Bone className="size-8 !rounded-full" />
        </div>
      </div>
    </div>
  );
}

/** Skeleton for the legal pages (privacy, terms, disclaimer). */
export function LegalSkeleton() {
  return (
    <main className="min-h-screen bg-[#f5f7fb] text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center gap-3 px-5 py-4">
          <Bone className="size-10" />
          <Bone className="size-6 !rounded" />
          <Bone className="h-5 w-48" />
        </div>
        <nav className="border-t border-slate-100 bg-slate-50">
          <div className="mx-auto flex max-w-5xl items-center gap-2 px-5 py-2.5">
            <Bone className="h-3 w-14" />
            <Bone className="h-3 w-24" />
          </div>
        </nav>
      </header>

      <article className="mx-auto max-w-5xl px-5 py-10">
        <Bone className="h-4 w-32" />
        <Bone className="mt-3 h-11 w-2/3" />
        <Bone className="mt-4 h-4 w-72" />

        <div className="mt-8 overflow-hidden rounded-[12px] border border-slate-200 bg-white shadow-sm">
          <div className="space-y-8 p-6 sm:p-9">
            {Array.from({ length: 4 }).map((_, section) => (
              <div key={section} className="space-y-3 border-b border-slate-100 pb-6 last:border-0">
                <Bone className="h-6 w-1/3" />
                <Bone className="h-4 w-full" />
                <Bone className="h-4 w-full" />
                <Bone className="h-4 w-4/5" />
              </div>
            ))}
          </div>
        </div>
      </article>
    </main>
  );
}

/** Skeleton for small centred pages such as sign-out. */
export function CenteredCardSkeleton({ label = "Loading…" }: { label?: string }) {
  return (
    <main className="grid min-h-screen place-items-center bg-gradient-to-br from-slate-50 via-[#f5f7fb] to-blue-50 p-5">
      <div className="flex w-full max-w-sm flex-col items-center rounded-[12px] border border-slate-200 bg-white p-8 text-center shadow-sm">
        <div className="mb-5 flex items-center gap-2">
          <Bone className="size-10" />
          <Bone className="h-5 w-40" />
        </div>
        <Bone className="size-12 !rounded-full" />
        <Bone className="mt-4 h-5 w-36" />
        <Bone className="mt-3 h-4 w-52" />
        <p className="mt-6 flex items-center justify-center gap-1.5 text-xs text-slate-400">
          <Building2 className="size-3 animate-pulse" />
          {label}
        </p>
      </div>
    </main>
  );
}
