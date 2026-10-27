import { redirect } from "next/navigation";
import { requireChatGPTUser } from "@/app/chatgpt-auth";
import { isConfiguredAdmin } from "@/lib/member-data";
import { mongoDb } from "@/lib/sql-mongo";
import type { SeedRequest } from "@/lib/seed-requests";
import type { SeedQuotation } from "@/lib/seed-trading";
import { ReportShell } from "@/components/report-shell";

export const dynamic = "force-dynamic";
const ist = (time: number) => new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata", dateStyle: "medium", timeStyle: "short",
}).format(new Date(time));

export default async function SeedTradeOversight({ searchParams }: {
  searchParams: Promise<{ page?: string; status?: string }>;
}) {
  const admin = await requireChatGPTUser("/admin/seed-trade");
  if (!isConfiguredAdmin(admin.email)) redirect("/join");
  const params = await searchParams;
  const page = Math.min(10000, Math.max(1, Number.parseInt(params.page || "1", 10) || 1));
  const status = ["published", "closed", "cancelled"].includes(params.status || "") ? params.status as SeedRequest["status"] : "";
  const db = await mongoDb();
  const filter = status ? { status } : {};
  const [total, requests] = await Promise.all([
    db.collection<SeedRequest>("seed_buy_requests").countDocuments(filter),
    db.collection<SeedRequest>("seed_buy_requests").find(filter).sort({ createdAt: -1 }).skip((page - 1) * 20).limit(20).toArray(),
  ]);
  const ids = requests.map(r => r.id);
  const quotes = ids.length ? await db.collection<SeedQuotation>("seed_quotations").find({ requestId: { $in: ids } }).sort({ createdAt: 1 }).toArray() : [];
  const reveals = ids.length ? await db.collection("audit_logs").find({ action: "seed.buyer_name_revealed", $or: ids.map(id => ({ details: { $regex: id } })) }).sort({ created_at: -1 }).limit(100).toArray() : [];
  return <ReportShell admin title="Seed trade oversight" description="Read-only review of requests, private quotations and buyer-name disclosures.">
    <div className="space-y-4">
      <nav className="flex gap-3 text-sm" aria-label="Request status">
        {(["", "published", "closed", "cancelled"] as const).map(value => <a key={value} className="rounded-lg border px-3 py-2" href={`/admin/seed-trade${value ? `?status=${value}` : ""}`}>{value || "All"}</a>)}
      </nav>
      <p className="text-sm text-slate-600">{total} requests · page {page}</p>
      {requests.map(r => {
        const offers = quotes.filter(q => q.requestId === r.id);
        return <section key={r.id} className="rounded-xl border bg-white p-5 text-sm shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-2"><h2 className="text-lg font-semibold">{r.crop} · {r.segment}</h2><span className="rounded-full bg-slate-100 px-3 py-1">{r.status}</span></div>
          <p className="mt-2">{r.ownerCompany} · {r.quantity} {r.quantityUnit} · {r.anonymous ? "Anonymous to suppliers" : "Company visible"} · {r.panIndia ? "Pan India" : r.supplierStates.join(", ")}</p>
          <p className="text-slate-600">ID {r.id} · Published {ist(r.publishedAt)} · quote deadline {ist(r.quotationDeadline)}</p>
          <details className="mt-3"><summary className="cursor-pointer font-medium">{offers.length} private quotations · inspect activity</summary>
            <div className="mt-3 space-y-2">
              {offers.map(q => <div key={q.id} className="rounded-lg border p-3">
                <strong>{q.supplierCompany}</strong> · {q.status} · {q.quantity} {q.quantityUnit} @ ₹{q.price}/{q.priceUnit}
                <p>Updated {ist(q.updatedAt)} · {q.revisions?.length || 0} revisions · buyer name {q.revealBuyerName ? "currently visible" : "hidden"}{q.everRevealed ? " · previously disclosed" : ""}</p>
                <p className="text-slate-600">Quote ID {q.id} · Germination {q.germinationAvailable ? "Yes" : "No"} · GOT {q.gotAvailable ? "Yes" : "No"} (supplier declarations)</p>
              </div>)}
              {reveals.filter(a => String(a.details || "").includes(r.id)).map(a => <p key={String(a._id)} className="text-amber-800">Buyer name revealed · {ist(Number(a.created_at))} · {String(a.details)}</p>)}
            </div>
          </details>
        </section>;
      })}
      {!requests.length && <p className="rounded-xl border bg-white p-5">No Seed requests in this view.</p>}
      <div className="flex gap-4 text-sm">{page > 1 && <a href={`/admin/seed-trade?page=${page - 1}${status ? `&status=${status}` : ""}`}>Previous</a>}{page * 20 < total && <a href={`/admin/seed-trade?page=${page + 1}${status ? `&status=${status}` : ""}`}>Next</a>}</div>
    </div>
  </ReportShell>;
}
