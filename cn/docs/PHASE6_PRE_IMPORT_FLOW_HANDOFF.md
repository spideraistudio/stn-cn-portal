# Phase 6 handoff — 22 October 2026

Cumulative from corrected Phase 5 including saved-crop/optional-segment mapping.
Implemented for PC-only local review. Phase 2 passed Windows acceptance.
The user confirmed recognised PDF mappings appear and new-product/repeat-party
mapping works. Overall Phases 3–5 Windows acceptance remains pending; Phase 6
Windows and native-browser acceptance is also pending. No public deployment.

Read PHASE_PLAN.md, README.md and docs/PHASE6_FINISH_SECURITY.md before continuing.
Previous detailed handoff is preserved at docs/PHASE5_PHASE_HANDOFF.md.

## Implemented

- Finalisation freezes server-owned calculations using the unchanged Update35.2
  Store and engine, only after all financial/review checks pass. Separate benefit
  rounding is unchanged. Client-supplied result/frozen settings are never trusted.
- Issue checks live permissions, expected revision, issued controls, owner-wide
  cross-workbook/project overlap, physical source stock/IPT and traced opening
  credit. Mark issued does not post anything to Tally.
- Revisions preserve frozen parents, lineage and cumulative previously issued
  benefits. Negative revised entitlements still block finalisation. Source-based
  revisions refresh reviewed source evidence when needed and retain unchanged
  row corrections/manual vouchers; changed financial inputs require review.
- Source-based freezing uses the same authoritative stock mask/calculation-only
  period envelope as Phase 5. The historical calculation envelope is stored
  separately from the frozen actual working-period dates. All original voucher
  and receipt dates remain unchanged. Frozen results remain readable after source
  reviews/settings change; stale unissued snapshots cannot be marked issued.
- Reports/State → HQ → Party overview use unchanged reporting/territory code
  over active workbooks in the selected owned project. Latest completed lineage
  wins; drafts do not suppress completed history; overlapping products are
  excluded with explicit review notes. NRV uses configured billing on net sold
  quantities. Freight/posted journal credits and requested-only changes are
  excluded. Phase 4's posted-ledger-CN audit remains separately available.
- Product CSV/report CSV use unchanged escaping/BOM logic. Requests remain display
  only. Product CSV and individual print preparation read canonical saved records,
  not browser-supplied results. Compact/detailed prints and workbook print
  selection retain the original UI, styling, frozen data and stale-selection
  checks. Attention review is separately read-only; actual print/export requires
  Export and print permission.
- Project interchange v3 now validates complete frozen arithmetic, original PDF
  evidence, revision graph and cumulative issued controls. Importing completed
  history additionally requires Finalise; issued history also requires Issue CN.
  IDs/layouts remap into an independent project, including parent/lineage and
  issued-table record references. Malformed/fabricated frozen results are rejected.
- New Start_Web_Phase6_Windows.bat; all earlier launchers remain compatible.
  Existing accounts and WEB data location remain unchanged. Supplied local admin
  recovery utilities remain included and unmodified.

## Party reopening correction

Imported source ledgers and calculator drafts were separate. Parties previously
listed only calculator records, while the legacy Open action relied on its
browser's cached record list. Parties now includes Saved PDF parties / ledgers
with original voucher counts and direct saved-statement opening, even before a
calculation draft exists. Open / Continue now reloads the canonical owned record
and result from the backend. Source address state is retained when creating the
calculation rather than discarded for a blank workbook state.

After restart, saved entries, dates, source details, mappings and allocations
remain available. A stale source-based draft shows the party and retained voucher
count plus an explicit source-review message. Replacement statements resolve to
the current saved source. An obsolete draft does not silently autosave over new
source decisions or open an unrelated party. No saved data is merged or cleared.

## Verification

- verification/phase6_full_web.txt: cumulative real HTTP suite, 69 tests.
- verification/phase6_finish_http.txt: six Phase 6 scenarios covering transitions,
  frozen/revised arithmetic and separate rounding, party/PDF reopening and
  restart, ownership/permissions/CSRF, CSV/NRV/requested-only exclusion, canonical
  print/workbook selection, duplicate issue, independent completed-history
  interchange/tamper rejection, and late Kharif frozen source evidence.
- verification/phase6_offline_regression.txt: 332 tests run, one skipped.
- verification/phase6_ui_model.txt: production shell/transport/source panel,
  cache-independent reopening, stale draft details/replacement link, summary print.
- Mapping action/DOM checks and selectors rerun; source preservation, Python
  compilation, JS syntax, package CRC/extraction/startup checks are included.
- All 140 Update35.2 baseline files and existing appearance/dragging/zoom assets
  remain byte-identical. No native-browser/Windows rendering acceptance is claimed.

## Run / next

Stop the old server, back up the WEB data folder, extract the full package into a
NEW program folder and run Start_Web_Phase6_Windows.bat using the same existing
WEB data location. Do not bootstrap an administrator again. Keep the independent
offline installation separate. Test the checklist in README.md.

Storage limits/temporary cleanup remain Phase 7; hosting is Phase 8; mobile is
deferred. Do not begin automatic cleanup or public deployment in this release.

## Phase 6 review correction — 22 October 2026

Phase 7 has not started. The supplied ZIP was named Phase1 but contains the
cumulative Phase 6 tree; the four requested Phase 6 documents were read first.
Only Phase 2 has overall Windows acceptance. Known mapping checks passed;
overall Phases 3–6 Windows acceptance remains pending.

A stale source-based draft could show party details once, then crash in the
ordinary calculation renderer after another redraw (including an attention-list
open). The source-review screen now remains available through ordinary redraws,
retaining party/location/state/season, voucher count and current source link.
The stale guard is scoped to the saved record, project and workbook, so it does
not suppress saving a different source party. Frozen/issued records are not
marked stale by edits to live source evidence. Attempting to open a deleted
record no longer replaces the currently open record before reporting the error.

Changes are limited to the web bridge, its regression harness and release docs.
No engine, server permission, catalogue/mapping, date, scheme, styling, allocation,
dragging, zoom or saved-layout code was changed. No data migration or cleanup.

Verification evidence: verification/phase6_review_*. The UI regression reproduces
against the attached original bridge (null result / ledger_closing crash) and
passes with the correction. It covers redraws, stale autosave suppression,
record/project/workbook isolation and frozen-source notifications. These are
model checks, not Windows/native rendering acceptance.

Windows follow-up: after the normal backed-up update, reopen a saved PDF party
and a saved calculation after restart. Open a draft whose source was reviewed
again via Dashboard attention; confirm the review page and statement link remain
visible. Then open another party, save, restart, and check its entries/allocations.
Run the full README checklist and report any error text before Phase 7 begins.
