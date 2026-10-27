# Temporary/permanent case numbers and billing-rate precision — 26 October 2026

Cumulative from STN_CN_Search_Layout_Fix_Windows_Installation.zip. Read this handoff first. Preserves the accepted GSTIN search panel, dashboard/search scrolling, both appearance themes, the separate Buy/Sell marketplace, billing-audit grouping and all five UX phases. No deployment, live migration or original Meet-Dev changes.

## STN case-number workflow

For a new report with Legal proceedings initiated, explicitly choose Temporary / filing number or Permanent / registered case number and enter the number. Later, open My reports and edit/request changes to that same report, choose Permanent and enter the registered number. The stored temporary reference is appended to server-generated history. Pending corrections also retain their earlier number; unchanged saves do not duplicate history. Previously stored numbers are shown under Previous case numbers in the form, member/admin details, approved seller experiences and administrator CSV export.

Approved reports continue through the existing revision/administrator-approval workflow. The approved temporary version remains searchable until its permanent revision is approved. Earlier approved records remain superseded history. A different member cannot edit the report, and a company admin cannot perform the platform review. Browser-submitted history is ignored. An optimistic guard checks the stored case fields before committing an edit so another case-number change cannot be silently overwritten.

Older reports have no assumed number type: they display Type not specified. An unchanged legacy number may remain unspecified during an unrelated edit; changing its number requires an explicit type. No bulk backfill or migration is performed. New Mongo document fields are additive and are written through normal report saves; the declarative schema is updated to reflect them. Removing the legal flag preserves earlier references in stored history. History has a 100-change ceiling; reaching it returns an explicit error rather than deleting earlier evidence.

## Billing audit: reproduced cause and correction

At 475 g packing, the previous comparison divided 901 by 0.475 to obtain a repeating per-kg Decimal, then multiplied it back. That yielded 900.9999999999999999999999999. The automatic return check used strict greater-than, so a printed return rate of 901 was incorrectly flagged as above supply. The same approach also produced awkward expected-rate/difference strings. This was an audit conversion error, not a changed billing rate in the statement.

Same-unit printed rates now compare directly and do not pass through per-kg conversion. Where units differ, conversion multiplies before dividing and uses the precision of the quoted rates, with at least two decimal places, before applying quantity. This prevents a sub-paise unit-conversion residue from becoming a large line difference on bulk quantities. More precise printed quotes retain their precision. The comparison trace explains cross-unit rounding. Approved-rate checks and explicitly selected original-bill splits use the same conversion helper. Their existing one-paise line tolerance remains; automatic same-unit return comparisons still detect genuine quoted differences. Opposing split errors do not cancel, and mixed real supply rates still require review. No FIFO, averaging or original invoice is inferred.

The original quantity, printed rate, amount, packing, dates, approved-rate records and saved original-bill choices are not rewritten. Item amount versus printed quantity × rate remains a separate evidence check. Missing mapping/state/effective-rate evidence remains explicitly unchecked, rather than being called a match. Matching rows remain hidden by default and View all checked entries remains available. Run Billing Rate Audit only again after installing; reimporting an unchanged statement is not required for this precision fix.

## Supplied PDF verification

Amreli.pdf was obtained read-only and its first page visually inspected. Its 97 pages parsed into 62 ledgers without import errors. A before/after comparison of 508 sale/return item rows used an explicit test catalogue matching printed product names/packing, and a test ALL-state approved rate of 901 for the 475 g products. It resolved 138 false Return rate above supply findings whose printed supply and return rates were both 901. One genuine above-supply finding remains, along with duplicate/conflicting source lines and missing earlier-sale evidence requiring review. The documents and test configuration were byte-for-byte unchanged by the audit run.

This reproduces the reported precision error in actual statement evidence. It does not claim to reproduce the user's saved workbook mappings, approved-rate settings or original-bill selections, which were not supplied. Earlier handoffs saying that the PDF was unavailable are historical. The PDF, parsed private ledgers and internal screenshots are excluded from the release ZIPs. See verification/case_rate_actual_pdf.txt for aggregate evidence only.

## Rabi-only CN from an annual statement

The existing Working season feature already supports this; no financial-engine change is needed. Keep the annual statement, create/select the Rabi period with confirmed start/end/cutoff dates and configure the applicable Rabi schemes. Review late Kharif returns, IPT and already-given CNs against their correct season even if they are posted during Rabi. Payment allocations retain original receipt dates, clear prior outstanding first and follow the selected scheme's ABS/CD dates. Review the selected-season net supply before finalising. A focused HTTP regression checks Kharif/Rabi projection against stock summaries while retaining the full original ledger and dates.

## Fresh verification

- TypeScript noEmit, production combined Next build and targeted changed-source lint passed. The two pre-existing internal-navigation warnings in the member reports panel remain; full-project lint is not claimed.
- Twelve Node tests passed: four case-number/history/rendering checks plus eight existing search/trading rules.
- Thirty-nine focused billing/model/HTTP/mapping/season tests passed (some inherited test classes overlap). Genuine one-paise and higher-precision differences, mixed rates, independent splits, large quantities, fractional packing and cross-unit quotes are covered.
- Existing billing UI controller check passed: 500 matches hidden by default, grouped findings, clear unchecked reasons and replacement on recheck.
- Original financial suite: 332 tests, 331 passed and one external-file-dependent skip. All 140 protected baseline files match.
- Real disposable Mongo/SQLite/gateway/Next HTTP journey passed case-number creation, pending correction, nonduplicating/server-owned history, permanent revision, approval, cross-owner denial, public approved visibility, saved edit form and typed CSV export. It also passed existing signup/staff permissions, seed requests/quotation/contact/privacy, source PDF to finalisation, exact 38,561 arithmetic, frozen history, independent import/export, separate storage accounting, module revocation, service restart, reset and logout.
- Real Chromium against those services passed the new case-number controls and saved permanent/history form in both themes. Existing cross-module navigation, contained signup approval and scoped password-reset browser checks passed. Different roles use separate browser processes in constrained single-process Chromium mode to avoid browser-context storage leakage in that test environment.
- Workspace browser regression passed both dashboard/search pages, contrast checks, long results, single content scrolling, error/empty/stale-response states, disabled search and preview. These layout checks use synthetic responses and mocked framework navigation; the case-number/full-stack checks use actual services.

Evidence: verification/case_rate_*.txt. Native Windows acceptance remains pending. Fresh checks do not replace testing the user's own stopped data copy on Windows.

Useful reproduction commands after dependency installation:

    node --import tsx --test tests/case-numbers.test.tsx tests/seed-market-search.test.ts tests/seed-trade.test.ts
    PYTHONPATH=cn/backend:cn/offline_baseline:cn/tests python -m unittest test_billing_audit test_billing_rate_fix test_billing_precision test_billing_http test_audit_mapping_model test_audit_mapping_http
    PYTHONPATH=cn/offline_baseline python -m unittest discover -s cn/offline_baseline/tests
    python cn/verify_baseline.py
    python integration/full_stack_test.py

The PYTHONPATH examples use POSIX shell syntax; use the equivalent Windows environment configuration for manual test execution. Build with NEXT_PUBLIC_COMMON_PORTAL=1, as configured by Windows setup. Browser checks need Playwright Chromium, or CN_BROWSER_EXECUTABLE and optionally CN_BROWSER_SINGLE_PROCESS=1 in constrained environments. They use synthetic test accounts and disposable data only.

## Windows installation and acceptance

Follow START_HERE_WINDOWS.md. Stop the existing app/Mongo cleanly, back up the COMPLETE integration-data folder including keys, extract into a new app folder, copy the complete stopped data folder and run Setup_Combined_Windows.bat. Then run Start_Local_Mongo_Windows.bat and Start_Combined_Windows.bat and open http://127.0.0.1:8787/portal. Keep existing credentials; do not recreate the admin.

Check temporary submission, later permanent revision, approval visibility, old-number history and both themes. In CN, rerun Billing Rate Audit only on the affected workbook. Confirm printed 901 versus 901 no longer flags, while real differences and incomplete comparisons remain actionable. Verify your Rabi working period, seasonal scheme dates and late Kharif assignments before calculating Rabi CN. Existing calculations, original dates, separate rounding, frozen reports, independent ownership, permissions and storage ceilings are preserved.

Both delivered ZIPs contain complete cumulative source and Windows setup/launch scripts, excluding installed dependencies, build caches, browser binaries, credentials, databases and private input documents.
