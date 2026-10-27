import { Building2 } from "lucide-react";

/**
 * Loading skeleton for auth pages (login, admin-login, forgot-password).
 * Matches the card-based layout with a gradient header band and form fields.
 */
export function AuthLoading({ label = "Loading…" }: { label?: string }) {
  return (
    <main className="grid min-h-screen place-items-center bg-[#f5f7fb] p-5">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -right-20 -top-20 size-96 rounded-full bg-[#15388c]/5 blur-3xl" />
        <div className="absolute -left-20 bottom-0 size-96 rounded-full bg-[#a57c10]/5 blur-3xl" />
      </div>
      <section className="relative w-full max-w-md">
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-200/50">
          {/* Header band skeleton */}
          <div className="gradient-mesh h-20 animate-pulse" />
          {/* Body skeleton */}
          <div className="p-8">
            <div className="h-7 w-2/3 animate-pulse rounded-lg bg-slate-200" />
            <div className="mt-3 h-4 w-full animate-pulse rounded bg-slate-100" />
            <div className="mt-2 h-4 w-4/5 animate-pulse rounded bg-slate-100" />
            {/* Form field skeletons */}
            <div className="mt-6 space-y-5">
              {[1, 2].map(i => (
                <div key={i}>
                  <div className="h-4 w-24 animate-pulse rounded bg-slate-200" />
                  <div className="mt-2 h-12 w-full animate-pulse rounded-xl border border-slate-200 bg-slate-50" />
                </div>
              ))}
            </div>
            {/* Button skeleton */}
            <div className="mt-6 h-12 w-full animate-pulse rounded-xl bg-[#15388c]/30" />
            {/* Link skeleton */}
            <div className="mt-5 flex justify-between">
              <div className="h-4 w-24 animate-pulse rounded bg-slate-100" />
              <div className="h-4 w-24 animate-pulse rounded bg-slate-100" />
            </div>
          </div>
        </div>
        <p className="mt-4 flex items-center justify-center gap-1.5 text-xs text-slate-400">
          <Building2 className="size-3 animate-pulse" />
          {label}
        </p>
      </section>
    </main>
  );
}
