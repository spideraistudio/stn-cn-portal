import Link from "next/link";
import { BrandLogo } from "@/components/brand-logo";
import { ContactForm } from "@/components/contact-form";
import { Mail, MapPin, ArrowLeft, MessageSquare, Clock, ShieldCheck } from "lucide-react";
import { BreadcrumbsJsonLd } from "@/components/breadcrumbs-jsonld";

export const dynamic = "force-dynamic";

// ContactPage JSON-LD — helps search engines understand the contact page.
const contactJsonLd = {
  "@context": "https://schema.org",
  "@type": "ContactPage",
  name: "Contact Sellers Trust Network",
  description: "Contact the grievance officer for membership, grievances, seller corrections, or account enquiries.",
  mainEntity: {
    "@type": "Organization",
    name: "Sellers Trust Network",
    email: "meetpatel.hmt@gmail.com",
    address: {
      "@type": "PostalAddress",
      streetAddress: "2nd Floor, Dhanlaxmi House, opposite Commerce & Arts College, NH-48, Motipura",
      addressLocality: "Himatnagar",
      addressRegion: "Gujarat",
      postalCode: "383001",
      addressCountry: "IN",
    },
  },
};

export default function ContactPage() {
  return (
    <main className="min-h-screen bg-[#f5f7fb] text-slate-900">
      <BreadcrumbsJsonLd items={[{ name: "Contact", path: "/contact" }]} />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(contactJsonLd) }}
      />
      {/* Header */}
      <header className="gradient-mesh relative overflow-hidden">
        <div className="pointer-events-none absolute -right-20 top-10 size-72 rounded-full bg-blue-400/20 blur-3xl" />
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
        <div className="relative z-10 mx-auto max-w-5xl px-5 pb-12 pt-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-amber-200">
            <MessageSquare className="size-4" />
            Get in touch
          </div>
          <h1 className="mt-3 text-4xl font-bold tracking-tight text-white sm:text-5xl">Contact us</h1>
          <p className="mt-3 max-w-2xl text-lg text-blue-100">
            Questions, grievances, seller correction requests, or membership
            enquiries — we aim to respond within 7–15 working days.
          </p>
        </div>
        <svg className="relative z-10 block w-full" viewBox="0 0 1440 60" preserveAspectRatio="none" style={{ height: "40px" }}>
          <path d="M0,30 C360,60 1080,0 1440,30 L1440,60 L0,60 Z" fill="#f5f7fb" />
        </svg>
      </header>

      <section className="mx-auto max-w-5xl px-5 py-12">
        <div className="grid gap-8 lg:grid-cols-[1.3fr_.7fr]">
          {/* Form */}
          <div className="animate-fade-in-up overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-lg">
            <div className="border-b border-slate-100 bg-slate-50 px-6 py-4 sm:px-8">
              <h2 className="font-semibold text-slate-900">Send a message</h2>
              <p className="mt-1 text-sm text-slate-500">
                Fill in the form and we&apos;ll route your enquiry to the right place.
              </p>
            </div>
            <div className="p-6 sm:p-8">
              <ContactForm />
            </div>
          </div>

          {/* Sidebar: contact details */}
          <aside className="animate-fade-in-up delay-100 space-y-4">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="flex items-center gap-2 font-semibold text-slate-900">
                <Mail className="size-4 text-[#15388c]" /> Email
              </h3>
              <a href="mailto:meetpatel.hmt@gmail.com" className="mt-2 block text-sm font-medium text-[#15388c] transition hover:underline">
                meetpatel.hmt@gmail.com
              </a>
              <p className="mt-1 text-xs text-slate-400">Grievance officer &amp; owner</p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="flex items-center gap-2 font-semibold text-slate-900">
                <MapPin className="size-4 text-[#15388c]" /> Address
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                2nd Floor, Dhanlaxmi House, opposite Commerce &amp; Arts College,
                NH-48, Motipura, Himatnagar, Sabarkantha, Gujarat 383001, India
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="flex items-center gap-2 font-semibold text-slate-900">
                <Clock className="size-4 text-[#15388c]" /> Response time
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                We aim to respond within <strong className="text-slate-900">7–15 working days</strong>.
                Seller correction requests require a GST certificate.
              </p>
            </div>

            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6">
              <h3 className="flex items-center gap-2 font-semibold text-emerald-900">
                <ShieldCheck className="size-4 text-emerald-700" /> Already a member?
              </h3>
              <p className="mt-2 text-sm leading-6 text-emerald-800">
                Log in to use the in-app profile-change, password-reset, and
                account-deletion request flows — faster than email.
              </p>
              <Link href="/login" className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-emerald-800 transition hover:gap-2.5">
                Member login <ArrowLeft className="size-4 rotate-180" />
              </Link>
            </div>
          </aside>
        </div>
      </section>
    </main>
  );
}
