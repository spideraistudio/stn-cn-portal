# Final UX Phase 5 local-PC package — 25 October 2026

All five UX phases are implemented. Start with START_HERE_WINDOWS.md, PHASE5_RELEASE_HANDOFF.md and TEST_RESULTS.md. Final Windows installation ZIP includes full source and setup scripts; it is not a standalone EXE. Native Windows acceptance and the actual affected Phase 3 billing PDF remain pending. No deployment or live migration.

# UX Phase 4 cumulative SOURCE — 24 October 2026

Category-first Ledger Audit with pending/reviewed counts, expandable party findings and separate collapsed reviewed items is implemented. CN/NRV remains available below the categories; billing checks remain independent. Read PHASE4_AUDIT_HANDOFF.md and TEST_RESULTS.md. Next: NEW_CHAT_PHASE5.txt. Browser visual and Windows acceptance remain pending. Final installation ZIP follows Phase 5; no deployment.

# Current delivery: UX Phase 3 cumulative SOURCE

Read PHASE3_BILLING_HANDOFF.md, TEST_RESULTS.md and NEW_CHAT_PHASE4.txt. This is not the final installation release. Windows acceptance and the actual reported billing PDF remain pending. Final installation ZIP follows UX Phase 5; no deployment is authorised.

# UX Phase 2 source handoff — 24 October 2026

Visible permission-scoped password reset actions and a viewport-contained signup approval dialog are implemented. Read `PHASE2_ADMIN_HANDOFF.md` and `UX_PHASE_PLAN.md`. Fresh evidence: `verification/ux_phase2_*`. Linux HTTP, production build and real Mongo/Chromium combined journey passed. Windows acceptance remains pending. Cumulative source only; final installation ZIP after all five UX phases. Next: `NEW_CHAT_PHASE3.txt`.

# UX Phase 1 source handoff — 24 October 2026

Shared Account & Settings and direct CN entry are implemented. Read `PHASE1_WORKFLOW_HANDOFF.md` and `UX_PHASE_PLAN.md` first. Fresh evidence: `verification/ux_phase1_*`. Linux checks passed; Windows acceptance remains pending. This is a development handoff; final installation delivery is after all five usability phases. Next chat: `NEW_CHAT_PHASE2.txt`.

# Latest update — staff storage ceiling — 24 October 2026

Read `STAFF_STORAGE_LIMIT_UPDATE.md` first. Staff create/edit forms in STN and the Account console now display the authenticated delegated ceiling and block above-limit values. Server enforcement and private CN ownership are unchanged. New evidence: `verification/storage_*.txt`. Fresh Linux HTTP/browser/build checks passed; Windows acceptance of this update remains pending. User reports successful Windows account creation with the preceding unified update.

# Latest update: unified account approval

Read UNIFIED_APPROVAL_UPDATE.md for the new one-form signup approval, staff module grants and backend Edit access. The separate creation/linking instructions below describe the earlier release and remain advanced compatibility tools. Use the new request form for normal signup approvals.

# STN + All Crop CN — local integration candidate

This is a complete source/local-test package. It has **not** been publicly deployed or accepted on Windows. Start with this file, then PHASE_HANDOFF.md. The original calculator documentation remains in `cn/`.

## Sources and protection

- STN: `spideraistudio/sellers-trust`, Meet-Dev commit `491d892e5b5b507e87e18393babb0d0ada387607`.
- All 284 retrieved files were verified against their GitHub blob hashes before integration edits.
- CN: supplied `CN_Web_Phase7_2_1_Audit_Mapping.zip`. The preserved Update35.2 files remain byte-identical (140 hash checks).
- Independent remote branch: `integration/stn-cn-2026-10-23`, created from Meet-Dev. The development code is in this package/local integration commit. No changes were pushed to Meet-Dev or the live site.
- Source configuration is MongoDB, including binary `file_objects`; it is not a MariaDB application. `db/schema.ts` is a legacy SQLite/Drizzle description, not the runtime database. The actual live deployment/commit was not accessed or inferred.

## First local Windows setup

Use a NEW folder and NEW local test data. Do not extract over either existing application.

1. Install Node.js 22.17+ (Node 24 recommended) and Python 3.10+ (available as `node`, `npm`, `python`).
2. Run `Setup_Combined_Windows.bat`. Internet is needed for npm, the PDF reader and the Playwright test browser. This installs from the included lockfile. It does not create accounts or touch live data.
3. Run `Start_Local_Mongo_Windows.bat` and leave that window open. It downloads MongoDB 7.0.24 on first use and starts it on **127.0.0.1:27017**. Local test records persist in `integration-data/mongo`. Alternatively, use your own local MongoDB service on that port. Do not run both at once.
4. Run `Setup_Combined_Admin_Windows.bat` ONCE. Choose your individual platform-superadmin username/password. No default real account/password is included.
5. Run `Start_Combined_Windows.bat`, leave it open, then open **http://127.0.0.1:8787/portal**. Sign in and choose CN Calculator or Seller Trust Network.
6. Keep both server windows open during use. Stop the application first and MongoDB second with Ctrl+C. Restart in the same order and use the same folder/data.

Ports: gateway 8787, private identity 8788, Next.js 3000, MongoDB 27017. If needed, run `python integration/run_local.py --port 8797 --identity-port 8798 --node-port 3010`. Always use the displayed **127.0.0.1** URL, not localhost. The launcher deliberately refuses non-loopback MongoDB and database names without the `integration_` prefix. This package is local-only; the WSGI gateway and development server are not a production hosting setup.

Linux/macOS equivalent: `npm ci --ignore-scripts`, `python3 -m pip install -r cn/offline_baseline/requirements.txt`, `npm run integration:mongo` in one terminal, then `python3 integration/run_local.py --setup-admin` once and `python3 integration/run_local.py` in another. Browser checks on Linux use the included test Chromium package.

## Set up companies and people

1. Platform superadmin: open STN dashboard → **CN & company management**, or `/portal/manage`. Create a company, choose CN-only/STN-only/both and optional subscription dates. Dates are interpreted in the browser's local time. Expiry is exclusive. No billing/payment processing was added.
2. Open **Users, quotas & password resets** (`/account`). Create the company's **Admin** and grant financial permissions, user-management rights, own allowance, maximum users and per-user allowance ceiling.
3. Return to company management. Assign that admin to its company BEFORE creating its users. Enable CN/STN independently. Admin defaults remain **1024 MiB own storage**, **five users**, **250 MiB per user**. Only superadmin changes those delegated limits.
4. Company admins create/manage/reset only their own users. Their users inherit the company, retain private CN ownership and have STN off until explicitly enabled. Disabled users still count towards the five-user limit. Create-user defaults and company-membership insertion are one transaction.
5. STN membership is separate: approve the company's existing STN application in the existing platform dashboard. Approval does not create a second password. Copy its exact STN member ID into an individual account's explicit link field. Lookup displays the company/status and the server verifies existence again on save. Existing IDs can also be obtained from the STN admin member-detail URL. The same company STN membership may be explicitly granted to its staff by their company admin; each staff member still uses an individual login and private CN workspace. A member ID cannot be linked across different companies. The company admin can grant only its own explicitly linked membership.
6. Users first sign in with a temporary password, change it in Account, then sign in with their own password. Shared session/module switches require no second login. Both modules' password changes and logout use Account/common controls.

Company admins do not gain STN platform powers. They cannot approve members, approve seller reports, modify another company or read anyone else's CN data. Company/module changes revoke affected sessions. Every financial operation rechecks CN permission and company entitlement; every STN member/admin action revalidates the central session and existing STN membership/category policy. Disabled/expired entitlements block both reads and writes to that module. Account management/recovery remains available. Re-enabling never restores a revoked session.

## Data and storage

CN remains individual-owned: company membership and platform administration do not open another person's workbooks, schemes, mappings, PDFs, allocations or frozen history. STN retains existing sharing, member/category/approval and quotation/contact rules. Both are physically stored on the local server in this setup; quotas are logical account allowances.

CN usage/allowances use the existing transactional accounting, concurrent-write reservations and protected temporary cleanup. STN storage is shown separately under common management and `/api/portal-stn/storage`: retained BSON document/file-body bytes, excluding indexes, journal and backups. No STN quota has been invented. No STN bytes are deducted from CN allowances. The platform view covers the installation; a member sees attributed own-member records/evidence. Network/shared and orphan data is included in the platform total rather than assigned to someone's CN quota.

Cleanup remains limited to registered inactive/unlinked/unprotected temporary CN blobs older than 60 days. Saved PDFs, workbook data, allocations and frozen history are protected. STN's existing explicit governance/cleanup actions retain their original policies; no new STN age-based cleanup was added.

## Existing-account migration rehearsal

Do not point this test launcher at live data. Stop and back up the current CN web application. Make a separate copy of the ENTIRE CN WEB data directory (including `accounts.sqlite3` and workspace directories). Use that COPY with `python integration/run_local.py --data C:\Test\CN_Copy`. Do not bootstrap a new admin for an existing copy. Existing CN IDs, credentials, quotas and work survive; the prior operator remains superadmin. Legacy accounts stay unassigned until explicitly mapped.

`python integration/migration_inventory.py --cn-copy C:\Test\CN_Copy` prints a read-only ID/role/quota inventory without password hashes or workbook contents. Rehearse STN only with an explicitly exported/sanitized local database restored under an `integration_` name. There is no automatic import from the live database, and no merging by company name, GST or email. Assign exact IDs deliberately. Moving a user between managing admins/companies retains private CN work but clears its previous company's STN link and disables STN until explicitly relinked.

Back up the stopped `integration-data` tree, including `portal-secrets.json`: it contains the private bridge secret and the STN identifier-lookup key. Protect it like a password file. If using an external local Mongo service, back up its integration database separately too. A real STN migration must preserve its original identifier-lookup key; the newly generated local key cannot search hashes made using a different key. The disposable tests prove service restart and record interchange, not restoration of your production backups. No live migration is included or authorized.

## Run verification

From this package folder:

```
python -m unittest discover -s cn/tests -p "test_*.py"
python integration/test_portal.py
python integration/run_cn_integrated_tests.py
npm run test:seed
python integration/full_stack_test.py
python integration/browser_cn.py
```

For `full_stack_test.py`, first STOP the manually started local Mongo window and the combined application: the test launches a disposable Mongo process on 27017 and its own temporary CN account directory/database. It uses only synthetic credentials and data. It never touches `integration-data`. Do not interrupt an actual working session to run it without saving first. Tests with Playwright on Windows need the installed test Chromium from Setup. These are automated checks, not Windows user acceptance.

`TEST_RESULTS.md` lists the actual executed checks, evidence files and remaining acceptance work. Earlier `cn/verification` files belong to the supplied baseline; NEW integration evidence is only under root `verification/`.
