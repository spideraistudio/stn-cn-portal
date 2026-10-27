"use client";
import { changeMemberStatus } from "@/app/actions";

const btnBase =
  "inline-flex h-10 items-center justify-center rounded-[12px] px-4 text-[13px] font-semibold transition";

export function MemberStatusForm({
  memberId,
  status,
  compact = false,
}: {
  memberId: number | string;
  status: string;
  compact?: boolean;
}) {
  const next =
    status === "pending" ? "rejected" : status === "approved" ? "deactivated" : "approved";
  const label =
    next === "rejected" ? "Reject" : next === "deactivated" ? "Deactivate" : "Reactivate";
  const tone =
    next === "rejected"
      ? "border border-rose-200 bg-white text-rose-700 hover:bg-rose-50"
      : next === "approved"
        ? "border border-emerald-200 bg-white text-emerald-700 hover:bg-emerald-50"
        : "border border-slate-200 bg-white text-[#15388c] hover:bg-slate-50";

  return (
    <form
      action={changeMemberStatus}
      onSubmit={event => {
        if (!window.confirm(`${label} this company membership?`)) event.preventDefault();
      }}
      className={compact ? "block" : "flex shrink-0 flex-wrap gap-2"}
    >
      <input type="hidden" name="memberId" value={memberId} />
      <button name="status" value={next} className={`${btnBase} ${compact ? "w-full" : ""} ${tone}`}>
        {label}
      </button>
    </form>
  );
}
