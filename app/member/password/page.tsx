import { redirect } from "next/navigation";
import { KeyRound, ShieldCheck } from "lucide-react";
import { currentMember } from "@/lib/member-session";
import { ReportShell } from "@/components/report-shell";
import { CredentialForm } from "@/components/credential-form";

export const dynamic = "force-dynamic";

export default async function PasswordPage() {
  const member = await currentMember();
  if (!member) redirect("/login");

  const mustChange = Boolean(member.mustChangePassword);

  return (
    <ReportShell
      title="Change password"
      description={
        mustChange
          ? "Replace your temporary password to open your workspace."
          : "Update your member login password."
      }
      actions={
        mustChange
          ? undefined
          : [{ href: "/member/account", label: "Back to account", variant: "secondary" }]
      }
    >
      <section className="mx-auto w-full max-w-xl rounded-[12px] border border-slate-200 bg-white p-5 sm:p-6">
        <div className="flex items-start gap-3">
          <span className="grid size-10 shrink-0 place-items-center rounded-[12px] bg-[#15388c]/10 text-[#15388c]">
            <KeyRound className="size-5" />
          </span>
          <div className="min-w-0">
            <p className="text-[11px] font-semibold uppercase tracking-[0.06em] text-slate-500">
              Member ID
            </p>
            <p className="mt-1 truncate font-mono text-[15px] font-semibold text-slate-900">
              {member.loginId || "Not issued"}
            </p>
          </div>
        </div>

        {mustChange ? (
          <div className="mt-5 flex gap-3 rounded-[12px] border border-amber-200 bg-amber-50 px-4 py-3 text-[13px] leading-5 text-amber-950">
            <ShieldCheck className="mt-0.5 size-4 shrink-0 text-amber-700" />
            <p>
              Your administrator shared a temporary password. Choose a private
              password now to continue into your company workspace.
            </p>
          </div>
        ) : (
          <p className="mt-5 text-[13px] leading-5 text-slate-600">
            Your Member ID stays the same. Use a password only you know, then
            keep this session active.
          </p>
        )}

        <CredentialForm change />
      </section>
    </ReportShell>
  );
}
