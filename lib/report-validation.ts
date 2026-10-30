import { z } from "zod";

const text = (max: number) => z.string().trim().min(2).max(max);

/** Convert INR amount string to integer paise. Optional legacy unit multipliers still accepted. */
export function amountPaise(amount: string, unit: string = "rupees") {
  const cleaned = String(amount || "").trim().replace(/,/g, "");
  const [whole, fraction = ""] = cleaned.split(".");
  const paise =
    Number(whole) * 100 + Number((fraction + "00").slice(0, 2));
  const multipliers: Record<string, number> = {
    rupees: 1,
    thousands: 1000,
    lakhs: 100000,
    crores: 10000000,
  };
  return paise * (multipliers[unit] ?? 1);
}

export const reportInput = z
  .object({
    requestId: z.string().uuid(),
    gstin: z
      .string()
      .trim()
      .toUpperCase()
      .regex(
        /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/,
        "Enter a valid 15-character GSTIN.",
      ),
    firmName: text(200),
    taluka: text(100),
    district: text(100),
    state: text(100),
    pincode: z.union([
      z
        .string()
        .trim()
        .regex(/^[1-9][0-9]{5}$/, "Enter a valid six-digit PIN code."),
      z.literal(""),
    ]),
    rating: z.number().int().min(0).max(10),
    dispute: z.boolean(),
    amount: z.string().max(20),
    /** @deprecated Prefer direct INR amount; kept for older clients. */
    unit: z
      .enum(["rupees", "thousands", "lakhs", "crores"])
      .optional()
      .default("rupees"),
    disputeType: z.enum([
      "payment_default",
      "agreement_breach",
      "misrepresentation",
      "other",
    ]),
    disputeOther: z.string().trim().max(1000),
    disputeStartMonth: z.string().max(7),
    disputeEndMonth: z.string().max(7),
    disputeOngoing: z.boolean(),
    requestSellerCorrection: z.boolean().default(false),
    legal: z.boolean(),
    caseNumber: z.string().trim().max(200),
    caseNumberType: z.enum(["temporary", "permanent", "unspecified"]).default("unspecified"),
    summary: z.string().trim().max(5000).optional().default(""),
  })
  .superRefine((v, c) => {
    const issue = (path: string, message: string) =>
      c.addIssue({ code: "custom", path: [path], message });
    const amount = String(v.amount || "").trim().replace(/,/g, "");
    if (v.dispute && !/^[0-9]{1,12}(\.[0-9]{1,2})?$/.test(amount)) {
      issue(
        "amount",
        "Enter the full amount in INR with up to two decimal places.",
      );
    }
    if (
      v.dispute &&
      (!Number.isSafeInteger(amountPaise(amount, v.unit)) ||
        amountPaise(amount, v.unit) <= 0)
    ) {
      issue("amount", "Enter a valid amount within the supported range.");
    }
    if (v.dispute && v.disputeType === "other" && v.disputeOther.length < 2) {
      issue("disputeOther", "Please specify the dispute type.");
    }
    const month = /^\d{4}-(0[1-9]|1[0-2])$/;
    const current = new Date().toISOString().slice(0, 7);
    if (
      v.dispute &&
      (!month.test(v.disputeStartMonth) || v.disputeStartMonth > current)
    ) {
      issue("disputeStartMonth", "Enter a valid dispute starting month.");
    }
    if (
      v.dispute &&
      !v.disputeOngoing &&
      (!month.test(v.disputeEndMonth) ||
        v.disputeEndMonth < v.disputeStartMonth ||
        v.disputeEndMonth > current)
    ) {
      issue(
        "disputeEndMonth",
        "Enter an ending month on or after the starting month.",
      );
    }
    if (v.legal && v.caseNumber.length < 2) {
      issue("caseNumber", "Enter the case or filing number.");
    }
  });

export function redactIdentifiers(value: string) {
  return value
    .replace(
      /\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b/gi,
      v => "***********" + v.slice(-4).toUpperCase(),
    )
    .replace(
      /\b[2-9][0-9]{3}[ -]?[0-9]{4}[ -]?[0-9]{4}\b/g,
      v => "XXXX XXXX " + v.slice(-4),
    );
}
