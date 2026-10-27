"use client";
import {CaseNumberInfo} from "./case-number-info";

import { useRef, useState, type FormEvent, type ReactNode } from "react";
import {
  AlertTriangle,
  Building2,
  Search,
  ShieldCheck,
  Star,
} from "lucide-react";
import { readJsonResponse } from "@/lib/client-response";
import { DetailSection } from "@/components/list-frame";
import type { ReportView } from "@/components/report-cards";

type Seller = {
  firm_name: string;
  taluka: string;
  district: string;
  state: string;
  pincode?: string;
  gstin: string;
  report_count: number;
  average_rating: number;
  reporting_companies: number;
  disputes: number;
  open_disputes: number;
  resolved_disputes: number;
  reported_amount_paise: number;
  resolved_amount_paise: number;
  legal_count: number;
  latest_reviewed_at: number;
  under_review: boolean;
};

function money(paise: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format((paise || 0) / 100);
}

function monthLabel(value: string) {
  const match = String(value || "").match(/^(\d{4})-(\d{2})$/);
  if (!match) return "—";
  const date = new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, 1));
  if (Number.isNaN(date.valueOf())) return "—";
  return new Intl.DateTimeFormat("en-IN", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(date);
}

function safeDate(value: string | number | null | undefined) {
  if (value == null || value === "") return "—";
  const date =
    typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value)
      ? new Date(`${value}T00:00:00`)
      : new Date(value);
  if (Number.isNaN(date.valueOf())) return "—";
  return date.toLocaleDateString("en-IN", { timeZone: "Asia/Kolkata" });
}

export function SellerSearch({
  categoryLabel,
}: {
  categoryLabel?: string;
}) {
  const searchVersion=useRef(0);
  const [query, setQuery] = useState("");
  const [reports, setReports] = useState<ReportView[] | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [more, setMore] = useState(false);
  const [seller, setSeller] = useState<Seller | null>(null);

  async function onSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if(busy)return;
    if(query.length!==15){setError("Enter the complete 15-character GSTIN.");return;}
    const version=++searchVersion.current;
    setBusy(true);
    setError("");
    setReports(null);
    setSeller(null);
    try {
      const response = await fetch("/api/seller-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await readJsonResponse<{
        error?: string;
        seller: Seller | null;
        reports: ReportView[];
        more: boolean;
      }>(response);
      if (!response.ok) throw new Error(data.error || "Search unavailable.");
      if(version!==searchVersion.current)return;
      setReports(data.reports);
      setSeller(data.seller);
      setMore(data.more);
    } catch (cause) {
      if(version!==searchVersion.current)return;
      setError(cause instanceof Error ? cause.message : "Search unavailable.");
    } finally {
      setBusy(false);
    }
  }

  function onQueryChange(value: string) {
    searchVersion.current++;
    setSeller(null);setReports(null);setError("");
    setQuery(value.toUpperCase().replace(/\s/g, "").slice(0, 15));
  }

  const results = (
    <div aria-live="polite">
      {error && (
        <div
          role="alert"
          className="mb-4 flex items-start gap-2.5 rounded-[12px] border border-rose-200 bg-rose-50 px-3.5 py-3 text-[13px] text-rose-800"
        >
          <AlertTriangle className="mt-0.5 size-4 shrink-0" />
          <div>
            <p className="font-semibold">
              {error.toLowerCase().includes("gstin") ||
              error.toLowerCase().includes("complete")
                ? "Check the GSTIN"
                : "Search unavailable"}
            </p>
            <p className="mt-0.5 text-[12px]">{error}</p>
          </div>
        </div>
      )}

      {reports && !seller && (
        <div className="rounded-[12px] border border-slate-200 bg-white px-4 py-10 text-center">
          <span className="mx-auto grid size-11 place-items-center rounded-[12px] bg-slate-100 text-slate-500">
            <Search className="size-5" />
          </span>
          <p className="mt-3 text-[14px] font-semibold text-slate-900">
            No approved record found
          </p>
          <p className="mx-auto mt-1 max-w-md text-[12px] leading-5 text-slate-500">
            No approved seller report matches this GSTIN in your category.
          </p>
          <a
            href="/member/submit-report"
            className="mt-4 inline-flex h-9 items-center rounded-[12px] bg-[#15388c] px-3.5 text-[12px] font-semibold text-white hover:bg-[#102d74]"
          >
            Submit a seller report
          </a>
        </div>
      )}

      {reports && seller && (
        <div className="grid gap-4 lg:grid-cols-[minmax(260px,320px)_minmax(0,1fr)] lg:items-start">
          <aside className="space-y-3 lg:sticky lg:top-0">
            {seller.under_review && (
              <div className="flex gap-2 rounded-[12px] border border-amber-200 bg-amber-50 px-3 py-2.5 text-[12px] text-amber-900">
                <AlertTriangle className="mt-0.5 size-3.5 shrink-0" />
                <p>
                  Seller identity is under review. Verify independently while
                  admin decides.
                </p>
              </div>
            )}

            <DetailSection title="Seller profile">
              <div className="space-y-3">
                <div>
                  <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-[0.06em] text-slate-500">
                    <Building2 className="size-3.5" />
                    Firm
                  </p>
                  <h2 className="mt-1 text-[15px] font-semibold leading-snug text-slate-900">
                    {seller.firm_name}
                  </h2>
                  <p className="mt-1 text-[12px] text-slate-500">
                    {seller.taluka}, {seller.district}, {seller.state}
                    {seller.pincode ? ` · ${seller.pincode}` : ""}
                  </p>
                  <p className="mt-2 font-mono text-[12px] text-slate-600">
                    GSTIN {seller.gstin}
                  </p>
                </div>

                <div className="flex items-center justify-between rounded-[12px] border border-slate-100 bg-slate-50 px-3 py-2.5">
                  <span className="text-[12px] text-slate-500">Average rating</span>
                  <span className="inline-flex items-center gap-1 text-[14px] font-semibold text-slate-900">
                    <Star className="size-3.5 fill-[#d6b447] text-[#d6b447]" />
                    {seller.average_rating}/10
                  </span>
                </div>

                <dl className="grid grid-cols-2 gap-2">
                  <Metric label="Reports" value={seller.report_count} />
                  <Metric label="Seller" value={seller.reporting_companies} />
                  <Metric label="Open disputes" value={seller.open_disputes} />
                  <Metric label="Resolved" value={seller.resolved_disputes} />
                  <Metric label="Legal" value={seller.legal_count} />
                  <Metric
                    label="Latest"
                    value={
                      seller.latest_reviewed_at
                        ? safeDate(seller.latest_reviewed_at)
                        : "—"
                    }
                  />
                  <Metric
                    label="Amount reported"
                    value={money(seller.reported_amount_paise)}
                  />
                  <Metric
                    label="Amount resolved"
                    value={money(seller.resolved_amount_paise)}
                  />
                </dl>
              </div>
            </DetailSection>
          </aside>

          <section className="min-w-0 space-y-3">
            <div className="flex items-center justify-between gap-2">
              <h3 className="text-[13px] font-semibold text-slate-900">
                Approved experiences
              </h3>
              <span className="text-[11px] text-slate-500">
                {reports.length}
                {more ? "+" : ""} shown
              </span>
            </div>
            {more && (
              <p className="text-[12px] text-slate-500">
                Showing the latest 100 approved experiences.
              </p>
            )}
            {reports.length === 0 ? (
              <div className="rounded-[12px] border border-slate-200 bg-white px-4 py-8 text-center text-[13px] text-slate-500">
                No experience summaries to show.
              </div>
            ) : (
              reports.map(report => (
                <ExperienceCard key={report.id} report={report} />
              ))
            )}
          </section>
        </div>
      )}
    </div>
  );

  return (
    <section className="stn-seller-search space-y-4" aria-label="Seller trust search">
      <form onSubmit={onSearch} className="stn-search-panel relative overflow-hidden rounded-[16px] border p-5 shadow-sm sm:p-7">
        <div aria-hidden className="stn-search-decoration pointer-events-none absolute -right-16 -top-20 size-56 rounded-full border-[28px]" />
        <div className="relative mb-5 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="stn-search-eyebrow flex items-center gap-2 text-[13px] font-semibold">
              <ShieldCheck className="size-4" />Verified network search
            </p>
            <h2 className="stn-search-heading mt-2 text-2xl font-semibold tracking-tight">Search seller by GSTIN</h2>
            <p className="stn-search-description mt-2 max-w-xl text-[13px] leading-5">
              Enter the complete 15-character GSTIN. Partial searches and seller lists are not available.
            </p>
          </div>
          {categoryLabel && <span className="stn-search-category rounded-full border px-4 py-2 text-[12px] font-semibold">Category: {categoryLabel}</span>}
        </div>
        <div className="relative grid items-end gap-3 sm:grid-cols-[minmax(0,1fr)_auto]">
          <label className="stn-search-label min-w-0 text-[13px] font-semibold">
            Seller GSTIN
            <div className="relative mt-2">
              <Search className="stn-search-input-icon pointer-events-none absolute left-4 top-1/2 size-5 -translate-y-1/2" />
              <input
                value={query}
                onChange={event => onQueryChange(event.target.value)}
                required minLength={15} maxLength={15}
                pattern="[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]"
                placeholder="27ABCDE1234F1Z5"
                aria-describedby="gstin-search-help"
                autoComplete="off" spellCheck={false}
                className="stn-search-input h-14 w-full rounded-[12px] border pl-12 pr-4 font-mono text-[16px] uppercase tracking-wider outline-none transition placeholder:normal-case placeholder:tracking-normal"
              />
            </div>
          </label>
          <button type="submit" disabled={busy || query.length !== 15} className="stn-search-submit inline-flex h-14 items-center justify-center gap-2 rounded-[12px] px-7 text-[15px] font-semibold transition">
            <Search className="size-5" />{busy ? "Searching…" : "Search seller"}
          </button>
        </div>
        <p id="gstin-search-help" className="stn-search-description relative mt-3 flex items-start gap-2 text-[12px] leading-5">
          <ShieldCheck className="mt-0.5 size-3.5 shrink-0" />
          Only approved reports in your assigned category appear. GSTIN remains masked in results.
        </p>
      </form>
      {(reports || error) && <div className="stn-search-results rounded-xl border p-4 sm:p-5">{results}</div>}
    </section>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: ReactNode;
}) {
  return (
    <div className="rounded-[12px] border border-slate-100 bg-slate-50 px-2.5 py-2">
      <dt className="text-[10px] font-semibold uppercase tracking-[0.05em] text-slate-500">
        {label}
      </dt>
      <dd className="mt-0.5 truncate text-[12px] font-semibold text-slate-900">
        {value}
      </dd>
    </div>
  );
}

function periodLabel(report: ReportView) {
  if (!report.dispute_start_month) return "Period not provided";
  const start = monthLabel(report.dispute_start_month);
  if (Number(report.dispute_resolved)) {
    return report.resolved_on
      ? `${start} – Resolved ${safeDate(report.resolved_on)}`
      : `${start} – Resolved`;
  }
  if (report.dispute_ongoing) return `${start} – Ongoing`;
  if (report.dispute_end_month) {
    return `${start} – ${monthLabel(report.dispute_end_month)}`;
  }
  return `${start} – —`;
}

function ExperienceCard({ report }: { report: ReportView }) {
  return (
    <article className="rounded-[12px] border border-slate-200 bg-white p-3.5 sm:p-4">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
          {!!report.dispute && report.reporter_company ? (
            <>
              <p className="text-[11px] font-semibold uppercase tracking-[0.05em] text-rose-700">
                Dispute reported by
              </p>
              <h4 className="mt-0.5 truncate text-[13px] font-semibold text-slate-900">
                {report.reporter_company}
              </h4>
            </>
          ) : (
            <h4 className="text-[13px] font-semibold text-slate-900">
              Company experience
            </h4>
          )}
          <p className="mt-0.5 text-[11px] text-slate-500">
            Reported {safeDate(report.created_at)}
          </p>
        </div>
        <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-semibold capitalize text-emerald-800">
          {report.rating}/10 · {report.status}
        </span>
      </div>

      <p className="mt-2.5 whitespace-pre-wrap break-words text-[13px] leading-5 text-slate-700">
        {report.summary}
      </p>

      {!!Number(report.dispute) && (
        <div
          className={`mt-3 rounded-[12px] px-3 py-2.5 text-[12px] ${
            report.dispute_resolved
              ? "bg-emerald-50 text-emerald-900"
              : "bg-rose-50 text-rose-900"
          }`}
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <strong>Commercial dispute</strong>
            <span className="rounded-full bg-white/70 px-2 py-0.5 text-[11px] font-semibold">
              {report.dispute_resolved ? "Resolved" : "Open"}
            </span>
          </div>
          <p className="mt-1">
            {report.dispute_type?.replaceAll("_", " ")}
            {report.dispute_other ? ` — ${report.dispute_other}` : ""} ·{" "}
            {money(Number(report.amount_paise) || 0)}
          </p>
          <p className="mt-1 text-[11px] opacity-90">{periodLabel(report)}</p>
        </div>
      )}

      {!!Number(report.legal) && (
        <div className="mt-2 rounded-[12px] bg-violet-50 px-3 py-2 text-[12px] text-violet-900"><p className="mb-2 font-semibold">Legal proceedings</p><CaseNumberInfo report={report}/></div>
      )}
    </article>
  );
}
