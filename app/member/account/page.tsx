import { KeyRound } from "lucide-react";
import { requireApprovedMember } from "@/lib/member-session";
import { reportDb } from "@/lib/report-store";
import { ReportShell } from "@/components/report-shell";
import { AccountDeletionForm } from "@/components/account-deletion-form";
import { DetailSection, ListFrame } from "@/components/list-frame";

export const dynamic = "force-dynamic";

export default async function Page() {
  const member = await requireApprovedMember();
  const pending = Boolean(
    await reportDb()
      .prepare(
        "SELECT id FROM account_deletion_requests WHERE member_id=? AND status='pending'",
      )
      .bind(member.id)
      .first(),
  );

  return (
    <ReportShell
      title="Account & security"
      description="Manage password security and account closure."
    >
      <ListFrame tone="detail">
        <div className="space-y-3 p-4 sm:p-5">
          <DetailSection title="Password security">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex min-w-0 items-start gap-3">
                <span className="grid size-10 shrink-0 place-items-center rounded-[12px] bg-[#15388c]/10 text-[#15388c]">
                  <KeyRound className="size-5" />
                </span>
                <div>
                  <p className="text-[13px] font-semibold text-slate-900">
                    Member login password
                  </p>
                  <p className="mt-0.5 text-[12px] leading-5 text-slate-500">
                    Change it if it may be known by another person or company.
                  </p>
                  {member.loginId && (
                    <p className="mt-1 font-mono text-[12px] text-slate-600">
                      {member.loginId}
                    </p>
                  )}
                </div>
              </div>
              <a
                href="/member/password"
                className="inline-flex h-10 items-center justify-center rounded-[12px] bg-[#15388c] px-4 text-[13px] font-semibold text-white transition hover:bg-[#102d74]"
              >
                Change password
              </a>
            </div>
          </DetailSection>

          <AccountDeletionForm pending={pending} />
        </div>
      </ListFrame>
    </ReportShell>
  );
}
