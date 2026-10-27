import Link from "next/link";
import { BrandLogo } from "@/components/brand-logo";
import {
  ChevronDown, ShieldCheck, FileSearch, Scale,
  Lock, Users, AlertCircle, ArrowRight
} from "lucide-react";
import { BreadcrumbsJsonLd } from "@/components/breadcrumbs-jsonld";
import { WebPageJsonLd } from "@/components/webpage-jsonld";

export const dynamic = "force-dynamic";

const faqs = [
  {
    category: "Membership",
    icon: Users,
    items: [
      {
        q: "How do I become a member?",
        a: "Submit a company registration on the Join page with your GSTIN, business details, and location. The administrator manually verifies each application and, after approval, shares your Member ID and temporary password.",
      },
      {
        q: "Is a third-party account required?",
        a: "No. Membership uses a separate Member ID and password issued by the administrator. No third-party account is needed to register or sign in.",
      },
      {
        q: "How long does approval take?",
        a: "The administrator reviews applications manually. You will receive your Member ID and temporary credentials only after verification is complete — there is no automatic approval.",
      },
      {
        q: "What if I forget my Member ID or password?",
        a: "Use the Forgot Password page to send a secure reset request. If you have lost your Member ID, contact the administrator directly at meetpatel.hmt@gmail.com.",
      },
    ],
  },
  {
    category: "Seller reports",
    icon: FileSearch,
    items: [
      {
        q: "How do I search for a seller?",
        a: "Once logged in, use the seller search feature. You must enter the seller's exact 15-character GSTIN — there is no partial or name-based search. This prevents enumeration and protects seller privacy.",
      },
      {
        q: "What information do search results show?",
        a: "Approved reports for that seller within your category: ratings, dispute history, resolution status, and factual summaries. GSTINs are masked (only last 4 digits visible) and review notes are never exposed to other members.",
      },
      {
        q: "Can I see reports from other categories?",
        a: "No. Category isolation is enforced. Agriculture members see only agriculture reports; 'Other' category members see only other-category reports. This prevents competitive intelligence leaking to rivals.",
      },
      {
        q: "What if a seller's information is wrong?",
        a: "The seller can request a correction by providing their GST certificate and the details of the challenged record. The record may be labelled 'under review' while investigated. See the Contact page to start this process.",
      },
    ],
  },
  {
    category: "Disputes",
    icon: Scale,
    items: [
      {
        q: "How do I report a dispute?",
        a: "After finding a seller, submit a structured report including the dispute type, disputed amount, rating, and a neutral factual summary. You can attach supporting documents (up to 1.5 MB each).",
      },
      {
        q: "What happens after I submit a report?",
        a: "Reports start in 'pending' status. An administrator reviews the submission, verifies identity and evidence, and either approves (making it searchable) or rejects it. You receive a notification when the decision is made.",
      },
      {
        q: "Can I edit a report after submission?",
        a: "Pending reports can be edited. Approved reports can only be changed by requesting a revision, which returns to admin approval. This preserves the integrity of the historical ledger.",
      },
      {
        q: "How are disputes resolved?",
        a: "You can submit a dispute resolution request with the resolution date, resolved amount, and a description. An administrator reviews and approves or rejects the resolution. Resolved disputes are marked accordingly.",
      },
    ],
  },
  {
    category: "Security",
    icon: ShieldCheck,
    items: [
      {
        q: "How are my credentials protected?",
        a: "Passwords are hashed with scrypt (a memory-hard key derivation function) and verified with timing-safe comparison. Session cookies are httpOnly, secure (in production), and sameSite=strict. Only a SHA-256 digest of the session token is stored server-side.",
      },
      {
        q: "What happens if I enter the wrong password too many times?",
        a: "After five incorrect attempts, your account is locked for 15 minutes. Repeated failed logins trigger a security event and notify the administrator. This protects against brute-force attacks.",
      },
      {
        q: "Can someone else use my account simultaneously?",
        a: "Only one active session is allowed per member. A new login replaces any earlier session and notifies you. If you receive this notification unexpectedly, change your password immediately and contact the administrator.",
      },
      {
        q: "Is my GSTIN visible to other members?",
        a: "No. GSTINs are HMAC-SHA256 hashed before storage. Other members see only the last four digits. Your full GSTIN is never exposed in search results or reports.",
      },
    ],
  },
  {
    category: "Data & privacy",
    icon: Lock,
    items: [
      {
        q: "How long is my data retained?",
        a: "Rejected applications and reports: 30 days after rejection (subject to legal holds). Approved reports and audit records: retained as part of the commercial-history ledger while the platform operates. In-app notifications: 10 days. Deactivated accounts: retained until deletion is approved.",
      },
      {
        q: "How do I close my account?",
        a: "Submit an account-deletion request from the member dashboard. An administrator reviews and approves it. After closure, approved historical reports may remain but your member-facing attribution is anonymised where possible.",
      },
      {
        q: "Can I request my data be corrected?",
        a: "Yes. Use the profile-change request flow in the member dashboard, or email the grievance officer. For seller record corrections, provide the GST certificate and relevant facts.",
      },
      {
        q: "Is the platform a credit rating or blacklist?",
        a: "No. The platform is one due-diligence input only. It does not provide credit ratings, guarantee payment, or recommend trading decisions. Always independently verify before acting.",
      },
    ],
  },
];

// FAQPage JSON-LD structured data for Google rich results (FAQ rich snippets).
const faqJsonLd = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: faqs.flatMap(section =>
    section.items.map(item => ({
      "@type": "Question",
      name: item.q,
      acceptedAnswer: { "@type": "Answer", text: item.a },
    }))
  ),
};

export default function FaqPage() {
  return (
    <main className="min-h-screen bg-[#f5f7fb] text-slate-900">
      <BreadcrumbsJsonLd items={[{ name: "FAQ", path: "/faq" }]} />
      <WebPageJsonLd name="FAQ — Sellers Trust Network" path="/faq" description="Frequently asked questions about membership, seller reports, disputes, security, and data privacy." />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
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
            <AlertCircle className="size-4" />
            Help center
          </div>
          <h1 className="mt-3 text-4xl font-bold tracking-tight text-white sm:text-5xl">Frequently asked questions</h1>
          <p className="mt-3 max-w-2xl text-lg text-blue-100">
            Everything you need to know about membership, seller reports, disputes, security, and data privacy.
          </p>
        </div>
        <svg className="relative z-10 block w-full" viewBox="0 0 1440 60" preserveAspectRatio="none" style={{ height: "40px" }}>
          <path d="M0,30 C360,60 1080,0 1440,30 L1440,60 L0,60 Z" fill="#f5f7fb" />
        </svg>
      </header>

      {/* FAQ sections */}
      <section className="mx-auto max-w-4xl px-5 py-12">
        <div className="space-y-10">
          {faqs.map((section, sIdx) => {
            const Icon = section.icon;
            return (
              <div key={section.category} className="animate-fade-in-up" style={{ animationDelay: `${sIdx * 0.1}s` }}>
                <div className="mb-5 flex items-center gap-3">
                  <span className="grid size-10 place-items-center rounded-xl bg-[#15388c]/5 text-[#15388c]">
                    <Icon className="size-5" />
                  </span>
                  <h2 className="text-2xl font-bold text-slate-900">{section.category}</h2>
                </div>
                <div className="space-y-3">
                  {section.items.map((item, iIdx) => (
                    <details key={iIdx} className="group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:border-[#15388c]/20">
                      <summary className="flex cursor-pointer list-none items-center justify-between gap-4 p-5">
                        <span className="font-semibold text-slate-900">{item.q}</span>
                        <ChevronDown className="size-5 shrink-0 text-slate-400 transition group-open:rotate-180" />
                      </summary>
                      <div className="border-t border-slate-100 px-5 py-4 text-sm leading-7 text-slate-600">
                        {item.a}
                      </div>
                    </details>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* CTA */}
        <div className="mt-12 rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900">Still have questions?</h2>
          <p className="mx-auto mt-2 max-w-md text-sm text-slate-500">
            Can&apos;t find the answer you&apos;re looking for? Contact the grievance officer directly.
          </p>
          <div className="mt-5 flex flex-wrap justify-center gap-3">
            <Link href="/contact" className="inline-flex items-center gap-2 rounded-xl bg-[#15388c] px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-[#15388c]/20 transition hover:bg-[#1d46a8]">
              Contact us <ArrowRight className="size-4" />
            </Link>
            <Link href="/join" className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
              Register company
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
