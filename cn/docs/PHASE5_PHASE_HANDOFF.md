# Phase 5 handoff — 22 October 2026

Implemented for local PC review, cumulative from the supplied Phase 4 ZIP.
**Phase 2 Windows acceptance is confirmed. Phases 3/4 Windows acceptance remains
unconfirmed; Phase 5 Windows/native-browser acceptance is pending.**
No public deployment, mobile work, quota enforcement or automatic cleanup.

## Delivered

- `/calculator`: the preserved Update35.2 Classic Emerald / Navy Studio shell,
  menus, guided schemes, ledger/manual forms, allocation workbench and diagrams.
  Original styles, font/art, card dragging, cursor zoom, lock and layout controls.
- Secure cookie/session/CSRF transport to owned web calculator APIs. No offline
  HTTP handler or server is started, and no raw database paths are accepted.
- Private per-request in-memory Store; fixed table data saved atomically under
  owner + workbook in the existing WEB SQLite database, with account audit.
- Server permissions on Save deltas, ABS/CD/Cash preview/apply, clear/release,
  scheme configuration, imports, Cash deductions and quick-creation shortcuts.
- Phase 4 import/mapping/review/audit/Year Link forms mounted in the original
  shell. Parties → Bulk Import PDFs / Open imported ledger → select season →
  Open in calculator resumes or creates the owned reviewed draft.
- Source bindings detect changed reviews/sources/periods/Year Link. Reopening
  changed evidence creates a separate new draft and keeps previous saved edits.
- Source-season projection retains late Kharif return/IPT stock in the reviewed
  season and excludes it from Rabi without moving any original date. Full
  ledger balances/receipt evidence remain intact. Details below and in security.
- Guided financial settings preserve source product/packing/period identities.
  New source groups begin empty and unconfirmed; production rates are never
  invented. Phase 3 opaque configuration dictionaries remain stored drafts.
- Separate per-record Classic/Navy layouts in owned Phase 3 layout records.
- Project backup v3 includes draft calculator tables/settings history plus
  Phase 4 PDFs/provenance. Independent import validates and remaps source,
  calculation, workbook, project and both appearance layout IDs. Source/user
  copies stay independent. Stale evidence is not approved by importing it.
- `Start_Web_Phase5_Windows.bat`, updated README/checklist and phase documentation.

## Preservation and boundaries

All 140 preserved Update35.2 files match baseline_manifest.json. Financial engine,
separate rounding, original receipt dates and existing frozen offline history
remain unchanged. The original offline installation is never opened or modified.
Existing Phase 2 accounts/permissions/revocation/audit and Phase 3/4 data remain.
Startup adds only calculator_workspaces in the WEB account database.

Source-bound calculation uses a calculation-only start-through-cutoff stock
envelope with a server-derived item mask from Phase 4 season decisions. Saved/UI
season dates remain the actual period dates. This permits reviewed late returns
to remain material returns and preserves return-bonus maths. ABS/CD date windows
are not extended. All original posting/receipt dates remain unchanged. Manual
standalone records retain the baseline's original period logic.

Source-based IPT decisions must be reviewed through the source forms; manual
standalone late-IPT review remains available. Phase 6 must retain baseline
cross-issued stock/late-IPT/traced-credit conflict checks before enabling issue.
This phase has no operational finalise/issue endpoint, so it cannot bypass them.

Financial menus/screens are retained, but online finalisation/issue/revisions,
completed reports, CSV/compact print/workbook print remain Phase 6. These controls
return an explicit phase message. Dashboard report/attention widgets dependent on
that future reporting API can show that message. This is not a claim that those
future report widgets are finished. Offline .cnwork/SQLite restore is not mounted;
web project JSON export/import is supported through Projects & workbooks.

## Verification

- `verification/phase5_final.txt`: cumulative account/foundation/workspace/ledger
  and calculator HTTP suite: 56 tests passed in 93.133 seconds, including
  11 new calculator tests.
- `verification/phase5_calculator_release.txt`: final targeted calculator suite.
- `verification/phase5_year_link.txt`: opening-credit cap/original-date test.
- `verification/phase5_scope_final.txt`: final season stock-display scope check.
- `verification/offline_phase5_regression.txt`: full preserved offline regression,
  332 tests passed with one skipped, including financial/source/history tests.
- `verification/preservation_phase5.txt`: all 140 baseline files match.
- `verification/phase5_ui_model.txt`: original shell/menu transport checks in Node
  VM. `verification/phase5_cursor_zoom.txt`: production Studio cursor-anchor
  geometry, scale limits, unchanged positions/layouts and Classic delegation.
- Python compilation, JavaScript syntax, mounted-form element-ID and ZIP integrity
  checks performed. No real account credentials or live workbooks used/bundled.

A native browser is unavailable here. Node/geometry tests do not establish rendered
browser or Windows visual acceptance. README contains the required PC checklist.
Do not label Phase 5 accepted until the user tests it on Windows.

## Run / next chat

Stop the old server and back up the WEB data folder. Extract into a NEW folder.
Run Setup_PDF_Windows.bat if needed, then Start_Web_Phase5_Windows.bat.
Keep existing accounts and `%LOCALAPPDATA%\AllCropCNWeb`, or the SAME custom
`--data` path. Do not bootstrap an administrator again for an existing install.
Open http://127.0.0.1:8787 → Open calculator, or `/calculator` directly.

Read this file, PHASE_PLAN.md, README.md and
`docs/PHASE5_INTERFACE_SECURITY.md` first in the next chat. Windows review comes
before acceptance; Phase 6 is finalisation/issue/report completion. Storage
limits/cleanup remain Phase 7, hosting Phase 8, mobile deferred. No public deploy.
Historical Phase 4 handoff remains at `docs/PHASE4_HANDOFF.md`.

## Phase 5 selection correction — 22 October 2026

- Project and workbook selections now persist together across reopening. A stale
  startup selection falls back to an owned project/workbook; failed switching
  restores the previous selection.
- Workbook creation through the calculator also saves its working period in the
  source review store, within the same permission-checked transaction.
- Statement and season lists explain empty states. Stock/open controls require
  a saved statement and a saved working period. No data/options are invented.
- Year Link starts with explicit choices, limits previous choices to complete
  April–March reports and current choices to the following year (partial allowed).
  A changed year selection cancels the earlier preview. Server validation remains
  authoritative for identity, reconciliation, dates and carry-forward amounts.
- Reload refreshes project/workbook lists while preserving valid choices. The
  embedded source panel is pinned to the sidebar workbook, preventing a hidden
  selector from opening a different workbook through the old callback.
- Existing workbooks with no source working period still need one added in
  Parties → Bulk Import PDFs → Working periods. Previously imported statements
  stay in their original workbook and user account. No automatic merging.
- Verification: phase5_selector_http.txt, phase5_selector_foundation.txt,
  phase5_selector_shell.txt, phase5_selector_options.txt and preservation checks.
  UI checks use a DOM model; Windows visual acceptance remains pending.

## Phase 5 PDF mapping correction — 22 October 2026

Read `docs/PHASE5_PRODUCT_MAPPING.md` for the actual offline/web comparison,
identity reuse rules, permissions, setup and Windows checklist. This update is
cumulative from the corrected Phase 5 selectors. Recognised own-workbook products
and saved choices now map on import; new/ambiguous/conflicting identities need
review. Older unresolved statements have a reuse action. Repeated names are
grouped, and permitted users can create/name a product and map it atomically.
No scheme rates or benefits are inferred from the PDF. Source originals and
financial code are unchanged. Saved-PDF mapping controls route to the authoritative
source panel; direct draft identity divergence is rejected server-side.

Verification: cumulative HTTP suite in `verification/phase5_mapping_http.txt`;
five dedicated mapping HTTP scenarios in `phase5_product_mapping_targeted.txt`;
332 offline regression tests with one skipped; all 140 baseline files unchanged.
Both mapping panels, selectors, shell transport and cursor zoom have Node model
checks. ZIP extraction/CRC, Python compilation and JS syntax are checked.

The supplied local admin recovery scripts are included unchanged. Existing
WEB accounts/data remain at the same location. No real user databases or login
credentials are bundled. Phase 2 Windows passed; Phases 3–5 Windows acceptance
remains pending. Finalisation/reports Phase 6, storage/cleanup Phase 7, hosting
Phase 8, mobile deferred, no public deployment.

## Mapping action feedback correction — 22 October 2026

An empty catalogue now says No saved products in this workbook. If products
exist but no packet weight matches, the dropdown says No products with this
printed packing. The new-product editor opens automatically when no compatible
existing product is available. No default products or packing are invented.

Create product and save mapping validates product name, crop, segment/group and
a positive packet weight before sending. Missing values are explained beside
the button and the relevant input is focused. Saving status and server failures
are shown in the mapping row; a successful save reloads the statement and brings
the confirmation into view. Enter weights in kg, e.g. 0.475 for 475 g.

The production button callbacks are now exercised in both standalone and embedded
panels by tests/product_mapping_actions.cjs, including the actual request payload,
empty catalogue, missing field, API failure and retry. Five real authenticated
PDF-mapping HTTP tests were rerun successfully. Browser/Windows acceptance is
still pending; a Chromium installation was unavailable in this environment.

## Saved crop choices and optional segment — 22 October 2026

User confirmed recognised products appear after import, and new-product saving
and repeat-party mapping reuse passed their Windows checks. This is acceptance
of those specific mapping checks only; overall Phases 3–5 Windows acceptance
still remains pending.

Both product-entry forms now offer saved workbook crops, an explicit Add new
crop choice, crop-filtered saved segment choices, and No segment — assign when
building / choosing a scheme as the default. The lists combine the workbook's
source catalogue and its saved financial settings only, under the current owner.
They do not expose another workbook/user or activate arbitrary Phase 3 drafts.
Case/whitespace variants of an existing crop resolve to its saved spelling.
Server creation reuses a unique existing name/crop/packing identity even when
the optional segment selection differs, avoiding a duplicate product for each
state grouping. Existing overlapping catalogue variants require an explicit
existing-product choice; none are merged or renamed automatically.

No-segment products use the unchanged offline Awaiting scheme placeholder,
with needs_assignment=true, empty unconfirmed benefits and no billing rate.
Choose Scheme / Group or Create Scheme for This Product assigns the state/season
group to the calculation through the preserved product_assignments mechanism.
A different calculation can use a different compatible scheme/group without
changing the PDF identity or previous calculation. These assignment changes now
also require Edit schemes server-side, like scheme overrides. Existing saved
assignments remain usable for read-only calculation. UI explains that permission.

Existing source crop/packing/segment identities and all previous data stay intact.
There is no financial engine or schema change, and no inferred benefits/rates.
New tests cover crop/segment lists, case normalization, no-segment placeholders,
identity reuse, two independent scheme assignments and revocation/isolation.
See verification/phase5_crop_segment_http.txt (six scenarios),
phase5_crop_segment_full.txt (cumulative suite), and updated Node action/model
checks. Overall Windows rendering/acceptance remains pending.
