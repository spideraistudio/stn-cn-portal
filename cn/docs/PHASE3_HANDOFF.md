# Phase 3 handoff — 21 October 2026

Implemented for local PC review, cumulative from the Windows-accepted Phase 2.
Phase 3 Windows/native browser acceptance is still pending. No public deployment.

## Delivered

- Owned projects, workbooks, draft schemes/settings, parties, files and layouts.
- Account-database transaction checks live session, permission and ownership on
  every new operation. No mutable global user/workbook routing or admin bypass.
- Server-generated IDs, strict fields, validated parents, revision guards;
  stale saves return 409. Archive only; parents with active children are protected.
- Source-file byte persistence/download; filenames never become filesystem paths.
- Independent Classic/Studio layout documents with validated card coordinates.
- Atomic, versioned project export/import: every import gets new IDs and creates
  a separate project. Unknown/invalid graphs fail without partial writes.
  Scheme-bearing imports require edit_schemes as well as import/ledger rights.
- Workspace audit records contain IDs/kinds/counts, not private document content.
- Local PC workspace console linked from the existing account centre.

## Preservation

All 140 baseline files match the original Update35.2 manifest. No financial
engine, original receipt date, rounding, frozen history or existing interface/
layout code changed. Existing web accounts/session/audit tables are retained;
startup adds the owned document table/index. Accounts and sessions are never
included in project interchange. No user financial data is bundled.

## Verification actually run

- verification/phase3_final.txt: 35 tests passed (32 cumulative account/foundation
  checks plus the first three workspace tests), 32.248 seconds.
- verification/phase3_workspace_extended.txt: all five final workspace tests
  passed, 10.847 seconds, including the two added checks for real simultaneous
  store writes/restart and file download/all-new-route permission boundaries.
  The earlier three workspace scenarios were rerun in this targeted check.
- Baseline preservation: 140 hashes match; Python compilation and both browser
  scripts' syntax pass. Final archive integrity checked.

HTTP tests cover own/cross-user reads, changes, archives, exports, downloads,
forged identity fields, identical IDs across owners, independent import copies,
failed imports, schemes permission bypass, stale revisions, revocation, file and
layout roundtrips. Direct parallel store calls verify one save succeeds and one
conflicts; restart retains saved documents. Native Chromium is not installed in
this environment, so no native browser/Windows visual acceptance is claimed.
No full financial suite rerun: source is unchanged and checksum verified.

## Windows review

Stop Phase 2, back up the web data folder, extract the complete new program
folder, run Start_Web_Phase3_Windows.bat. Existing default data/accounts are
reused. Do not rerun admin setup. Use the SAME explicit --data path if previously
configured. Open http://127.0.0.1:8787 and choose Open projects & workbooks.
Test the README checklist with two accounts and a two-tab stale-save check.

## Boundaries / next phase

This is document storage, not migrated financial operations. Scheme/settings
configuration uses advanced JSON in this review console; guided calculator
settings remain later work. Workbooks are metadata containers, not a claim of
completed ledger migration. Files are stored, not parsed. Archives are not part
of active-project interchange; no purge/restore endpoint is exposed.
Project interchange JSON is not the existing offline backup format.

Read docs/PHASE3_WORKSPACES.md for API shapes, permissions, request-size limits,
layout reference boundaries and transaction design. docs/PHASE2_HANDOFF.md and
PHASE2_SECURITY.md retain prior security evidence. docs/ARCHITECTURE.md includes
an update clarifying the current single-database document storage decision.
Quota is still metadata, no automatic cleanup. Phase 7 owns enforcement and safe
temporary cleanup. Mobile deferred; hosting Phase 8. No public deployment.

Next: Phase 4 ledger/season adapters. Preserve original dates, material vs freight
CN classification, IPT, Year Link and late Kharif CN in Rabi statements. Use
explicit owned project/workbook scope, retain live transaction authorization and
validate/remap cross-document financial references in the adapter. Do not expose
the offline loopback app or accept client ownership/frozen state.
