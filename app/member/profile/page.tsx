import { Building2, MapPin } from "lucide-react";
import { requireApprovedMember } from "@/lib/member-session";
import { reportDb } from "@/lib/report-store";
import { ReportShell } from "@/components/report-shell";
import { ProfileChangeForm } from "@/components/profile-change-form";
import { DetailSection, ListFrame } from "@/components/list-frame";

export const dynamic = "force-dynamic";

export default async function Page() {
  const member = await requireApprovedMember();
  const pending = Boolean(
    await reportDb()
      .prepare(
        "SELECT id FROM profile_change_requests WHERE member_id=? AND status='pending'",
      )
      .bind(member.id)
      .first(),
  );

  const categoryLabel =
    member.category === "agriculture"
      ? "Agriculture"
      : member.otherCategory || "Other";

  return (
    <ReportShell
      title="Company profile"
      description="Review your company identity and request updates to approved contact details."
    >
      <ListFrame tone="detail">
        <div className="space-y-3 p-4 sm:p-5">
          <DetailSection title="Locked company identity">
            <div className="flex items-start gap-3 border-b border-slate-100 pb-3">
              <span className="grid size-10 shrink-0 place-items-center rounded-[12px] bg-[#15388c]/10 text-[#15388c]">
                <Building2 className="size-5" />
              </span>
              <div className="min-w-0">
                <p className="text-[15px] font-semibold text-slate-900">
                  {member.companyName}
                </p>
                <p className="mt-0.5 font-mono text-[12px] text-slate-500">
                  {member.gstin}
                </p>
              </div>
            </div>
            <dl className="mt-3 grid gap-3 sm:grid-cols-2">
              <Info label="Member ID" value={member.loginId || "Not issued"} mono />
              <Info label="Category" value={categoryLabel} />
              <Info
                label="Location"
                value={`${member.taluka}, ${member.district}, ${member.state} ${member.pincode}`}
                className="sm:col-span-2"
                icon
              />
            </dl>
            <p className="mt-3 text-[12px] text-slate-500">
              Company name, GSTIN, category and location remain locked.
            </p>
          </DetailSection>

          <ProfileChangeForm
            member={{
              responsiblePersonName: member.responsiblePersonName,
              mobileNumber: member.mobileNumber,
              email: member.email,
              address: member.address,
            }}
            pending={pending}
          />
        </div>
      </ListFrame>
    </ReportShell>
  );
}

function Info({
  label,
  value,
  mono,
  icon,
  className = "",
}: {
  label: string;
  value: string;
  mono?: boolean;
  icon?: boolean;
  className?: string;
}) {
  return (
    <div className={className}>
      <dt className="text-[11px] font-semibold uppercase tracking-[0.06em] text-slate-500">
        {label}
      </dt>
      <dd
        className={`mt-1 break-words text-[13px] font-medium text-slate-900 ${
          mono ? "font-mono" : ""
        } ${icon ? "flex items-start gap-1.5" : ""}`}
      >
        {icon ? <MapPin className="mt-0.5 size-3.5 shrink-0 text-slate-400" /> : null}
        {value}
      </dd>
    </div>
  );
}
