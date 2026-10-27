# Phase 4 — owned ledger, audit and season adapters

22 October 2026. Local PC development review only; no hosted endpoint.
Read PHASE2_SECURITY.md for account/session/CSRF/Origin/Host protections and
PHASE3_WORKSPACES.md for the existing document layer.

## Runtime and persistence

`LedgerService` invokes the preserved Update35.2 import, audit and Year Link
functions. The baseline path is fixed application code, never a request path.
The offline HTTP server and offline Store are not mounted or used. No mutable
current-user/current-workbook object exists. No original financial file changed.

Startup adds `ledger_workspaces(owner, workbook, revision, payload)` in the same
web SQLite database as account/session/document state. One state holds that
workbook's validated catalogue/periods, immutable parsed source ledgers, review
notes, product mappings, evidence-bound audit reviews and reviewed year links.
All transactions resolve the owned workbook and project through DataStore.
Administrator status grants no access to another user's data.

A workbook state revision protects the complete review/config/import boundary.
Changing one ledger invalidates stale saves from another tab in that workbook.
Existing Phase 2/3 rows, accounts, sessions, schemes/settings and layouts remain.
Phase 3 arbitrary scheme/settings draft dictionaries are retained; they are not
silently activated as financial configuration. This phase's typed product
catalogue is saved per workbook and contains no benefit rates/slabs.

## APIs

All routes begin `/api/ledger/workbooks/{owned-workbook-id}`. Existing sessions,
mandatory password changes, exact Host/Origin, CSRF and JSON guards apply. No
query-based identity selection, user header or raw filesystem path is accepted.
POST read/preview routes also require CSRF because they use the existing POST
contract. Every operation requires view_workspace plus the permission below.

| Method / suffix | Purpose | Additional permission |
|---|---|---|
| GET / | Catalogue, periods, ledger metadata, link status | none |
| GET /ledgers/{id} | Original evidence plus effective draft review | none |
| PUT /config | Revision + catalogue and/or periods | edit_schemes for catalogue; edit_ledger for periods |
| POST /preview-import | Revision + files; read-only parsed batch preview | import_statements + edit_ledger |
| POST /apply-import | Same files/revision + preview_digest, replacements/reason when needed | import_statements + edit_ledger |
| POST /mapping | Revision, ledger_id, entry_index, item_index, product_id, optional same_name | edit_ledger |
| POST /review | Revision, ledger_id, entry_index, review | edit_ledger |
| POST /reread | Revision + ledger_id; re-read saved PDF, no mutation | import_statements |
| POST /summary | Ledger_id + saved season | none |
| POST /audit | Start/end, optional owned ledger_ids | none |
| POST /audit-review | Revision, start/end, review_id, reason, optional reset/ledger_ids | edit_ledger |
| POST /year-preview | Revision, previous_id, current_id, optional identity_reason | none |
| POST /year-apply | Same + confirmed original receipt amounts and reason | edit_ledger |

PDF files use `{name, content_base64}` or an owned saved `{file_id}`. Stored files
must belong to the same project and this workbook or the project-wide scope.
Physical source PDF filenames are display values, never storage paths.

## Import boundaries

Preview parses all selected files without writing files, parties or ledgers.
The batch is rejected if any ledger fails parsing; remove/correct that file and
retry. Valid combined-party PDFs are supported. A running-balance mismatch is
preserved as a warning/review need, never silently repaired.

The digest binds source bytes, owned workbook, state revision, file revisions
and parsed document signatures. Apply reparses the input and verifies it. PDF
work happens outside the account write lock; apply then rechecks the live session,
permissions, owned workbook and revisions inside BEGIN IMMEDIATE. All source
files, party rows, ledgers and audit commit together. Revocation during parsing
prevents commit. Invalid/stale operations leave no partial files/parties/ledgers.

Repeated exact imports are idempotent. Different statements for an existing
party/reporting period require an explicit replacement selection and note.
Previous source versions remain immutable history with superseded_by metadata.
Only exactly unchanged voucher content carries review/mapping decisions to the
replacement; changed/new or ambiguously repeated rows need fresh review.
Two different same-party/same-period files cannot be applied in one batch.
Active statements drive audit/default selection; earlier history remains readable.

Linked PDF content cannot be replaced or archived through the generic Phase 3
API. A filename change retaining identical bytes is allowed. Linked parties and
workbooks can retain editable display metadata, but cannot be archived while
ledger history exists. No financial snapshot/issue/allocation mutation is added.

## Catalogue and season reviews

Mapping can only select an existing typed product. Product/packing creation
requires edit_schemes. Detected explicit packing must match the selected product,
keeping DAWAT 1 kg and 3 kg separate. Source quantities/rates/amounts and source
originals never change through mapping. Source fractional packets/negative stock
quantities are flagged for review in the summary rather than silently rounded.

Period names and dates/cutoffs are explicit, saved and non-overlapping; no season
or state is guessed. Once source ledgers exist, existing period dates and product
crop/segment/packing identities cannot be silently reinterpreted; add another
period/product. Catalogue labels and aliases can be updated with scheme rights.

Voucher reviews have only kind, season, cn_class, crop and a required reason.
They cannot write a source date, original, balance, amount or issued/frozen state.
Existing receipt type/date cannot be reassigned to a benefit season. Posted CN
classifications are scheme, freight or other; material returns are stock vouchers
with source item quantities. Journal CNs cannot be mapped as eligible scheme CNs.

Season stock includes only that period's source stock or an explicit reviewed
season assignment. A late IPT assignment must be after that period's end and on
or before its cutoff. A reviewed IPT belongs to exactly one season in that source
ledger; it is excluded from the posting season's stock summary. Supply, IPT in,
IPT out, returns, net supply, net sold and net kg are separate values.

Late Kharif CNs posted during Rabi retain their November date and ledger credit.
An explicit Kharif benefit-season review excludes them from Rabi's scheme-CN
list. Unreviewed posted scheme CN seasons are flagged, never guessed. These are
ledger/season review outputs; actual Rabi benefit/CN calculation is Phases 5–6.
Full ledger opening/closing continues to include every posted entry once.

## Audit and Year Link

Audit uses the unchanged baseline's multiset union for overlapping statements,
exact payment-reference/narration checks, strict material-return matching, mixed
rate checks and complete-period IPT coverage. Categories are shown before
individual findings. Not-applicable decisions require a note and a server-
recomputed evidence ID for the exact selected posting-date range and current
workbook revision. Reviews cannot fabricate arbitrary findings. Audit reviews
are ledger rights, independent of scheme-edit permission.

Audit is by posting date. Season stock is by explicit season review. Keep those
purposes distinct when reviewing a late CN. The baseline audit's posted-CN/NRV
analysis is read-only and retains its freight/journal/material exclusions; it is
not the final Phase 6 reporting interface.

Year Link calls analyse_pair/attach_link on owned source IDs, never client-supplied
ledger documents. Full previous April–March coverage, next 1 April current start,
identity/location reasons, reconciliation and closing/opening equality are checked.
The user confirms the unspent amount per original receipt. The preserved engine
caps the combined sources at actual opening credit, keeps original dates and
creates no second receipt or automatic ABS allocation. Replaced source ledgers
mark saved links stale; later calculation adapters must block use until re-reviewed.

## Cumulative backup

`/api/projects/{id}/export` returns version 1 for document-only projects and
version 2 plus ledger_bundle when workbook ledger state exists. Version 1 imports
still work. Version 2 includes source files, prior source versions, review/mapping
records, audit notes, catalogue/periods and Year Link evidence. Import requires
edit_schemes, edit_ledger and import_statements for ledger-bearing state.

Before write, every source PDF is reparsed and matched by document signature;
backup-supplied originals/balances are not trusted. Reviews/mappings are validated
against the parsed entries and catalogue. Year Link proof is rebuilt from the
validated PDFs and confirmed receipt amounts. All project/document/workbook/
ledger/file/party IDs are remapped. Layout record_id is remapped when it refers
to a known imported object; card positions/theme/lock are retained. Source voucher
IDs and product identities stay stable within the independent workbook.

Import creates a new project; nothing merges into another user's active data.
No account, session, administrator, quota or permission data is exported.
The complete web data directory, backed up with the server stopped, remains the
operator recovery backup; project interchange is not an account-registry backup.

## Limits and remaining work

16 MiB workspace JSON transport bound; 10 MiB PDF batch picker bound; up to 30
files per request. These are transport/parser limits, not per-user storage quota.
Allowance enforcement, reservations, streaming, safe temporary cleanup and scale
controls remain Phase 7. No auto-deletion, mobile or public deployment.

The local wsgiref runner processes PDF requests synchronously. The UI reports file
preparation progress and an indeterminate PDF-reading stage; it does not invent
server-side parsing percentages. Background job execution/hosted operations are
later work. Scanned PDFs/OCR and unknown layouts are rejected explicitly.

Next adapters must retain immutable source dates and the distinction between
source ledger balances, stock season reviews and proposed benefit amounts.
Phase 5 owns guided financial settings, manual amount/quantity corrections,
manual entries and ABS/CD/Cash UI; Phase 6 owns frozen CN/issue/report workflows.
Translate Phase 4 season-review metadata into compatible calculation inputs
without moving receipt dates or mutating the baseline engine. Reuse its late-IPT
and cross-issued source-conflict checks when issue workflows are enabled.
