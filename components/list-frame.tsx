import type { ReactNode } from "react";

/**
 * Full-bleed list chrome: table touches card edges, pagination sticks to bottom.
 * Cancels workspace content padding so the panel is edge-to-edge.
 */
export function ListFrame({
  header,
  children,
  footer,
  tone = "list",
}: {
  header?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  /** list = white table canvas; detail = soft grey XPRO detail canvas */
  tone?: "list" | "detail";
}) {
  const canvas = tone === "detail" ? "bg-[#f5f7fb]" : "bg-white";
  return (
    <div
      className={`-m-4 flex h-[calc(100%+2rem)] min-h-0 flex-col overflow-hidden sm:-m-5 sm:h-[calc(100%+2.5rem)] lg:-m-6 lg:h-[calc(100%+3rem)] ${canvas}`}
    >
      {header ? (
        <div className="shrink-0 border-b border-slate-100 bg-white">{header}</div>
      ) : null}
      <div className="min-h-0 flex-1 overflow-auto overscroll-contain">{children}</div>
      {footer ? (
        <div className="shrink-0 border-t border-slate-100 bg-white">{footer}</div>
      ) : null}
    </div>
  );
}

/** XPRO-style detail section card with accent bar on the title */
export function DetailSection({
  title,
  children,
  className = "",
  action,
}: {
  title: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}) {
  return (
    <section className={`overflow-hidden rounded-[12px] border border-slate-200 bg-white ${className}`}>
      <div className="flex items-center justify-between gap-3 border-b border-slate-100 px-4 py-3">
        <div className="flex min-w-0 items-center gap-2.5">
          <span className="h-5 w-1 shrink-0 rounded-full bg-[#15388c]" />
          <h3 className="truncate text-[14px] font-semibold text-slate-900">{title}</h3>
        </div>
        {action}
      </div>
      <div className="p-4">{children}</div>
    </section>
  );
}
