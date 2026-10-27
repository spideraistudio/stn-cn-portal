import { redirect } from "next/navigation";
import { requireChatGPTUser } from "@/app/chatgpt-auth";
import { isConfiguredAdmin } from "@/lib/member-data";
import { actionLabel, auditEntries } from "@/lib/admin-dashboard";
import { ReportShell } from "@/components/report-shell";
import {
  SearchToolbar,
  FilterField,
  FilterInput,
  FilterSelect,
} from "@/components/filter-bar";
import {
  LIST_PAGE_SIZE,
  ListPagination,
  paginateItems,
  parseListPage,
} from "@/components/list-pagination";
import { ListFrame } from "@/components/list-frame";

export const dynamic = "force-dynamic";

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{
    q?: string;
    action?: string;
    from?: string;
    to?: string;
    page?: string;
  }>;
}) {
  const user = await requireChatGPTUser("/admin/audit");
  if (!isConfiguredAdmin(user.email)) redirect("/join");
  const params = await searchParams;
  const q = String(params.q || "").trim().toLowerCase();
  const action = String(params.action || "");
  const page = parseListPage(params.page);
  const from = /^\d{4}-\d{2}-\d{2}$/.test(String(params.from || ""))
    ? new Date(`${params.from}T00:00:00Z`).valueOf()
    : 0;
  const to = /^\d{4}-\d{2}-\d{2}$/.test(String(params.to || ""))
    ? new Date(`${params.to}T23:59:59.999Z`).valueOf()
    : Number.MAX_SAFE_INTEGER;
  const all = await auditEntries();
  const actions = [...new Set(all.map(entry => entry.action))].sort();
  const filtered = all.filter(
    entry =>
      (!q ||
        `${entry.source} ${entry.actor} ${entry.subject} ${entry.details || ""} ${actionLabel(entry.action)}`
          .toLowerCase()
          .includes(q)) &&
      (!action || entry.action === action) &&
      entry.created_at >= from &&
      entry.created_at <= to,
  );
  const paged = paginateItems(filtered, page, LIST_PAGE_SIZE);

  const filterParams = {
    q: typeof params.q === "string" ? params.q : undefined,
    action: action || undefined,
    from: params.from || undefined,
    to: params.to || undefined,
  };

  const activeFilterCount = [action, params.from, params.to].filter(Boolean).length;

  const filters = (
    <SearchToolbar
      action="/admin/audit"
      searchDefault={typeof params.q === "string" ? params.q : ""}
      searchPlaceholder="Search..."
      clearHref="/admin/audit"
      activeFilterCount={activeFilterCount}
    >
      <FilterField label="Action">
        <FilterSelect name="action" defaultValue={action}>
          <option value="">All actions</option>
          {actions.map(value => (
            <option key={value} value={value}>
              {actionLabel(value)}
            </option>
          ))}
        </FilterSelect>
      </FilterField>
      <FilterField label="From date">
        <FilterInput type="date" name="from" defaultValue={params.from} />
      </FilterField>
      <FilterField label="To date">
        <FilterInput type="date" name="to" defaultValue={params.to} />
      </FilterField>
    </SearchToolbar>
  );

  return (
    <ReportShell
      admin
      title="Audit trail"
      description="Read-only history of membership and report activity."
      filters={filters}
    >
      <ListFrame
        header={
          <div className="px-4 py-3 text-[13px] text-slate-500">
            {paged.total} matching event(s) from the latest {all.length} records.
          </div>
        }
        footer={
          <ListPagination
            basePath="/admin/audit"
            params={filterParams}
            page={paged.page}
            total={paged.total}
            pageSize={LIST_PAGE_SIZE}
          />
        }
      >
        {paged.items.length ? (
          paged.items.map((entry, index) => (
            <article
              key={`${entry.source}-${entry.created_at}-${index}`}
              className="grid gap-2 border-b border-slate-100 px-4 py-4 last:border-0 md:grid-cols-[1.4fr_1fr_auto]"
            >
              <div>
                <p className="font-semibold text-slate-900">{actionLabel(entry.action)}</p>
                <p className="mt-1 text-sm text-slate-600">
                  {entry.subject}
                  {entry.details ? ` · ${entry.details}` : ""}
                </p>
              </div>
              <div className="text-sm">
                <p>{entry.actor}</p>
                <p className="mt-1 capitalize text-slate-500">{entry.source}</p>
              </div>
              <time className="text-sm text-slate-500">
                {new Date(entry.created_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })}
              </time>
            </article>
          ))
        ) : (
          <p className="p-7 text-slate-600">No audit events match these filters.</p>
        )}
      </ListFrame>
    </ReportShell>
  );
}
