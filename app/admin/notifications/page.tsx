import { redirect } from "next/navigation";
import { requireChatGPTUser } from "@/app/chatgpt-auth";
import { isConfiguredAdmin } from "@/lib/member-data";
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
  const user = await requireChatGPTUser("/admin/notifications");
  if (!isConfiguredAdmin(user.email)) redirect("/join");

  const params = await searchParams;
  const q = String(params.q || "").trim();
  const status = String(params.status || "");
  const items = await listNotifications("admin", null);

  const filters = (
    <SearchToolbar
      action="/admin/notifications"
      searchDefault={q}
      searchPlaceholder="Search notifications..."
      clearHref="/admin/notifications"
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
      admin
      title="Notifications"
      description="New work and security warnings requiring administrator attention."
      filters={filters}
      actions={[{ href: "/admin/audit", label: "Audit trail", variant: "secondary" }]}
    >
      <NotificationList
        initial={items}
        admin
        query={q}
        unreadOnly={status === "unread" ? true : status === "read" ? false : null}
      />
    </ReportShell>
  );
}
