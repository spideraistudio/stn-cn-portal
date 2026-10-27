"use client";
import {caseNumberType, type CaseNumberType} from "@/lib/case-numbers";
import {CaseNumberInfo} from "@/components/case-number-info";

import { useRef, useState, type InputHTMLAttributes } from "react";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { LocationFields } from "@/components/location-fields";
import { DetailSection, ListFrame } from "@/components/list-frame";
import { IndianAmountInput, parseIndianAmount } from "@/components/indian-amount-input";

export type EditableReport = {
  id: string;
  status: string;
  gstin: string;
  firm_name: string;
  taluka: string;
  district: string;
  state: string;
  pincode?: string;
  rating: number;
  dispute: number;
  amount_paise: number | null;
  dispute_type: string | null;
  dispute_other: string | null;
  dispute_start_month: string | null;
  dispute_end_month: string | null;
  dispute_ongoing: number;
  legal: number;
  case_number: string | null;
  case_number_type?: CaseNumberType | null;
  case_number_history?: string | null;
  summary: string;
  documents?: { id: string; name: string }[];
};

type SellerIdentity = {
  seller_id: string;
  firm_name: string;
  taluka: string;
  district: string;
  state: string;
  pincode?: string;
  gstin: string;
  report_count: number;
  average_rating: number;
};

const control =
  "h-10 w-full rounded-[12px] border border-slate-200 bg-white px-3 text-[13px] text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10 disabled:bg-slate-100 disabled:text-slate-600";
const labelClass = "mb-1.5 block text-[12px] font-medium text-slate-700";
const btnPrimary =
  "inline-flex h-10 items-center justify-center rounded-[12px] bg-[#15388c] px-4 text-[13px] font-semibold text-white transition hover:bg-[#102d74] disabled:opacity-50";
const btnGhost =
  "inline-flex h-10 items-center justify-center rounded-[12px] border border-slate-200 bg-white px-4 text-[13px] font-semibold text-slate-700 transition hover:bg-slate-50";

function Choice({
  name,
  label,
  options,
  value,
  onChange,
}: {
  name: string;
  label: string;
  options: [string, string][];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div>
      <label htmlFor={name} className={labelClass}>
        {label}
      </label>
      <Select name={name} required value={value} onValueChange={onChange}>
        <SelectTrigger id={name} className="h-10 w-full rounded-[12px] text-[13px]">
          <SelectValue placeholder="Select" />
        </SelectTrigger>
        <SelectContent>
          {options.map(([id, text]) => (
            <SelectItem value={id} key={id}>
              {text}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

function Field({
  name,
  label,
  defaultValue,
  ...props
}: {
  name: string;
  label: string;
  defaultValue?: string | number;
} & InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="block">
      <span className={labelClass}>{label} *</span>
      <input
        name={name}
        required
        defaultValue={defaultValue}
        className={`${control} ${props.readOnly ? "bg-slate-100 text-slate-600" : ""}`}
        maxLength={200}
        {...props}
      />
    </label>
  );
}

export function ReportForm({ initial }: { initial?: EditableReport }) {
  const [dispute, setDispute] = useState(Boolean(initial?.dispute));
  const [legal, setLegal] = useState(Boolean(initial?.legal));
  const [numberType, setNumberType] = useState<CaseNumberType | "">(initial ? caseNumberType(initial.case_number_type) : "");
  const [ongoing, setOngoing] = useState(Boolean(initial?.dispute_ongoing));
  const [rating, setRating] = useState(initial ? String(initial.rating) : "");
  const [type, setType] = useState(initial?.dispute_type || "payment_default");
  const [kept, setKept] = useState<string[]>(
    initial?.documents?.map(document => document.id) || [],
  );
  const [seller, setSeller] = useState<SellerIdentity | null>(null);
  const [checkedGstin, setCheckedGstin] = useState("");
  const [checkingSeller, setCheckingSeller] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [success, setSuccess] = useState(false);
  const [revision, setRevision] = useState(false);
  const requestId = useRef<string | null>(null);

  if (success) {
    return (
      <ListFrame tone="detail">
        <div className="p-4 sm:p-5">
          <section className="rounded-[12px] border border-emerald-200 bg-white p-5">
            <h2 className="text-[15px] font-semibold text-slate-900">
              {revision ? "Changes sent for admin approval" : "Report saved"}
            </h2>
            <p className="mt-2 text-[13px] leading-5 text-slate-600">
              {revision
                ? "The current approved report remains searchable until the admin approves this revision."
                : "This pending report remains hidden until admin approval."}
            </p>
            <a
              href="/member/reports"
              className="mt-4 inline-flex h-10 items-center rounded-[12px] bg-[#15388c] px-4 text-[13px] font-semibold text-white hover:bg-[#102d74]"
            >
              Return to my reports
            </a>
          </section>
        </div>
      </ListFrame>
    );
  }

  const identityLocked = Boolean(initial) || Boolean(seller);
  const identityFieldsKey = initial
    ? `edit-${initial.id}`
    : seller
      ? `locked-${seller.seller_id}`
      : `open-${checkedGstin || "blank"}`;

  return (
    <form
      className="h-full min-h-0"
      onSubmit={async event => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        const get = (key: string) => String(form.get(key) || "").trim();
        const summary = get("summary");
        const caseNumber = get("caseNumber");
        setError("");

        if (rating === "") {
          setError("Select an experience rating before submitting.");
          return;
        }
        if (summary.length < 20) {
          setError("Business summary must be at least 20 characters.");
          return;
        }
        if (legal && (!numberType || (numberType === "unspecified" && caseNumber !== initial?.case_number))) {
          setError("Choose Temporary / filing number or Permanent / registered case number.");
          return;
        }
        if (legal && caseNumber.length < 2) {
          setError("Enter the case or filing number for legal proceedings.");
          return;
        }
        if (dispute) {
          const amount = parseIndianAmount(get("amount"));
          if (!/^[0-9]{1,12}(\.[0-9]{1,2})?$/.test(amount) || Number(amount) <= 0) {
            setError("Enter the full disputed amount in INR (e.g. 2,58,205).");
            return;
          }
          if (!get("disputeStartMonth")) {
            setError("Enter the dispute start month.");
            return;
          }
          if (!ongoing && !get("disputeEndMonth")) {
            setError("Enter the dispute end month, or mark it as ongoing.");
            return;
          }
          if (type === "other" && get("disputeOther").length < 2) {
            setError("Please specify the dispute type.");
            return;
          }
        }

        const files = form
          .getAll("documents")
          .filter((item): item is File => item instanceof File && item.size > 0);
        if (files.length > 3 || files.some(file => file.size > 1.5 * 1024 * 1024)) {
          setError("Upload at most three files, and keep each file at 1.5 MB or smaller.");
          return;
        }

        setBusy(true);
        requestId.current ||= crypto.randomUUID();
        const lockedIdentity = initial
          ? {
              firmName: initial.firm_name,
              taluka: initial.taluka,
              district: initial.district,
              state: initial.state,
              pincode: initial.pincode || "",
            }
          : seller
            ? {
                firmName: seller.firm_name,
                taluka: seller.taluka,
                district: seller.district,
                state: seller.state,
                pincode: seller.pincode || "",
              }
            : null;
        const report = {
          requestId: requestId.current,
          gstin: get("gstin").toUpperCase(),
          firmName: lockedIdentity?.firmName || get("firmName"),
          taluka: lockedIdentity?.taluka || get("taluka"),
          district: lockedIdentity?.district || get("district"),
          state: lockedIdentity?.state || get("state"),
          pincode: lockedIdentity?.pincode ?? get("pincode"),
          rating: Number(rating),
          dispute,
          amount: parseIndianAmount(get("amount")),
          unit: "rupees",
          disputeType: type,
          disputeOther: get("disputeOther"),
          disputeStartMonth: get("disputeStartMonth"),
          disputeEndMonth: get("disputeEndMonth"),
          disputeOngoing: ongoing,
          requestSellerCorrection: false,
          legal,
          caseNumber,
          caseNumberType: numberType || "unspecified",
          summary,
        };
        const payload = new FormData();
        payload.set("report", JSON.stringify(report));
        if (initial) {
          payload.set("sourceId", initial.id);
          payload.set("keepDocuments", JSON.stringify(kept));
        }
        files.forEach(file => payload.append("documents", file));
        try {
          const response = await fetch(initial ? "/api/report-edit" : "/api/reports", {
            method: "POST",
            body: payload,
          });
          const contentType = response.headers.get("content-type") || "";
          if (!contentType.includes("application/json")) {
            if (response.status === 401 || response.status === 403 || response.redirected) {
              throw new Error(
                "Your secure site session has expired. Refresh the page, sign in again if asked, and then retry.",
              );
            }
            if (response.status === 413) {
              throw new Error(
                "The upload was too large. Keep each document at 1.5 MB or smaller.",
              );
            }
            throw new Error(
              "The server could not complete this submission. Your form is still here; please retry once.",
            );
          }
          const data = (await response.json()) as { error?: string; revision?: boolean };
          if (!response.ok) throw new Error(data.error || "Unable to save this report.");
          setRevision(Boolean(data.revision));
          setSuccess(true);
        } catch (cause) {
          setError(cause instanceof Error ? cause.message : "Unable to save. Please retry.");
        } finally {
          setBusy(false);
        }
      }}
      noValidate
    >
      <ListFrame
        tone="detail"
        footer={
          <div className="space-y-2 px-4 py-3 sm:px-5">
            {error && (
              <p
                role="alert"
                className="rounded-[12px] border border-rose-200 bg-rose-50 px-3 py-2 text-[12px] font-medium text-rose-700"
              >
                {error}
              </p>
            )}
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-[12px] text-slate-500">
                Documents optional · max 3 files · 1.5 MB each
              </p>
              <div className="flex flex-wrap gap-2">
                <a href={initial ? "/member/reports" : "/member"} className={btnGhost}>
                  Cancel
                </a>
                <button type="submit" disabled={busy} className={btnPrimary}>
                  {busy
                    ? "Saving…"
                    : initial?.status === "approved"
                      ? "Send for approval"
                      : initial
                        ? "Save pending report"
                        : "Submit for approval"}
                </button>
              </div>
            </div>
          </div>
        }
      >
        <fieldset
          disabled={busy}
          className="space-y-3 p-4 disabled:opacity-70 sm:p-5"
        >
          {initial && (
            <div className="rounded-[12px] border border-amber-200 bg-amber-50 px-3.5 py-3 text-[13px] text-amber-900">
              {initial.status === "approved"
                ? "Saving creates a pending revision. The approved report stays unchanged until admin approval."
                : "You are editing your pending report directly."}
            </div>
          )}

          <DetailSection title="Seller identity">
            <div className="space-y-3">
              <label className="block">
                <span className={labelClass}>Seller GSTIN *</span>
                <input
                  name="gstin"
                  required
                  minLength={15}
                  maxLength={15}
                  autoComplete="off"
                  readOnly={!!initial}
                  defaultValue={initial?.gstin}
                  className={`${control} ${initial ? "bg-slate-100 text-slate-600" : ""}`}
                  onChange={event => {
                    if (event.target.value.toUpperCase() !== checkedGstin) {
                      setSeller(null);
                    }
                  }}
                  onBlur={
                    initial
                      ? undefined
                      : async event => {
                          const input = event.currentTarget;
                          const gstin = input.value.trim().toUpperCase();
                          input.value = gstin;
                          if (
                            !/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/.test(
                              gstin,
                            )
                          ) {
                            setSeller(null);
                            setCheckedGstin("");
                            return;
                          }
                          if (gstin === checkedGstin) return;
                          setCheckingSeller(true);
                          setError("");
                          setCheckedGstin(gstin);
                          try {
                            const response = await fetch("/api/seller-identity", {
                              method: "POST",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify({ gstin }),
                            });
                            const data = (await response.json()) as {
                              seller?: SellerIdentity | null;
                              error?: string;
                            };
                            if (!response.ok) {
                              setSeller(null);
                              setError(data.error || "Unable to look up this GSTIN.");
                              return;
                            }
                            setSeller(data.seller || null);
                          } catch {
                            setSeller(null);
                            setError("Unable to look up this GSTIN. Please try again.");
                          } finally {
                            setCheckingSeller(false);
                          }
                        }
                  }
                />
              </label>
              <p className="text-[12px] text-slate-500">
                {initial
                  ? `GSTIN is locked after submission and ends in ${initial.gstin.slice(-4)}.`
                  : checkingSeller
                    ? "Checking for an existing seller…"
                    : seller
                      ? "Existing seller found — firm name and location are filled and locked."
                      : "Enter the complete GSTIN. Matching sellers autofill firm name and location."}
              </p>
              {seller && (
                <div className="rounded-[12px] border border-emerald-200 bg-emerald-50 px-3.5 py-3">
                  <p className="text-[13px] font-semibold text-emerald-950">
                    {seller.firm_name} · {seller.report_count} report(s) · avg{" "}
                    {seller.average_rating}/10
                  </p>
                  <p className="mt-1 text-[12px] text-emerald-900">
                    {seller.taluka}, {seller.district}, {seller.state}
                    {seller.pincode ? ` · ${seller.pincode}` : ""}
                  </p>
                </div>
              )}
              <Field
                key={`${identityFieldsKey}-firm`}
                name="firmName"
                label="Firm name"
                readOnly={identityLocked}
                defaultValue={seller?.firm_name || initial?.firm_name}
              />
            </div>
          </DetailSection>

          <DetailSection title="Operating location">
            <div
              key={`${identityFieldsKey}-location`}
              className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"
            >
              <LocationFields
                compact
                defaultState={seller?.state || initial?.state}
                defaultDistrict={seller?.district || initial?.district}
                defaultPincode={seller?.pincode || initial?.pincode}
                readOnly={identityLocked}
              />
              <Field
                name="taluka"
                label="Taluka / Tehsil"
                readOnly={identityLocked}
                maxLength={100}
                defaultValue={seller?.taluka || initial?.taluka}
              />
            </div>
            {(initial || seller) && (
              <p className="mt-3 text-[12px] text-slate-500">
                {initial
                  ? "Seller identity is locked. Only experience and documents can change."
                  : "Seller identity comes from the approved profile and will not be changed."}
              </p>
            )}
          </DetailSection>

          <DetailSection title="Commercial experience">
            <Choice
              name="rating"
              label="Experience rating (0–10) *"
              options={Array.from({ length: 11 }, (_, index) => [
                String(index),
                `${index} / 10`,
              ])}
              value={rating}
              onChange={setRating}
            />
          </DetailSection>

          <DetailSection title="Disputes and legal filings">
            <div className="space-y-3">
              <label className="flex items-center gap-2.5 rounded-[12px] border border-slate-200 px-3.5 py-2.5 text-[13px] font-medium">
                <Checkbox
                  checked={dispute}
                  onCheckedChange={value => setDispute(value === true)}
                />
                Commercial dispute exists
              </label>
              {dispute && (
                <div className="space-y-3 rounded-[12px] border border-rose-200 bg-rose-50/80 p-3.5">
                  <IndianAmountInput
                    name="amount"
                    label="Disputed amount (INR)"
                    required
                    className={control}
                    defaultValue={
                      initial?.amount_paise
                        ? Number(initial.amount_paise) / 100
                        : ""
                    }
                    hint="Enter the full amount in rupees. Shown as 2,58,205 for easy reading."
                  />
                  <Choice
                    name="disputeType"
                    label="Type of dispute *"
                    options={[
                      ["payment_default", "Payment default"],
                      ["agreement_breach", "Agreement breach"],
                      ["misrepresentation", "Misrepresentation"],
                      ["other", "Other"],
                    ]}
                    value={type}
                    onChange={setType}
                  />
                  {type === "other" && (
                    <Field
                      name="disputeOther"
                      label="Please specify"
                      maxLength={1000}
                      defaultValue={initial?.dispute_other || ""}
                    />
                  )}
                  <div className="grid gap-3 sm:grid-cols-2">
                    <Field
                      name="disputeStartMonth"
                      label="Dispute started (month/year)"
                      type="month"
                      max={new Date().toISOString().slice(0, 7)}
                      defaultValue={initial?.dispute_start_month || ""}
                    />
                    {!ongoing && (
                      <Field
                        name="disputeEndMonth"
                        label="Dispute ended (month/year)"
                        type="month"
                        max={new Date().toISOString().slice(0, 7)}
                        defaultValue={initial?.dispute_end_month || ""}
                      />
                    )}
                  </div>
                  <label className="flex items-center gap-2.5 rounded-[12px] bg-white/80 px-3 py-2 text-[13px] font-medium">
                    <Checkbox
                      checked={ongoing}
                      onCheckedChange={value => setOngoing(value === true)}
                    />
                    This dispute is ongoing
                  </label>
                </div>
              )}
              <label className="flex items-center gap-2.5 rounded-[12px] border border-slate-200 px-3.5 py-2.5 text-[13px] font-medium">
                <Checkbox
                  checked={legal}
                  onCheckedChange={value => setLegal(value === true)}
                />
                Legal proceedings initiated
              </label>
              {legal && (
                <div className="rounded-[12px] border border-violet-200 bg-violet-50/80 p-3.5">
                  <div className="mb-3">
                    <label htmlFor="report-case-number-type" className={labelClass}>Case number type *</label>
                    <select id="report-case-number-type" name="caseNumberType" className={control} required value={numberType} onChange={event => setNumberType(event.target.value as CaseNumberType | "")}>
                      <option value="" disabled>Choose number type</option>
                      {initial && caseNumberType(initial.case_number_type) === "unspecified" && <option value="unspecified">Type not specified (existing report)</option>}
                      <option value="temporary">Temporary / filing number</option>
                      <option value="permanent">Permanent / registered case number</option>
                    </select>
                  </div>
                  <Field
                    name="caseNumber"
                    label={numberType === "temporary" ? "Temporary / filing number" : numberType === "permanent" ? "Permanent / registered case number" : "Case / filing number"}
                    defaultValue={initial?.case_number || ""}
                    required
                  />
                  <p className="mt-2 text-xs text-slate-600">When the permanent number is assigned, update this report. Earlier numbers remain in its history.</p>
                  {initial?.case_number && <details className="mt-3 text-xs"><summary>Currently saved case details</summary><CaseNumberInfo report={initial}/></details>}
                </div>
              )}
            </div>
          </DetailSection>

          <DetailSection title="Factual business summary">
            <label className="block">
              <span className={labelClass}>Business summary *</span>
              <textarea
                name="summary"
                required
                minLength={20}
                maxLength={5000}
                rows={5}
                defaultValue={initial?.summary}
                className="w-full rounded-[12px] border border-slate-200 bg-white px-3 py-2.5 text-[13px] outline-none transition focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10"
              />
            </label>
          </DetailSection>

          <DetailSection title="Supporting documents">
            <div className="space-y-3">
              {initial?.documents?.map(document => (
                <label
                  key={document.id}
                  className="flex items-center gap-2.5 text-[13px]"
                >
                  <Checkbox
                    checked={kept.includes(document.id)}
                    onCheckedChange={value =>
                      setKept(current =>
                        value === true
                          ? [...current, document.id]
                          : current.filter(id => id !== document.id),
                      )
                    }
                  />
                  <span className="break-all">Keep {document.name}</span>
                </label>
              ))}
              <p className="text-[12px] text-slate-500">
                PDF, JPG or PNG · maximum three documents total · 1.5 MB each
              </p>
              <input
                aria-label="New supporting documents"
                name="documents"
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png"
                className="w-full rounded-[12px] border border-dashed border-slate-300 bg-white px-3 py-3 text-[12px] text-slate-600"
              />
            </div>
          </DetailSection>
        </fieldset>
      </ListFrame>
    </form>
  );
}
