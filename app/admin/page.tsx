import { redirect } from "next/navigation";
import Link from "next/link";
import { chatGPTSignInPath, getChatGPTUser } from "../chatgpt-auth";
import { isConfiguredAdmin } from "@/lib/member-data";
import { adminCounts } from "@/lib/admin-dashboard";
import { ReportShell } from "@/components/report-shell";
import { AdminDashboardCharts } from "@/components/admin-dashboard-charts";
import {
  AlertTriangle,
  ArrowRight,
  Building2,
  CheckCircle2,
  Clock3,
  FileCheck2,
  FileText,
  FileX2,
  Gavel,
  IndianRupee,
  KeyRound,
  Users,
  type LucideIcon,
} from "lucide-react";

export const dynamic = "force-dynamic";

const money = (paise: number) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format((Number(paise) || 0) / 100);

const num = (value: number) =>
  new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(Number(value) || 0);

type Tone = "amber" | "emerald" | "rose" | "slate" | "blue";

const toneClass: Record<Tone, { value: string; icon: string; soft: string; arrow: string }> = {
  amber: {
    value: "text-amber-800",
    icon: "bg-amber-50 text-amber-700",
    soft: "border-amber-200 bg-amber-50/70",
    arrow: "text-amber-600",
  },
  emerald: {
    value: "text-emerald-800",
    icon: "bg-emerald-50 text-emerald-700",
    soft: "border-emerald-200 bg-emerald-50/70",
    arrow: "text-emerald-600",
  },
  rose: {
    value: "text-rose-800",
    icon: "bg-rose-50 text-rose-700",
    soft: "border-rose-200 bg-rose-50/70",
    arrow: "text-rose-600",
  },
  slate: {
    value: "text-slate-800",
    icon: "bg-slate-100 text-slate-600",
    soft: "border-slate-200 bg-slate-50",
    arrow: "text-slate-500",
  },
  blue: {
    value: "text-[#15388c]",
    icon: "bg-[#ece8f8] text-[#15388c]",
    soft: "border-blue-200 bg-blue-50/60",
    arrow: "text-[#15388c]",
  },
};

type StatCard = {
  label: string;
  value: string | number;
  href: string;
  tone: Tone;
  icon: LucideIcon;
};

type StatGroup = {
  title: string;
  cards: StatCard[];
};

function TotalsGrid({ cards }: { cards: StatCard[] }) {
  return (
    <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3 xl:grid-cols-4">
      {cards.map(card => {
        const Icon = card.icon;
        const tone = toneClass[card.tone];
        return (
          <Link
            key={card.label}
            href={card.href}
            className="group rounded-[12px] border border-slate-200 bg-white px-3 py-3 transition hover:border-[#15388c]/35 hover:shadow-sm"
          >
            <div className="flex items-start justify-between gap-2">
              <p className="text-[11px] font-medium leading-snug text-slate-500">{card.label}</p>
              <span className={`grid size-7 shrink-0 place-items-center rounded-[8px] ${tone.icon}`}>
                <Icon className="size-3.5" />
              </span>
            </div>
            <p className={`mt-2 text-[18px] font-semibold tracking-tight ${tone.value}`}>
              {typeof card.value === "number" ? num(card.value) : card.value}
            </p>
            <div
              className={`mt-2 flex items-center justify-end gap-1 text-[11px] font-semibold ${tone.arrow} opacity-70 transition group-hover:translate-x-0.5 group-hover:opacity-100`}
            >
              <span>Open</span>
              <ArrowRight className="size-3.5" />
            </div>
          </Link>
        );
      })}
    </div>
  );
}

export default async function AdminPage() {
  const user = await getChatGPTUser();
  if (!user) {
    return (
      <main className="grid min-h-screen place-items-center bg-[#f5f7fb] p-5">
        <a
          href={chatGPTSignInPath("/admin")}
          target="_top"
          className="rounded-[12px] bg-[#15388c] px-7 py-4 font-semibold text-white"
        >
          Administrator sign in
        </a>
      </main>
    );
  }
  if (!isConfiguredAdmin(user.email)) redirect("/join");

  const counts = await adminCounts();

  const attentionNeeded =
    counts.pendingMembers +
    counts.pendingReports +
    counts.pendingResolutions +
    counts.pendingPasswordResets;

  const groups: StatGroup[] = [
    {
      title: "Needs attention",
      cards: [
        {
          label: "Pending companies",
          value: counts.pendingMembers,
          href: "/admin/companies?status=pending",
          tone: "amber",
          icon: Building2,
        },
        {
          label: "Pending reports",
          value: counts.pendingReports,
          href: "/admin/reports?status=pending",
          tone: "amber",
          icon: FileText,
        },
        {
          label: "Pending resolutions",
          value: counts.pendingResolutions,
          href: "/admin/resolutions",
          tone: "amber",
          icon: Gavel,
        },
        {
          label: "Password resets",
          value: counts.pendingPasswordResets,
          href: "/admin/companies",
          tone: "slate",
          icon: KeyRound,
        },
      ],
    },
    {
      title: "Membership",
      cards: [
        {
          label: "Approved members",
          value: counts.approvedMembers,
          href: "/admin/companies?status=approved",
          tone: "emerald",
          icon: Users,
        },
        {
          label: "Deactivated",
          value: counts.deactivatedMembers,
          href: "/admin/companies?status=deactivated",
          tone: "slate",
          icon: Building2,
        },
        {
          label: "Rejected applicants",
          value: counts.rejectedMembers,
          href: "/admin/companies?status=rejected",
          tone: "rose",
          icon: FileX2,
        },
        {
          label: "Expiring in 30 days",
          value: counts.expiringMemberships,
          href: "/admin/companies?status=approved",
          tone: "amber",
          icon: Clock3,
        },
      ],
    },
    {
      title: "Seller reports",
      cards: [
        {
          label: "All reports",
          value: counts.totalReports,
          href: "/admin/reports?status=all",
          tone: "blue",
          icon: FileText,
        },
        {
          label: "Approved reports",
          value: counts.approvedReports,
          href: "/admin/reports?status=approved",
          tone: "emerald",
          icon: FileCheck2,
        },
        {
          label: "Rejected reports",
          value: counts.rejectedReports,
          href: "/admin/reports?status=rejected",
          tone: "slate",
          icon: FileX2,
        },
        {
          label: "Reports with open dispute",
          value: counts.openDisputes,
          href: "/admin/reports?status=approved&disputeStatus=reported",
          tone: "rose",
          icon: AlertTriangle,
        },
        {
          label: "Reports with resolved dispute",
          value: counts.resolvedDisputes,
          href: "/admin/reports?status=approved&disputeStatus=resolved",
          tone: "emerald",
          icon: CheckCircle2,
        },
      ],
    },
    {
      title: "Dispute resolutions",
      cards: [
        {
          label: "Pending resolutions",
          value: counts.pendingResolutions,
          href: "/admin/resolutions",
          tone: "amber",
          icon: Gavel,
        },
        {
          label: "Approved resolutions",
          value: counts.approvedResolutions,
          href: "/admin/resolutions",
          tone: "emerald",
          icon: CheckCircle2,
        },
        {
          label: "Rejected resolutions",
          value: counts.rejectedResolutions,
          href: "/admin/resolutions",
          tone: "rose",
          icon: FileX2,
        },
      ],
    },
    {
      title: "Dispute amounts",
      cards: [
        {
          label: "Total disputed",
          value: money(counts.totalDisputedPaise),
          href: "/admin/reports?status=approved&disputeStatus=reported",
          tone: "rose",
          icon: IndianRupee,
        },
        {
          label: "Amount resolved",
          value: money(counts.resolvedDisputedPaise),
          href: "/admin/reports?status=approved&disputeStatus=resolved",
          tone: "emerald",
          icon: IndianRupee,
        },
        {
          label: "Open disputed",
          value: money(counts.openDisputedPaise),
          href: "/admin/reports?status=approved&disputeStatus=reported",
          tone: "amber",
          icon: IndianRupee,
        },
      ],
    },
  ];

  return (
    <ReportShell
      admin
      title="Platform overview"
      description="Review pending work and monitor Sellers Trust Network activity."
      actions={[
        { href: "/admin/reports?status=pending", label: "Review reports", variant: "primary" },
        { href: "/admin/companies?status=pending", label: "Member companies", variant: "secondary" },
      ]}
    >
      <div className="space-y-5">
        <div
          className={`rounded-[12px] border px-4 py-3 ${
            attentionNeeded > 0 ? toneClass.amber.soft : toneClass.emerald.soft
          }`}
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-[13px] font-semibold text-slate-900">
              {attentionNeeded > 0
                ? `${num(attentionNeeded)} item${attentionNeeded === 1 ? "" : "s"} need attention`
                : "Queue is clear"}
              <span className="ml-2 font-normal text-slate-600">
                · Cos {num(counts.pendingMembers)} · Reports {num(counts.pendingReports)} · Res{" "}
                {num(counts.pendingResolutions)}
              </span>
            </p>
            {counts.unusualLast24 > 0 ? (
              <Link
                href="/admin/audit?q=security"
                className="inline-flex items-center gap-1 rounded-[12px] border border-rose-200 bg-rose-50 px-2.5 py-1 text-[11px] font-semibold text-rose-800"
              >
                {num(counts.unusualLast24)} security alert{counts.unusualLast24 === 1 ? "" : "s"}
                <ArrowRight className="size-3.5" />
              </Link>
            ) : null}
          </div>
        </div>

        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <span className="h-4 w-1 rounded-full bg-[#15388c]" />
            <h2 className="text-[13px] font-semibold text-slate-900">Totals</h2>
          </div>

          {groups.map(group => (
            <div key={group.title} className="space-y-2">
              <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-500">
                {group.title}
              </p>
              <TotalsGrid cards={group.cards} />
            </div>
          ))}
        </section>

        <section className="space-y-2.5">
          <div className="flex items-center gap-2">
            <span className="h-4 w-1 rounded-full bg-[#15388c]" />
            <h2 className="text-[13px] font-semibold text-slate-900">Graphs</h2>
          </div>
          <AdminDashboardCharts
            pendingMembers={counts.pendingMembers}
            approvedMembers={counts.approvedMembers}
            rejectedMembers={counts.rejectedMembers}
            deactivatedMembers={counts.deactivatedMembers}
            pendingReports={counts.pendingReports}
            approvedReports={counts.approvedReports}
            rejectedReports={counts.rejectedReports}
            openDisputes={counts.openDisputes}
            resolvedDisputes={counts.resolvedDisputes}
            pendingResolutions={counts.pendingResolutions}
            approvedResolutions={counts.approvedResolutions}
            rejectedResolutions={counts.rejectedResolutions}
            totalDisputedPaise={counts.totalDisputedPaise}
            openDisputedPaise={counts.openDisputedPaise}
            resolvedDisputedPaise={counts.resolvedDisputedPaise}
          />
        </section>
      </div>
    </ReportShell>
  );
}
