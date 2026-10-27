UPDATE32 — APPLIED-BENEFIT PRINT + WORKBOOK PRINTING
19 October 2026. Cumulative from Update31. All earlier financial rules, UI choices,
Cash controls and PDF header fixes retained. Windows acceptance pending.

INDIVIDUAL DETAILED WORKING
Review & Finish -> Print Detailed Working now contains:
* Compact product totals and only non-zero product benefit breakdowns.
* Only payable/applied benefit CNs, or previously issued/revised CN adjustments
  that must remain visible even when current entitlement is zero.
* Applied quantity/extra/net tier only, actual ABS product rows, used CD payment
  periods, Cash deduction/funding working, and qualifying return bonus working.
* Progressive quantities list only used bands, including the established highest
  rate continuation. No complete configured slab lists or recursive per-field
  configuration dumps for these current benefit formats.
* Actual precise CN, separate rounding, previous issue, proposed new amount,
  narration, totals and balance remain. Requested adjustments show only when
  present and stay display-only. Zero-CN products remain visible in product totals.
The supplied example has three products and one Rs30 Quantity CN: 12kg x Rs2.50.
An A4 Chromium layout reconstruction using those figures fits ONE page, down from
four. Two pages is a target for ordinary parties, not a hard clipping limit.
Large party reports naturally continue if required to preserve all applied work.
Normal Print Summary remains available with its existing content.

WORKBOOK PRINT
Workbooks -> each active workbook (also Existing calculations) has:
* Print Workbook Summary: one party-wise table with period, status, ledger,
  full CN entitlement, new CN and balance. No total of ledger balances across
  periods, to avoid counting the same balance repeatedly.
* Print All Parties' Detailed Working: the workbook index plus a fresh page for
  each selected party's compact applied working.
A selector allows all/some parties and one saved version per party+location+season.
Latest populated ledger is initially selected, so a newer empty draft does not
hide an imported ledger. Revisions are not added together. Different seasons
remain explicit. Deleted parties and other workbooks/projects are excluded.
Current open draft is saved first, like individual printing. Preview/rendering
then uses a read-only SQLite snapshot of saved records and settings. A changed
workbook invalidates the selection fingerprint. Completed results stay frozen
and are never recalculated; unavailable historical results are reported explicitly.
Draft/incomplete calculations are marked provisional. The print operation does
not finalise or issue CNs. Missing/error results are not silently shown as zero.
Use the print dialog -> Save as PDF to share. No messaging or online upload occurs.

VERIFICATION
311 Python tests passed (including actual Update31 PDF regression, six workbook
print snapshot/version/deletion/frozen tests and one authenticated/scope HTTP test).
Eight existing UI/API smoke suites passed with the print expectation updated.
Applied-print JS tests passed: zero omission, reversals, progressive used bands,
CD used rows, fixed Net CN, escaping and financial objects unchanged.
Native Chromium tests passed for the individual report and workbook selection,
all/none, two-party Summary Rs6000, combined Detail Rs2000 + Rs4000, correct
working, page boundaries and restoration of the active party globals.
A4 PDFs rendered and inspected. Individual example: one page. Two-party combined
working: index + one page per party (three pages). White print background and
readable text; no clipping. No private input PDFs or browser images bundled.
Eleven updater backup/rollback checks passed. Source/program parity checked.
The calculation engine and financial stores are byte-identical to Update31.

CONTINUATION
1 Individual compact applied working: COMPLETE.
2 Workbook Summary / all-party Detail + selection: COMPLETE.
3 Regression, browser/PDF verification and packaging: COMPLETE.
Next: user Windows acceptance. Continue cumulatively from Update32. Preserve
both UI options, saved positions/preferences/data/settings and all financial rules.
Read LATEST_HANDOFF.md, STABLE_BUTTON_FIX.md, TEST_RESULTS.txt and PHASE_PROGRESS.md.
