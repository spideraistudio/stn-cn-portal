import { requireApprovedMember } from "@/lib/member-session";
import { listNotifications } from "@/lib/notifications";
import { NotificationList } from "@/components/notification-list";
import { ReportShell } from "@/components/report-shell";
import {
  SearchToolbar,
  FilterField,
  FilterSelect,
} from "@/components/filter-bar";

export const dynamic = "force-dynamic";

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; status?: string }>;
}) {
  const member = await requireApprovedMember();
  const params = await searchParams;
  const q = String(params.q || "").trim();
  const status = String(params.status || "");
  const items = await listNotifications("member", member.id);

  const filters = (
    <SearchToolbar
      action="/member/notifications"
      searchDefault={q}
      searchPlaceholder="Search notifications..."
      clearHref="/member/notifications"
      activeFilterCount={[status].filter(Boolean).length}
    >
      <FilterField label="Status">
        <FilterSelect name="status" defaultValue={status}>
          <option value="">All</option>
          <option value="unread">Unread only</option>
          <option value="read">Read only</option>
        </FilterSelect>
      </FilterField>
    </SearchToolbar>
  );

  return (
    <ReportShell
      title="Notifications"
      description="Updates about your membership, reports, corrections, resolutions and account security."
      filters={filters}
    >
      <NotificationList
        initial={items}
        query={q}
        unreadOnly={status === "unread" ? true : status === "read" ? false : null}
      />
    </ReportShell>
  );
}
