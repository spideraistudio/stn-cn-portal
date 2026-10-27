import Link from "next/link";
import { LandingNav } from "@/components/landing-nav";
import { BreadcrumbsJsonLd } from "@/components/breadcrumbs-jsonld";
import { WebPageJsonLd } from "@/components/webpage-jsonld";
import {
  Check, ShieldCheck, Sparkles, Zap, Crown,
  ArrowRight, Info
} from "lucide-react";

export const dynamic = "force-dynamic";

const plans = [
  {
    name: "Free",
    icon: ShieldCheck,
    price: "₹0",
    period: "forever",
    description: "Core membership for verified companies.",
    features: [
      "Admin-verified company membership",
      "Exact GSTIN seller search",
      "Submit seller reports",
      "Dispute resolution requests",
      "Member notifications",
      "Category-isolated access",
    ],
    cta: "Register company",
    ctaHref: "/join",
    highlight: false,
    badge: "Current plan",
  },
  {
    name: "Trial",
    icon: Sparkles,
    price: "₹0",
    period: "14 days",
    description: "Full access to evaluate the platform.",
    features: [
      "Everything in Free",
      "Priority search queue",
      "Extended search limits",
      "Early access to new features",
      "Dedicated onboarding support",
    ],
    cta: "Contact administrator",
    ctaHref: "/contact",
    highlight: false,
    badge: "Limited trial",
  },
  {
    name: "Monthly",
    icon: Zap,
    price: "₹499",
    period: "per month",
    description: "For active businesses with ongoing due-diligence needs.",
    features: [
      "Everything in Free",
      "Higher search limits",
      "Priority dispute review",
      "CSV export access",
      "Email support",
      "Monthly billing",
    ],
    cta: "Contact administrator",
    ctaHref: "/contact",
    highlight: true,
    badge: "Most popular",
  },
  {
    name: "Annual",
    icon: Crown,
    price: "₹4,999",
    period: "per year",
    description: "Best value for established businesses.",
    features: [
      "Everything in Monthly",
      "Maximum search limits",
      "Priority dispute review",
      "Dedicated account manager",
      "Annual billing (save 16%)",
      "Early access to new features",
    ],
    cta: "Contact administrator",
    ctaHref: "/contact",
    highlight: false,
    badge: "Best value",
  },
];

export default function PlansPage() {
  return (
    <main className="min-h-screen bg-[#f5f7fb] text-slate-900">
      <BreadcrumbsJsonLd items={[{ name: "Plans", path: "/plans" }]} />
      <WebPageJsonLd name="Membership Plans — Sellers Trust Network" path="/plans" description="Membership plans for Sellers Trust Network — Free, Trial, Monthly, and Annual options for verified Indian businesses." />

      {/* Hero */}
      <section className="gradient-mesh relative overflow-hidden">
        <div className="pointer-events-none absolute -right-20 top-10 size-72 rounded-full bg-blue-400/20 blur-3xl animate-float-slow" />
        <LandingNav />
        <div className="relative z-10 mx-auto max-w-5xl px-5 pb-12 pt-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-amber-200">
            <Crown className="size-4" />
            Membership
          </div>
          <h1 className="mt-3 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Choose your membership plan
          </h1>
          <p className="mt-3 max-w-2xl text-lg text-blue-100">
            Membership is currently free for verified companies. Paid plans unlock
            higher limits, priority review, and dedicated support — contact the
            administrator to upgrade.
          </p>
        </div>
        <svg className="relative z-10 block w-full" viewBox="0 0 1440 60" preserveAspectRatio="none" style={{ height: "40px" }}>
          <path d="M0,30 C360,60 1080,0 1440,30 L1440,60 L0,60 Z" fill="#f5f7fb" />
        </svg>
      </section>

      {/* Plans grid */}
      <section className="mx-auto max-w-6xl px-5 py-12">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {plans.map((plan, i) => {
            const Icon = plan.icon;
            return (
              <div
                key={plan.name}
                className={`animate-fade-in-up relative flex flex-col rounded-3xl border bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg ${plan.highlight ? "border-[#15388c] ring-2 ring-[#15388c]/10" : "border-slate-200"}`}
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                {/* Badge */}
                {plan.badge && (
                  <span className={`absolute -top-3 left-6 rounded-full px-3 py-1 text-xs font-semibold ${plan.highlight ? "bg-[#15388c] text-white" : "bg-amber-100 text-amber-800"}`}>
                    {plan.badge}
                  </span>
                )}

                {/* Icon + name */}
                <div className="flex items-center gap-3">
                  <span className={`grid size-11 place-items-center rounded-xl ${plan.highlight ? "bg-[#15388c] text-white" : "bg-[#15388c]/5 text-[#15388c]"}`}>
                    <Icon className="size-6" />
                  </span>
                  <h3 className="text-xl font-bold text-slate-900">{plan.name}</h3>
                </div>

                {/* Price */}
                <div className="mt-4">
                  <span className="text-3xl font-bold text-slate-900">{plan.price}</span>
                  <span className="ml-1 text-sm text-slate-500">/ {plan.period}</span>
                </div>
                <p className="mt-1 text-sm text-slate-500">{plan.description}</p>

                {/* Features */}
                <ul className="mt-5 flex-1 space-y-2.5">
                  {plan.features.map(feature => (
                    <li key={feature} className="flex items-start gap-2 text-sm text-slate-700">
                      <Check className="mt-0.5 size-4 shrink-0 text-emerald-600" />
                      {feature}
                    </li>
                  ))}
                </ul>

                {/* CTA */}
                <Link
                  href={plan.ctaHref}
                  className={`mt-6 flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold transition ${plan.highlight ? "bg-[#15388c] text-white shadow-lg shadow-[#15388c]/20 hover:bg-[#1d46a8]" : "border border-slate-200 text-slate-700 hover:bg-slate-50"}`}
                >
                  {plan.cta}
                  <ArrowRight className="size-4" />
                </Link>
              </div>
            );
          })}
        </div>

        {/* Info note */}
        <div className="mt-10 flex items-start gap-3 rounded-2xl border border-blue-200 bg-blue-50 p-5 text-sm text-blue-900">
          <Info className="mt-0.5 size-5 shrink-0 text-blue-600" />
          <div>
            <p className="font-semibold">All plans include:</p>
            <p className="mt-1 text-blue-800">
              Admin-verified membership · Category isolation · GSTIN-masked search ·
              scrypt password hashing · httpOnly secure cookies · Per-request audit
              logging · 30-day data retention governance.
            </p>
            <p className="mt-2 text-blue-700">
              Plan assignment and upgrades are handled by the administrator. Contact{" "}
              <a href="mailto:meetpatel.hmt@gmail.com" className="font-semibold underline">meetpatel.hmt@gmail.com</a>{" "}
              to change your plan.
            </p>
          </div>
        </div>

        {/* FAQ teaser */}
        <div className="mt-8 text-center">
          <p className="text-sm text-slate-500">Have questions about membership?</p>
          <Link href="/faq" className="mt-2 inline-flex items-center gap-1.5 text-sm font-semibold text-[#15388c] transition hover:gap-2.5">
            Read the FAQ <ArrowRight className="size-4" />
          </Link>
        </div>
      </section>
    </main>
  );
}
