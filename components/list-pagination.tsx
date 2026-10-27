import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";

export const LIST_PAGE_SIZE = 10;

export function parseListPage(value: unknown) {
  const n = Number(value);
  return Number.isFinite(n) && n >= 1 ? Math.floor(n) : 1;
}

export function paginateItems<T>(items: T[], page: number, pageSize = LIST_PAGE_SIZE) {
  const total = items.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const safePage = Math.min(Math.max(1, page), totalPages);
  const start = (safePage - 1) * pageSize;
  return {
    items: items.slice(start, start + pageSize),
    total,
    page: safePage,
    pageSize,
    totalPages,
    from: total === 0 ? 0 : start + 1,
    to: Math.min(start + pageSize, total),
  };
}

function buildHref(basePath: string, params: Record<string, string | undefined>, page: number) {
  const q = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (key === "page") continue;
    if (value) q.set(key, value);
  }
  if (page > 1) q.set("page", String(page));
  const qs = q.toString();
  return qs ? `${basePath}?${qs}` : basePath;
}

function pageWindow(current: number, totalPages: number) {
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1);
  const pages = new Set<number>([1, totalPages, current, current - 1, current + 1]);
  if (current <= 3) [2, 3, 4].forEach(p => pages.add(p));
  if (current >= totalPages - 2) [totalPages - 1, totalPages - 2, totalPages - 3].forEach(p => pages.add(p));
  return [...pages].filter(p => p >= 1 && p <= totalPages).sort((a, b) => a - b);
}

/** XPRO-style list footer: “Showing X–Y of Z” + page controls */
export function ListPagination({
  basePath,
  params = {},
  page,
  total,
  pageSize = LIST_PAGE_SIZE,
}: {
  basePath: string;
  params?: Record<string, string | undefined>;
  page: number;
  total: number;
  pageSize?: number;
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const safePage = Math.min(Math.max(1, page), totalPages);
  const from = total === 0 ? 0 : (safePage - 1) * pageSize + 1;
  const to = Math.min(safePage * pageSize, total);
  if (total === 0) return null;

  const pages = pageWindow(safePage, totalPages);

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 bg-white px-4 py-3">
      <p className="text-[13px] text-slate-500">
        Showing <span className="font-semibold text-slate-700">{from}</span> to{" "}
        <span className="font-semibold text-slate-700">{to}</span> of{" "}
        <span className="font-semibold text-slate-700">{total}</span> entries
      </p>
      <div className="flex items-center gap-1">
        <Link
          href={buildHref(basePath, params, Math.max(1, safePage - 1))}
          aria-disabled={safePage <= 1}
          className={`inline-flex size-8 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 transition ${
            safePage <= 1 ? "pointer-events-none opacity-40" : "hover:bg-slate-50"
          }`}
        >
          <ChevronLeft className="size-4" />
        </Link>
        {pages.map((p, index) => {
          const prev = pages[index - 1];
          const showGap = prev != null && p - prev > 1;
          return (
            <span key={p} className="flex items-center gap-1">
              {showGap && <span className="px-1 text-slate-400">…</span>}
              <Link
                href={buildHref(basePath, params, p)}
                className={`inline-flex size-8 items-center justify-center rounded-full text-[13px] font-semibold transition ${
                  p === safePage
                    ? "bg-[#15388c] text-white"
                    : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
                }`}
              >
                {p}
              </Link>
            </span>
          );
        })}
        <Link
          href={buildHref(basePath, params, Math.min(totalPages, safePage + 1))}
          aria-disabled={safePage >= totalPages}
          className={`inline-flex size-8 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-600 transition ${
            safePage >= totalPages ? "pointer-events-none opacity-40" : "hover:bg-slate-50"
          }`}
        >
          <ChevronRight className="size-4" />
        </Link>
      </div>
    </div>
  );
}
