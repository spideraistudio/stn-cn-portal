# Phase 6 — finish, frozen history and reports

22 October 2026. Cumulative with Phase 2–5 ownership/session/source rules.
This is local PC development and automated verification, not production security
certification or a claim of Windows/native-browser acceptance.

## Scope and transactions

All calculator actions authenticate a live session, require view_workspace,
resolve the project and workbook under that owner and use the existing account
SQLite write transaction. Financial functions run in an independent in-memory
Store; the original offline server and database are never opened. On success,
changed tables and account audit commit atomically. Failure discards the private
runtime and rolls back the account transaction. No client owner/path is accepted.
Record revision is checked at transitions. Original receipt dates cannot change.

## Permission matrix

| Operation | Additional rights |
|---|---|
| record, calculate, workbook-review | Read-only own workspace |
| finalise | finalise |
| issue | issue_cn |
| revise | finalise + edit_ledger |
| report, territory-report, product-csv, print-record, workbook-print | export_print |
| Existing mapping / new product | edit_ledger / edit_ledger + edit_schemes |
| Scheme/group assignment or scheme override | edit_schemes |
| Project import | Existing import/ledger/scheme/allocation requirements |
| Import finalised / issued history | Above plus finalise / finalise + issue_cn |

Administrator status does not give cross-owner access. Direct API, Save,
allocation shortcuts, import and alternate printing/export routes retain their
permission checks. Dashboard attention uses workbook-review; actual workbook
printing uses workbook-print. Read-only financial results do not require
permission to mutate a scheme. No quotas or cleanup are enabled.

## Finalisation and source projection

The unchanged Store.finalise/engine validates and freezes the saved draft.
Requests supply only the owned saved ID and expected revision. Browser-computed
results, frozen settings and historical calculation envelopes are not accepted
through Save. All calculation issues block finalisation; separate benefit
rounding and display-only requested changes remain engine-owned.

Source drafts revalidate the bound ledger/reviews, working periods and Year Link.
The Phase 5 authoritative stock-season mask is reapplied. Store.finalise reads
SQLite directly, so its private settings row is temporarily given the same
calculation-only stock envelope used by ordinary Phase 5 calculations. The saved
workbook settings row is restored before commit. Frozen settings retain actual
working-period dates; the exact historical calculation envelope is separately
stored in web_calculation_settings for reproducible validation. Original source
and voucher/receipt dates are unchanged. ABS/CD date windows are never extended.

The result's stock_scope excludes records whose stock items are all authoritatively
masked out. This preserves source-based late returns/IPT without admitting them
into two seasons. Manual standalone calculations use unchanged baseline semantics.

Frozen results return their stored history even when live settings or source
reviews later change. Issuing a formerly finalised source snapshot requires its
source binding still to be current; otherwise revise/review the new evidence.
No frozen record is recomputed from today's schemes just to view or print it.

## Issue and revisions

The unchanged Store.issue checks status, revision, positive proposed adjustments,
cumulative already-issued identities, late IPT and traced opening-credit limits.
The web adapter additionally scans all of the owner's workbook/project snapshots,
including archived/deleted history, in the same account transaction. Different
lineages cannot issue overlapping party/benefit periods or reuse selected physical
stock/IPT. Physical source comparison ignores map IDs and numeric display formatting.
Traced opening receipt use is capped across the owner's workbooks. Independent
users are not combined. Mark issued records application history; it sends no
posting or message to Tally or any external application.

Store.revise keeps the completed parent and its issued entitlement ledger. The
new draft must reconfirm its current ledger; negative revised benefits remain
blocked. For updated sources, the adapter follows the saved replacement chain,
loads current reviewed evidence/Year Link, preserves manual vouchers and unchanged
row corrections, updates product identities, and requires financial review of new
or changed rows. When evidence is unchanged, existing corrections are retained.
Old snapshots and their original dates/settings remain untouched.

## Reports, CSV and printing

The unchanged reporting/territory functions receive only active workbooks in the
selected owned project. A neutral empty legacy slot satisfies their interface;
it contains no offline/private data. Latest completed lineage/season snapshots
win; draft revisions do not hide earlier completed history. Duplicate completed
product/period rows are excluded with review notes. HQ derives from saved PDF
Group evidence, never an invented address-based classification.

Configured-billing NRV, product/unit conversions, weighted aggregation and
freight/journal/requested-only exclusions stay in the preserved reporting code.
Phase 4's posted-ledger-CN report remains separately available through Ledger Audit.
CSV uses preserved formula escaping, full numeric precision and UTF-8 BOM.

Product CSV and individual print preparation retrieve canonical saved records and
revision, ignoring browser-supplied calculations or result fields. Compact and
detailed HTML use the existing UI functions and print CSS. Workbook selection
uses the preserved digest and one-version-per-party/season rules. Draft source
results use the authoritative web projection; frozen snapshots use saved results.
Printing/attention selection never finalises or issues a record. Native A4/Windows
print layout still requires the user's checklist.

## Completed project interchange

Format v3 remains compatible with prior draft-only exports and now supports
completed snapshots. Validation reparses source PDFs, preserves originals,
validates settings through the unchanged Store, and recomputes frozen arithmetic
with the stored actual/calculation settings. Results with issues, missing proof,
wrong totals, missing revision parents, unproven prior issued amounts or inconsistent
cumulative issued controls are rejected before committing any new project.
Importing completed/issued history requires the transition permissions listed
above, in addition to existing import/configuration permissions. This is explicit
history import, not acceptance of a browser-supplied frozen result through Save.

Import remaps workbooks, source ledgers, records, parent/lineage references,
issued-control record IDs and separate appearance layout IDs into an independent
project. It does not merge another user's data or revive stale source evidence.
Frozen results remain readable if their original source reviews later changed.
The source project is unchanged; future duplicate-issue checks still scan all
of that owner's projects.

## Party reopening

State now exposes owned saved-PDF party metadata independently of calculation
drafts. The Parties screen offers a saved-statement path before a draft exists.
Open / Continue retrieves the saved record through POST record, rather than using
only a cached browser list. Changed source evidence returns retained party/voucher
details and a review message plus the current replacement source ID. Missing old
statement selections do not silently open an unrelated party. Known stale drafts
cannot autosave over newly reviewed source evidence while navigating the shell.

## Verification boundary

See PHASE_HANDOFF.md and verification/phase6_*. Automated checks cover arithmetic,
transitions, ownership, permissions/CSRF, restart/reopening, frozen/late source
history, backups/tampering and report/print selection. All baseline source hashes
and preserved appearance/interaction assets match. DOM/HTML model tests do not
establish native rendering or Windows acceptance. Phases 3–6 overall Windows
acceptance remains pending. Storage/cleanup is Phase 7, hosting Phase 8, mobile
deferred; no public deployment.

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

## Phase 6.2 import/reopen integration

The source panel refreshes the owned shell state after a committed source change.
Single-party apply continues via the same server-authorised open-source action;
multiple parties require an explicit party button. No source dates, schemes,
benefits, ownership, review, issue or finalise rules are changed by this routing.
Missing working periods remain an explicit user choice, not an inferred season.
Saved source selectors and the existing five-step components are used in-place.

The bridge checks canonical source freshness before saving a source draft during
navigation. A stale snapshot is retained and shown read-only with its actual saved
vouchers and allocation values. Current calculated benefits are not fabricated
from stale evidence. The record/project/workbook stale guard and backend save
validation remain active. Frozen/issued history is unaffected by live source
notifications. Detached source views do not replace a newly selected workspace.

Real Linux Chromium tests now exercise the real DOM, event listeners and HTTP
flow, including a server restart and fresh browser context; Windows acceptance
remains pending. See verification/phase6_import_flow_browser.txt and the current
handoff. No Phase 7 storage enforcement/cleanup or deployment is included.

## Phase 6.3 — original-screen transport

The original offline screens call native-* calculator actions. No offline HTTP
server/database is opened. Every action still resolves the live account, owned
project/workbook and source objects; every mutation retains CSRF, revision and
permission enforcement. GET native-state adds canonical source-only party rows
for display only; it does not fabricate persisted calculation records.

Single/native bulk imports use the preserved parser and authoritative owned
PDF/source storage. Changed statements require explicit replacement review.
Inline native-map atomically updates canonical identity mapping and the current
draft; existing identity reuse requires Edit ledger, new identity creation also
requires Edit schemes. No PDF sale rate is converted into a scheme term.

Native audit/year operations reparse owned saved PDF references server-side;
browser-supplied source entries/amounts are ignored. NA reviews and crop/product
CN attribution bind to owned source evidence. Year Link retains original dates,
reconciliation/remaining-credit caps and existing draft allocations. Independent
project transfers reuse the established full graph/frozen-arithmetic validation.
Compressed uploads have bounded decoding; nothing is merged into the current
project. Importing completed/issued history retains the transition rights.

Unconfirmed-season imports may be stored/viewed as drafts. This does not supply
confirmed production dates or permit finalisation. Stale-source display is
explicitly provisional and read-only; frozen records return stored results.
Refresh retains allocations, unchanged source corrections and prior-issued
lineage; old drafts remain when the physical source is replaced. The ordinary
Save/transition endpoints still reject stale/fabricated provenance and date edits.

Evidence: phase63 native HTTP tests, real Linux Chromium with exact renderer
comparisons, cumulative security tests and unchanged offline regression. Windows
acceptance is pending. No storage cleanup, hosting or public deployment occurs.

## Phase 6.3.1 — opening-credit Save boundary

The Save guard formerly treated the entire opening_sources array as immutable
Year Link proof, blocking the original opening-credit allocation action. Manual
sources may now carry only id, amount and a null/absent date. They require Allocate
payments permission, including changes without an allocation row. The preserved
engine enforces total opening-credit capacity, unique source identities, nonnegative
amounts and shared allocation limits. Dated sources require canonical reviewed
Year Link receipt evidence, compared exactly against the saved/owned source.
prior_year_link, prior_issued, lineage, source and web_source protections remain.

Backup/import validation applies the same distinction and rebinds canonical linked
proof while retaining manual sources. Native refresh retains manual registrations
alongside canonical linked receipts. The browser queue settles after failure only
for retry scheduling: the initiating caller still receives the error, edits remain
in memory, and navigation retries Save before leaving. No error is labelled saved.
No engine/baseline changes, storage cleanup or deployment. Windows acceptance
remains pending; see verification/phase631_* for automated evidence.

Year Link transfer compares the complete financial proof in canonical JSON form
so Decimal values from a PDF reparse match saved numeric strings. An old audit
display filename is ignored; dates, amounts, identities, signatures and reviewed
remaining balances are still compared. New native links use the registered source
documents directly. This also corrects a pre-existing native Year Link backup
validation mismatch.

## Phase 6.3.2 — CD product-card attribution

The browser derives product-card shares from canonical result regular_net values
and existing CD pool rows. Direct rows are counted once, pooled shares are marked
Shared CD, and paise remainders are assigned deterministically. Attribution is
display only: no new Save/API mutation or permission bypass is introduced. No
engine, source, original date, Year Link, rounding, frozen proof or allocation
row changes. Missing/zero positive weights do not fabricate a distribution.
Existing CD preview/apply, usage/cap/release and benefit computations remain the
server authority. New assets are included in the fixed app asset whitelist.

## Phase 7 cumulative note
The financial boundaries above remain. Storage enforcement/temporary cleanup is
now implemented; historical “no quota/cleanup” statements describe Phase 6 only.
See PHASE7_STORAGE_SECURITY.md. Latest CD-card Windows check passed specifically;
only Phase 2 has overall acceptance. Other Phases 3–6 checks remain pending.
