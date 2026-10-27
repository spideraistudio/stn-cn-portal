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

# Final UX Phase 5 local-PC package — 25 October 2026

All five UX phases are implemented. Start with START_HERE_WINDOWS.md, PHASE5_RELEASE_HANDOFF.md and TEST_RESULTS.md. Final Windows installation ZIP includes full source and setup scripts; it is not a standalone EXE. Native Windows acceptance and the actual affected Phase 3 billing PDF remain pending. No deployment or live migration.

# UX Phase 4 cumulative SOURCE — 24 October 2026

Category-first Ledger Audit with pending/reviewed counts, expandable party findings and separate collapsed reviewed items is implemented. CN/NRV remains available below the categories; billing checks remain independent. Read PHASE4_AUDIT_HANDOFF.md and TEST_RESULTS.md. Next: NEW_CHAT_PHASE5.txt. Browser visual and Windows acceptance remain pending. Final installation ZIP follows Phase 5; no deployment.

# UX Phase 3 source handoff — 24 October 2026

Explicit approved-rate unit selection fixes a reproduced multi-kg packet mismatch path. Recorded-state selection, rate/packing comparison trace and save/recheck status are implemented. Read PHASE3_BILLING_HANDOFF.md for the full diagnosis and limits. Actual affected user PDF and Windows acceptance remain pending. Fresh evidence: verification/ux_phase3_*. Cumulative SOURCE only; next: NEW_CHAT_PHASE4.txt. Final installation after Phase 5.

# UX Phase 2 source handoff — 24 October 2026

Visible permission-scoped password reset actions and a viewport-contained signup approval dialog are implemented. Read `PHASE2_ADMIN_HANDOFF.md` and `UX_PHASE_PLAN.md`. Fresh evidence: `verification/ux_phase2_*`. Linux HTTP, production build and real Mongo/Chromium combined journey passed. Windows acceptance remains pending. Cumulative source only; final installation ZIP after all five UX phases. Next: `NEW_CHAT_PHASE3.txt`.

# UX Phase 1 source handoff — 24 October 2026

Shared Account & Settings and direct CN entry are implemented. Read `PHASE1_WORKFLOW_HANDOFF.md` and `UX_PHASE_PLAN.md` first. Fresh evidence: `verification/ux_phase1_*`. Linux checks passed; Windows acceptance remains pending. This is a development handoff; final installation delivery is after all five usability phases. Next chat: `NEW_CHAT_PHASE2.txt`.

# Latest handoff — staff storage ceiling — 24 October 2026

Read `STAFF_STORAGE_LIMIT_UPDATE.md` first. Staff create/edit forms in STN and the Account console now display the authenticated delegated ceiling and block above-limit values. Server enforcement and private CN ownership are unchanged. New evidence: `verification/storage_*.txt`. Fresh Linux HTTP/browser/build checks passed; Windows acceptance of this update remains pending. User reports successful Windows account creation with the preceding unified update.

# Unified signup approval — 24 October 2026

Apply STN_CN_Unified_Accounts_Update.zip; read UNIFIED_APPROVAL_UPDATE.md. Existing STN request pages now combine company/admin creation, credentials, module grants, CN permissions, storage/seat limits and subscription terms. Staff creation and existing-user access/reset are available within the backend. SQLite preparation is atomic; Mongo approval uses a disabled, idempotent reservation before activation. No name/GST/email matching, account overwrites or financial engine changes. The default local launcher builds/reuses the production frontend, with the local shared-session cookie explicitly configured. The Next request now receives the nonce CSP needed for hydration; the browser policy remains strict. New evidence: verification/unified_*. Actual Windows checks remain pending. The prior Windows Mongo fix is cumulative.

# Windows startup fix — 24 October 2026

The user reported STN stuck while CN opens. Windows screenshots show MongoDB exit code 2 and STN connection refusal on 127.0.0.1:27017. The launcher incorrectly passed the Unix-only --nounixsocket option on Windows. It now builds platform-appropriate arguments, pins port 27017 (disables silent port generation), preserves persistent data and records startup errors. Apply the small STN_CN_Windows_Mongo_Fix.zip overlay; see WINDOWS_MONGO_FIX.md. Platform-argument tests and actual Linux Mongo restart/data-retention checks pass; Windows retest remains pending. New evidence is verification/windows_mongo_*. No engine, schema, user account, live branch or live database changes.

# Combined STN + All Crop CN — integration candidate

23 October 2026. Read `INTEGRATION_README.md`, `PHASE_PLAN.md` and `TEST_RESULTS.md` first. CN's entire supplied handoff remains at `cn/PHASE_HANDOFF.md`; its original phase-plan, README and requested security/audit/proposal documents remain in `cn/`.

## Completed local implementation

- Independent source copy of Meet-Dev commit `491d892e5b5b507e87e18393babb0d0ada387607`. All 284 source files verified against GitHub blob hashes before edits. New remote branch `integration/stn-cn-2026-10-23` was created at that source. Integration changes are in the local package and local commit/patch; the remote integration branch remains at its baseline unless separately pushed. Original Meet-Dev and live application are unchanged.
- Source uses Next.js 16.3.3, Node and MongoDB (`lib/sql-mongo.ts`, `lib/runtime-env.ts`). SQL-looking queries are translated to MongoDB; binary uploads live in `file_objects`. Legacy Drizzle schema is not a MariaDB configuration. Existing source's sequential, nontransactional Mongo batches are preserved; new company/account limits use the existing transactional SQLite authority instead. Invalid-certificate TLS bypass was removed; local tests explicitly disable TLS only for loopback Mongo.
- The Python CN account/session service is the common authority. `PortalAccounts` extends it with company/entitlement/link records without moving financial data. One opaque HttpOnly cookie serves the portal and both modules. STN validates it through the secret-authenticated loopback identity listener on every request. No passwords or tokens enter URLs, browser identity headers are not trusted, legacy STN session cookies are ignored in combined mode and credential endpoints cannot bypass the common login.
- A same-origin local gateway serves CN's unchanged paths and forwards STN paths. Exact path boundaries avoid `/api/me` capturing `/api/member…`. Unsafe methods require the exact configured origin. Private identity routes are unavailable through the gateway; the separate listener rejects other routes. Introspection fails closed when unavailable and is uncached.
- Common portal: two module choices, module switchers, shared logout and forced temporary-password change. STN's existing administrator dashboard/sidebar links to common CN/company management. `/account` retains the accepted CN account/permission/quota UI. Company admins never receive platform STN approval, review or governance authority.
- Company module plans/dates, per-user module switches, explicit STN member-ID lookup/validation, scoped session revocation and password reset. Company changes revoke sessions; module entitlement is also rechecked live. Password changes/reset revoke both modules. No payment processing.
- Existing defaults preserved: admin 1024 MiB own allowance, five assigned-user slots, user 250 MiB allowance/default/ceiling; superadmin controls them. Financial grants remain intersected with managing-admin grants. Membership insertion and account/slot creation are atomic. Company reassignment is explicit; a cross-company managing-admin reassignment clears the former STN link. CN ownership/history remains with the person.
- CN Update35.2 engine and all 140 baseline files are unchanged. The actual five-step screens, saved parties/mappings, optional segment workflow, both themes, diagrams, CD card attribution, dragging, left-drag panning, cursor zoom, layouts, dates, ABS/CD/IPT, late Kharif, April–March Year Link, frozen history/reports, Billing Rate Audit and direct audit mapping remain.
- CN storage/transaction reservations and protected 60-day temporary cleanup remain. STN retained BSON/file usage is separately reported; zero STN bytes are charged to CN allowances. STN quota is currently unconfigured rather than assigned an invented limit.

## Main changed/new areas

`cn/backend/cn_web/portal.py`, `portal_http.py`, `portal_static/` contain company policy and common UI. `accounts.py` has two transaction hooks for creation/reassignment. Calculator `web-session.js` adds the module-switch link; account login returns to module choice. No engine rewrite or replacement calculator pages.

`lib/portal-session.ts`, `lib/member-session.ts`, `app/chatgpt-auth.ts` adapt STN authentication. Original member approval/category checks remain. STN membership approval no longer creates another password in combined mode; login/reset/password pages route to common Account. Account-deletion password verification checks the central password. Seed APIs use the exact shared-origin validator. `app/api/portal-stn/` provides separated storage and explicit member lookup.

`integration/run_local.py` is a local-only gateway/launcher. `integration/mongo_local.mjs` starts persistent loopback test MongoDB; the full-stack test uses disposable data instead. `integration/migration_inventory.py` is a read-only inventory for an explicitly supplied CN data copy. No live import, name/email/GST matching or automatic account merge exists.

## Verification and acceptance

See `TEST_RESULTS.md` for fresh evidence. Unit/API suites and Linux Chromium are not Windows acceptance. New 7.2/7.2.1 audit additions remain Windows-pending. No user acceptance is inferred from inherited verification files.

The combined journey uses real Node/Next.js, real local MongoDB 7.0.24 and Python/SQLite. It exercises shared login, forced change, legacy-cookie denial, platform/company separation, explicit link existence checking, seed trading/contact exchange, seller reporting/approval/search, full source-PDF-to-frozen-report flow, exact ₹38,561 arithmetic parity, independent export/import, private data boundaries, separate accounting, module disable/re-enable, password reset, logout and actual service restart. All data/credentials are synthetic and disposed.

## Important boundaries before the next phase

1. Obtain Windows acceptance with `WINDOWS_ACCEPTANCE.md`; keep CN's earlier acceptance record intact.
2. Rehearse with separate stopped copies of the user's actual CN data and an explicitly restored/sanitized STN database. The tests cover the old CN hierarchy and independent interchange, but actual legacy STN credential/account migration is not claimed complete. Do not create a second superadmin for copied existing CN data.
3. A company admin may explicitly grant its linked STN membership to its own staff. Every person retains individual credentials and a private CN workspace. The same STN member ID cannot cross company boundaries, and one company cannot silently switch to another STN membership. Central access audit records the acting admin/target identity and exact member ID; STN business records keep their original member-scoped ownership/sharing. This is an explicit permission grant, not account or record merging.
4. Retain the real STN identifier lookup key during any future database migration. The local fresh key is only for local fresh/synthetic data. Back up stopped CN data, MongoDB and portal secret/key material together and demonstrate restore before cutover. Tests prove service restart/interchange, not production backup recovery.
5. Existing STN nontransactional batches and the general SQL-to-Mongo emulator are inherited source behavior. Test production concurrency/transactional requirements separately before public rollout. This candidate's account/quotas do not rely on those batches.
6. The local dev gateway is not a public server. TLS, trusted proxy hardening, production workers/restart supervision, backup operations, database sizing, load testing and a real deployment migration remain a future approved staging phase.

No purchase, public deployment, live database migration or modification of the original source branch was performed.
