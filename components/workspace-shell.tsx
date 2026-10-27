"use client";

import Link from "next/link";
import { PortalSwitch } from "@/components/portal-switch";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { createPortal } from "react-dom";
import { usePathname } from "next/navigation";
import { AppSidebar } from "@/components/app-sidebar";
import { NotificationMenu } from "@/components/notification-menu";

export type WorkspaceAction = {
  href: string;
  label: string;
  variant?: "primary" | "secondary" | "ghost";
  external?: boolean;
};

export type WorkspacePageMeta = {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: WorkspaceAction[];
};

type WorkspaceMetaContextValue = {
  setPageMeta: (meta: WorkspacePageMeta | null) => void;
  filterHost: HTMLElement | null;
};

const WorkspaceMetaContext = createContext<WorkspaceMetaContextValue | null>(null);

/** Put page title + action buttons into the second (page) header bar. */
export function useWorkspacePageMeta(meta: WorkspacePageMeta) {
  const ctx = useContext(WorkspaceMetaContext);
  useEffect(() => {
    if (!ctx) return;
    ctx.setPageMeta(meta);
    return () => ctx.setPageMeta(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ctx, meta.eyebrow, meta.title, meta.description, JSON.stringify(meta.actions ?? [])]);
}

/** Portal filter / toolbar controls into the second header bar. */
export function WorkspaceFilters({ children }: { children: ReactNode }) {
  const ctx = useContext(WorkspaceMetaContext);
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted || !ctx?.filterHost) return null;
  return createPortal(children, ctx.filterHost);
}

const ADMIN_DEFAULTS: Record<string, WorkspacePageMeta> = {
  "/admin": {
    title: "Platform overview",
    description: "Review pending work and monitor Sellers Trust Network activity.",
    actions: [
      { href: "/admin/reports", label: "Review reports", variant: "primary" },
      { href: "/admin/companies", label: "Member companies", variant: "secondary" },
      { href: "/admin/preview", label: "Member preview", variant: "ghost" },
    ],
  },
  "/admin/companies": {
    title: "Member Company",
    description: "Review company identity and manage member access.",
  },
  "/admin/reports": {
    title: "Seller reports",
    description: "Review pending submissions or filter the full report history.",
  },
  "/admin/resolutions": {
    eyebrow: "Administrator console",
    title: "Dispute resolutions",
    description: "Pending requests appear first. Decisions stay in review history.",
  },
  "/admin/notifications": {
    eyebrow: "Administrator console",
    title: "Notifications",
    description: "New work and security warnings requiring attention.",
  },
  "/admin/pilot": {
    eyebrow: "Administrator console",
    title: "Pilot Center",
    description: "Track pilot issues, checks and test accounts.",
  },
  "/admin/governance": {
    eyebrow: "Administrator console",
    title: "Data governance",
    description: "Correction, deletion, retention and legal-hold actions.",
  },
  "/admin/audit": {
    eyebrow: "Administrator console",
    title: "Audit trail",
    description: "Read-only history of membership and report activity.",
  },
  "/admin/security": {
    eyebrow: "Administrator console",
    title: "Account & security",
    description: "Manage your administrator password.",
  },
  "/admin/preview": {
    eyebrow: "Administrator console",
    title: "Member preview",
    description: "Preview the member workspace with fictional sample data.",
  },
};

const MEMBER_DEFAULTS: Record<string, WorkspacePageMeta> = {
  "/member": {
    eyebrow: "Company workspace",
    title: "Dashboard",
    description: "Search sellers, submit reports and manage your company membership.",
    actions: [
      { href: "/member/sellers", label: "Search sellers", variant: "primary" },
      { href: "/member/submit-report", label: "Submit report", variant: "secondary" },
      { href: "/member/profile", label: "Company profile", variant: "ghost" },
    ],
  },
  "/member/sellers": {
    eyebrow: "Company workspace",
    title: "Search sellers",
    description: "Search approved business experience reports in your category.",
  },
  "/member/submit-report": {
    eyebrow: "Company workspace",
    title: "Submit report",
    description:
      "Provide factual business information. Admin approval is required before other members can find it.",
  },
  "/member/reports": {
    eyebrow: "Company workspace",
    title: "My reports",
    description: "Search your submissions or open a seller report.",
  },
  "/member/profile": {
    eyebrow: "Company workspace",
    title: "Company profile",
    description: "Review company identity and request contact updates.",
  },
  "/member/account": {
    eyebrow: "Company workspace",
    title: "Account & security",
    description: "Manage password security and account closure.",
  },
  "/member/issues": {
    eyebrow: "Company workspace",
    title: "Report a problem",
    description: "Send a problem to the administrator and follow testing status.",
  },
  "/member/about": {
    eyebrow: "Company workspace",
    title: "About us",
    description: "Why Sellers Trust Network was created.",
  },
  "/member/contact": {
    eyebrow: "Company workspace",
    title: "Contact us",
    description: "Support, privacy and grievance contact details.",
  },
  "/member/notifications": {
    eyebrow: "Company workspace",
    title: "Notifications",
    description: "Updates about membership, reports and account security.",
  },
  "/member/password": {
    eyebrow: "Company workspace",
    title: "Change password",
    description: "Update your member login password.",
  },
};

function resolveDefaultMeta(path: string, admin: boolean): WorkspacePageMeta {
  const map = admin ? ADMIN_DEFAULTS : MEMBER_DEFAULTS;
  if (map[path]) return map[path];

  if (admin && path.startsWith("/admin/members/")) {
    return {
      title: "Company detail",
      description: "Review membership status, reports and account activity.",
    };
  }
  if (admin && path.startsWith("/admin/companies")) {
    return {
      title: "Member Company",
      description: "Review company identity and manage member access.",
    };
  }
  if (!admin && path.includes("/member/reports/") && path.endsWith("/edit")) {
    return {
      eyebrow: "Company workspace",
      title: "Edit report",
      description: "Update your report before or after administrator review.",
    };
  }
  if (!admin && path.includes("/member/reports/") && path.endsWith("/resolve")) {
    return {
      eyebrow: "Company workspace",
      title: "Mark dispute resolved",
      description: "Submit a resolution request for administrator approval.",
    };
  }

  return {
    eyebrow: admin ? "Administrator console" : "Company workspace",
    title: admin ? "Administrator" : "Member workspace",
  };
}

function ActionButton({ action }: { action: WorkspaceAction }) {
  const base =
    "inline-flex h-9 items-center justify-center rounded-[12px] px-3.5 text-[12px] font-semibold transition whitespace-nowrap";
  const styles =
    action.variant === "primary"
      ? "bg-[#15388c] text-white shadow-sm hover:bg-[#102d74]"
      : action.variant === "ghost"
        ? "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
        : "border border-blue-200 bg-white text-[#15388c] hover:bg-blue-50";

  if (action.external) {
    return (
      <a href={action.href} className={`${base} ${styles}`}>
        {action.label}
      </a>
    );
  }
  return (
    <Link href={action.href} className={`${base} ${styles}`}>
      {action.label}
    </Link>
  );
}

export function WorkspaceShell({
  admin = false,
  notificationCount = 0,
  children,
}: {
  admin?: boolean;
  notificationCount?: number;
  children: ReactNode;
}) {
  const path = usePathname();
  const [override, setOverride] = useState<WorkspacePageMeta | null>(null);
  const [filterHost, setFilterHost] = useState<HTMLElement | null>(null);
  const [filterOccupied, setFilterOccupied] = useState(false);
  const filterHostRef = useRef<HTMLDivElement>(null);

  const setPageMeta = useCallback((meta: WorkspacePageMeta | null) => {
    setOverride(meta);
  }, []);

  const ctx = useMemo(
    () => ({ setPageMeta, filterHost }),
    [setPageMeta, filterHost],
  );

  useEffect(() => {
    setOverride(null);
  }, [path]);

  useEffect(() => {
    setFilterHost(filterHostRef.current);
  }, []);

  // Detect when portal content is present so we can show the filter strip chrome
  useEffect(() => {
    if (!filterHost) {
      setFilterOccupied(false);
      return;
    }
    const sync = () => setFilterOccupied(filterHost.childElementCount > 0);
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(filterHost, { childList: true });
    return () => observer.disconnect();
  }, [filterHost, path]);

  const meta = override ?? resolveDefaultMeta(path, admin);

  return (
    <WorkspaceMetaContext.Provider value={ctx}>
      <div className="stn-workspace h-dvh overflow-hidden bg-[#f5f7fb]">
        <AppSidebar admin={admin} />
        <div className="flex h-dvh flex-col gap-3 p-3 lg:pl-[var(--stn-sidebar-offset,calc(244px+1.5rem))]">
          {/* 1) Main chrome header */}
          <header className="stn-topbar z-20 flex h-14 shrink-0 items-center justify-between gap-4 rounded-[12px] border border-slate-200/80 bg-white px-4 shadow-sm sm:px-5">
            <div className="min-w-0 pl-14 lg:pl-0">
              <p className="truncate text-[13px] font-semibold text-[#15388c]">
                Sellers Trust Network
              </p>
              <p className="truncate text-[12px] text-slate-500">
                {admin ? "Administrator workspace" : "Member workspace"}
              </p>
            </div>
            <div className="flex items-center gap-4"><PortalSwitch admin={admin}/><NotificationMenu initialCount={notificationCount} admin={admin} /></div>
          </header>

          {/* 2) Page header — compact title + XPRO search/filter toolbar */}
          <header className="stn-page-heading z-20 shrink-0 rounded-[12px] border border-slate-200/80 bg-white shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-5">
              <div className="min-w-0 flex-1">
                <h1 className="truncate text-[15px] font-semibold tracking-tight text-slate-900 sm:text-[16px]">
                  {meta.title}
                </h1>
                {meta.description && (
                  <p className="mt-0.5 max-w-2xl truncate text-[12px] text-slate-500">
                    {meta.description}
                  </p>
                )}
              </div>
              {(meta.actions?.length ?? 0) > 0 && (
                <div className="flex flex-wrap items-center justify-end gap-2">
                  {meta.actions!.map(action => (
                    <ActionButton key={`${action.href}-${action.label}`} action={action} />
                  ))}
                </div>
              )}
            </div>
            <div
              className={
                filterOccupied
                  ? "border-t border-slate-100 px-4 py-3 sm:px-5"
                  : undefined
              }
            >
              <div ref={filterHostRef} data-workspace-filters />
            </div>
          </header>

          {/* Inner data panel */}
          <div className="stn-content min-h-0 flex-1 overflow-hidden rounded-[12px] border border-slate-200/80 bg-[#f8fafc] shadow-sm">
            <div className="stn-page-scroll h-full min-h-0 overflow-y-auto overscroll-contain p-4 sm:p-5 lg:p-6" data-workspace-scroll>
              {children}
            </div>
          </div>
        </div>
      </div>
    </WorkspaceMetaContext.Provider>
  );
}
