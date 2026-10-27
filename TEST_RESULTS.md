# Latest: clean new-profile repository preparation — 27 October 2026

Read CLEAN_START_HANDOFF.md and README.md first. New profiles and blank workbooks now start without catalogue or schemes; existing saved payloads are preserved. Demo-party buttons are removed. Prepared for a separate private stn-cn-portal repository; remote publication and Windows acceptance remain pending. No deployment, live migration or original Meet-Dev changes. Unknown-packet-weight schemes remain pending. Earlier notes are historical.

# Latest: multi-company statement import — 26 October 2026

Read MULTI_COMPANY_STATEMENT_HANDOFF.md first. Added and verified Avani, Remik and Dhanwel statement layouts. Remik MILKY WHITE quantities and Dhanwel KDS-726 quantities/rates use the user's packet confirmations. Missing units/pack weights and unprinted or mismatched invoice amounts still require review; unresolved details block finalisation. Public visitor UI, registration/approval, all five UX phases and previous case-number/billing precision fixes remain cumulative. No deployment, live migration or original Meet-Dev changes. Windows acceptance of the public UI and new importer remains pending. Earlier records below are historical.

# Fresh public visitor and registration verification — 26 October 2026

See PUBLIC_VISITOR_UI_HANDOFF.md for scope, commands and limitations. Actual combined production/gateway Chromium checks passed both themes, readable text (tested contrast ≥4.5:1), viewport fit, keyboard/focus, fixed hover geometry, preserved values on failures and delayed double-submit prevention. A real public browser application was stored pending without credentials, duplicate submission left one record, actual administrator approval granted modules, and shared first login required password change. The full existing real-service STN/CN regression journey passed, including private ownership, financial fixture ₹38,561, case history, frozen work, account grants/revocation and restart.

TypeScript, targeted lint and production build passed. Twelve case/seed Node tests and 28 billing tests passed. Original financial suite: 332 run, 331 passed, one external-file-dependent skip. All 140 protected baseline files match. Records: verification/public_ui_*. Native Windows acceptance of this public UI remains pending. The user accepted the preceding update on their PC; older pending statements below refer to historical deliveries. No deployment/live migration or original Meet-Dev changes.

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

## Billing correction verification

The previous-turn logs verification/billing_fix_*.txt record 78 focused model/HTTP tests, 2 additional save/recheck HTTP tests, 332 financial tests (331 passed, one external-PDF skip), 24 portal tests, 1 storage test and 3 controller checks. Those exact fixed Python/JS bytes were transferred onto the intact cumulative source; protected baseline hashes still match. Fresh rebase checks: 16 targeted model/HTTP tests, all three controller scripts and all 140 baseline hashes passed. Evidence: verification/billing_fix_rebase_*.txt. Earlier Phase 5 build/browser/full-stack records below are inherited evidence, not fresh runs of this correction. No fresh Chromium, Next build or full Mongo/STN journey was executed for this correction.

# Fresh UX Phase 5 verification — 25 October 2026

All five UX phases are implemented. Fresh Linux evidence below supersedes earlier missing-browser notes. Native Windows acceptance, the actual affected Phase 3 PDF/workbook and live migration/backup rehearsal remain pending. Internal screenshots used synthetic data and are not packaged.

| Check | Executed result | Evidence |
|---|---|---|
| TypeScript / changed-file ESLint / production Next build | Passed; combined mode | ux_phase5_typecheck.txt, ux_phase5_lint.txt, ux_phase5_build.txt |
| Full disposable Mongo/SQLite/gateway/Next/Chromium journey | Passed: approval/reset sizing, shared login, cross-module themes, trading/report/search, source PDF workflow, exact ₹38,561 fixture, privacy/frozen history/interchange/accounting/revocation/restart/logout | ux_phase5_full_stack.txt, ux_phase5_full_stack_server.txt |
| Phase 4 real browser acceptance | Passed category/party/finding expansion, reviewed keyboard disclosure, review/reopen, unchanged evidence, full export including reviewed items, both CN themes and 800px viewport | ux_phase5_audit_browser.txt |
| Billing real browser | Passed rates, original-bill selection, review/reload and themes | ux_phase5_billing_browser.txt |
| Audit mapping real browser | Passed direct source mapping from NRV and billing, source preservation, recheck, reload reuse and themes | ux_phase5_mapping_browser.txt |
| Original CN real browser through common authority | Passed preserved renderers, five steps, mapping, party reopen/service restart, allocation retention, bulk audit and April–March Year Link | ux_phase5_original_browser.txt |
| Original financial regression | 332 run, 331 passed; one external-PDF-dependent test skipped | ux_phase5_engine_tests.txt |
| CN HTTP/workspace/regression suite | 118 run: 117 passed initially; one outdated test assertion corrected and passed separately (see explanation below) | ux_phase5_cn_tests.txt, ux_phase5_cn_initial.txt, ux_phase5_form_contract.txt |
| Portal account regressions | 24 passed | ux_phase5_portal.txt |
| Phase 1 / Phase 2 / storage ceilings | 2 / 1 / 1 passed | ux_phase5_phase1.txt, ux_phase5_phase2.txt, ux_phase5_storage.txt |
| Seed rules / Mongo platform arguments | 5 / 3 passed | ux_phase5_seed_rules.txt, ux_phase5_mongo_options.txt |
| Phase 3 / Phase 4 JS controllers | Passed | ux_phase5_phase3_controller.txt, ux_phase5_phase4_controller.txt |
| Protected financial baseline | All 140 files match | ux_phase5_baseline.txt |

All evidence is in verification/. Suites overlap; do not add their counts as unique scenarios.

The CN suite's only initial failure was an old HTML form inventory which omitted the existing combined-app cn_access/stn_access checkboxes from create-user. Those fields existed in the Phase 4 source. The assertion was updated to include the two exact field names; no application validation or account behavior was changed. The focused rerun passed. The full initial log is retained transparently rather than relabelled as an all-pass run.

Browser screenshots were inspected for CN audit, portal and STN member dashboard in both themes. A Navy contrast problem on an inherited hard-coded light panel was fixed, then the browser journey/screenshots were repeated. Theme screenshots wait for the existing colour transition before inspection. Native Windows setup/batch execution, printing, real user data and all inherited STN governance edge cases are not certified by these checks.

Bundled Linux Chromium extraction initially failed when the environment rejected archive chown. The same binary/fonts/libraries were extracted without applying archive ownership; actual Chromium checks then passed. The test harness accepts an explicit executable. No browser security disabling flag was enabled.

Windows installation is source-based: setup installs locked dependencies and builds the frontend. No Linux node_modules/build output, browser binary, synthetic database, secret or user data is shipped. See START_HERE_WINDOWS.md and PHASE5_RELEASE_HANDOFF.md.

# Fresh UX Phase 4 verification — 24 October 2026

Category-first audit presentation only; no audit detection, financial engine or saved review schema changes. Read PHASE4_AUDIT_HANDOFF.md. Windows and browser visual acceptance remain pending.

| Check | Executed result | Evidence |
|---|---|---|
| Actual grouping/finding/review renderers in JS VM | Passed counts, category-before-NRV order, closed disclosures, pending/reviewed/reopen, stale IDs, exact party locations, bulk periods, escaping, empty/all-reviewed and no mutation | verification/ux_phase4_ui.txt |
| Owned HTTP audit plus Phase 3 rates/state and audit mapping | 17 tests passed (overlapping inherited cases) | verification/ux_phase4_http.txt |
| Combined gateway asset routing and actual owned audit review/reopen | 1 focused test passed through gateway with no STN server | verification/ux_phase4_http_focused.txt |
| Preserved original audit/review evidence regression | 19 tests passed; includes stale source/period fingerprints, review backup and workbook scoping | verification/ux_phase4_evidence.txt |
| Portal permissions/accounts | 24 tests passed | verification/ux_phase4_portal.txt |
| Phase 1 first workbook/navigation | 2 tests passed | verification/ux_phase4_phase1.txt |
| Phase 2 scoped reset | 1 test passed | verification/ux_phase4_phase2.txt |
| Phase 3 save/recheck controller | Passed | verification/ux_phase4_phase3_ui.txt |
| Storage ceilings | 1 test passed | verification/ux_phase4_storage.txt |
| Protected Update35.2 files | All 140 match | verification/ux_phase4_baseline.txt |
| Changed JS/Python syntax | Passed | verification/ux_phase4_syntax.txt |

Counts overlap and are not unique-scenario totals. The first new HTTP harness used a POST for the state read; it was corrected to the existing GET contract. Final runs above passed without relaxing application validation.

No Chromium executable is installed in this environment. JS VM tests validate renderer output and logic, not actual browser layout/accessibility. The mapping browser harness was updated to expand CN/NRV before clicking a product, but not executed. No new Next build or Mongo/Chromium full-stack run is claimed. Phase 5 must include browser/theme/full-workflow checks; native Windows acceptance remains pending. The actual affected Phase 3 billing PDF/workbook is still unavailable.

Reproduce from root:

```
node cn/tests/test_ux_phase4_ui.cjs
PYTHONPATH=cn/backend:cn/offline_baseline:cn/tests python -m unittest test_ux_phase4_http test_ux_phase3 test_audit_mapping_http -v
PYTHONPATH=cn/offline_baseline:cn/offline_baseline/tests python -m unittest test_audit_reviews test_ledger_audit -v
node cn/tests/test_ux_phase3_ui.cjs
python integration/test_portal.py
python integration/test_ux_phase1.py
python integration/test_ux_phase2.py
python integration/test_storage_ceiling.py
python cn/verify_baseline.py
```

Earlier results follow as historical evidence.

# Fresh UX Phase 3 verification — 24 October 2026

Linux synthetic tests only; actual affected PDF/workbook and Windows acceptance remain pending. Read PHASE3_BILLING_HANDOFF.md for the rate-source trace and reproduction. Earlier sections are historical evidence, not rerun claims.

| Check | Executed result | Evidence |
|---|---|---|
| Rate/state regression plus existing billing/audit mapping | 23 tests passed (includes inherited/overlapping cases) | verification/ux_phase3_targeted.txt |
| Native calculator, ledger, frozen finish and mapping | 42 tests passed | verification/ux_phase3_cn_regression.txt |
| Portal permissions/accounts | 24 tests passed | verification/ux_phase3_portal.txt |
| Phase 1 first workbook/navigation | 2 tests passed | verification/ux_phase3_phase1.txt |
| Phase 2 scoped reset | 1 test passed | verification/ux_phase3_phase2.txt |
| Delegated storage ceilings | 1 test passed | verification/ux_phase3_storage.txt |
| Actual billing JS controller with minimal DOM/HTTP harness | Passed explicit-unit default, state/new-state controls, save/recheck success and failure, stale-result clearing | verification/ux_phase3_ui.txt |
| Protected engine files | All 140 match | verification/ux_phase3_baseline.txt |
| Changed JS/Python syntax | Passed Node syntax checks and Python compilation | verification/ux_phase3_syntax.txt |

Reproduction: a 4 kg packet sold at 1,200/packet mismatches by 9,000 for 10 packets when 300/kg is entered into the former default-packet rate row. Explicit kg selection corrects the comparison; statement evidence and original-bill return comparisons remain unchanged. This is a verified defect path, not confirmation that the unseen reported PDF has the same cause.

No Chromium executable was installed here. The existing browser billing harness was updated for the new dropdown/unit selection but NOT executed; the JS harness is not browser rendering verification. No new Next production build or full Mongo/Chromium combined journey was run; STN/Next production source is unchanged. Phase 1/2 browser results below remain historical. Both-theme visual behavior, real Windows sizing/zoom/printing and the real affected workbook require acceptance testing.

Reproduce from root:

```
PYTHONPATH=cn/backend:cn/offline_baseline:cn/tests python -m unittest test_ux_phase3 test_billing_audit test_billing_http test_audit_mapping_http test_audit_mapping_model -v
PYTHONPATH=cn/backend:cn/offline_baseline:cn/tests python -m unittest test_native_interface_http test_calculator_http test_ledger_http test_finish_http test_product_mapping_http -v
node cn/tests/test_ux_phase3_ui.cjs
python integration/test_portal.py
python integration/test_ux_phase1.py
python integration/test_ux_phase2.py
python integration/test_storage_ceiling.py
python cn/verify_baseline.py
```

# UX Phase 2 source handoff — 24 October 2026

Visible permission-scoped password reset actions and a viewport-contained signup approval dialog are implemented. Read `PHASE2_ADMIN_HANDOFF.md` and `UX_PHASE_PLAN.md`. Fresh evidence: `verification/ux_phase2_*`. Linux HTTP, production build and real Mongo/Chromium combined journey passed. Windows acceptance remains pending. Cumulative source only; final installation ZIP after all five UX phases. Next: `NEW_CHAT_PHASE3.txt`.

## Fresh Phase 2 verification

- `ux_phase2_reset.txt`: focused real-HTTP test passed for own-staff reset, cross-company/admin/self denial for delegated admins, staff denial, missing management rights, invalid CSRF/password, unchanged grants/allowances, revocation and forced change, platform company-admin reset, unaffected foreign sessions.
- `ux_phase2_portal.txt`: 24 account/portal tests passed.
- `ux_phase2_storage.txt`: delegated storage-ceiling test passed.
- `ux_phase2_phase1.txt`: two Phase 1 first-workbook/ownership/rollback/navigation tests passed.
- `ux_phase2_baseline.txt`: all 140 protected Update35.2 files match.
- `ux_phase2_typecheck.txt`, `ux_phase2_lint.txt`, `ux_phase2_build.txt`: TypeScript, changed-component ESLint and optimized production build passed.
- `ux_phase2_full_stack.txt`, `ux_phase2_full_stack_server.txt`: real disposable MongoDB/SQLite/gateway/Next/Chromium journey passed. Includes actual signup approval and staff creation, exact membership-scoped reset list, visible company-admin/own-staff actions, cancel, platform resetting company admin, new login forced change and no uncaught page errors. Approval bounds/field reachability checked at 1366x768, 1024x600, 800x450 and 640x384 effective CSS viewports. Internal synthetic screenshot inspected for layout; screenshots are not included in this source handoff.
- The same full-stack run passed seller reporting, seed quotation/contact flow, original source-PDF workflow, exact ₹38,561 calculation, private ownership (including denial to platform admin), independent export/import, frozen history, separate accounting, module revocation and real service restart.

Browser startup initially encountered extraction ownership and executable/runtime-library errors in this environment. The final run used a fully extracted local Chromium with its adjacent runtime libraries and passed. These Linux viewport simulations do not certify native Windows browser zoom, printing or user-data migration. No Windows acceptance or deployment claimed.

# UX Phase 1 source handoff — 24 October 2026

Shared Account & Settings and direct CN entry are implemented. Read `PHASE1_WORKFLOW_HANDOFF.md` and `UX_PHASE_PLAN.md` first. Fresh evidence: `verification/ux_phase1_*`. Linux checks passed; Windows acceptance remains pending. This is a development handoff; final installation delivery is after all five usability phases. Next chat: `NEW_CHAT_PHASE2.txt`.

# Latest verification — staff storage ceiling — 24 October 2026

Read `STAFF_STORAGE_LIMIT_UPDATE.md` first. Staff create/edit forms in STN and the Account console now display the authenticated delegated ceiling and block above-limit values. Server enforcement and private CN ownership are unchanged. New evidence: `verification/storage_*.txt`. Fresh Linux HTTP/browser/build checks passed; Windows acceptance of this update remains pending. User reports successful Windows account creation with the preceding unified update.

# Unified approval update — 24 October 2026

Fresh evidence: unified_accounts.txt (four targeted transaction/retry/forced-change tests), unified_portal_regression.txt (24 passed), unified_full_stack.txt (real signup approval, same-request retry, actual Chromium signup form and staff account creation in STN, plus complete CN/STN regression journey), unified_typecheck.txt, unified_lint.txt, unified_build.txt and unified_baseline.txt. Local production startup build/reuse is recorded in unified_startup_build.txt. This update fixes request CSP nonce propagation and uses the production frontend by default; the browser journey passed with that mode and no uncaught page errors. Actual Windows user acceptance is pending. Earlier reports below remain the original integration record, not repeated claims for this update.

# Fresh local verification — 23 October 2026

All results below were produced in this integration workspace on Linux with synthetic data. They are **not Windows acceptance**. Root `verification/` contains the fresh evidence; inherited `cn/verification/` files remain historical.

| Check | Actual result | Evidence |
|---|---|---|
| STN source provenance | 284 GitHub blob hashes matched the pinned Meet-Dev source snapshot | `source_snapshot.txt`, `integration/source-manifest.json` |
| Preserved Update35.2 | All 140 protected files match | `baseline_hashes.txt` |
| Original offline financial/application regression | 332 tests run; 331 passed, one conditional external-PDF test skipped | `offline_regression.txt` |
| Cumulative CN web baseline | 104 tests passed | `cn_cumulative.txt` |
| CN APIs through common authority | 59 tests passed; includes ownership, ledger/mapping, calculations, frozen finish/reports, storage/concurrency, hierarchy and audit | `cn_integrated_http.txt` |
| Common portal/accounts | 24 tests passed: auth, limits, company boundaries, grants, explicit links, schema preservation, expiry, revocation/reset, CSRF and malformed requests | `portal_http.txt` |
| STN seed rules | Five tests passed with a fixed synthetic clock; original expired-date tests were corrected in the test harness only | `stn_seed_rules.txt` |
| Full real-service combined journey | Passed with Next.js, Python/SQLite and disposable MongoDB 7.0.24 | `full_stack.txt`, `full_stack_server.txt` |
| Original CN browser journey through common accounts | Passed; exact original renderers, five steps, import/mapping, saved-party and real restart, bulk/audit/Year Link | `cn_original_browser.txt` |
| Billing Rate Audit browser | Passed rates, original-bill choice, review, reload and both themes | `billing_browser.txt` |
| Direct unmapped audit mapping browser | Passed source-prefilled mapping/save/recheck, reuse and both audit entry points | `audit_mapping_browser.txt` |
| CD product card browser/model | Passed pooled crop attribution, both themes, restart/cap/excess and no financial mutation | `cd_cards_browser.txt`, `cd_card_model.txt` |
| Panning/dragging and account browser | Passed Navy pan, independent card drag, Navy after shared login/module choice, delegated defaults/scoped user creation/resets | `pan_drag_browser.txt` |
| Transport/model | Passed authenticated transport, canonical reopen/stale routing and print | `transport.txt` |
| Build/type/static checks | Optimized Next build passed; TypeScript passed; targeted changed-file ESLint and Python compilation passed | `build.txt`, `typecheck.txt`, `lint_changed.txt`, `lint_final.txt` |

The suites overlap; their counts must not be added as a count of unique scenarios.

## Real combined journey coverage

- Individual login, forced password change, shared portal/CN/STN switching in actual Linux Chromium; no second login and no uncaught page errors.
- Company-admin rejection from platform APIs; explicit delegated staff STN grants to the linked company membership; cross-company linking rejected; invalid member lookup does not change the saved link; legacy STN cookies/credential endpoints do not bypass central authentication.
- Real MongoDB seed request, Gujarat versus other-state scope, anonymous buyer, own-quotation rejection, supplier quotation, buyer selection, contacts and completion/history.
- Seller report submission, platform approval and approved GST search through the original STN pipeline.
- Source PDF import → direct product mapping → scheme assignment → receipt settlement → frozen finalisation/report, retaining original dates and late Kharif classification. A separate preserved arithmetic fixture yields exactly **₹38,561**, then issues/freezes/exports/reports correctly.
- CN access denied to another company, the same-company staff member and even platform superadmin. Export/import creates an independent project. Editing schemes does not recompute frozen results. STN accounting deducts zero CN bytes.
- Independent module disable and immediate session revocation; denied STN member/report/search/profile/deletion/upload APIs; re-enable/new login; actual Node/gateway restart with unchanged stored CN result and STN history; scoped reset, forced change and shared logout.

## Test harness/environment notes

The optional skipped offline test needs a separately supplied two-page regression PDF via `CN_REGRESSION_PDF`. Its absence is not treated as a pass. Browser checks use actual Linux Chromium; the broad inherited journey uses reduced motion, while its targeted CD-card check retains its existing motion setup. The hierarchy browser assertions were updated for the requested common portal/module-choice route. The transport VM received a missing `CustomEvent` DOM shim; application behavior was not weakened to satisfy the harness.

The first MongoDB 8.2 test binary could not start under this environment's sandbox. The executed real-service tests use MongoDB 7.0.24 with Unix sockets/diagnostic collection disabled. A failed generic browser download was replaced with the bundled Linux test Chromium. A stale Next build cache was cleared before the successful clean build. Build and dev-server runs must be sequential when sharing one checkout.

## Still pending

- All new integration Windows installation/interaction/printing acceptance, plus new 7.2/7.2.1 audit acceptance. Earlier user acceptance remains recorded in the CN baseline.
- Actual legacy STN account/database/lookup-key migration, real-user-data copy rehearsal and production backup restoration. Synthetic legacy-CN hierarchy/schema/interchange checks are not a live migration rehearsal.
- The STN end-to-end coverage above does not claim exhaustive acceptance of every inherited governance, legal-hold, deletion, resolution or moderation edge case. Those functions retain source policies and common auth gates; include them in private staging/user acceptance as applicable.
- Public hosting, deployed-commit verification, production capacity/concurrency, TLS/trusted-proxy/process supervision and operational restore/cutover. No purchases, public deployment or live database changes occurred.
