"use client";

import {
  useEffect,
  useId,
  useState,
  type FormEvent,
  type InputHTMLAttributes,
  type ReactNode,
  type SelectHTMLAttributes,
} from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Download, ListFilter, Search, X } from "lucide-react";

export const filterControlClass =
  "h-10 w-full rounded-[12px] border border-slate-200 bg-white px-3 text-[13px] text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/15";

export const filterLabelClass =
  "mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.06em] text-slate-500";

const pillBtn =
  "inline-flex h-10 items-center gap-2 rounded-[12px] border border-slate-300 bg-white px-4 text-[13px] font-medium text-slate-800 transition hover:bg-slate-50";

/** Search + Filter + Export. Enter in search keeps current filters; Filter opens a modal. */
export function SearchToolbar({
  action,
  searchName = "q",
  searchDefault = "",
  searchPlaceholder = "Search...",
  clearHref,
  exportHref,
  exportLabel = "Export",
  children,
  hiddenFields,
  activeFilterCount = 0,
}: {
  action?: string;
  searchName?: string;
  searchDefault?: string;
  searchPlaceholder?: string;
  clearHref?: string;
  exportHref?: string;
  exportLabel?: string;
  children?: ReactNode;
  hiddenFields?: ReactNode;
  activeFilterCount?: number;
}) {
  const reactId = useId();
  const titleId = `stn-filter-title-${reactId.replace(/:/g, "")}`;
  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const router = useRouter();
  const pathname = usePathname();
  const hasFilters = Boolean(children);
  const basePath = action || pathname;

  useEffect(() => setMounted(true), []);

  function pushParams(params: URLSearchParams) {
    params.delete("page");
    const qs = params.toString();
    setOpen(false);
    router.push(qs ? `${basePath}?${qs}` : basePath);
  }

  /** Enter in search box: update q only, keep other query params. */
  function onSearchSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const q = String(new FormData(form).get(searchName) || "").trim();
    const params = new URLSearchParams(
      typeof window !== "undefined" ? window.location.search : "",
    );
    if (q) params.set(searchName, q);
    else params.delete(searchName);
    pushParams(params);
  }

  /** Apply Filters: replace filter fields from the modal form, keep search text. */
  function onFilterApply(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const panel = event.currentTarget;
    const panelData = new FormData(panel);
    const params = new URLSearchParams();

    // Keep current search text from the toolbar input
    const searchInput = document.querySelector<HTMLInputElement>(
      `form[data-stn-search] input[name="${searchName}"]`,
    );
    const q = String(searchInput?.value || searchDefault || "").trim();
    if (q) params.set(searchName, q);

    panelData.forEach((value, key) => {
      const v = String(value).trim();
      if (v) params.set(key, v);
    });

    // Preserve hidden context (e.g. memberId) from the search form
    const searchForm = document.querySelector<HTMLFormElement>("form[data-stn-search]");
    if (searchForm) {
      const hidden = new FormData(searchForm);
      hidden.forEach((value, key) => {
        if (key === searchName) return;
        if (panelData.has(key)) return;
        const v = String(value).trim();
        if (v) params.set(key, v);
      });
    }

    pushParams(params);
  }

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const filterModal =
    hasFilters && open && mounted
      ? createPortal(
          <div className="fixed inset-0 z-[200]">
            <button
              type="button"
              className="absolute inset-0 bg-black/40"
              aria-label="Close filters"
              onClick={() => setOpen(false)}
            />
            <div
              role="dialog"
              aria-modal="true"
              aria-labelledby={titleId}
              className="absolute left-1/2 top-[12vh] z-[201] w-[min(92vw,520px)] -translate-x-1/2 overflow-hidden rounded-[12px] border border-slate-200 bg-white shadow-xl sm:top-1/2 sm:-translate-y-1/2"
            >
              <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3.5">
                <p id={titleId} className="text-[16px] font-semibold text-slate-900">
                  Filters
                </p>
                <button
                  type="button"
                  className="grid size-8 place-items-center rounded-[12px] text-slate-500 hover:bg-slate-100"
                  aria-label="Close filters"
                  onClick={() => setOpen(false)}
                >
                  <X className="size-4" />
                </button>
              </div>

              <form onSubmit={onFilterApply}>
                <div className="grid gap-4 px-5 py-5 sm:grid-cols-2">{children}</div>
                <div className="flex items-center justify-between gap-3 border-t border-slate-100 bg-[#f8fafc] px-5 py-3.5">
                  {clearHref ? (
                    <Link
                      href={clearHref}
                      onClick={() => setOpen(false)}
                      className="inline-flex h-10 items-center rounded-[12px] bg-slate-100 px-4 text-[13px] font-medium text-slate-600 transition hover:bg-slate-200"
                    >
                      Clear All
                    </Link>
                  ) : (
                    <span />
                  )}
                  <button
                    type="submit"
                    className="inline-flex h-10 items-center rounded-[12px] border border-slate-900 bg-white px-5 text-[13px] font-semibold text-slate-900 transition hover:bg-slate-50"
                  >
                    Apply Filters
                  </button>
                </div>
              </form>
            </div>
          </div>,
          document.body,
        )
      : null;

  return (
    <>
      <form
        data-stn-search
        method="get"
        action={basePath}
        onSubmit={onSearchSubmit}
        className="flex w-full flex-wrap items-center gap-2.5"
      >
        {hiddenFields}

        <div className="relative min-w-[180px] flex-1 sm:max-w-md lg:max-w-lg">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
          <input
            name={searchName}
            defaultValue={searchDefault}
            placeholder={searchPlaceholder}
            className="h-10 w-full rounded-[12px] border border-slate-200 bg-white py-2 pl-10 pr-4 text-[13px] text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/12"
          />
        </div>

        <div className="ml-auto flex flex-wrap items-center gap-2">
          {hasFilters ? (
            <button
              type="button"
              className={pillBtn}
              aria-expanded={open}
              aria-haspopup="dialog"
              onClick={() => setOpen(true)}
            >
              <ListFilter className="size-4" />
              Filter
              {activeFilterCount > 0 && (
                <span className="grid min-w-5 place-items-center rounded-[12px] bg-[#15388c] px-1.5 text-[11px] font-semibold text-white">
                  {activeFilterCount}
                </span>
              )}
            </button>
          ) : (
            <button type="submit" className={pillBtn}>
              <Search className="size-4" />
              Search
            </button>
          )}

          {exportHref && (
            <a href={exportHref} className={pillBtn}>
              <Download className="size-4" />
              {exportLabel}
            </a>
          )}
        </div>
      </form>

      {filterModal}
    </>
  );
}

export function FilterField({
  label,
  className = "",
  children,
}: {
  label?: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <label className={`block ${className}`}>
      {label ? <span className={filterLabelClass}>{label}</span> : null}
      {children}
    </label>
  );
}

export function FilterInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={filterControlClass} {...props} />;
}

export function FilterSelect({
  children,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement> & { children?: ReactNode }) {
  return (
    <select className={filterControlClass} {...props}>
      {children}
    </select>
  );
}

export function FilterBar({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={`flex flex-wrap items-end gap-2.5 ${className}`}>{children}</div>;
}

export function FilterActions({
  clearHref,
  applyLabel = "Filter",
  children,
}: {
  clearHref?: string;
  applyLabel?: string;
  children?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2 pb-0.5">
      <button
        type="submit"
        className="inline-flex h-10 items-center rounded-[12px] bg-[#15388c] px-4 text-[13px] font-semibold text-white"
      >
        {applyLabel}
      </button>
      {clearHref && (
        <Link
          href={clearHref}
          className="inline-flex h-10 items-center rounded-[12px] border border-slate-200 bg-white px-4 text-[13px] font-semibold text-slate-700"
        >
          Clear
        </Link>
      )}
      {children}
    </div>
  );
}
