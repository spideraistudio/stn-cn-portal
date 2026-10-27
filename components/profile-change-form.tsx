"use client";

import { useState } from "react";
import { readJsonResponse } from "@/lib/client-response";
import { DetailSection } from "@/components/list-frame";

const control =
  "h-10 w-full rounded-[12px] border border-slate-200 bg-white px-3 text-[13px] text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10 disabled:bg-slate-100";
const labelClass = "mb-1.5 block text-[12px] font-medium text-slate-700";
const btnPrimary =
  "inline-flex h-10 items-center justify-center rounded-[12px] bg-[#15388c] px-4 text-[13px] font-semibold text-white transition hover:bg-[#102d74] disabled:opacity-50";

export function ProfileChangeForm({
  member,
  pending,
}: {
  member: {
    responsiblePersonName: string;
    mobileNumber: string;
    email: string;
    address: string;
  };
  pending: boolean;
}) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [ok, setOk] = useState(false);

  return (
    <DetailSection title="Contact details">
      <form
        onSubmit={async event => {
          event.preventDefault();
          setBusy(true);
          setMessage("");
          setOk(false);
          const body = Object.fromEntries(new FormData(event.currentTarget));
          try {
            const response = await fetch("/api/profile-change", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(body),
            });
            const data = await readJsonResponse<{ error?: string }>(response);
            if (!response.ok) {
              throw new Error(data.error || "Unable to submit changes.");
            }
            setOk(true);
            setMessage("Profile changes sent for administrator approval.");
          } catch (cause) {
            setMessage(
              cause instanceof Error ? cause.message : "Unable to submit changes.",
            );
          } finally {
            setBusy(false);
          }
        }}
      >
        <fieldset
          disabled={pending || busy}
          className="grid gap-3 sm:grid-cols-2 disabled:opacity-70"
        >
          <label className="block">
            <span className={labelClass}>Responsible person *</span>
            <input
              name="responsiblePersonName"
              required
              minLength={2}
              maxLength={120}
              defaultValue={member.responsiblePersonName}
              className={control}
            />
          </label>
          <label className="block">
            <span className={labelClass}>Mobile number *</span>
            <input
              name="mobileNumber"
              required
              pattern="[6-9][0-9]{9}"
              defaultValue={member.mobileNumber}
              className={control}
            />
          </label>
          <label className="block sm:col-span-2">
            <span className={labelClass}>Email address *</span>
            <input
              name="email"
              required
              type="email"
              maxLength={160}
              defaultValue={member.email}
              className={control}
            />
          </label>
          <label className="block sm:col-span-2">
            <span className={labelClass}>Company address *</span>
            <textarea
              name="address"
              required
              minLength={5}
              maxLength={500}
              rows={4}
              defaultValue={member.address}
              className="w-full rounded-[12px] border border-slate-200 bg-white px-3 py-2.5 text-[13px] outline-none transition focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10 disabled:bg-slate-100"
            />
          </label>
          <div className="sm:col-span-2">
            <button type="submit" className={btnPrimary}>
              {busy ? "Sending…" : "Request profile changes"}
            </button>
          </div>
        </fieldset>

        {pending && (
          <p className="mt-3 rounded-[12px] border border-amber-200 bg-amber-50 px-3 py-2.5 text-[12px] text-amber-900">
            A profile-change request is already awaiting administrator approval.
          </p>
        )}
        {message && (
          <p
            role="status"
            className={`mt-3 rounded-[12px] border px-3 py-2.5 text-[12px] ${
              ok
                ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                : "border-rose-200 bg-rose-50 text-rose-700"
            }`}
          >
            {message}
          </p>
        )}
      </form>
    </DetailSection>
  );
}
