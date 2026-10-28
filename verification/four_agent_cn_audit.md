# CN audit — 28 October 2026

Scope: disposable local test accounts/workbooks only. No deployment, live database, existing user work, or GitHub changes. No new CN implementation changes were required. The recovered test corrections expand closed review details before visible-text assertions and permit only the already-approved clean-start/statement-review changes in the otherwise preserved offline renderers.

## Completed verification

- Clean-profile model/HTTP: 5 tests passed. New profiles and blank workbooks start empty; existing settings/history remain intact; cross-user reads are denied.
- Protected baseline: all 140 original files match.
- Actual private statement acceptance: 5 tests passed using the three supplied PDFs. Imports reconcile 35 / 31 / 6 vouchers to closing balances -35053.00 / 1243450.00 / 42000.00 respectively. Repeat import, ownership, save/reopen and unresolved-review finalisation guards passed. These private files must remain outside release ZIPs.
- Chromium clean-profile journey passed in Classic and Studio, including initial workbook form, empty catalogue/schemes/parties, settings/import entry, reload and no sample actions or page errors.
- Chromium billing journey passed PDF import, independent billing audit, approved-rate save, original bill matching, review reason, reload retention and both themes; no page errors.
- Chromium original five-tab journey passed inline mapping, ordinary Parties/Open, real service restart, source refresh with preserved allocations, bulk import, Ledger Audit, April–March Year Link and older saved-source party reopening. No page errors or failed APIs.

## Running at report creation

- 59-test combined-account regression: see verification/full_audit_cn_integrated.txt.
- Original financial suite: see verification/full_audit_financial.txt.

## Limits

Linux/Chromium checks are not native Windows acceptance or internet-production certification. Browser runtime uses test-fonts.conf because the generic bundled font configuration references unavailable fonts. Unknown packet-weight/per-packet schemes remain deferred: ledger_service.validate_catalogue still requires positive packing_kg; no dummy weight was introduced. No universal statement-format support is claimed.

Raw results are verification/full_audit_clean_profiles.txt, full_audit_baseline.txt, full_audit_clean_browser.txt, full_audit_billing_browser.txt, full_audit_offline_browser.txt and full_audit_private_statements.txt.
