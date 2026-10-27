# Phase 6.2 handoff — PDF workflow and party reopening

22 October 2026. Cumulative from the Phase 6 review ZIP. Phase 7 has NOT started.
Phase 2 passed Windows acceptance; specific PDF mapping checks passed. Overall
Phases 3–6 Windows acceptance remains pending. No public deployment or cleanup.

Read PHASE_PLAN.md, README.md and docs/PHASE6_FINISH_SECURITY.md first.
Previous handoff: docs/PHASE6_PRE_IMPORT_FLOW_HANDOFF.md.

## User feedback and cause

The previous correction did not fix the main import-to-calculator flow. Applying
PDFs persisted source ledgers but did not open the calculation or refresh the
shell's party list. The long source screen omitted the five calculation steps
and buried its continuation button. A stale source draft also exposed only a
voucher count, so its saved work looked absent. Automatic navigation saves could
block opening Parties when another tab had reviewed the source.

## Corrected flow

- Source import/review shows the same five workflow steps at the top, with saved
  statement, working-season selection and a visible Continue to Check Ledger.
- Applying a single-party import automatically opens its owned saved draft at
  Check Ledger. Repeat imports reuse a current draft and its saved allocations.
- Batch imports refresh the main party/source list immediately and provide one
  clearly labelled Open button per source, without silently choosing a party.
- With no working period, the PDF and actual vouchers stay visible. The screen
  explains that an explicit date/season choice is needed; dates are not invented.
  Adding the period enables continuation in the same screen.
- Import completion scrolls the workflow controls into view. Opening a calculation
  scrolls to its title/steps instead of leaving the user at the old import position.
- Stale source drafts show all five steps, their actual saved vouchers/original
  dates and saved payment allocations read-only, plus the current-source link.
  Stale financial totals are not represented as current calculated benefits.
- Autosave checks source freshness before navigation, so source review in another
  tab cannot trap the user before Parties/Open. Stale snapshots stay unchanged.
- A detached source screen cannot replace a party after changing pages/workbooks.
- Sidebar badge: Phase 6.2 · PDF & party fix. New launcher:
  Start_Web_Phase6_Import_Fix_Windows.bat. Old launchers remain compatible.

## Preservation and permissions

Only the web bridge/source-panel UI and test/release files changed. All 140
Update35.2 baseline files and the existing styles, financial engine, allocation
workbench, dragging, cursor zoom and saved-layout implementation remain unchanged.
No backend permission has changed. Import/apply/open/save continue through owned,
live-permission/CSRF/revision-checked APIs. No issuing/finalisation is automatic.
Source dates, original evidence, optional segments, saved-crop choices, recognised
mapping reuse, independent workspaces, Year Link and frozen results stay intact.

## Verification

- verification/phase6_import_flow_browser.txt: real Linux Chromium using actual
  HTML, events and HTTP; single-PDF and Step 1 file import; five visible steps;
  batch and repeat import; immediate directory refresh; exact party/voucher/date/
  allocation persistence; server shutdown/recreation plus fresh browser context;
  both interfaces; stale-source read-only detail navigation; empty-period guidance
  and continuation. No uncaught page errors or failed API calls in these flows.
- Native runner: tests/run_phase6_browser_flow.py + tests/browser_phase6_flow.cjs.
  Requires Node Playwright and a Chromium executable; uses temporary synthetic
  accounts/workbooks only. CN_BROWSER_EXECUTABLE selects an installed Chromium.
- verification/phase6_import_flow_web.txt: all 69 cumulative real-HTTP tests pass.
- Mapping action/DOM, selector, web transport/stale-model and geometry zoom checks
  are rerun; baseline hashes, compilation, ZIP extraction and startup checked.
- Native browser testing is Linux Chromium, not Windows acceptance. The unchanged
  offline engine's 332-test regression result remains in phase6_review_offline.txt
  (one skipped); its sources are byte-identical in this package.

## Next Windows check

Back up WEB data, stop the old server, extract to a NEW folder, run the new
launcher, and confirm the sidebar badge says Phase 6.2. Use the existing login
and WEB data location. Import/apply one PDF: its own party should open at Check
Ledger with steps 1–5. Restart and reopen it; verify receipts, supply, returns,
original dates and allocations. For older saved PDFs choose the source party
and Continue to Check Ledger at the top. Keep Phase 7 on hold pending feedback.
