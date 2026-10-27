"use client";

import { useState } from "react";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { readJsonResponse } from "@/lib/client-response";
import { PasswordStrengthMeter } from "@/components/password-strength-meter";

export function CredentialForm({ change = false }: { change?: boolean }) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [newPassword, setNewPassword] = useState("");

  const fields = change
    ? [
        ["currentPassword", "Current or temporary password"],
        ["password", "New password"],
        ["confirmPassword", "Confirm new password"],
      ]
    : [
        ["loginId", "Member ID"],
        ["password", "Password"],
      ];

  return (
    <form
      className={change ? "mt-6 space-y-4" : "mt-6 space-y-5"}
      onSubmit={async event => {
        event.preventDefault();
        setBusy(true);
        setError("");
        try {
          const data = Object.fromEntries(new FormData(event.currentTarget));
          const response = await fetch("/api/member-auth", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              ...data,
              action: change ? "password" : "login",
            }),
          });
          const result = await readJsonResponse<{ error?: string; redirect: string }>(
            response,
          );
          if (!response.ok) {
            throw new Error(result.error || "Unable to complete the request.");
          }
          window.location.assign(result.redirect);
        } catch (e) {
          setError(e instanceof Error ? e.message : "Please try again.");
          setBusy(false);
        }
      }}
    >
      {fields.map(([name, label]) => {
        const isPassword = name !== "loginId";
        const isConfirm = name === "confirmPassword";
        const isNew = name === "password" && change;
        const showToggle = isPassword && (!change || name !== "currentPassword");
        const revealed = isConfirm ? showConfirm : showPassword;

        return (
          <label key={name} className="block text-[13px] font-medium text-slate-700">
            {label}
            <div className="relative mt-1.5">
              <input
                className="h-11 w-full rounded-[12px] border border-slate-200 bg-white px-3.5 pr-11 text-[14px] outline-none transition placeholder:text-slate-400 focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10"
                name={name}
                required
                type={isPassword ? (showToggle && revealed ? "text" : "password") : "text"}
                autoComplete={
                  name === "loginId"
                    ? "username"
                    : change && name !== "currentPassword"
                      ? "new-password"
                      : "current-password"
                }
                maxLength={128}
                minLength={change && name !== "currentPassword" ? 12 : 1}
                onChange={
                  isNew ? e => setNewPassword(e.target.value) : undefined
                }
              />
              {showToggle && (
                <button
                  type="button"
                  onClick={() =>
                    isConfirm
                      ? setShowConfirm(v => !v)
                      : setShowPassword(v => !v)
                  }
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 transition hover:text-slate-600"
                  aria-label={revealed ? "Hide password" : "Show password"}
                >
                  {revealed ? (
                    <EyeOff className="size-4" />
                  ) : (
                    <Eye className="size-4" />
                  )}
                </button>
              )}
            </div>
            {isNew && <PasswordStrengthMeter password={newPassword} />}
          </label>
        );
      })}

      {error && (
        <div
          role="alert"
          className="rounded-[12px] border border-rose-200 bg-rose-50 px-3.5 py-3 text-[13px] font-medium text-rose-700"
        >
          {error}
        </div>
      )}

      <button
        disabled={busy}
        className={`flex h-11 items-center justify-center gap-2 rounded-[12px] bg-[#15388c] px-5 text-[13px] font-semibold text-white transition hover:bg-[#102d74] disabled:opacity-50 ${
          change ? "w-full sm:w-auto sm:min-w-[180px]" : "h-12 w-full shadow-lg shadow-[#15388c]/20 hover:bg-[#1d46a8] hover:shadow-xl"
        }`}
      >
        {busy && <Loader2 className="size-4 animate-spin" />}
        {busy ? "Please wait…" : change ? "Change password" : "Log in"}
      </button>

      <p className="text-[12px] leading-5 text-slate-500">
        {change
          ? "Use 12–128 characters. Your current session will remain active."
          : "Forgot your ID or password? Contact your administrator for new temporary credentials."}
      </p>
    </form>
  );
}
