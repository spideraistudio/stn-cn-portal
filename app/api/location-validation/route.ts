import { readJsonBody } from "@/lib/request-body";
import { NextResponse } from "next/server";
import { validateIndianLocation } from "@/lib/india-locations";
import { isOriginValid } from "@/lib/origin-check";

export async function POST(request: Request) {
  if (!isOriginValid(request)) return NextResponse.json({ error: "Invalid request origin." }, { status: 403 });
  try {
    const data = await readJsonBody(request) as Record<string, unknown>;
    const result = validateIndianLocation(String(data.state || ""), String(data.district || ""), String(data.pincode || ""));
    return NextResponse.json(result, { status: result.valid ? 200 : 400, headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json({ valid: false, error: "The location could not be checked." }, { status: 400 });
  }
}
