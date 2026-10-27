"use client";

import { useMemo, useState } from "react";
import { ArrowRight, Bell, CheckCheck } from "lucide-react";
import type { AppNotification } from "@/lib/notifications";
import { readJsonResponse } from "@/lib/client-response";
import { ListFrame } from "@/components/list-frame";
import { LIST_PAGE_SIZE, paginateItems } from "@/components/list-pagination";

function formatWhen(value: number) {
  return new Date(value).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
}

export function NotificationList({
  initial,
  admin = false,
  query = "",
  unreadOnly = null,
}: {
  initial: AppNotification[];
  admin?: boolean;
  query?: string;
  /** null = all, true = unread only, false = read only */
  unreadOnly?: boolean | null;
}) {
  const [items, setItems] = useState(initial);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return items.filter(item => {
      if (unreadOnly === true && item.read_at) return false;
      if (unreadOnly === false && !item.read_at) return false;
      if (!q) return true;
      return `${item.title} ${item.message} ${item.type}`.toLowerCase().includes(q);
    });
  }, [items, query, unreadOnly]);

  const paged = paginateItems(filtered, page, LIST_PAGE_SIZE);
  const selected = items.find(item => item.id === selectedId) ?? null;
  const unread = items.filter(item => !item.read_at).length;

  async function mark(id?: string) {
    setError("");
    try {
      const audience = admin ? "admin" : "member";
      const response = await fetch("/api/notifications", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(id ? { id, audience } : { all: true, audience }),
      });
      const data = await readJsonResponse<{ error?: string }>(response);
      if (!response.ok) throw new Error(data.error || "Unable to update notification.");
      setItems(current =>
        current.map(item => (!id || item.id === id ? { ...item, read_at: Date.now() } : item)),
      );
      return true;
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to update notification.");
      return false;
    }
  }

  async function open(item: AppNotification) {
    if (!item.read_at && !(await mark(item.id))) return;
    window.location.assign(item.href);
  }

  if (selected) {
    return (
      <ListFrame
        tone="detail"
        header={
          <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
            <div className="flex min-w-0 items-center gap-2.5">
              <button
                type="button"
                onClick={() => setSelectedId(null)}
                className="inline-flex h-9 items-center gap-1.5 rounded-[12px] border border-slate-200 px-3 text-[13px] font-semibold text-slate-700 hover:bg-slate-50"
              >
                ← Back
              </button>
              <div className="min-w-0">
                <h2 className="truncate text-[15px] font-semibold text-slate-900">{selected.title}</h2>
                <p className="text-[12px] text-slate-500">{formatWhen(selected.created_at)}</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => open(selected)}
              className="inline-flex h-9 items-center gap-1.5 rounded-[12px] bg-[#15388c] px-3 text-[13px] font-semibold text-white hover:bg-[#102d74]"
            >
              Open details
              <ArrowRight className="size-4" />
            </button>
          </div>
        }
      >
        <div className="p-4">
          <div className="overflow-hidden rounded-[12px] border border-slate-200 bg-white">
            <div className="border-b border-slate-100 px-4 py-3">
              <div className="flex items-center gap-2.5">
                <span className="h-5 w-1 rounded-full bg-[#15388c]" />
                <h3 className="text-[14px] font-semibold text-slate-900">Notification</h3>
              </div>
            </div>
            <div className="space-y-3 p-4">
              <p className="text-[13px] leading-6 text-slate-700">{selected.message}</p>
              <div className="flex flex-wrap gap-2 text-[12px]">
                <span className="rounded-[12px] bg-slate-100 px-2.5 py-1 font-medium capitalize text-slate-600">
                  {selected.type.replaceAll("_", " ")}
                </span>
                <span
                  className={`rounded-[12px] px-2.5 py-1 font-semibold ${
                    selected.read_at
                      ? "bg-slate-100 text-slate-600"
                      : "bg-amber-50 text-amber-800"
                  }`}
                >
                  {selected.read_at ? "Read" : "Unread"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </ListFrame>
    );
  }

  return (
    <ListFrame
      header={
        <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-[12px] border border-amber-200 bg-amber-50 px-3 py-1 text-[12px] font-semibold text-amber-800">
              {unread} unread
            </span>
            <span className="rounded-[12px] border border-slate-200 bg-slate-50 px-3 py-1 text-[12px] text-slate-600">
              {filtered.length} notification{filtered.length === 1 ? "" : "s"}
            </span>
          </div>
          {unread > 0 ? (
            <button
              type="button"
              onClick={() => mark()}
              className="inline-flex h-9 items-center gap-1.5 rounded-[12px] border border-slate-200 bg-white px-3 text-[12px] font-semibold text-[#15388c] hover:bg-slate-50"
            >
              <CheckCheck className="size-4" />
              Mark all read
            </button>
          ) : null}
        </div>
      }
      footer={
        paged.total > LIST_PAGE_SIZE ? (
          <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
            <p className="text-[13px] text-slate-500">
              Showing {paged.from}–{paged.to} of {paged.total}
            </p>
            <div className="flex gap-1">
              <button
                type="button"
                disabled={paged.page <= 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
                className="inline-flex size-8 items-center justify-center rounded-full border border-slate-200 text-slate-600 disabled:opacity-40"
              >
                ‹
              </button>
              <span className="inline-flex size-8 items-center justify-center rounded-full bg-[#15388c] text-[12px] font-semibold text-white">
                {paged.page}
              </span>
              <button
                type="button"
                disabled={paged.page >= paged.totalPages}
                onClick={() => setPage(p => Math.min(paged.totalPages, p + 1))}
                className="inline-flex size-8 items-center justify-center rounded-full border border-slate-200 text-slate-600 disabled:opacity-40"
              >
                ›
              </button>
            </div>
          </div>
        ) : null
      }
    >
      {error ? (
        <p role="alert" className="m-4 rounded-[12px] bg-rose-50 p-3 text-[13px] text-rose-700">
          {error}
        </p>
      ) : null}

      {paged.items.length === 0 ? (
        <div className="grid place-items-center p-12 text-center">
          <Bell className="size-8 text-slate-300" />
          <p className="mt-3 text-[13px] text-slate-500">No notifications match these filters.</p>
        </div>
      ) : (
        <table className="w-full min-w-[720px] table-fixed text-left">
          <thead className="sticky top-0 z-10">
            <tr className="border-b border-slate-100 bg-[#fafbfc] text-[11px] font-semibold uppercase tracking-[0.12em] text-[#15388c]">
              <th className="w-[34%] px-4 py-3">Title</th>
              <th className="w-[36%] px-3 py-3">Message</th>
              <th className="w-[12%] px-3 py-3">Status</th>
              <th className="w-[14%] px-3 py-3">When</th>
              <th className="w-[4%] px-3 py-3 text-right" />
            </tr>
          </thead>
          <tbody>
            {paged.items.map(item => (
              <tr
                key={item.id}
                className={`cursor-pointer border-b border-slate-100 last:border-0 transition hover:bg-slate-50/80 ${
                  item.read_at ? "bg-white" : "bg-amber-50/40"
                }`}
                onClick={() => setSelectedId(item.id)}
              >
                <td className="px-4 py-3">
                  <div className="flex items-start gap-2">
                    {!item.read_at ? (
                      <span className="mt-1.5 size-2 shrink-0 rounded-full bg-amber-500" />
                    ) : (
                      <span className="mt-1.5 size-2 shrink-0 rounded-full bg-transparent" />
                    )}
                    <span className="min-w-0">
                      <span className="block truncate text-[13px] font-semibold text-slate-900">
                        {item.title}
                      </span>
                      <span className="mt-0.5 block truncate text-[11px] capitalize text-slate-500">
                        {item.type.replaceAll("_", " ")}
                      </span>
                    </span>
                  </div>
                </td>
                <td className="px-3 py-3 text-[13px] text-slate-600">
                  <span className="line-clamp-2">{item.message}</span>
                </td>
                <td className="px-3 py-3">
                  <span
                    className={`inline-flex rounded-[12px] px-2 py-1 text-[11px] font-semibold ${
                      item.read_at
                        ? "bg-slate-100 text-slate-600"
                        : "bg-amber-50 text-amber-800"
                    }`}
                  >
                    {item.read_at ? "Read" : "Unread"}
                  </span>
                </td>
                <td className="whitespace-nowrap px-3 py-3 text-[12px] text-slate-500">
                  {formatWhen(item.created_at)}
                </td>
                <td className="px-3 py-3 text-right">
                  <ArrowRight className="ml-auto size-4 text-[#15388c] opacity-60" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </ListFrame>
  );
}
