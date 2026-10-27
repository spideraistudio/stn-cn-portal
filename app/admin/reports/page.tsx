import { redirect } from "next/navigation";
import { requireChatGPTUser } from "@/app/chatgpt-auth";
import { isConfiguredAdmin, parseMemberId } from "@/lib/member-data";
import { adminReportList } from "@/lib/report-list";
import { syncResolvedDisputesFromApprovals } from "@/lib/sync-resolved-disputes";
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
  parseListPage,
} from "@/components/list-pagination";
import { AdminReportsPanel } from "@/components/admin-reports-panel";

export const dynamic = "force-dynamic";

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{
    page?: string;
    q?: string;
    status?: string;
    category?: string;
    from?: string;
    to?: string;
    memberId?: string;
    disputeStatus?: string;
  }>;
}) {
  const user = await requireChatGPTUser("/admin/reports");
  if (!isConfiguredAdmin(user.email)) redirect("/join");
  await syncResolvedDisputesFromApprovals();
  const params = await searchParams;
  const status = String(params.status || "pending");
  const category = String(params.category || "");
  const q = String(params.q || "").trim();
  const page = parseListPage(params.page);
  const from = /^\d{4}-\d{2}-\d{2}$/.test(String(params.from || ""))
    ? new Date(`${params.from}T00:00:00Z`).valueOf()
    : 0;
  const to = /^\d{4}-\d{2}-\d{2}$/.test(String(params.to || ""))
    ? new Date(`${params.to}T23:59:59.999Z`).valueOf()
    : 0;
  const memberId = parseMemberId(params.memberId);
  const disputeStatus = ["reported", "resolved"].includes(String(params.disputeStatus || ""))
    ? String(params.disputeStatus)
    : "";

  const { reports, total } = await adminReportList(
    {
      q,
      status,
      category,
      from,
      to,
      memberId: memberId ?? undefined,
      disputeStatus,
    },
    { page, pageSize: LIST_PAGE_SIZE },
  );

  const filterParams = {
    q: q || undefined,
    status: status || undefined,
    category: category || undefined,
    from: params.from || undefined,
    to: params.to || undefined,
    memberId: memberId ? String(memberId) : undefined,
    disputeStatus: disputeStatus || undefined,
  };

  const activeFilterCount = [
    status && status !== "pending" ? status : "",
    category,
    params.from,
    params.to,
  ].filter(Boolean).length;

  const filters = (
    <SearchToolbar
      action="/admin/reports"
      searchDefault={q}
      searchPlaceholder="Search..."
      clearHref="/admin/reports"
      exportHref="/api/admin/export?type=reports"
      activeFilterCount={activeFilterCount}
      hiddenFields={
        memberId ? (
          <>
            <input type="hidden" name="memberId" value={memberId} />
            <input type="hidden" name="disputeStatus" value={disputeStatus} />
          </>
        ) : null
      }
    >
      <FilterField label="Status">
        <FilterSelect name="status" defaultValue={status}>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="superseded">Superseded</option>
          <option value="all">All statuses</option>
        </FilterSelect>
      </FilterField>
      <FilterField label="Category">
        <FilterSelect name="category" defaultValue={category}>
          <option value="">All categories</option>
          <option value="agriculture">Agriculture</option>
          <option value="other">Other</option>
        </FilterSelect>
      </FilterField>
      <FilterField label="From date">
        <FilterInput type="date" name="from" defaultValue={params.from} />
      </FilterField>
      <FilterField label="To date">
        <FilterInput type="date" name="to" defaultValue={params.to} />
      </FilterField>
      <FilterField label="Dispute">
        <FilterSelect name="disputeStatus" defaultValue={disputeStatus}>
          <option value="">All disputes</option>
          <option value="reported">Reports with open dispute</option>
          <option value="resolved">Reports with resolved dispute</option>
        </FilterSelect>
      </FilterField>
    </SearchToolbar>
  );

  return (
    <ReportShell
      admin
      title="Seller reports"
      description="Review pending submissions or filter the full report history."
      filters={filters}
    >
      <AdminReportsPanel
        reports={reports}
        total={total}
        companyFilter={
          memberId ? (
            <a href="/admin/reports" className="text-[13px] font-semibold text-[#15388c] underline">
              Clear company filter
            </a>
          ) : null
        }
        pagination={
          <ListPagination
            basePath="/admin/reports"
            params={filterParams}
            page={page}
            total={total}
            pageSize={LIST_PAGE_SIZE}
          />
        }
      />
    </ReportShell>
  );
}
