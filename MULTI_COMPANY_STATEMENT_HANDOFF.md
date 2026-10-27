# Multi-company statement import — 26 October 2026

Cumulative base: STN_CN_Public_Visitor_Registration_Source_Handoff.zip. Includes the visitor/registration phase, all five UX phases, temporary/permanent case-number history and billing-rate precision fixes. The preceding case-number/rate update was accepted on Windows. Windows acceptance of the public UI and this importer update remains pending. No deployment, live migration or original Meet-Dev changes.

## Supported evidence

Added backend adapters for text PDFs with (1) Tally-style To/By vouchers, explicit debit/credit and running balance, (2) itemised account statements with separate Sale/Bill lines, and (3) compact account statements with document types and Qty/Rate detail. The original importer remains the fallback, unchanged. This is deterministic layout support developed from examples, not universal AI training or OCR. A different company's layout still needs validation before it can be claimed supported.

All supplied statements reconcile exactly:

| Issuer | Vouchers | Item lines | Opening | Closing |
| --- | ---: | ---: | ---: | ---: |
| Avani | 35 | 41 | ₹24,258 credit | ₹35,053 credit |
| Remik | 6 | 6 | Unprinted zero, requires review | ₹42,000 debit |
| Dhanwel | 31 | 51 | ₹3,000 credit | ₹12,43,450 debit |

Avani's supplementary stock-summary totals agree with the detailed voucher totals and are not imported again. Quantity and value totals are checked in aggregate, not per product. Sales-return spelling and the material-received narration are recognised; the latter remains IPT in, not an additional invoice. Freight journals remain separate postings. Dhanwel's reversed credit/debit column order, shifted receipt amounts, repeated unnumbered receipts and items continuing onto the next page are handled. Missing receipt references remain visibly generated page/line references, never invented bank references. Purchase/Purchase Return entries require classification review. Carry totals and running balances are checked; missing ledger pages and inconsistent balances fail import.

## Confirmed units and remaining review

User confirmed on 26 October 2026:

- Remik MILKY WHITE 3 KG: printed quantity 15 = 15 packets; printed 3 kg packing means 45 kg. The unit rule is restricted to that issuer and exact normalised product name. All six occurrences in the supplied statement use this same product. Total is 120 packets / 360 kg, invoice value ₹42,000.
- Dhanwel SOYABEAN SEEDS KDS-726: 250 = 250 packets and ₹2,400 is the packet rate. Working extension is ₹6,00,000. Packet weight is not printed and is NOT inferred. Map the correct packet weight before any kg conversion.

These units are labelled `confirmed_profile`, with a confirmation note; they are not misrepresented as printed units. All other missing units remain `unknown`: the supplied Dhanwel statement has 50 such lines. Other companies/products do not inherit these confirmations. Packings using “grms/grams” are recognised separately from catalogue selection. A printed 500 g pack cannot be mapped to a different pack size.

Dhanwel does not print item amounts. Quantity × rate is stored as a labelled working extension, never a verified printed line amount. Several voucher totals differ from these extensions; the importer does not apportion discounts or taxes. For example, the first invoice's combined extensions exceed its voucher total by ₹12,500. Obtain invoice details, verify or correct the line amounts, and enter an amount-review reason. Existing engine reconciliation still blocks a stock voucher whose item amounts do not equal its voucher amount; a review note alone cannot override this.

Use a separate workbook per supplier to keep product mappings, schemes and rates organised. Issuing company is included in repeat-import matching for these new formats, and Year Link rejects different known issuers. Keep the original PDF; reimport uses the same deterministic entries and the existing replacement-review workflow.

## Check Ledger workflow

A statement-review panel shows the issuer, readable layout name, report period and verified supplementary summary. Where needed:

1. Confirm zero opening balance with a reason (Remik does not print it).
2. Map product and actual packing; no pack size or scheme is invented.
3. Expand a voucher. Choose kg or packet for each unprinted unit and enter a unit-confirmation reason. “Packet” also represents a physical bag with the mapped bag weight.
4. For working item amounts, enter the invoice-verification reason and correct amounts where supported by evidence. Source corrections require the existing correction reason.
5. Review classification, stock summary, scheme and payment allocation through the existing workflow.

These reviews cover the full imported statement, even when calculating one season. The calculation still uses the existing selected-season rules and original receipt dates. Canonical source evidence generates server-side blockers; deleting browser warnings cannot remove them. Review fields use existing save, ownership and edit-ledger permissions. Original PDFs and source details remain unchanged; changes are draft corrections. Finalisation is unavailable until these and all existing engine checks pass. No CN was finalised for the private samples because their schemes, mappings and missing invoice details were not supplied.

## Verification

- `verification/multi_statement_tests.txt`: 5 tests, including actual three-PDF import, stable reparse, missing-page rejection, repeat import, save/reopen, private ownership, edit permission, finalisation blocking and Dhanwel project export/independent import; canonical review gates, grams packing and malformed-PDF validation.
- `verification/multi_statement_browser.txt`: real Chromium imports all three PDFs, renders review controls in both themes, exercises confirmation fields, saves and reloads; no page errors. Screenshots were inspected internally and are not distributed.
- `verification/multi_statement_regressions.txt`: 59 combined-account CN HTTP regression tests. Covers existing ledger replacement, mappings, original dates, allocations, freeze/finish, independent transfers, quotas, billing precision and hierarchy behavior.
- `verification/multi_statement_engine.txt`: original 332-test financial suite, 331 passed, one external-PDF-dependent skip.
- `verification/multi_statement_baseline.txt`: all 140 protected baseline files unchanged.
- `verification/multi_statement_package.txt`: cumulative source retention, unchanged STN/public UI files and ZIP integrity.

An initial malformed-PDF regression returned HTTP 500 rather than 400; the adapter now converts PDF reader failures into the existing validation response. Final test logs reflect the corrected implementation. Initial browser harness retries corrected its module path and reload readiness, not the application workflow. This phase did not repeat the entire STN production registration lifecycle: its prior passing evidence is retained in PUBLIC_VISITOR_UI_HANDOFF.md, and those files remain byte-for-byte unchanged. Browser checks ran on Linux; native Windows acceptance remains pending.

Private PDFs, extracted text, screenshots, databases, credentials, dependencies and runtime caches are excluded from the ZIPs. No live account or saved user workbook was edited.

## Windows installation / acceptance

Both ZIPs contain the complete cumulative project and Windows setup scripts, not a standalone EXE. Follow START_HERE_WINDOWS.md: stop the running app and MongoDB, back up the COMPLETE integration-data folder including keys, extract into a fresh folder, copy the stopped data folder, then run Setup_Combined_Windows.bat, Start_Local_Mongo_Windows.bat and Start_Combined_Windows.bat. Preserve existing credentials and do not recreate the administrator.

Create separate test workbooks for the three suppliers; import the original PDFs. Check the counts and balances above, profile-confirmed packet units, product/packing mapping, unknown-unit controls, invoice amount review, repeat imports and saved draft reopening in both themes. Reopen older saved work to confirm continuity. Do not treat the Dhanwel statement's unprinted units or working extensions as fully reviewed. Public UI Windows acceptance is still pending as described in the preceding handoff.

## Reproduce

Run from project root after setup:

```
python cn/verify_baseline.py
python integration/run_cn_integrated_tests.py
```

Set PYTHONPATH to cn/backend, cn/offline_baseline and cn/tests for `python -m unittest test_multi_statement -v`; set CN_MULTI_STATEMENT_DIR to a directory containing only the three private sample PDFs to run that acceptance check (otherwise it is explicitly skipped). Run original engine tests with PYTHONPATH=cn/offline_baseline and `python -m unittest discover -s cn/offline_baseline/tests`. Linux path separators are `:`; Windows uses `;`.

For the browser check use cn/tests/run_phase6_browser_flow.py with CN_BROWSER_TEST=browser_multi_statement.cjs, CN_MULTI_STATEMENT_DIR, Playwright, and a compatible Chromium installation. CN_BROWSER_EXECUTABLE/CN_CHROMIUM_PACKAGE select the constrained test runtime; browser libraries/fonts are environmental requirements. All HTTP/browser test data is disposable.
