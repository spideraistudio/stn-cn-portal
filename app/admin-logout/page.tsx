"use client";
import { useEffect, useRef, useState } from "react";
import { Loader2, AlertCircle } from "lucide-react";

export default function Page() {
  const [error, setError] = useState(false);
  const started = useRef(false);

  async function logout() {
    try {
      const response = await fetch("/api/admin-auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "logout" }),
      });
      if (!response.ok) throw new Error();
      location.replace("/admin-login");
    } catch {
      setError(true);
    }
  }

  // Fire-once logout on mount. setState only happens inside the async
  // resolution (after await), so it is not synchronous within the effect.
  useEffect(() => {
    if (started.current) return;
    started.current = true;
    void logout();
  }, []);

  return (
    <main className="grid min-h-screen place-items-center bg-gradient-to-br from-slate-50 via-[#f5f7fb] to-blue-50 p-5">
      <div className="flex w-full max-w-sm flex-col items-center rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        {error ? (
          <>
            <div className="grid size-12 place-items-center rounded-full bg-rose-50">
              <AlertCircle className="size-6 text-rose-600" />
            </div>
            <h1 className="mt-4 text-lg font-semibold text-slate-900">Sign-out incomplete</h1>
            <p className="mt-2 text-sm text-slate-500">The sign-out request did not finish. Please try again.</p>
            <button
              onClick={logout}
              className="mt-5 w-full rounded-lg bg-[#15388c] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#1d46a8]"
            >
              Retry sign out
            </button>
          </>
        ) : (
          <>
            <Loader2 className="size-8 animate-spin text-[#15388c]" />
            <h1 className="mt-4 text-lg font-semibold text-slate-900">Signing out…</h1>
            <p className="mt-2 text-sm text-slate-500">Closing your administrator session.</p>
          </>
        )}
      </div>
    </main>
  );
}
