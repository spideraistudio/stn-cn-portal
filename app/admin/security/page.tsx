import { requireChatGPTUser } from "@/app/chatgpt-auth";
import { currentAdminCredential } from "@/lib/admin-credentials";
import { ReportShell } from "@/components/report-shell";
import { AdminPasswordForm } from "@/components/admin-password-form";
export const dynamic="force-dynamic";
export default async function Page(){
 await requireChatGPTUser("/admin/security");
 const credential=await currentAdminCredential();
 return <ReportShell admin title="Account & security" description="Manage your administrator password."><section className="max-w-2xl rounded-[12px] border bg-white p-6"><p className="text-sm text-slate-500">Administrator ID</p><p className="mt-1 font-mono font-semibold">{credential?.login_id}</p>{credential?.version===0&&<p className="mt-5 rounded-[12px] border border-amber-200 bg-amber-50 p-4 text-amber-900">Your initial password was shared during setup. Replace it with a private password now.</p>}<AdminPasswordForm/></section></ReportShell>;
}
