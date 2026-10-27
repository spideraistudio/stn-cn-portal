# UX Phase 1 — shared navigation and direct CN entry

24 October 2026. Development/source handoff, not the final installation release.
Baseline: STN_CN_Staff_Storage_Limit_Update.zip. This package contains complete cumulative source. User requested one phase per chat and a final installation ZIP after all five UX phases. Phase 1 implementation and the checks below are complete; Windows acceptance is pending. Continue with Phase 2 using NEW_CHAT_PHASE2.txt.

## Delivered

- `/account` is now **Account & Settings**, with Users & Permissions, Account & Security, Help & Contact, and About & Policies. Existing personal security, scoped management, quotas, resets and audit remain available. The management group is hidden for staff and admins without user-management rights; the shared users page verifies role/management rights server-side as well.
- `/settings/users` reuses unified staff creation/access editing for company admins and platform superadmin. It works for CN-only company admins without requiring STN membership. The existing server permission/ceiling enforcement is unchanged.
- Combined STN navigation removes Company users, Account & security, Report a problem, About, Contact and legal links from its primary sidebar. The existing header exposes Account & Settings. Old member bookmarks redirect to the shared destinations through the local gateway. Original standalone STN navigation remains conditional on combined mode.
- `/settings/issues` relocates the existing approved-STN-member issue form/history. Its existing membership/category gates and storage remain unchanged. CN-only users and platform admins without member identity get the existing support-email composer with explicit wording that they must send it in their email application. No common issue database or new notification flow was introduced. The inherited issue form now captures the form element before its asynchronous request so a successful submission can reset reliably.
- Membership closure remains gated by the original approved-member flow at `/settings/closure`. Shared password/session security remains at `/account`. No closure policy was changed.
- Public `/about`, `/contact`, `/privacy`, `/terms` and `/disclaimer` remain accessible before login and now include a shared portal/settings return bar. Existing policy wording is retained; legal text was not rewritten to invent CN-specific terms.
- Selecting CN opens `/calculator`. A first-time user sees an empty dashboard with one first-workbook form (name/state/season/start/end/cutoff). The backend creates the private project/workbook/period in one transaction and enforces existing CN permissions, quota accounting and ownership. Failed validation rolls everything back. Required temporary-password change still precedes this journey.
- Returning users restore a valid saved workbook/project selection, or fall back to their own available workbook when browser selection is stale. `/workspace` now redirects to `/calculator` in combined mode; the old raw project/JSON editor is absent from the normal flow. Existing Workbooks, Parties, Settings, import/export and project selection remain in the calculator.
- Calculator footer links point to Account & Settings. Its header shows workbook/project, working season and financial year derived from the season start. Both Classic Emerald and Navy Studio remain usable.

## Fresh verification on Linux

Evidence is `verification/ux_phase1_*`; earlier verification files remain historical.

- Two focused HTTP tests: first workbook creation, dates, atomic rollback, private owner scope, foreign-project rejection, missing-permission rejection, settings links and legacy workspace redirect.
- Existing portal/account regression: 24 tests passed.
- Existing delegated staff storage-ceiling regression passed.
- TypeScript passed; changed-file ESLint passed. One inherited drawer effect has a local lint explanation to preserve its intentional close-on-navigation behaviour.
- Optimized production Next build passed with combined-portal UI enabled.
- All 140 protected Update35.2 files match the baseline.
- Real Linux Chromium through actual Python gateway/SQLite, private identity listener and production Next server: fresh login → CN → first workbook → dashboard; reload returns to the same saved workbook; both themes; season/FY context; `/workspace` redirect; CN-only admin creates a staff account in shared settings; problem-report email fallback; old STN redirects; staff forced password change and denial from user management; public policy/contact pages without login; no uncaught page errors.

The focused browser journey uses only disposable synthetic CN accounts. It does not use a Mongo database and does not re-certify approved-member issue submission/closure, the full STN trading journey, native Windows printing, or the user's own PDFs. Their existing routes/policies remain in place. A prior browser harness check mistakenly waited on a Mongo-dependent health route; the final check waits on the gateway health endpoint. The first-workbook empty screen initially used a renderer that expected an existing workbook; this was fixed and the final complete journey passed.

Reproduce (after dependency setup and production build):

```
python integration/test_ux_phase1.py
python integration/test_portal.py
python integration/test_storage_ceiling.py
python cn/verify_baseline.py
npx tsc --noEmit
```

Linux browser: `python integration/run_ux_phase1_browser.py`, with `CN_BROWSER_EXECUTABLE` pointing to an installed Chromium if needed. This environment required extracting the bundled Chromium without applying archive ownership. The harness uses a separate temporary account directory and closes its own services. Its build fingerprint assumes the current production build is already built with `NEXT_PUBLIC_COMMON_PORTAL=1`.

## Windows checklist — pending until final user testing

- New user changes temporary password, selects CN, creates the first workbook in the calculator dashboard, then reopens the same workbook after logout/restart.
- Existing users retain their workbooks, source PDFs, mappings, schemes, calculations and saved layouts; both themes work.
- Account & Settings is reachable from both modules; moved pages and old bookmarks work; staff cannot access Company Users.
- CN-only company admin creates/manages only their own staff with the granted ceiling; account reset rights remain scoped.
- Approved STN member reports a problem and reopens its existing report history from shared settings; the original membership-closure flow remains accessible. CN-only report page clearly prepares an email.
- Contact/policies remain public and provide a return link. Check actual Windows window sizing after Phase 2 and visual consistency after Phase 5.

## Remaining agreed phases

2. Visible user/admin password-reset actions in STN administration and responsive signup approval form.
3. Reproduce/fix billing-rate variation issue; recorded-state chooser with new-state entry; explicit save/recheck behaviour. Preserve original-bill return comparison.
4. Category-first ledger audit with counts and expandable findings/reviewed items.
5. Consistent visual styles across portal/STN/CN using accepted Emerald/Navy themes; complete workflow regression and final installation ZIP.

No public deployment, live database migration, automatic account matching, original Meet-Dev modification, data migration or financial-engine change was performed. CN data stays individually owned, including against company-admin access. CN/STN storage accounting stays separate.
