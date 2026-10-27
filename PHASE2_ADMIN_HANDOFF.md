# UX Phase 2 — scoped reset actions and signup approval sizing

24 October 2026. Cumulative development source based on STN_CN_UX_Phase1_Source_Handoff.zip. Not the final installation release. Windows acceptance remains pending. Continue with NEW_CHAT_PHASE3.txt; do not deploy.

## Delivered

- Visible individual **Reset password** buttons in STN administration (`/admin/cn`) and shared company user management (`/settings/users`, also reused by the legacy member users component). Platform superadmin sees eligible company admins/staff; a managing company admin sees only their own staff. Self and platform-superadmin reset buttons are omitted; personal password change remains in Account & Security.
- Approved-member **Reset password** opens a list filtered by the exact existing `stn_member_id`. No company-name/email/GST guesses or automatic account links. Unlinked accounts show an explicit explanation and remain manageable by their exact login in Account & Settings.
- Each reset dialog identifies the target username, requires temporary-password confirmation, explains both-app sign-out/forced change, supports cancellation, and clears the password inputs after success/close. Passwords are not stored in component state or logged.
- Reset calls the existing common `/api/admin/users/{id}/reset-password` endpoint with the session CSRF token. Existing server scope, management-rights validation, password policy, audit event, forced temporary-password change, login-lockout clearing and session revocation are reused. Reset sends no grants, quota or account-enabled fields. Access editing is now a separate **Save access** operation.
- After new account creation the reset list refreshes without a page reload. STN company management additionally checks platform role on the server before rendering in combined mode.
- Pending-signup actions now open an accessible dialog instead of embedding the entire approval form in the narrow company-actions area. Width is capped at 48rem, height at viewport minus 2rem. Header and Close remain outside the scrolling body; the submit action is sticky inside that body. Fields use one/two responsive columns, minimum-width constraints and wrapping permissions/application options. Native required/min/max validation, delegated storage limits and the existing approval transaction/retry behavior are retained.
- The unified account form captures its form element before the asynchronous request and clears the submitted temporary password after success. Standalone STN legacy credential behavior is unchanged.

## Source changes

`components/unified-password-reset.tsx` (new), `unified-users-editor.tsx`, `unified-account-form.tsx`, `admin-credentials.tsx`, and `app/admin/cn/page.tsx`.

Tests: `integration/test_ux_phase2.py` (new) and expanded `integration/browser_combined.cjs`. The full-stack runner accepts `INTEGRATION_SERVER_LOG` to keep fresh evidence separate. No account backend, database schema, financial engine, calculator UI, saved data or storage-policy code changed.

## Verification

Fresh Phase 2 evidence is under `verification/ux_phase2_*`; earlier evidence is historical. TypeScript, changed-file ESLint, production build, 24 portal tests, focused reset test, storage-ceiling test, two Phase 1 tests and all 140 engine hashes passed. The real Mongo/SQLite/Next/Chromium combined journey passed, including actual approval, scoped resets, forced change, four effective viewport sizes and preserved ₹38,561 arithmetic/private ownership. See TEST_RESULTS.md for detailed executed results. Tests use disposable synthetic accounts/databases, never user data.

Reproduce after dependency setup:

```
python integration/test_ux_phase2.py
python integration/test_portal.py
python integration/test_storage_ceiling.py
python integration/test_ux_phase1.py
python cn/verify_baseline.py
npx tsc --noEmit
NEXT_PUBLIC_COMMON_PORTAL=1 npm run build
python integration/full_stack_test.py
```

The Linux browser harness supports `CN_BROWSER_EXECUTABLE` for a pre-extracted Chromium. This environment required extracting bundled Chromium/fonts without archive ownership changes. Initial browser startup attempts failed at environment extraction/executable handling; those are not application passes. Browser viewport checks represent effective CSS desktop sizes (including the reduced space produced by zoom), not native Windows zoom acceptance.

## Pending Windows acceptance

- Platform admin opens an approved company and resets its explicitly linked company-admin/staff login. Only that person is signed out; they must change the temporary password before using either app.
- Company admin resets their own staff; other company/admin users are absent and forged requests remain denied. An admin without management rights cannot reset staff.
- Cancel/mismatched passwords do not reset anything. Correct reset leaves account access, storage allowance, CN work and schemes unchanged.
- Open signup approval from company details at normal/maximized Windows desktop sizes and 100%, 125%, 150%, 200% browser zoom. Scroll inside the dialog; all fields, submission and Close are reachable without resizing the browser. Confirm real Windows keyboard/focus and native date controls.
- Retain all Phase 1 acceptance items and final full workflow acceptance in Phase 5. No public deployment or final installation release yet.
