# Latest: clean new-profile repository preparation — 27 October 2026

Read CLEAN_START_HANDOFF.md and README.md first. New profiles and blank workbooks now start without catalogue or schemes; existing saved payloads are preserved. Demo-party buttons are removed. Prepared for a separate private stn-cn-portal repository; remote publication and Windows acceptance remain pending. No deployment, live migration or original Meet-Dev changes. Unknown-packet-weight schemes remain pending. Earlier notes are historical.

# Latest: multi-company statement import — 26 October 2026

Read MULTI_COMPANY_STATEMENT_HANDOFF.md first. Added and verified Avani, Remik and Dhanwel statement layouts. Remik MILKY WHITE quantities and Dhanwel KDS-726 quantities/rates use the user's packet confirmations. Missing units/pack weights and unprinted or mismatched invoice amounts still require review; unresolved details block finalisation. Public visitor UI, registration/approval, all five UX phases and previous case-number/billing precision fixes remain cumulative. No deployment, live migration or original Meet-Dev changes. Windows acceptance of the public UI and new importer remains pending. Earlier records below are historical.

# Latest: public visitor website and registration — 26 October 2026

Read PUBLIC_VISITOR_UI_HANDOFF.md first. The previous case-number/rate-precision update was accepted by the user on Windows. This cumulative update modernises the visitor homepage, company application, pending-success guidance and login in both themes, while preserving administrator approval and credentials/permissions. New public UI Windows acceptance remains pending. No deployment, live migration or original Meet-Dev changes. Earlier notes below are historical.

# Latest: case numbers and billing-rate precision — 26 October 2026

Read CASE_NUMBERS_RATE_PRECISION_HANDOFF.md first. Temporary/permanent STN case references and server-owned history are implemented through the existing review flow. The 475 g / 901 conversion false flag is reproduced and corrected, including verification against the supplied Amreli PDF with test mappings. Existing saved-workbook configuration has not been supplied; native Windows acceptance remains pending. All previous UI/search and five UX phases remain cumulative. Earlier records below are historical.

# Latest: STN search layout, scrolling and theme correction — 25 October 2026

Read STN_SEARCH_LAYOUT_HANDOFF.md first. The accepted large GSTIN search panel is first on the dashboard and shared with Search sellers; Seed marketplace remains on Buy/Sell Requirements. Theme contrast and nested search scrolling are corrected. Includes the cumulative billing fixes and all five UX phases. Native Windows acceptance remains pending. Earlier records below are historical.

# Latest: STN reference design and search — 25 October 2026

Read STN_REFERENCE_DESIGN_HANDOFF.md first. Dashboard/design, search and component-browser validation are complete. Includes all earlier billing fixes and five UX phases. Windows acceptance and the actual reported billing PDF verification remain pending. Earlier evidence below is historical.

# STN UI and quotation form update — 25 October 2026

Read STN_UI_HANDOFF.md first. This cumulative update includes the billing audit fix and all five UX phases. Windows visual/interaction acceptance remains pending.

# Billing Rate Audit correction — 25 October 2026

Cumulative from the intact STN_CN_UX5_Windows_Installation.zip supplied in this chat. Supersedes both earlier Billing_Audit_Fix_*_Candidate.zip packages. The source-integrity limitation is resolved: all 755 intact files from the earlier partial upload match this complete archive. The authoritative current proxy.ts and all five UX phases are preserved. No history-restored runtime files are used.

Start with BILLING_RATE_FIX_HANDOFF.md and START_HERE_WINDOWS.md. Native Windows acceptance and verification with the actual affected ledger PDF/workbook remain pending. That PDF was not supplied. No deployment, live migration or original Meet-Dev changes.

# STN + All Crop CN — Windows installation

UX phases 1–5 cumulative package · 25 October 2026

This ZIP contains the complete application source and Windows setup/launch scripts. It is not a standalone EXE and does not contain Node.js, Python, node_modules, a prebuilt Next app, MongoDB binaries, passwords or user databases. Internet is required for first setup and the first MongoDB download. After installation, use your normal Windows browser at http://127.0.0.1:8787/portal.

## Existing installation — preserve your work first

1. Stop the combined app and MongoDB consoles cleanly (Ctrl+C). Make a separate backup of the COMPLETE existing `integration-data` folder, including `cn`, `mongo` and `portal-secrets.json`. Keep the old application folder unchanged as a rollback copy.
2. Extract this ZIP into a new folder, for example `C:\STN_CN_UX5`. Do not run from inside the ZIP.
3. For the default previous setup, copy the complete STOPPED `integration-data` folder into the new folder. Copy it, do not move it or merge selected database files. This retains existing accounts, per-person work, STN records and secret/lookup keys together. Do not copy old `node_modules` or `.next`.
4. If you used custom data locations, environment variables, a different Mongo database or an external Mongo service, retain that configuration and use those same paths. Do not point the new package at a partial copy or create a fresh admin over existing data. This package performs no automatic legacy account/database migration.
5. Run `Setup_Combined_Windows.bat`. Keep the console open and read any error. Then follow Daily startup below. **Do not run Setup_Combined_Admin_Windows.bat for existing accounts.** Log in with your existing credentials.

## Fresh installation only

1. Install 64-bit Node.js 22.17+ within 22.x, or Node.js 24+, including npm. Install Python 3.10 or newer with Add Python to PATH. Reopen the terminal after installation.
2. Extract the ZIP into a writable folder outside Program Files. Double-click `Setup_Combined_Windows.bat`. It checks prerequisites, installs the locked Node packages and Python PDF dependency, and builds the combined frontend. Allow it to finish. A failure is not a completed installation.
3. Double-click `Setup_Combined_Admin_Windows.bat` ONCE and choose the platform administrator username/password. Retain them privately. No default credentials are supplied.
4. Follow Daily startup.

## Daily startup

1. Open `Start_Local_Mongo_Windows.bat`. Wait for “MongoDB ready on 127.0.0.1:27017”. First start downloads MongoDB 7.0.24 and can take longer. Leave this console running.
2. Open `Start_Combined_Windows.bat`. Wait for the local gateway/Next server to be ready. It may rebuild the frontend on the first launch after a source change. Leave this console running.
3. Open http://127.0.0.1:8787/portal. Sign in and choose CN Calculator or Seller Trust Network. New temporary-password users must change their password first.
4. To stop, press Ctrl+C in the combined-app console and then the MongoDB console. Saved data remains in `integration-data`.

This is the local PC edition. It deliberately refuses non-loopback MongoDB and non-test-prefixed database names. Do not expose these local development services publicly. No hosting or deployment is included.

## Appearance and the five usability phases

Appearance is available in the portal, Account & Settings, STN and CN. Choose Classic Emerald or Navy Studio. The selection is browser-local and follows navigation on the same local address. CN's direct appearance selector also retains its existing saved preference. This setting never edits financial settings or permissions. Use the same address consistently; localhost and 127.0.0.1 have separate browser storage.

- Shared Account & Settings, direct CN dashboard and first-workbook creation.
- Visible permission-scoped password resets and contained signup approval dialog.
- Explicit billing-rate unit, recorded/new-state chooser, comparison trace and save/recheck status.
- Category-first audit, expandable party/finding evidence and collapsed reviewed findings. CN/NRV is below the categories; Billing Rate Audit remains separate.
- Shared Emerald/Navy appearance and combined regression checks.

## Acceptance on your Windows PC — still required

1. Confirm existing login, company permissions, private workbooks, mappings, schemes, allocations, original dates, frozen history and both themes.
2. Test new-user first workbook, signup approval at 100/125/150/200% zoom, and own-staff password reset. A reset must not alter permissions or work.
3. Test the actual PDF that produced the billing-rate complaint. Compare printed rate/unit, saved packing, approved period rate/unit and selected original bills. That real PDF was not supplied during development; the synthetic reproduced case does not certify it.
4. Run Ledger Checks, expand category → party → finding, mark Not Applicable, inspect its reason, reopen it, and export with sections collapsed. All findings must remain in the export.
5. Expand CN/NRV and map an unmapped product; save/recheck. Verify freight/journal exclusions. Run Billing Rate Audit independently.
6. Complete one known CN calculation and compare totals, separate rounding, original receipt dates, frozen reports, CSV and Windows print. Check STN seller search, report and approved seed trading as allowed by the account.

Linux automated, real Mongo/SQLite/Next/Chromium checks are recorded in TEST_RESULTS.md. They are not native Windows acceptance or certification of a live migration/backup restoration.

## If something fails

- “npm is not recognized”: install the required Node.js including npm, reopen the window and rerun setup.
- Python not found: enable Python on PATH; check Windows app-execution aliases if `python` opens the Store.
- STN does not open: check the Mongo console and `integration-data\mongo-startup.log`, then the combined-app console. Do not delete data or recreate accounts as a workaround.
- Port 27017, 3000, 8787 or 8788 already in use: stop the earlier app consoles before starting another copy.
- To roll back: stop both services and use the untouched old application plus its stopped backup data. Never run two app copies against the same data folder.

No source push, public deployment, live migration or modification to the original Meet-Dev branch was performed.
