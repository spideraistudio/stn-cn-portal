# Staff storage ceiling update — 24 October 2026

Apply `STN_CN_Staff_Storage_Limit_Update.zip` to the existing combined application's folder. This cumulative overlay includes the unified account update and Windows Mongo fix. No dependencies changed. It contains no accounts, credentials, databases, integration-data, or generated frontend build.

## Install on your Windows PC

1. Stop the combined application and MongoDB windows. Back up your existing application/data folder.
2. Extract this ZIP and copy its contents into the existing `STN_CN_Integration_Local` folder, replacing matching source files. Do not run administrator setup again.
3. Start `Start_Local_Mongo_Windows.bat`, then `Start_Combined_Windows.bat`. Let the automatic frontend rebuild finish.
4. Sign in using your existing account.

## Changed behavior

STN → Company Users now shows **Granted maximum: 250 MiB per staff user** (or the actual ceiling granted by the platform superadmin). Both creation and Edit existing user access enforce this maximum using browser number-field validation. Above-limit entries remain visible with an inline error so they can be corrected; the browser blocks submission. This includes pasted values such as 2560. The allowed creation default stays at 250 MiB or the lower ceiling, if granted less.

The CN Account & permissions console also displays and enforces the ceiling for creating and editing staff. It additionally checks the amount before sending a request. The maximum comes from the authenticated server account, not a hard-coded 250 MiB value. Platform superadmin forms retain their ability to grant higher limits. No saved allowance is changed automatically.

Server authorization remains unchanged and independently rejects grants above the company admin's ceiling. The admin's own 1024 MiB allowance is separate from the staff ceiling. Staff count limits, private CN workspaces, separate CN/STN accounting, STN approval/category policies and Update35.2 calculations are unchanged.

## Fresh verification

- Real HTTP: company-admin create and increase attempts at 251 and 2560 MiB rejected with 403; failed creation leaves no staff account and failed edits preserve the saved allowance. A valid 250 MiB grant succeeds. Company-admin attempts to edit their own delegation are denied. A platform-superadmin increase to 500 MiB allows a subsequent staff increase to 500 MiB.
- Isolated Linux Chromium: actual React create/edit components and original Account HTML/JS, using synthetic mocked API responses. Checked ceilings of 100, 250 and 500 MiB; maximum display, defaults, invalid 2560 MiB entries, blocked submissions and platform-superadmin exemption. This is targeted form verification, not another full MongoDB/STN journey.
- Four unified account tests and 24 existing portal/account regression tests passed.
- TypeScript, changed-component ESLint and optimized Next.js production build passed.
- All 140 preserved Update35.2 baseline files match.

Evidence: `verification/storage_*.txt`. Reproduce targeted checks with `python integration/test_storage_ceiling.py` and `node integration/browser_storage_ceiling.mjs` (Linux Chromium installed through existing dependencies; optional `CN_BROWSER_EXECUTABLE` selects an installed binary). Chromium was unpacked without archive ownership changes for this container, which rejects archive chown operations.

Full Windows acceptance is still pending. The user's successful account creation on Windows with the previous update is recorded separately; it does not accept this new form change. No public deployment, live data migration, account matching, live branch edit or financial engine change occurred.

## Windows checks for this update

- Company admin → STN → Company Users: see granted maximum, try 2560 MiB in creation and editing; saving is blocked with a clear correction message. Enter 250 MiB (or the granted maximum); saving succeeds.
- Repeat through Account & permissions. Reopen existing users and check their saved allowances and work are retained.
- Platform superadmin: raise a test company admin's ceiling, then reload that admin's page and confirm the new maximum appears. An already open form can show the prior ceiling until reloaded; the server always applies the current grant.
- Confirm module switching and existing CN work still open on your PC.
