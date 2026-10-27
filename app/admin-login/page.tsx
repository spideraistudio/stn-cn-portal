import { redirect } from "next/navigation";
import { AdminLoginForm } from "@/components/admin-login-form";
import { BrandLogo } from "@/components/brand-logo";
import { getChatGPTUser } from "../chatgpt-auth";
import { ShieldCheck, Lock } from "lucide-react";

export const dynamic="force-dynamic";
export default async function Page({searchParams}:{searchParams:Promise<{returnTo?:string}>}){
 if(await getChatGPTUser())redirect("/admin");
 const returnTo=String((await searchParams).returnTo||"/admin");
 return (
  <main className="grid min-h-screen place-items-center bg-[#f5f7fb] p-5">
    {/* Decorative background */}
    <div className="pointer-events-none fixed inset-0 overflow-hidden">
      <div className="absolute -right-20 -top-20 size-96 rounded-full bg-[#15388c]/5 blur-3xl" />
      <div className="absolute -left-20 bottom-0 size-96 rounded-full bg-[#a57c10]/5 blur-3xl" />
    </div>

    <section className="relative w-full max-w-md animate-fade-in-up">
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-200/50">
        {/* Header band */}
        <div className="gradient-mesh px-8 py-7">
          <a href="/home" className="flex items-center gap-3">
            <span className="grid size-11 place-items-center rounded-xl bg-white/10 ring-1 ring-white/20 backdrop-blur-md">
              <BrandLogo compact className="size-9" />
            </span>
            <div>
              <p className="text-sm font-semibold text-amber-200">Sellers Trust Network</p>
              <p className="text-xs text-blue-100">Administrator access</p>
            </div>
          </a>
        </div>

        {/* Form body */}
        <div className="p-8">
          <h1 className="text-3xl font-bold tracking-tight text-[#15388c]">Administrator sign in</h1>
          <p className="mt-2 text-slate-600">Use the separate administrator ID and password.</p>

          <AdminLoginForm returnTo={returnTo}/>

          <div className="mt-6 flex items-center justify-between gap-3 border-t border-slate-100 pt-5 text-sm font-semibold">
            <a href="/login" className="text-[#15388c] underline transition hover:text-[#1d46a8]">Member sign in</a>
            <span className="flex items-center gap-1.5 text-slate-400">
              <Lock className="size-3.5" /> Secure area
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-center gap-2 text-xs text-slate-400">
        <ShieldCheck className="size-3.5" />
        All administrator actions are audit-logged
      </div>
    </section>
  </main>
 );
}
