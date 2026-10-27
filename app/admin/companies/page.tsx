import { redirect } from "next/navigation";
import { requireChatGPTUser } from "@/app/chatgpt-auth";
import { isConfiguredAdmin, listMembersForAdmin } from "@/lib/member-data";
import { adminCounts } from "@/lib/admin-dashboard";
import { ReportShell } from "@/components/report-shell";
import {
  SearchToolbar,
  FilterField,
  FilterInput,
  FilterSelect,
} from "@/components/filter-bar";
import {
  AdminCompaniesPanel,
  type CompanyListItem,
} from "@/components/admin-companies-panel";
import {
  LIST_PAGE_SIZE,
  ListPagination,
  paginateItems,
  parseListPage,
} from "@/components/list-pagination";

export const dynamic = "force-dynamic";

export default async function CompaniesPage({
  searchParams,
}: {
  searchParams: Promise<{
    q?: string;
    status?: string;
    category?: string;
    from?: string;
    to?: string;
    page?: string;
  }>;
}) {
  const user = await requireChatGPTUser("/admin/companies");
  if (!isConfiguredAdmin(user.email)) redirect("/join");

  const params = await searchParams;
  const q = String(params.q || "").trim().toLowerCase();
  const status = String(params.status || "");
  const category = String(params.category || "");
  const page = parseListPage(params.page);
  const from = /^\d{4}-\d{2}-\d{2}$/.test(String(params.from || ""))
    ? new Date(`${params.from}T00:00:00Z`).valueOf()
    : 0;
  const to = /^\d{4}-\d{2}-\d{2}$/.test(String(params.to || ""))
    ? new Date(`${params.to}T23:59:59.999Z`).valueOf()
    : Number.MAX_SAFE_INTEGER;

  const [allMembers, counts] = await Promise.all([listMembersForAdmin(), adminCounts()]);
  const filtered: CompanyListItem[] = allMembers
    .filter(member => {
      const created = new Date(member.createdAt).valueOf();
      const createdOk = !Number.isFinite(created) || (created >= from && created <= to);
      return (
        createdOk &&
        (!q ||
          `${member.companyName} ${member.gstin} ${member.loginId || ""} ${member.responsiblePersonName} ${member.mobileNumber} ${member.email}`
            .toLowerCase()
            .includes(q)) &&
        (!status || member.status === status) &&
        (!category || member.category === category)
      );
    })
    .map(member => ({
      id: String(member.id),
      companyName: member.companyName || "",
      loginId: member.loginId ?? null,
      gstin: member.gstin || "",
      status: member.status || "pending",
      category: member.category || "agriculture",
      otherCategory: member.otherCategory ?? null,
      responsiblePersonName: member.responsiblePersonName || "",
      mobileNumber: member.mobileNumber || "",
      email: member.email || "",
      address: member.address || "",
      taluka: member.taluka || "",
      district: member.district || "",
      state: member.state || "",
      pincode: member.pincode || "",
      createdAt: new Date(member.createdAt).toISOString(),
      reportedDisputes: Number(member.reportedDisputes || 0),
      resolvedDisputes: Number(member.resolvedDisputes || 0),
      hasCredentials: Boolean(member.passwordHash),
      searchEnabled: Boolean(member.searchEnabled),
    }));

  const paged = paginateItems(filtered, page, LIST_PAGE_SIZE);
  const filterParams = {
    q: typeof params.q === "string" ? params.q : undefined,
    status: status || undefined,
    category: category || undefined,
    from: params.from || undefined,
    to: params.to || undefined,
  };

  const filters = (
    <SearchToolbar
      action="/admin/companies"
      searchDefault={typeof params.q === "string" ? params.q : ""}
      searchPlaceholder="Search..."
      clearHref="/admin/companies"
      exportHref="/api/admin/export?type=members"
      activeFilterCount={[status, category, params.from, params.to].filter(Boolean).length}
    >
      <FilterField label="Status">
        <FilterSelect name="status" defaultValue={status}>
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="deactivated">Deactivated</option>
        </FilterSelect>
      </FilterField>
      <FilterField label="Category">
        <FilterSelect name="category" defaultValue={category}>
          <option value="">All categories</option>
          <option value="agriculture">Agriculture</option>
          <option value="other">Other</option>
        </FilterSelect>
      </FilterField>
      <FilterField label="Joined from">
        <FilterInput type="date" name="from" defaultValue={params.from} />
      </FilterField>
      <FilterField label="Joined to">
        <FilterInput type="date" name="to" defaultValue={params.to} />
      </FilterField>
    </SearchToolbar>
  );

  return (
    <ReportShell
      admin
      title="Member Company"
      description="Review company identity and manage member access."
      filters={filters}
    >
      <AdminCompaniesPanel
        members={paged.items}
        pendingCount={counts.pendingMembers}
        totalCount={paged.total}
        pagination={
          <ListPagination
            basePath="/admin/companies"
            params={filterParams}
            page={paged.page}
            total={paged.total}
            pageSize={LIST_PAGE_SIZE}
          />
        }
      />
    </ReportShell>
  );
}
