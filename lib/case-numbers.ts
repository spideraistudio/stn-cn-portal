export type CaseNumberType = "temporary" | "permanent" | "unspecified";
export type CaseNumberRecord = {case_number?: unknown; case_number_type?: unknown; case_number_history?: unknown};
export type CaseNumberHistory = {number: string; type: CaseNumberType; replaced_at: number}[];

export function caseNumberType(value: unknown): CaseNumberType {
  return value === "temporary" || value === "permanent" ? value : "unspecified";
}
export function caseNumberLabel(value: unknown) {
  return value === "temporary" ? "Temporary / filing number" : value === "permanent" ? "Permanent / registered case number" : "Case / filing number (type not specified)";
}
export function caseNumberHistory(value: unknown): CaseNumberHistory {
  let rows = value;
  if (typeof rows === "string") { try { rows = JSON.parse(rows); } catch { return []; } }
  if (!Array.isArray(rows)) return [];
  return rows.filter(r => r && typeof r.number === "string" && r.number.length <= 200 && Number.isFinite(r.replaced_at))
    .map(r => ({number: r.number, type: caseNumberType(r.type), replaced_at: r.replaced_at}));
}

/** History is generated from stored evidence, never accepted from the browser. */
export function updatedCaseNumbers(input: {legal: boolean; caseNumber: string; caseNumberType: CaseNumberType}, source?: CaseNumberRecord, now = Date.now()) {
  const prior = typeof source?.case_number === "string" ? source.case_number : "";
  const previousType = caseNumberType(source?.case_number_type);
  const number = input.legal ? input.caseNumber : null;
  const type = input.legal ? input.caseNumberType : "unspecified";
  if (input.legal && type === "unspecified" && (!source || number !== prior || previousType !== "unspecified")) {
    throw new Error("Choose Temporary / filing number or Permanent / registered case number.");
  }
  const history = caseNumberHistory(source?.case_number_history);
  if (prior && (number !== prior || type !== previousType)) {
    if (history.length >= 100) throw new Error("This report has reached its case-number history limit. Contact the administrator.");
    history.push({number: prior, type: previousType, replaced_at: now});
  }
  return {number, type, history: JSON.stringify(history)};
}
