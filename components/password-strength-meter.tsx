"use client";
import { useMemo } from "react";
import { Check, X } from "lucide-react";

type Props = { password: string };

const criteria = [
  { label: "12+ characters", test: (p: string) => p.length >= 12 },
  { label: "Uppercase letter", test: (p: string) => /[A-Z]/.test(p) },
  { label: "Lowercase letter", test: (p: string) => /[a-z]/.test(p) },
  { label: "Number", test: (p: string) => /[0-9]/.test(p) },
  { label: "Special character", test: (p: string) => /[^A-Za-z0-9]/.test(p) },
];

export function PasswordStrengthMeter({ password }: Props) {
  const { score, passed, label, color } = useMemo(() => {
    const passed = criteria.map(c => c.test(password));
    const score = passed.filter(Boolean).length;
    const labels = ["Very weak", "Weak", "Fair", "Good", "Strong", "Excellent"];
    const colors = [
      "bg-rose-500", "bg-rose-500", "bg-amber-500",
      "bg-yellow-500", "bg-emerald-500", "bg-emerald-600",
    ];
    return {
      score, passed,
      label: labels[score],
      color: colors[score],
    };
  }, [password]);

  if (!password) return null;

  return (
    <div className="mt-3 animate-fade-in space-y-2.5 rounded-xl border border-slate-200 bg-slate-50 p-4">
      {/* Strength bar */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-600">Password strength</span>
        <span className={`text-xs font-semibold ${score <= 1 ? "text-rose-600" : score <= 2 ? "text-amber-600" : score <= 3 ? "text-yellow-600" : "text-emerald-600"}`}>
          {label}
        </span>
      </div>
      <div className="flex gap-1.5">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${i < score ? color : "bg-slate-200"}`}
          />
        ))}
      </div>
      {/* Criteria checklist */}
      <div className="grid grid-cols-2 gap-1.5 pt-1">
        {criteria.map((c, i) => (
          <div key={c.label} className="flex items-center gap-1.5 text-xs">
            {passed[i] ? (
              <Check className="size-3.5 shrink-0 text-emerald-600" />
            ) : (
              <X className="size-3.5 shrink-0 text-slate-400" />
            )}
            <span className={passed[i] ? "text-slate-700" : "text-slate-400"}>{c.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
