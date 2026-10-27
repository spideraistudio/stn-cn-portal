"use client";

import { useState, type InputHTMLAttributes } from "react";

/** Strip Indian grouping commas → plain numeric string for API. */
export function parseIndianAmount(value: string) {
  return String(value || "")
    .trim()
    .replace(/,/g, "")
    .replace(/[^\d.]/g, "");
}

/** Format a numeric string as Indian readable amount, e.g. 258205 → 2,58,205 */
export function formatIndianAmount(raw: string) {
  const cleaned = parseIndianAmount(raw);
  if (!cleaned) return "";

  const hasDot = cleaned.includes(".");
  const [wholePart, ...fracParts] = cleaned.split(".");
  const fraction = fracParts.join("").slice(0, 2);
  const whole = wholePart.replace(/^0+(?=\d)/, "") || (hasDot || fraction ? "0" : "");

  if (!whole && !hasDot) return "";

  const formattedWhole = new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 0,
  }).format(Number(whole || "0"));

  if (hasDot) return `${formattedWhole}.${fraction}`;
  return formattedWhole;
}

type Props = {
  name: string;
  label: string;
  defaultValue?: string | number;
  /** When set, shows “Reset to full amount” using this INR value. */
  fullAmount?: string | number;
  hint?: string;
  className?: string;
  labelClassName?: string;
} & Omit<
  InputHTMLAttributes<HTMLInputElement>,
  "name" | "defaultValue" | "value" | "onChange" | "type"
>;

/** Amount input that shows Indian grouping (2,58,205) while typing. */
export function IndianAmountInput({
  name,
  label,
  defaultValue = "",
  fullAmount,
  hint,
  className = "",
  labelClassName = "",
  required,
  ...props
}: Props) {
  const formattedFull =
    fullAmount === "" || fullAmount == null
      ? ""
      : formatIndianAmount(String(fullAmount));
  const initial =
    defaultValue === "" || defaultValue == null
      ? formattedFull
      : formatIndianAmount(String(defaultValue));
  const [display, setDisplay] = useState(initial);
  const raw = parseIndianAmount(display);
  const canReset =
    Boolean(formattedFull) && parseIndianAmount(display) !== parseIndianAmount(formattedFull);

  return (
    <div className={labelClassName}>
      <div className="mb-1.5 flex flex-wrap items-center justify-between gap-2">
        <span className="block text-[12px] font-medium text-slate-700">
          {label}
          {required ? " *" : ""}
        </span>
        {formattedFull ? (
          <button
            type="button"
            disabled={!canReset}
            onClick={() => setDisplay(formattedFull)}
            className="text-[11px] font-semibold text-[#15388c] hover:underline disabled:cursor-default disabled:text-slate-400 disabled:no-underline"
          >
            Reset to full amount
          </button>
        ) : null}
      </div>
      <input type="hidden" name={name} value={raw} required={required} />
      <input
        {...props}
        type="text"
        inputMode="decimal"
        autoComplete="off"
        value={display}
        placeholder={props.placeholder || "e.g. 2,58,205"}
        onChange={event => setDisplay(formatIndianAmount(event.target.value))}
        className={
          className ||
          "h-10 w-full rounded-[12px] border border-slate-200 bg-white px-3 text-[13px] text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10 disabled:bg-slate-100"
        }
      />
      {hint ? (
        <span className="mt-1 block text-[11px] font-normal text-slate-500">{hint}</span>
      ) : null}
    </div>
  );
}
