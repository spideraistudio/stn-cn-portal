# Phase 5 — authenticated Update35.2 interface adapter

22 October 2026. Read the Phase 2, 3 and 4 security documents as cumulative rules.
This is local PC development, not a production security certification.

## Interface and transport

`/calculator` serves the existing offline shell, menus, forms and guided financial
builder. The preserved CSS, studio art/font, diagram implementation, payment
workbench, Cash options and appearance scripts are copied without redesign.
Only shell labels, owned scope initialization, authenticated transport, and
source-workflow mounts change. Import/audit/Year Link forms reuse Phase 4 handlers
inside the original shell instead of navigating to the temporary console.
Account administration and Phase 3 document management remain separate links.

`web-session.js` maps original calculator requests to `/api/calculator/{action}`.
There is no fallback to `/api/save` on the offline server. Cookie authentication,
live session restrictions, exact Host/Origin, CSRF and JSON limits remain central.
Layout query IDs are carried in a header so the existing no-query API rule stays.
Only the calculator HTML allows inline style values, needed for original dynamic
card/SVG positions; scripts remain external-only. Account pages keep their strict
style policy. Every identifier/header is a lookup selector, never an identity.

## Owned runtime and atomic commits

`calculator_workspaces(owner, workbook, revision, payload)` is added to the same
web-only SQLite database. A fixed-schema JSON snapshot holds the unchanged
Store tables: records, settings history, audit, issued and bulk_imports.
Each request reconstructs an independent **in-memory SQLite** Store. No temporary
financial database, user-controlled filesystem path, global current-user Store,
offline HTTP handler or offline application server is used.

An account-database write transaction authenticates the live session, checks
view_workspace and operation permissions, resolves both owned project/workbook,
runs the private runtime, and commits its fixed table rows plus account audit.
A failure rolls back everything. Preview actions do not persist the runtime.
No account/private data is written on the initial state read. Initial source
catalogue scheme IDs are deterministic until the first permitted financial save.

Record revision, settings version and original allocation fingerprints retain
the baseline concurrency/preview protections. Admin status does not grant access
to another user's calculator. Generic workbook/project archive is blocked while
calculator history exists. Saved scheme/record tombstones and frozen baseline
files remain intact; this phase cannot issue or finalise online CNs.

## Permission matrix

All actions require view_workspace and owned project/workbook resolution.

| Actions | Additional rights |
|---|---|
| state, calculate, validate-limits, validate-scheme | none; read-only |
| settings, sync-catalogue | edit_schemes; changed source periods also edit_ledger |
| product-delete / scheme-delete | edit_schemes + delete_records |
| open-source, manual ledger fields and reviewed corrections in save | edit_ledger |
| allocation-only save deltas, ABS/CD/Cash preview/apply/clear/release | allocate_payments |
| scheme overrides / Cash deduction configuration in saves | edit_schemes |
| late-ipt-review | edit_ledger; Phase 4 source decisions remain authoritative |
| party-delete | delete_records; guarded baseline preview/confirm semantics |
| workbooks (independent financial setup) | edit_ledger + edit_schemes |
| ui-preferences | view_workspace; own saved record required for layout writes |
| project export | export_print |
| calculator-bearing project import | import_statements + edit_ledger + edit_schemes + allocate_payments |

Whole-record Save compares allocation and ledger fields against the owned stored
record, preventing a user without allocation rights from writing allocations
through a ledger shortcut. Scheme overrides/Cash deduction changes are checked
separately. Settings imports and offline restore shortcuts cannot bypass scheme
rights. No browser-supplied owner, frozen result or issued status is promoted.
New manual receipt originals are captured server-side; existing posting dates
cannot change. Manual ledger corrections need the existing review reasons and
reconciliation checks. Supplied source/Year Link metadata cannot replace stored
provenance through Save.

## Phase 4 source and season projection

Open-source takes saved ledger ID, saved season and current Phase 4 revision.
It reads the source, mappings/reviews and reviewed Year Link server-side. The
record contains a binding to source digest, reviewed periods and Year Link.
Calculation/allocation rejects stale evidence. Opening changed evidence creates
a separate draft; previous source/drafts are retained rather than overwritten.
Source originals, posting dates, receipt dates, amounts and full ledger closing
are retained. Source originals cannot be omitted from saved/imported records.

For a source-bound calculation, the adapter constructs a **calculation-only
stock envelope** from the selected period's original start through cutoff.
It reapplies an authoritative item mask from each Phase 4 stock-season review:
explicit assignment wins, otherwise original start/end determines inclusion.
Items belonging to another season are excluded with a reason. This permits a
late return to remain a return (including return-bonus behaviour), and includes
reviewed late IPT once, without changing any original date or quantity or the
financial engine. Saved/UI working-period dates are not extended; ABS booking
and CD windows remain the configured scheme dates. Manual standalone records
continue to use the original period logic, with no source envelope.

Late-IPT assignment/cutoff is validated in Phase 4 before projection. Future
Phase 6 issue integration must still enforce cross-issued stock/receipt overlap,
late-IPT conflict, traced-credit conflict and frozen-history checks; this phase
does not expose an issue endpoint that could bypass those checks.

Posted Kharif CNs remain ledger credits in Rabi. Phase 4's source summary retains
scheme/freight/journal/material distinctions and explicit season review. This
phase does not reinterpret posted CN as a new receipt or automatically deduct it
as a newly-issued Rabi scheme benefit. Actual posted-CN NRV remains the read-only
Phase 4 report; online issue/report completion belongs to Phase 6.

Financial settings are validated with the unchanged baseline Store validators.
Source catalogue groups begin with empty, unconfirmed benefits, not invented
production rates. Existing product crop/segment/packing and saved period dates
remain protected. Guided financial saves synchronize typed catalogue metadata;
newly added source products/periods can be loaded explicitly. Phase 3 arbitrary
scheme dictionaries remain saved and are never automatically activated.

## Layouts and project interchange

Layouts reuse Phase 3 owned layout records. Classic's `record::classic` and Navy's
`record` keys remain separate. Position coordinates/keys/lock/theme are validated.
Record/layout data survives restart. No financial permission is required to move
cards or save appearance. UI selection/zoom itself makes no financial mutation.

Project format v3 extends v1/v2 with calculator_bundle. Current Phase 5 snapshots
contain drafts only; fabricated issued/finalised snapshots are rejected. Imported
settings use unchanged financial validation; records validate bounds, source
originals, voucher conservation and Year Link evidence. Source PDFs still reparse
through Phase 4 validation. Records, workbooks, projects and ledger IDs are remapped,
including both appearance layout keys. Earlier project copies are never modified.
Stale source bindings stay stale after import; import does not approve new source
evidence. No account/session/quota/permission metadata is exported.

Web JSON project import is supported. Offline .cnwork/SQLite archive restoration
is deliberately not mounted. Back up the entire WEB data folder with the server
stopped for operator recovery. The 16 MiB JSON and existing PDF parser bounds are
transport limits, not per-user quota enforcement.

## Verification and remaining acceptance

Real HTTP tests exercise ownership/admin denial, sessions/CSRF, direct-save and
import permission bypasses, revision/digest conflicts, preview nonmutation,
ABS/CD/Cash engine parity, CD surplus release, July ABS rejection, source-season
projection, original dates/Year Link cap, independent backup/import and layout
restart. Source CSS/workbench/studio files are byte-compared with Update35.2.
The preserved full offline regression suite and baseline hash check are also run.
Node VM transport/menu checks and the existing cursor-geometry harness are model
checks, not native-browser rendering or Windows visual acceptance.

A native browser is unavailable in this environment. Windows layout, dragging,
calendar, scrolling, imported-form display and real-workbook acceptance remain
pending. Phase 2 alone has user-confirmed Windows acceptance. Phase 6 still owns
finalisation/issue/report/print controls. Quotas/cleanup Phase 7; hosting Phase 8;
mobile deferred. No public deployment.

## PDF mapping correction

See `PHASE5_PRODUCT_MAPPING.md`. Import stores only unambiguous own-workbook
product identities. Saved choices are derived from active validated ledger
mappings with the same printed name, unit and detected packing. Conflict blocks
automatic reuse. Neither recognition nor manual mapping mutates the source or
derives financial scheme terms.

The owned, revision-checked POST `resolve-mappings` requires Edit ledger and fills
only unresolved items. POST `mapping` accepts exactly one of existing product_id
or new_product. The latter additionally requires Edit schemes, validates typed
catalogue metadata and commits product + mapping atomically. Same-name scope
compares name/unit/packing and validates each affected item. Both routes require
view_workspace and owner/workbook resolution; admin status grants no cross-owner
access. GET remains read-only.

PDF-backed calculator Save rejects direct product/packing/crop/segment divergence
from the saved draft's source identity. UI controls route source identity changes
through the saved statement panel and subsequent open-source action. Previous
drafts remain preserved by the existing source-staleness contract.

Saved crop/segment choice lists resolve only from the authenticated owner's
selected workbook catalogue and latest saved calculator settings. New product
creation canonicalizes existing crop/segment spelling and prevents a second
identity for a unique name/crop/packing merely because a different optional
segment was selected. No-segment products seed the unchanged Awaiting scheme
placeholder; product_assignments is now permission-checked with scheme overrides
on every Save/allocation shortcut. Existing saved assignment calculation remains
read-only and available without permission to change the assignment.
