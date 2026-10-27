"use client";
import { useEffect, useState } from "react";
import { Bell, CheckCheck } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import type { AppNotification } from "@/lib/notifications";

export function NotificationMenu({
  initialCount = 0,
  admin = false,
}: {
  initialCount?: number;
  admin?: boolean;
}) {
  const [count, setCount] = useState(initialCount);
  const [items, setItems] = useState<AppNotification[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [busy, setBusy] = useState(false);
  const audience = admin ? "admin" : "member";

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const response = await fetch(`/api/notifications?audience=${audience}`, { cache: "no-store" });
        const data = (await response.json()) as { items?: AppNotification[]; unread?: number };
        if (!response.ok || cancelled) return;
        const list = data.items || [];
        const unread =
          typeof data.unread === "number"
            ? data.unread
            : list.filter(item => !item.read_at).length;
        setCount(unread);
      } catch {
        /* keep initialCount */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [audience]);

  async function load(open: boolean) {
    if (!open || loaded) return;
    setBusy(true);
    try {
      const response = await fetch(`/api/notifications?audience=${audience}`, { cache: "no-store" });
      const data = (await response.json()) as { items?: AppNotification[] };
      if (response.ok) {
        const list = data.items || [];
        setItems(list);
        setCount(list.filter(item => !item.read_at).length);
        setLoaded(true);
      }
    } finally {
      setBusy(false);
    }
  }

  async function mark(id?: string) {
    const response = await fetch("/api/notifications", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(id ? { id, audience } : { all: true, audience }),
    });
    if (!response.ok) return;
    setItems(current =>
      current.map(item => (!id || item.id === id ? { ...item, read_at: Date.now() } : item)),
    );
    setCount(id ? Math.max(0, count - 1) : 0);
  }

  return (
    <Popover onOpenChange={load}>
      <PopoverTrigger asChild>
        <button
          type="button"
          className="relative grid size-10 place-items-center rounded-full text-[#15388c] transition hover:bg-blue-50 dark:text-blue-200 dark:hover:bg-slate-800"
          aria-label={`${count} unread notifications`}
        >
          <Bell className="size-5" />
          {count > 0 && (
            <span className="absolute right-0 top-0 grid min-w-5 place-items-center rounded-full bg-rose-600 px-1 text-xs font-semibold text-white">
              {count > 99 ? "99+" : count}
            </span>
          )}
        </button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-[min(92vw,380px)] overflow-hidden p-0">
        <div className="flex items-center justify-between border-b px-4 py-3">
          <div>
            <h2 className="font-semibold">Notifications</h2>
            <p className="text-xs text-slate-500">{count} unread</p>
          </div>
          {count > 0 && (
            <button
              onClick={() => mark()}
              className="flex items-center gap-1 text-sm font-semibold text-emerald-700"
            >
              <CheckCheck className="size-4" />
              Mark all read
            </button>
          )}
        </div>
        <div className="max-h-[28rem] overflow-y-auto">
          {busy ? (
            <p className="p-6 text-center text-sm text-slate-500">Loading…</p>
          ) : items.length ? (
            items.slice(0, 12).map(item => (
              <button
                key={item.id}
                onClick={() => {
                  if (!item.read_at) mark(item.id);
                }}
                className={`block w-full border-b px-4 py-3 text-left last:border-0 ${
                  item.read_at ? "bg-white dark:bg-slate-900" : "bg-blue-50 dark:bg-blue-950/40"
                }`}
              >
                <div className="flex items-start gap-3">
                  {!item.read_at && <span className="mt-2 size-2 shrink-0 rounded-full bg-blue-600" />}
                  <div>
                    <p className="text-sm font-semibold">{item.title}</p>
                    <p className="mt-1 text-sm leading-5 text-slate-600">{item.message}</p>
                    <p className="mt-1 text-xs text-slate-500">
                      {new Date(item.created_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })}
                    </p>
                  </div>
                </div>
              </button>
            ))
          ) : (
            <p className="p-7 text-center text-sm text-slate-500">No notifications yet.</p>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
