import { readJsonBody } from "@/lib/request-body";
import { NextResponse } from "next/server";
import { reportDb, reportMember, identifierKey } from "@/lib/report-store";

/** Lightweight GSTIN identity lookup for report forms (no search quota). */
export async function POST(request: Request) {
  const reply = (data: object, status = 200) =>
    NextResponse.json(data, { status, headers: { "Cache-Control": "no-store" } });
  const member = await reportMember();
  if (!member) {
    return reply(
      { error: "An approved membership and assigned category are required." },
      403,
    );
  }
  try {
    const body = (await readJsonBody(request)) as { gstin?: string };
    const gstin = String(body.gstin || "")
      .trim()
      .toUpperCase();
    if (!/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/.test(gstin)) {
      return reply({ error: "Enter the complete valid GSTIN." }, 400);
    }
    const key = identifierKey(member.category, "gst", gstin);
    const db = reportDb();
    const [identity, totals] = await Promise.all([
      db
        .prepare(
          "SELECT r.seller_id,r.firm_name,r.taluka,r.district,r.state,r.pincode,s.gst_last4 FROM seller_reports r JOIN sellers s ON s.id=r.seller_id JOIN members m ON m.id=r.member_id WHERE r.category=? AND s.gst_lookup=? AND r.status='approved' AND m.is_pilot=? ORDER BY COALESCE(r.reviewed_at,r.created_at) DESC LIMIT 1",
        )
        .bind(member.category, key, Number(member.isPilot))
        .first<Record<string, unknown>>(),
      db
        .prepare(
          "SELECT count(*) report_count,avg(rating) average_rating FROM seller_reports r JOIN sellers s ON s.id=r.seller_id JOIN members m ON m.id=r.member_id WHERE r.category=? AND s.gst_lookup=? AND r.status='approved' AND m.is_pilot=?",
        )
        .bind(member.category, key, Number(member.isPilot))
        .first<{ report_count: number; average_rating: number }>(),
    ]);
    if (!identity) return reply({ seller: null });
    return reply({
      seller: {
        seller_id: String(identity.seller_id),
        firm_name: String(identity.firm_name),
        taluka: String(identity.taluka),
        district: String(identity.district),
        state: String(identity.state),
        pincode: String(identity.pincode || ""),
        gstin: `***********${identity.gst_last4}`,
        report_count: Number(totals?.report_count || 0),
        average_rating: Math.round(Number(totals?.average_rating || 0) * 10) / 10,
      },
    });
  } catch {
    return reply({ error: "Seller lookup is temporarily unavailable. Please try again." }, 503);
  }
}
