# Update23 — Premium studio and native-window option

Read root READ_ME_FIRST.txt and LATEST_HANDOFF.md first. Browser launchers preserved. Native first setup requires pywebview/WebView2; no Windows binary bundled.

# Update22 — Connected allocation flow

Use root READ_ME_FIRST.txt and LATEST_HANDOFF.md for current installation/status. Detailed HQ dashboard is next.

# Update 21 — Full software UI

Use the root READ_ME_FIRST.txt for installation and LATEST_HANDOFF.md for current status. The user uses Start_Calculator.bat. Update20 is accepted; Update21 visual acceptance is pending.

CURRENT UPDATE: all requested batches are included. Read LATEST_HANDOFF.md and the update package READ_ME_FIRST.txt first. Do not replace live data with this source folder.

# All-crop offline CN calculator — Phase 6 development build

This runs on your PC using Python, a local SQLite database and your normal browser. No hosting, cloud database, API key or cloud AI is used. The PDF reader needs a one-time installation; afterwards calculation, importing supported PDFs and saving work offline.

## Start on Windows

1. Install Python 3.11 or later with the Python launcher (`py`) enabled, if not already installed.
2. Extract this ZIP to a permanent folder, such as `Documents\All_Crop_CN`.
3. Run `Setup_Windows.bat` once. This installs the PDF reader and its dependencies; internet is needed for this initial setup.
4. Run `Start_Calculator.bat`. Keep its window open. Your browser opens `http://127.0.0.1:8765`.
5. Close the command window to stop the app. Launch it again to reopen saved drafts and history.

Mac/Linux: install `requirements.txt` using Python, then run `python3 app.py`. Data stays in `data/calculator.sqlite3` inside the extracted folder. Do not move only the launcher away from the app. Use Settings → Backup regularly. This is a development build, not a packaged Windows EXE.

## First review

Dashboard → Import Ashapura test PDF loads the included original PDF as a reviewable draft. Its closing balance is ₹21,84,524 and all 8 product/packing variants are retained. The already-posted ₹2,000 bajra CN is separate from sales returns. Unmatched products and returns without matching seasonal supply must be mapped or classified with reasons; the app does not guess.

Before finalisation, configure and confirm the production season dates, applicable states and crop ABS periods. Numerical references are preloaded from the latest handoff. Settings remain draft until confirmed; missing values do not become zero. No automatic state fallback is used. Premium and Deluxe are separate, and DAWAT 1 kg / 3 kg stay separate.

## Workflow

- **Select Party:** party, address state, season and documented seasonal state override. Choose a scheme for each existing segment. Import a supported text Tally PDF or enter manually.
- **Check Ledger:** enter opening/closing balance and confirmed old dues; review every voucher, map products and packing, preserve source lines and record correction reasons. Item amounts must reconcile each sale/return voucher. All ledger entries remain in accounting even if outside CN eligibility.
- **Assign Payments:** old dues clear chronologically before allocating available money. Split receipts manually into product ABS, segment CD, eligible cash or documented settlement outside the benefit pool. A split never creates a receipt. To transfer unused CD money, reduce its previous assignment and create a destination allocation from the same original source. Exact decimal allocation amounts are supported.
- **Check Benefits:** expand separate Quantity, ABS, CD, Return, Extra, Net rate and eligible Cash CN workings. Full decimal precision is retained, with each separate CN rounded nearest rupee, half up.
- **Review & Finish:** fixes are required before finalisation. Finish freezes ledger, allocations, settings and engine version. Mark Issued is a separate action and does not post to Tally. Revisions preserve earlier records and propose differences from already-issued entitlements; decreases block automatic issue.

Cash returns need an explicit additional deduction rate per kg and remark, including zero. The CN floors at zero; excess deductions require review. Cash advance eligibility uses supplied quantity. If invoice rates vary, enter reviewed cash invoice/return value shares with source references rather than replacing them with a guessed rate.

After revising an issued calculation, review a current ledger that includes posted earlier CNs and confirm it. Do not reuse the old pre-issue closing as though the earlier CNs had never been issued.

## New scheme

Settings → Create New Scheme by crop. Select products/packing in one segment; enable or disable benefits; edit ABS token/incentive and dates; add/remove quantity/extra tiers and inclusive CD periods; set the return threshold/rate. Whole quantity or progressive quantity mode is supported. Extra uses the highest qualifying tier only. Preview gives a plain-English description. Save Scheme Draft retains it in the settings draft; **Save settings version** persists it.

Net rate cannot stack with regular benefits. Cash remains its separate restricted allocation. Changed settings create new versions; issued rules stay frozen. For a new product/segment, use the catalogue/mapping editor and retain stable product/segment IDs. A new scheme for existing products can be selected in Select Party. The catalogue editor and advanced cash settings currently use structured JSON; simpler editors can follow during UI refinement.

## Save, history, backup and export

Draft changes autosave after a brief pause; Save Draft saves immediately. The saved time is shown at the top. Stale writes are rejected. History supports searching and comparing saved versions. Print Summary uses the browser print dialog. Export produces JSON containing summary, separate CN details, source snapshot and status. Backup includes records, all settings versions, issued identities and audit records. Restore previews replacement and creates an automatic safety backup first.

## Verification and limitations

37 automated Python tests passed: confirmed arithmetic, Saini reconciliation, bajra cap, crop examples, DAWAT separation, date/slab boundaries, cash safeguards, payment conservation, persistence, finalisation, duplicate issue and HTTP checks. JavaScript syntax and a UI runtime/template smoke test passed.

Real Chromium interaction/visual testing was unavailable here (no browser executable; cloud browser cannot reach the local server). Windows installation and full real-account click-through remain Phase 7/8 checks. The importer is a conservative adapter for the supplied text-based Tally layout, not OCR or a universal PDF parser. Unsupported layouts/entries block review. No Tally posting integration is included.

Saini's approved ₹1,42,535 final outstanding is retained as a dashboard reference and independent regression test. Representative dates in that test are explicitly synthetic; no actual missing Saini receipt dates have been invented. September production allocation still needs actual input.

Bajra native Microsoft Excel recalculation remains pending. No source Excel formulas were copied into the engine or repaired, and this app's passing tests do not certify those workbooks.

Run automated tests: `python -m unittest discover -s tests -v` from this folder.
