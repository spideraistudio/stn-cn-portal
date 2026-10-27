import { randomUUID } from "node:crypto";
import { mongoDb } from "@/lib/sql-mongo";
import type { MemberId } from "@/lib/member-data";
import stateDistricts from "@/lib/data/state-districts.json";

export type SeedRequest = {
  id: string; ownerId: MemberId; ownerCompany: string; status: "published" | "closed" | "cancelled";
  createdAt: number; updatedAt: number; publishedAt: number; closedAt?: number;
  crop: string; segment: string; description: string; varietyType: "hybrid" | "research";
  productMatch: "exact" | "equivalent"; quantity: number; quantityUnit: "kg" | "MT";
  partialAllowed: boolean; cleaning: "clean" | "raw" | "either";
  treatment: "treated" | "untreated" | "either"; germinationRequired: boolean; gotRequired: boolean;
  deliveryState: string; deliveryDistrict: string; destination: string; deliveryBy: string;
  transport: "included" | "excluded" | "negotiable"; paymentTerms: string;
  quotationDeadline: number; anonymous: boolean; panIndia: boolean; supplierStates: string[];
};
const states = stateDistricts as Record<string, string[]>;
const clean = (v: unknown, max: number) => typeof v === "string" ? v.trim().slice(0, max + 1) : "";
const choice = <T extends string>(v: unknown, allowed: readonly T[]): v is T => allowed.includes(v as T);
const bool = (v: unknown) => typeof v === "boolean";
const dateOnly = (v: unknown) => typeof v === "string" && /^\d{4}-\d{2}-\d{2}$/.test(v) && new Date(`${v}T00:00:00+05:30`).toLocaleDateString("en-CA", { timeZone: "Asia/Kolkata" }) === v;

export function validateSeedRequest(raw: Record<string, unknown>, now = Date.now()) {
  const crop = clean(raw.crop, 80), segment = clean(raw.segment, 80), description = clean(raw.description, 1200);
  const destination = clean(raw.destination, 240), deliveryState = clean(raw.deliveryState, 80), deliveryDistrict = clean(raw.deliveryDistrict, 100);
  const paymentTerms = clean(raw.paymentTerms, 400);
  const quantity = raw.quantity;
  const deadline = typeof raw.quotationDeadline === "string" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(raw.quotationDeadline)
    ? Date.parse(`${raw.quotationDeadline}:00+05:30`) : NaN;
  const selected = raw.supplierStates;
  if (!crop || crop.length > 80 || !segment || segment.length > 80 || !description || description.length > 1200) throw new Error("Enter crop, segment and a product description.");
  if (!choice(raw.varietyType, ["hybrid", "research"]) || !choice(raw.productMatch, ["exact", "equivalent"])) throw new Error("Choose the product type and acceptable match.");
  if (typeof quantity !== "number" || !Number.isFinite(quantity) || quantity <= 0 || quantity > 100000000 || !choice(raw.quantityUnit, ["kg", "MT"])) throw new Error("Enter a positive quantity and kg or MT unit.");
  if (![raw.partialAllowed, raw.germinationRequired, raw.gotRequired, raw.anonymous, raw.panIndia].every(bool)) throw new Error("Complete all Yes/No choices.");
  if (!choice(raw.cleaning, ["clean", "raw", "either"]) || !choice(raw.treatment, ["treated", "untreated", "either"])) throw new Error("Choose the required seed condition.");
  if (!states[deliveryState] || !states[deliveryState].includes(deliveryDistrict) || !destination || destination.length > 240) throw new Error("Choose a valid delivery state, district and destination.");
  if (!dateOnly(raw.deliveryBy) || Date.parse(`${raw.deliveryBy}T23:59:59+05:30`) < now) throw new Error("Choose a future delivery date.");
  if (!choice(raw.transport, ["included", "excluded", "negotiable"]) || paymentTerms.length > 400) throw new Error("Choose transportation terms.");
  if (!Number.isFinite(deadline) || deadline <= now || deadline > Date.parse(`${raw.deliveryBy}T23:59:59+05:30`)) throw new Error("Quotation deadline must be in the future and no later than delivery.");
  if (!Array.isArray(selected) || selected.length > Object.keys(states).length || selected.some(v => typeof v !== "string" || !states[v])) throw new Error("Select valid supplier states.");
  const supplierStates = [...new Set(selected as string[])].sort();
  if (!raw.panIndia && !supplierStates.length) throw new Error("Select at least one supplier state or Pan India.");
  return { crop, segment, description, varietyType: raw.varietyType, productMatch: raw.productMatch, quantity, quantityUnit: raw.quantityUnit,
    partialAllowed: raw.partialAllowed, cleaning: raw.cleaning, treatment: raw.treatment, germinationRequired: raw.germinationRequired,
    gotRequired: raw.gotRequired, deliveryState, deliveryDistrict, destination, deliveryBy: raw.deliveryBy, transport: raw.transport,
    paymentTerms, quotationDeadline: deadline, anonymous: raw.anonymous, panIndia: raw.panIndia, supplierStates: raw.panIndia ? [] : supplierStates } as Pick<SeedRequest, "crop" | "segment" | "description" | "varietyType" | "productMatch" | "quantity" | "quantityUnit" | "partialAllowed" | "cleaning" | "treatment" | "germinationRequired" | "gotRequired" | "deliveryState" | "deliveryDistrict" | "destination" | "deliveryBy" | "transport" | "paymentTerms" | "quotationDeadline" | "anonymous" | "panIndia" | "supplierStates">;
}
export async function createSeedRequest(ownerId: MemberId, ownerCompany: string, values: ReturnType<typeof validateSeedRequest>) {
  const now = Date.now(); const request: SeedRequest = { ...values, id: randomUUID(), ownerId, ownerCompany, status: "published", createdAt: now, updatedAt: now, publishedAt: now };
  await (await mongoDb()).collection<SeedRequest>("seed_buy_requests").insertOne(request);
  return request;
}
export async function listOwnSeedRequests(ownerId: MemberId) {
  return (await mongoDb()).collection<SeedRequest>("seed_buy_requests").find({ ownerId }).sort({ createdAt: -1 }).toArray();
}
export async function getOwnSeedRequest(ownerId: MemberId, id: string) {
  return (await mongoDb()).collection<SeedRequest>("seed_buy_requests").findOne({ ownerId, id });
}
export async function closeOwnSeedRequest(ownerId: MemberId, id: string, action: "closed" | "cancelled") {
  const now = Date.now();
  const result = await (await mongoDb()).collection<SeedRequest>("seed_buy_requests").findOneAndUpdate(
    { ownerId, id, status: "published" }, { $set: { status: action, updatedAt: now, closedAt: now } }, { returnDocument: "after" });
  return result;
}
