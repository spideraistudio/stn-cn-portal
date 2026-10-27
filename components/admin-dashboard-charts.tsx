"use client";

import { Bar, BarChart, CartesianGrid, Cell, LabelList, XAxis, YAxis } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";

const inr = (paise: number) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format((Number(paise) || 0) / 100);

const inrShort = (paise: number) => {
  const n = (Number(paise) || 0) / 100;
  if (n >= 1_00_00_000) return `₹${(n / 1_00_00_000).toFixed(1)}Cr`;
  if (n >= 1_00_000) return `₹${(n / 1_00_000).toFixed(1)}L`;
  if (n >= 1_000) return `₹${(n / 1_000).toFixed(1)}k`;
  return inr(paise);
};

function pct(part: number, total: number) {
  if (!total) return "0%";
  return `${Math.round((part / total) * 100)}%`;
}

const memberConfig = {
  count: { label: "Companies", color: "#15388c" },
} satisfies ChartConfig;

const reportConfig = {
  count: { label: "Reports", color: "#0f766e" },
} satisfies ChartConfig;

const moneyConfig = {
  amount: { label: "Amount", color: "#d97706" },
} satisfies ChartConfig;

function ChartCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <section className="overflow-hidden rounded-[12px] border border-slate-200 bg-white">
      <div className="border-b border-slate-100 px-4 py-2.5">
        <h3 className="text-[13px] font-semibold text-slate-900">{title}</h3>
        <p className="text-[11px] text-slate-500">{subtitle}</p>
      </div>
      <div className="p-3">{children}</div>
    </section>
  );
}

export function AdminDashboardCharts({
  pendingMembers,
  approvedMembers,
  rejectedMembers,
  deactivatedMembers,
  pendingReports,
  approvedReports,
  rejectedReports,
  openDisputes,
  resolvedDisputes,
  pendingResolutions,
  approvedResolutions,
  rejectedResolutions,
  totalDisputedPaise,
  openDisputedPaise,
  resolvedDisputedPaise,
}: {
  pendingMembers: number;
  approvedMembers: number;
  rejectedMembers: number;
  deactivatedMembers: number;
  pendingReports: number;
  approvedReports: number;
  rejectedReports: number;
  openDisputes: number;
  resolvedDisputes: number;
  pendingResolutions: number;
  approvedResolutions: number;
  rejectedResolutions: number;
  totalDisputedPaise: number;
  openDisputedPaise: number;
  resolvedDisputedPaise: number;
}) {
  const memberTotal =
    pendingMembers + approvedMembers + rejectedMembers + deactivatedMembers;
  const reportTotal = pendingReports + approvedReports + rejectedReports;
  const disputeTotal = openDisputes + resolvedDisputes;

  const members = [
    { label: "Pending", count: pendingMembers, fill: "#d97706" },
    { label: "Approved", count: approvedMembers, fill: "#059669" },
    { label: "Rejected", count: rejectedMembers, fill: "#e11d48" },
    { label: "Deactivated", count: deactivatedMembers, fill: "#64748b" },
  ];

  const reports = [
    { label: "Pending", count: pendingReports, fill: "#d97706" },
    { label: "Approved", count: approvedReports, fill: "#059669" },
    { label: "Rejected", count: rejectedReports, fill: "#64748b" },
  ];

  const moneyRows = [
    { label: "Total disputed", amount: totalDisputedPaise / 100, fill: "#e11d48" },
    { label: "Still open", amount: openDisputedPaise / 100, fill: "#d97706" },
    { label: "Resolved", amount: resolvedDisputedPaise / 100, fill: "#059669" },
  ];

  const queueItems = [
    { label: "Pending companies", value: pendingMembers },
    { label: "Pending reports", value: pendingReports },
    { label: "Pending resolutions", value: pendingResolutions },
    { label: "Approved resolutions", value: approvedResolutions },
    { label: "Rejected resolutions", value: rejectedResolutions },
    { label: "Reports with open dispute", value: openDisputes },
    { label: "Reports with resolved dispute", value: resolvedDisputes },
  ];
  const queueMax = Math.max(...queueItems.map(q => q.value), 1);

  return (
    <div className="space-y-3">
      <div className="grid gap-2 sm:grid-cols-3">
        <div className="rounded-[12px] border border-slate-200 bg-white px-3.5 py-3">
          <p className="text-[11px] font-medium text-slate-500">Membership approved</p>
          <p className="mt-1 text-[20px] font-semibold text-emerald-800">
            {pct(approvedMembers, memberTotal)}
          </p>
          <p className="mt-0.5 text-[11px] text-slate-500">
            {approvedMembers} of {memberTotal} companies
          </p>
        </div>
        <div className="rounded-[12px] border border-slate-200 bg-white px-3.5 py-3">
          <p className="text-[11px] font-medium text-slate-500">Reports approved</p>
          <p className="mt-1 text-[20px] font-semibold text-[#15388c]">
            {pct(approvedReports, reportTotal)}
          </p>
          <p className="mt-0.5 text-[11px] text-slate-500">
            {approvedReports} of {reportTotal} reports
          </p>
        </div>
        <div className="rounded-[12px] border border-slate-200 bg-white px-3.5 py-3">
          <p className="text-[11px] font-medium text-slate-500">Dispute amount open</p>
          <p className="mt-1 text-[20px] font-semibold text-amber-800">
            {pct(openDisputedPaise, totalDisputedPaise)}
          </p>
          <p className="mt-0.5 text-[11px] text-slate-500">
            {inrShort(openDisputedPaise)} of {inrShort(totalDisputedPaise)}
          </p>
        </div>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        <ChartCard title="Companies by status" subtitle={`${memberTotal} total · membership mix`}>
          {memberTotal > 0 ? (
            <>
              <ChartContainer config={memberConfig} className="h-[200px] w-full !aspect-auto">
                <BarChart
                  data={members}
                  layout="vertical"
                  margin={{ top: 4, right: 56, left: 4, bottom: 4 }}
                >
                  <CartesianGrid horizontal={false} strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    allowDecimals={false}
                    tickLine={false}
                    axisLine={false}
                    fontSize={10}
                  />
                  <YAxis
                    type="category"
                    dataKey="label"
                    tickLine={false}
                    axisLine={false}
                    width={78}
                    fontSize={11}
                  />
                  <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                  <Bar dataKey="count" radius={[0, 6, 6, 0]} barSize={18}>
                    {members.map(row => (
                      <Cell key={row.label} fill={row.fill} />
                    ))}
                    <LabelList
                      dataKey="count"
                      position="right"
                      className="fill-slate-700 text-[10px] font-semibold"
                      formatter={v => `${Number(v)} · ${pct(Number(v), memberTotal)}`}
                    />
                  </Bar>
                </BarChart>
              </ChartContainer>
              <div className="mt-1 flex flex-wrap gap-3 px-1">
                {members.map(row => (
                  <span
                    key={row.label}
                    className="inline-flex items-center gap-1.5 text-[11px] text-slate-600"
                  >
                    <span className="size-2 rounded-full" style={{ background: row.fill }} />
                    {row.label}
                  </span>
                ))}
              </div>
            </>
          ) : (
            <p className="grid h-[160px] place-items-center text-[12px] text-slate-500">
              No company data yet
            </p>
          )}
        </ChartCard>

        <ChartCard title="Reports by status" subtitle={`${reportTotal} total · pending vs decided`}>
          {reportTotal > 0 ? (
            <>
              <ChartContainer config={reportConfig} className="h-[200px] w-full !aspect-auto">
                <BarChart
                  data={reports}
                  layout="vertical"
                  margin={{ top: 4, right: 56, left: 4, bottom: 4 }}
                >
                  <CartesianGrid horizontal={false} strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    allowDecimals={false}
                    tickLine={false}
                    axisLine={false}
                    fontSize={10}
                  />
                  <YAxis
                    type="category"
                    dataKey="label"
                    tickLine={false}
                    axisLine={false}
                    width={70}
                    fontSize={11}
                  />
                  <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                  <Bar dataKey="count" radius={[0, 6, 6, 0]} barSize={22}>
                    {reports.map(row => (
                      <Cell key={row.label} fill={row.fill} />
                    ))}
                    <LabelList
                      dataKey="count"
                      position="right"
                      className="fill-slate-700 text-[10px] font-semibold"
                      formatter={v => `${Number(v)} · ${pct(Number(v), reportTotal)}`}
                    />
                  </Bar>
                </BarChart>
              </ChartContainer>
              <div className="mt-1 flex flex-wrap gap-3 px-1">
                {reports.map(row => (
                  <span
                    key={row.label}
                    className="inline-flex items-center gap-1.5 text-[11px] text-slate-600"
                  >
                    <span className="size-2 rounded-full" style={{ background: row.fill }} />
                    {row.label}
                  </span>
                ))}
              </div>
            </>
          ) : (
            <p className="grid h-[160px] place-items-center text-[12px] text-slate-500">
              No report data yet
            </p>
          )}
        </ChartCard>
      </div>

      <div className="grid gap-3 lg:grid-cols-[1.25fr_0.75fr]">
        <ChartCard
          title="Dispute amounts"
          subtitle="Pending + approved disputes · rupee comparison"
        >
          {totalDisputedPaise > 0 || openDisputedPaise > 0 || resolvedDisputedPaise > 0 ? (
            <ChartContainer config={moneyConfig} className="h-[190px] w-full !aspect-auto">
              <BarChart
                data={moneyRows}
                layout="vertical"
                margin={{ top: 4, right: 72, left: 4, bottom: 4 }}
              >
                <CartesianGrid horizontal={false} strokeDasharray="3 3" />
                <XAxis
                  type="number"
                  tickLine={false}
                  axisLine={false}
                  fontSize={10}
                  tickFormatter={v => inrShort(Number(v) * 100)}
                />
                <YAxis
                  type="category"
                  dataKey="label"
                  tickLine={false}
                  axisLine={false}
                  width={96}
                  fontSize={11}
                />
                <ChartTooltip
                  content={
                    <ChartTooltipContent
                      hideLabel
                      formatter={value => inr(Number(value) * 100)}
                    />
                  }
                />
                <Bar dataKey="amount" radius={[0, 6, 6, 0]} barSize={22}>
                  {moneyRows.map(row => (
                    <Cell key={row.label} fill={row.fill} />
                  ))}
                  <LabelList
                    dataKey="amount"
                    position="right"
                    className="fill-slate-700 text-[10px] font-semibold"
                    formatter={v => inrShort(Number(v) * 100)}
                  />
                </Bar>
              </BarChart>
            </ChartContainer>
          ) : (
            <p className="grid h-[150px] place-items-center text-[12px] text-slate-500">
              No disputed amounts on pending/approved reports
            </p>
          )}
        </ChartCard>

        <ChartCard
          title="Admin queue"
          subtitle={
            disputeTotal
              ? `${pct(resolvedDisputes, disputeTotal)} of tracked disputes resolved`
              : "Items waiting for action"
          }
        >
          <ul className="space-y-3">
            {queueItems.map(item => {
              const width = Math.max(item.value ? 8 : 0, Math.round((item.value / queueMax) * 100));
              return (
                <li key={item.label}>
                  <div className="mb-1 flex items-center justify-between text-[12px]">
                    <span className="text-slate-600">{item.label}</span>
                    <span className="font-semibold text-slate-900">{item.value}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-[#15388c] transition-all"
                      style={{ width: `${width}%` }}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        </ChartCard>
      </div>
    </div>
  );
}
