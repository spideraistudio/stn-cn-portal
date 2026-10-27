import Link from "next/link";
import { ShieldCheck, ArrowLeft, FileText, ChevronRight, Home } from "lucide-react";
import { BreadcrumbsJsonLd } from "@/components/breadcrumbs-jsonld";

export function LegalPage({ title, path, effective, children }: { title: string; path: string; effective: string; children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-[#f5f7fb] text-slate-900">
      <BreadcrumbsJsonLd items={[{ name: title, path }]} />
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center gap-3 px-5 py-4">
          <Link href="/home" className="grid size-10 place-items-center rounded-xl bg-[#15388c]/5 text-[#15388c] transition hover:bg-[#15388c] hover:text-white" aria-label="Back to home">
            <ArrowLeft className="size-5" />
          </Link>
          <ShieldCheck className="size-6 text-emerald-700" />
          <Link href="/home" className="font-semibold text-slate-900 transition hover:text-[#15388c]">Sellers Trust Network</Link>
        </div>
        {/* Visual breadcrumb trail */}
        <nav aria-label="Breadcrumb" className="border-t border-slate-100 bg-slate-50">
          <ol className="mx-auto flex max-w-5xl items-center gap-1.5 px-5 py-2.5 text-xs text-slate-500">
            <li><Link href="/home" className="flex items-center gap-1 transition hover:text-[#15388c]"><Home className="size-3" />Home</Link></li>
            <li aria-hidden="true"><ChevronRight className="size-3 text-slate-300" /></li>
            <li className="font-medium text-slate-700">{title}</li>
          </ol>
        </nav>
      </header>

      <article className="mx-auto max-w-5xl px-5 py-10">
        <div className="mb-8 flex items-center gap-2 text-sm font-semibold text-[#a57c10]">
          <FileText className="size-4" />
          Legal information
        </div>
        <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">{title}</h1>
        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-slate-500">
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-emerald-500" />
            Effective: {effective}
          </span>
          <span>Last updated: 12 September 2026</span>
        </div>

        <div className="mt-8 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
          <div className="space-y-8 p-6 leading-7 sm:p-9 [&_h2]:mt-2 [&_h2]:text-xl [&_h2]:font-bold [&_h2]:text-slate-900 [&_h3]:mt-1 [&_h3]:font-semibold [&_h3]:text-slate-800 [&_li]:ml-5 [&_li]:list-disc [&_li]:marker:text-slate-300 [&_p]:text-slate-600 [&_a]:font-medium [&_a]:text-[#15388c] [&_a]:underline [&_ul]:space-y-2 [&_section]:border-b [&_section]:border-slate-100 [&_section]:pb-6 [&_section:last-child]:border-0">
            {children}
          </div>
        </div>

        <div className="mt-6 flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-5 text-sm">
          <p className="text-slate-500">
            Questions? Contact the grievance officer:
          </p>
          <a href="mailto:meetpatel.hmt@gmail.com" className="font-semibold text-[#15388c] transition hover:text-[#1d46a8]">
            meetpatel.hmt@gmail.com
          </a>
        </div>
      </article>
    </main>
  );
}
