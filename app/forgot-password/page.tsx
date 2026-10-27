import { ForgotPasswordForm } from "@/components/forgot-password-form";
import { KeyRound, ArrowLeft } from "lucide-react";

export default function Page() {
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
            <div className="flex items-center gap-3">
              <span className="grid size-11 place-items-center rounded-xl bg-white/10 ring-1 ring-white/20 backdrop-blur-md">
                <KeyRound className="size-5 text-amber-300" />
              </span>
              <div>
                <p className="text-sm font-semibold text-amber-200">Sellers Trust Network</p>
                <p className="text-xs text-blue-100">Password recovery</p>
              </div>
            </div>
          </div>

          {/* Form body */}
          <div className="p-8">
            <h1 className="text-3xl font-bold tracking-tight text-[#15388c]">Forgot password</h1>
            <p className="mt-2 text-slate-600">
              Send a secure request to the administrator. If the details match an
              account, a temporary password will be prepared and shared manually.
            </p>
            <ForgotPasswordForm/>
            <a href="/login" className="mt-6 flex items-center justify-center gap-2 text-sm font-semibold text-[#15388c] transition hover:text-[#1d46a8]">
              <ArrowLeft className="size-4" />
              Return to member login
            </a>
          </div>
        </div>
      </section>
    </main>
  );
}
