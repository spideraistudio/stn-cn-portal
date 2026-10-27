UPDATE31 — TALLY CONTINUATION-HEADER PDF FIX
19 October 2026. Cumulative from Update30. Update29 was accepted on Windows;
Update30/new Update31 user acceptance remains pending.

CAUSE
The supplied two-page Tally ledger prints a full Ledger: party name on page 1,
but Ledger: party name : report-period Page N on its continuation. The old
first-page matcher captured the continuation suffix as part of a second party
name and split one ledger into two documents. This led to a missing closing
balance and/or a misleading combined-ledger/Bulk Import route.

FIX
Recognise the explicit Ledger: name : date-to-date [Page N] continuation form
before the full first-page header. Join same-party continuation pages. Actual
different parties and repeated full first-page headers retain their boundaries.
No broad fuzzy matching, amount inference, OCR or party merging introduced.
All Update30 changes (Regular + Cash controls and reviewed removal), both UIs,
card layouts, saved preferences, data and settings are retained.
The only runtime change from Update30 is tally_detailed.py header detection.

SUPPLIED PDF VERIFICATION
One complete party; 2 pages, 12 distinct vouchers, reconciled closing Rs602385.
Opening credit Rs552875; sales Rs2088000; receipt Rs100000 on 13 July 2026;
sales return Rs820840; four freight/expense Journal CNs totalling Rs11900.
Freight journals remain posted expense CNs; they are not material returns or
additional receipts. Bill references/carry totals are not counted as receipts.
Stock net: 32D55 1700 packets / 6800kg; 32D12 84 packets / 336kg; Ranbanka
60 packets / 240kg; 14D88 86 packets / 129kg; Redgram 114kg; Res.Angur 262kg;
Green Gram 11 packets / 22kg. Product matches depend on the actual workbook's
catalogue; unknown catalogue products still require explicit mapping.
Original dates, voucher amounts, source snapshots and saved-source re-read agree.
Both /api/import and /api/reparse checked using the actual supplied PDF; single
import returns one complete party, not the combined-ledger route. Preview/import
parsing alone does not create saved party records.

TESTS
304 Python tests passed, with CN_REGRESSION_PDF set to the supplied file. Includes
three header/boundary tests and an actual-PDF money/stock/reparse regression.
Existing 49-party / 69-page detailed PDF and other formats pass regression.
All eight existing UI/API smoke suites passed. Eleven updater backup/rollback
checks passed. Native UI unchanged, so new browser-layout checks were unnecessary.
The new private source PDF is not bundled. Its regression test is optional and
uses CN_REGRESSION_PDF when provided. Generic header tests are always included.
This fixes this explicit header family; other unsupported PDFs need inspection.

USE
Close calculator/server, extract ZIP, run Update_CN.bat, select app.py in the
existing working calculator folder, reopen normally. Reimport the original PDF
into the intended party/workbook and review the import preview before accepting.
If a previous attempt created an incomplete draft, inspect its existing entries
before accepting a reimport; never delete saved party work just to fix this issue.
No need to split/convert the PDF. Saved calculations are not silently rewritten.

RESUME
All implementation/testing/packaging phases complete. Windows acceptance pending.
Continue cumulatively from Update31, preserving all financial rules and existing
features. Read LATEST_HANDOFF.md, STABLE_BUTTON_FIX.md, TEST_RESULTS.txt and
PHASE_PROGRESS.md before future changes. The source and verification logs are
included in this package.
