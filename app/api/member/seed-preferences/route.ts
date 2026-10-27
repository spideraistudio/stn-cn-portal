import { isOriginValid } from "@/lib/origin-check";
import { NextResponse } from "next/server";
import { currentMember } from "@/lib/member-session";
import { categoryAccess } from "@/lib/category-access";
import { readJsonBody, RequestBodyError } from "@/lib/request-body";
import { seedNotificationsEnabled, setSeedNotifications } from "@/lib/seed-preferences";

const reply = (body: object, status = 200) => NextResponse.json(body, {
  status,
  headers: { "Cache-Control": "private, no-store" },
});

async function authorizedMember() {
  const member = await currentMember();
  return member && !member.mustChangePassword && categoryAccess(member)?.id === "agriculture"
    ? member
    : null;
}

export async function GET() {
  const member = await authorizedMember();
  if (!member) return reply({ error: "Approved Agriculture membership required." }, 403);
  return reply({ seedNotifications: await seedNotificationsEnabled(member.id) });
}

export async function POST(request: Request) {
  const member = await authorizedMember();
  if (!member) return reply({ error: "Approved Agriculture membership required." }, 403);
  if (!isOriginValid(request)) return reply({ error: "Invalid request origin." }, 403);
  try {
    const body = await readJsonBody(request);
    if (typeof body.seedNotifications !== "boolean" || Object.keys(body).length !== 1) {
      return reply({ error: "Choose on or off for Seed notifications." }, 400);
    }
    if (!(await setSeedNotifications(member, body.seedNotifications))) {
      return reply({ error: "Membership changed. Please refresh and try again." }, 409);
    }
    return reply({ seedNotifications: body.seedNotifications });
  } catch (error) {
    if (error instanceof RequestBodyError) return reply({ error: error.message }, error.status);
    if (error instanceof SyntaxError) return reply({ error: "Invalid request." }, 400);
    throw error;
  }
}
