import Link from "next/link";
import { BrandLogo } from "@/components/brand-logo";
import {
  ShieldCheck, Scale, Building2, MapPin, Mail,
  ArrowRight, CheckCircle2, Users, FileSearch, BadgeCheck
} from "lucide-react";
import { BreadcrumbsJsonLd } from "@/components/breadcrumbs-jsonld";
import { WebPageJsonLd } from "@/components/webpage-jsonld";

export const dynamic = "force-dynamic";

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-[#f5f7fb] text-slate-900">
      <BreadcrumbsJsonLd items={[{ name: "About", path: "/about" }]} />
      <WebPageJsonLd name="About Sellers Trust Network" path="/about" description="A private trust network built for Indian businesses — verified seller reports, dispute resolution, and category isolation." />
      {/* ── Hero ── */}
      <section className="gradient-mesh relative overflow-hidden">
        <div className="pointer-events-none absolute -right-20 top-10 size-72 rounded-full bg-blue-400/20 blur-3xl animate-float-slow" />
        <nav className="relative z-10 mx-auto flex max-w-5xl items-center justify-between px-5 py-5">
          <Link href="/home" className="flex items-center gap-3">
            <span className="grid size-11 place-items-center rounded-xl bg-white/10 ring-1 ring-white/20 backdrop-blur-md">
              <BrandLogo compact className="size-9" />
            </span>
            <span className="text-lg font-semibold text-white">Sellers Trust Network</span>
          </Link>
          <Link href="/" className="rounded-lg px-4 py-2 text-sm font-semibold text-white/90 transition hover:bg-white/10">
            Home
          </Link>
        </nav>
        <div className="relative z-10 mx-auto max-w-5xl px-5 pb-16 pt-8">
          <span className="animate-fade-in-up inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1.5 text-sm font-medium text-amber-200 ring-1 ring-white/20 backdrop-blur-md">
            <BadgeCheck className="size-4" /> About the platform
          </span>
          <h1 className="animate-fade-in-up delay-100 mt-5 max-w-3xl text-4xl font-bold leading-tight text-white sm:text-5xl">
            A private trust network built for Indian businesses
          </h1>
          <p className="animate-fade-in-up delay-200 mt-5 max-w-2xl text-lg leading-relaxed text-blue-100">
            Sellers Trust Network helps verified companies share structured,
            evidence-backed seller reports so members can make informed trading
            decisions — without exposing competitive intelligence to rivals.
          </p>
        </div>
        <svg className="relative z-10 block w-full" viewBox="0 0 1440 60" preserveAspectRatio="none" style={{ height: "40px" }}>
          <path d="M0,30 C360,60 1080,0 1440,30 L1440,60 L0,60 Z" fill="#f5f7fb" />
        </svg>
      </section>

      {/* ── Mission ── */}
      <section className="mx-auto max-w-5xl px-5 py-16">
        <div className="grid gap-10 lg:grid-cols-[1.2fr_.8fr]">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wider text-[#a57c10]">Our mission</p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
              Trust through transparency, not blacklisting
            </h2>
            <p className="mt-4 leading-7 text-slate-600">
              Every trading relationship carries risk. Sellers Trust Network exists
              so that verified companies can help each other avoid unreliable
              partners — based on factual, documented experiences rather than
              rumor or hearsay.
            </p>
            <p className="mt-3 leading-7 text-slate-600">
              Reports are member-submitted, administratively reviewed, and
              category-isolated. Sellers can request corrections with a GST
              certificate. The goal is not to blacklist, but to build a shared
              ledger of commercial reality.
            </p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="font-semibold text-slate-900">Platform at a glance</h3>
            <dl className="mt-4 space-y-3 text-sm">
              {[
                { k: "Members", v: "Admin-verified companies" },
                { k: "Search", v: "Exact GSTIN lookup" },
                { k: "Categories", v: "Agriculture · Other" },
                { k: "Reports", v: "Structured + evidence" },
                { k: "Disputes", v: "Resolution workflow" },
                { k: "Retention", v: "30-day governance" },
              ].map(({ k, v }) => (
                <div key={k} className="flex items-center justify-between border-b border-slate-100 pb-2 last:border-0">
                  <dt className="text-slate-500">{k}</dt>
                  <dd className="font-medium text-slate-900">{v}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="border-y border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-5 py-16">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-semibold uppercase tracking-wider text-[#a57c10]">How it works</p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">Built around verified facts</h2>
          </div>
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {[
              { icon: Building2, title: "Verified membership", desc: "Companies register with GSTIN and business details. The administrator manually verifies and approves each application before credentials are issued." },
              { icon: FileSearch, title: "Exact-match search", desc: "Members search a seller by GSTIN only — no enumeration, no scraping. Results show approved reports within the member's category." },
              { icon: Scale, title: "Structured reports", desc: "Reports include ratings, dispute details, amounts, legal status, and evidence. Disputes have a resolution workflow with admin oversight." },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title}>
                <div className="grid size-14 place-items-center rounded-2xl bg-gradient-to-br from-[#15388c] to-[#2852a4] text-white shadow-lg shadow-blue-900/20">
                  <Icon className="size-7" />
                </div>
                <h3 className="mt-4 text-xl font-semibold text-slate-900">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-500">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Security ── */}
      <section className="mx-auto max-w-5xl px-5 py-16">
        <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
          <div className="grid lg:grid-cols-2">
            <div className="gradient-mesh p-8 text-white sm:p-10">
              <ShieldCheck className="size-10 text-amber-300" />
              <h2 className="mt-4 text-2xl font-bold sm:text-3xl">Security by design</h2>
              <p className="mt-3 text-blue-100">
                Every layer is hardened — from authentication to data retention.
              </p>
              <ul className="mt-6 space-y-2.5">
                {[
                  "scrypt password hashing",
                  "HMAC-SHA256 GSTIN masking",
                  "httpOnly · secure · sameSite cookies",
                  "Rate-limited authentication",
                  "File-upload magic-byte validation",
                  "Per-request audit logging",
                ].map(item => (
                  <li key={item} className="flex items-center gap-2 text-sm text-blue-50">
                    <CheckCircle2 className="size-4 text-emerald-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="p-8 sm:p-10">
              <h3 className="text-xl font-semibold text-slate-900">Privacy-first approach</h3>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                GSTINs are HMAC-hashed before storage; only the last four digits
                appear in results. Supporting evidence is restricted to the
                submitting member and administrators. Category isolation ensures
                agriculture intelligence never leaks to other categories.
              </p>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                Sellers can challenge any record by providing their GST certificate.
                Challenged records are labelled &ldquo;under review&rdquo; while investigated.
              </p>
              <Link href="/privacy" className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-[#15388c] transition hover:gap-2.5">
                Read the privacy policy <ArrowRight className="size-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── Owner ── */}
      <section className="mx-auto max-w-5xl px-5 pb-16">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
            <div className="grid size-16 shrink-0 place-items-center rounded-2xl bg-[#15388c]/5 text-[#15388c]">
              <Users className="size-8" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold uppercase tracking-wider text-[#a57c10]">Operator &amp; grievance officer</p>
              <h2 className="mt-2 text-2xl font-bold text-slate-900">Meet Patel</h2>
              <p className="mt-2 text-sm leading-7 text-slate-600">
                Sellers Trust Network is operated by Meet Patel, an individual,
                from Himatnagar, Sabarkantha, Gujarat. Meet Patel serves as the
                Grievance Officer and Owner.
              </p>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <div className="flex items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4">
                  <MapPin className="mt-0.5 size-5 shrink-0 text-[#15388c]" />
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Address</p>
                    <p className="mt-1 text-sm text-slate-700">2nd Floor, Dhanlaxmi House, opposite Commerce &amp; Arts College, NH-48, Motipura, Himatnagar, Sabarkantha, Gujarat 383001, India</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4">
                  <Mail className="mt-0.5 size-5 shrink-0 text-[#15388c]" />
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Email</p>
                    <a href="mailto:meetpatel.hmt@gmail.com" className="mt-1 block text-sm font-medium text-[#15388c] transition hover:underline">meetpatel.hmt@gmail.com</a>
                  </div>
                </div>
              </div>
              <div className="mt-6 flex flex-wrap gap-3">
                <Link href="/contact" className="inline-flex items-center gap-2 rounded-xl bg-[#15388c] px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-[#1d46a8]">
                  Contact <ArrowRight className="size-4" />
                </Link>
                <Link href="/join" className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
                  Register company
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
