import { isOriginValid } from "@/lib/origin-check";
import { NextResponse } from "next/server";
import { currentMember } from "@/lib/member-session";
import { categoryAccess } from "@/lib/category-access";
import { readJsonBody, RequestBodyError } from "@/lib/request-body";
import { createSeedRequest, listOwnSeedRequests, validateSeedRequest } from "@/lib/seed-requests";
import { notifyEligibleSeedMembers } from "@/lib/seed-trading";
const reply = (body: object, status = 200) => NextResponse.json(body, { status, headers: { "Cache-Control": "private, no-store" } });
async function member() { const m = await currentMember(); return m && !m.mustChangePassword && categoryAccess(m)?.id === "agriculture" ? m : null; }
export async function GET() { const m = await member(); return m ? reply({ requests: await listOwnSeedRequests(m.id) }) : reply({ error: "Approved Agriculture membership required." }, 403); }
export async function POST(request: Request) {
  const m = await member(); if (!m) return reply({ error: "Approved Agriculture membership required." }, 403);
  if (!isOriginValid(request)) return reply({ error: "Invalid request origin." }, 403);
  try { const values = validateSeedRequest(await readJsonBody(request)); const created = await createSeedRequest(m.id, m.companyName, values); await notifyEligibleSeedMembers(created); return reply({ request: created }, 201); }
  catch (error) { if (error instanceof RequestBodyError) return reply({ error: error.message }, error.status); if (error instanceof SyntaxError || error instanceof Error) return reply({ error: error.message }, 400); throw error; }
}
