"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bell,
  Building2,
  CircleHelp,
  FilePlus2,
  Files,
  FlaskConical,
  Gavel,
  Home,
  Info,
  LogOut,
  Mail,
  PanelLeftClose,
  Search,
  ScrollText,
  ShieldCheck,
  UserCog,
} from "lucide-react";
import { BrandLogo } from "@/components/brand-logo";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

const SIDEBAR_BG = "#102d74";
const ACTIVE = "var(--suite-nav-accent, #d6b447)";
const MUTED = "rgba(255,255,255,0.78)";
const HOVER = "rgba(255,255,255,0.08)";
/** Equal outer inset around the floating sidebar / header chrome */
const INSET = "0.75rem";

type NavItem = {
  href: string;
  label: string;
  icon: typeof Home;
  exact?: boolean;
};

const memberNav: NavItem[] = [
  { href: "/member", label: "Dashboard", icon: Home, exact: true },
  { href: "/member/users", label: "Company users", icon: UserCog },
  { href: "/member/sellers", label: "Search sellers", icon: Search },
  { href: "/member/submit-report", label: "Submit report", icon: FilePlus2 },
  { href: "/member/buy-sell", label: "Buy/Sell Requirements", icon: Files },
  { href: "/member/reports", label: "My reports", icon: Files },
  { href: "/member/profile", label: "Company profile", icon: Building2 },
  { href: "/member/account", label: "Account & security", icon: UserCog },
  { href: "/member/issues", label: "Report a problem", icon: CircleHelp },
  { href: "/member/about", label: "About us", icon: Info },
  { href: "/member/contact", label: "Contact us", icon: Mail },
  { href: "/privacy", label: "Privacy Policy", icon: ShieldCheck },
  { href: "/terms", label: "Terms of Use", icon: ScrollText },
  { href: "/disclaimer", label: "Disclaimer", icon: Gavel },
];

const adminNav: NavItem[] = [
  { href: "/admin/cn", label: "CN & company management", icon: Building2 },
  { href: "/admin", label: "Dashboard", icon: Home, exact: true },
  { href: "/admin/companies", label: "Member Company", icon: Building2 },
  { href: "/admin/reports", label: "Seller reports", icon: Files },
  { href: "/admin/resolutions", label: "Resolutions", icon: Gavel },
  { href: "/admin/notifications", label: "Notifications", icon: Bell },
  { href: "/admin/seed-trade", label: "Seed trade oversight", icon: Files },
  { href: "/admin/pilot", label: "Pilot Center", icon: FlaskConical },
  { href: "/admin/governance", label: "Data governance", icon: ShieldCheck },
  { href: "/admin/audit", label: "Audit trail", icon: ScrollText },
  { href: "/admin/security", label: "Account & security", icon: UserCog },
];

function isActive(path: string, item: NavItem) {
  if (item.exact || item.href === "/admin" || item.href === "/member") return path === item.href;
  if (item.href === "/admin/companies") {
    return path === "/admin/companies" || path.startsWith("/admin/companies/") || path.startsWith("/admin/members/");
  }
  return path === item.href || path.startsWith(`${item.href}/`);
}

function SidebarChrome({
  admin,
  path,
  collapsed,
  onToggleCollapse,
  wrapLink,
  className = "",
  logoOpensDrawer = false,
}: {
  admin: boolean;
  path: string;
  collapsed: boolean;
  onToggleCollapse?: () => void;
  wrapLink: (node: ReactNode) => ReactNode;
  className?: string;
  /** When collapsed, logo expands the rail instead of navigating home */
  logoOpensDrawer?: boolean;
}) {
  const allItems = admin ? adminNav : memberNav;
  const shared = new Set(['/member/users','/member/account','/member/issues','/member/about','/member/contact','/privacy','/terms','/disclaimer','/admin/security']);
  const items = process.env.NEXT_PUBLIC_COMMON_PORTAL==='1' ? allItems.filter(item=>!shared.has(item.href)) : allItems;
  const home = admin ? "/admin" : "/member";
  const showCollapseToggle = Boolean(onToggleCollapse) && !collapsed;

  const logoMark = (
    <span className="grid size-9 shrink-0 place-items-center overflow-hidden rounded-[12px] bg-white/10">
      <BrandLogo compact className="size-7" />
    </span>
  );

  return (
    <aside
      className={`flex h-full flex-col rounded-[12px] text-white shadow-sm ${
        collapsed ? "w-[72px]" : "w-[244px]"
      } ${className}`}
      style={{ background: SIDEBAR_BG }}
    >
      <div className="flex h-full flex-col p-3">
        <div className={`mb-4 flex items-center gap-2 ${collapsed ? "flex-col" : ""}`}>
          {collapsed && logoOpensDrawer && onToggleCollapse ? (
            <button
              type="button"
              onClick={onToggleCollapse}
              className="flex flex-col items-center gap-1 rounded-[12px] outline-none transition hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-[#d6b447]/60"
              aria-label="Open sidebar"
              title="Open sidebar"
            >
              {logoMark}
            </button>
          ) : (
            wrapLink(
              <Link
                href={home}
                className={`flex min-w-0 items-center gap-2.5 ${collapsed ? "" : "flex-1"}`}
              >
                {logoMark}
                {!collapsed && (
                  <span className="truncate text-[15px] font-bold leading-tight tracking-tight">
                    Sellers Trust
                  </span>
                )}
              </Link>,
            )
          )}

          {/* Drawer toggle only when expanded — hidden in collapsed/small rail */}
          {showCollapseToggle && (
            <button
              type="button"
              onClick={onToggleCollapse}
              className="grid size-8 shrink-0 place-items-center rounded-[12px] border border-white/15 text-white/70 transition hover:bg-white/10 hover:text-white"
              aria-label="Collapse sidebar"
            >
              <PanelLeftClose className="size-4" />
            </button>
          )}
        </div>

        <nav aria-label="Primary" className="flex flex-1 flex-col gap-1.5 overflow-y-auto">
          {items.map(item => {
            const active = isActive(path, item);
            const Icon = item.icon;
            return (
              <div key={item.href}>
                {wrapLink(
                  <Link
                    href={item.href}
                    prefetch
                    title={collapsed ? item.label : undefined}
                    aria-current={active ? "page" : undefined}
                    className={`flex items-center gap-3 rounded-[12px] px-3 py-2.5 text-[13px] font-medium transition ${
                      collapsed ? "justify-center px-0" : ""
                    }`}
                    style={{
                      color: active ? ACTIVE : MUTED,
                      background: active ? "rgba(214,180,71,0.12)" : "transparent",
                      border: active ? `1.5px solid ${ACTIVE}` : "1.5px solid transparent",
                    }}
                    onMouseEnter={e => {
                      if (!active) e.currentTarget.style.background = HOVER;
                    }}
                    onMouseLeave={e => {
                      if (!active) e.currentTarget.style.background = "transparent";
                    }}
                  >
                    <Icon className="size-[18px] shrink-0" strokeWidth={1.75} />
                    {!collapsed && <span className="truncate">{item.label}</span>}
                  </Link>,
                )}
              </div>
            );
          })}
        </nav>

        <div className="mt-3 border-t border-white/10 pt-3">
          {wrapLink(
            <a
              href={admin ? "/admin-logout" : "/logout"}
              title={collapsed ? "Sign out" : undefined}
              className={`flex items-center gap-3 rounded-[12px] px-3 py-2.5 text-[13px] font-medium transition ${
                collapsed ? "justify-center px-0" : ""
              }`}
              style={{ color: MUTED }}
              onMouseEnter={e => {
                e.currentTarget.style.background = HOVER;
                e.currentTarget.style.color = "#fff";
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = "transparent";
                e.currentTarget.style.color = MUTED;
              }}
            >
              <LogOut className="size-[18px] shrink-0" strokeWidth={1.75} />
              {!collapsed && "Sign out"}
            </a>,
          )}
          {!collapsed && (
            <p className="px-3 pb-1 pt-3 text-[10px] font-semibold uppercase tracking-[0.08em] text-white/40">
              {admin ? "Administrator" : "Member workspace"}
            </p>
          )}
        </div>
      </div>
    </aside>
  );
}

export function AppSidebar({ admin = false }: { admin?: boolean }) {
  const path = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const rail = collapsed ? 72 : 244;

  useEffect(() => {
    document.documentElement.style.setProperty(
      "--stn-sidebar-offset",
      `calc(${INSET} + ${rail}px + ${INSET})`,
    );
    document.documentElement.style.setProperty("--stn-chrome-inset", INSET);
    return () => {
      document.documentElement.style.removeProperty("--stn-sidebar-offset");
      document.documentElement.style.removeProperty("--stn-chrome-inset");
    };
  }, [rail]);

  // Close mobile drawer on route change
  useEffect(() => {
    // Reset the navigation drawer when a destination opens.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMobileOpen(false);
  }, [path]);

  return (
    <>
      {/* Desktop floating rail */}
      <div
        className="fixed z-30 hidden lg:flex"
        style={{
          top: INSET,
          bottom: INSET,
          left: INSET,
          width: rail,
        }}
      >
        <SidebarChrome
          admin={admin}
          path={path}
          collapsed={collapsed}
          logoOpensDrawer
          onToggleCollapse={() => setCollapsed(v => !v)}
          wrapLink={node => node}
        />
      </div>

      {/* Mobile: logo opens drawer (no separate Menu / drawer icon) */}
      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <SheetTrigger asChild>
          <button
            type="button"
            className="fixed z-40 grid size-11 place-items-center rounded-[12px] shadow-md lg:hidden"
            style={{ background: SIDEBAR_BG, top: INSET, left: INSET }}
            aria-label="Open navigation menu"
          >
            <span className="grid size-9 place-items-center overflow-hidden rounded-[12px] bg-white/10">
              <BrandLogo compact className="size-7" />
            </span>
          </button>
        </SheetTrigger>
        <SheetContent
          side="left"
          showCloseButton
          className="w-[min(100%,280px)] gap-0 border-0 bg-transparent p-3 text-white sm:max-w-[280px] [&>button]:right-5 [&>button]:top-5 [&>button]:text-white"
        >
          <SheetTitle className="sr-only">
            {admin ? "Administrator navigation" : "Member navigation"}
          </SheetTitle>
          <SheetDescription className="sr-only">Open a Sellers Trust Network section.</SheetDescription>
          <SidebarChrome
            admin={admin}
            path={path}
            collapsed={false}
            className="pr-8"
            wrapLink={node => <SheetClose asChild>{node}</SheetClose>}
          />
        </SheetContent>
      </Sheet>
    </>
  );
}
