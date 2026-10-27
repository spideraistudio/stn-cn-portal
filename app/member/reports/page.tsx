import { requireApprovedMember } from "@/lib/member-session";
import { categoryAccess } from "@/lib/category-access";
import { reportList } from "@/lib/report-list";
import { ReportShell } from "@/components/report-shell";
import { SearchToolbar } from "@/components/filter-bar";
import {
  LIST_PAGE_SIZE,
  ListPagination,
  paginateItems,
  parseListPage,
} from "@/components/list-pagination";
import { MemberReportsPanel } from "@/components/member-reports-panel";

export const dynamic = "force-dynamic";

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ page?: string; q?: string }>;
}) {
  const member = await requireApprovedMember();
  const category = categoryAccess(member);
  const params = await searchParams;
  const q = String(params.q || "").trim();
  const page = parseListPage(params.page);

  if (!category) {
    return (
      <ReportShell title="My reports" description="Your submitted reports">
        <p className="text-[13px] text-slate-600">
          Category assignment is required before you can view reports.
        </p>
      </ReportShell>
    );
  }

  const { reports: allReports } = await reportList(
    { id: member.id, category: category.id },
    Date.now() + 1,
    q,
  );
  const paged = paginateItems(allReports, page, LIST_PAGE_SIZE);

  return (
    <ReportShell
      title="My reports"
      description="Search your submissions or open a seller report."
      filters={
        <SearchToolbar
          searchDefault={q}
          searchPlaceholder="Search firm, GSTIN, summary…"
          clearHref={q ? "/member/reports" : undefined}
        />
      }
      actions={[
        { href: "/member/submit-report", label: "Submit report", variant: "primary" },
      ]}
    >
      <MemberReportsPanel
        reports={paged.items}
        total={paged.total}
        emptySearch={Boolean(q)}
        pagination={
          <ListPagination
            basePath="/member/reports"
            params={{ q: q || undefined }}
            page={paged.page}
            total={paged.total}
            pageSize={LIST_PAGE_SIZE}
          />
        }
      />
    </ReportShell>
  );
}
