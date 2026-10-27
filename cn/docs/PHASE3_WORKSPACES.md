# Phase 3 independent workspaces

Local development only. Phase 2 account console accepted on the user's Windows
PC. Phase 3 native browser/Windows acceptance remains pending.

## Data model and migration

Startup adds one workspace_documents table/index in the existing web account
SQLite database, without replacing accounts or sessions. Rows use composite
(owner, id) keys. The existing random directory registry remains available for
later engine adapters; this phase stores document/file bytes transactionally in
SQLite rather than introducing filesystem mutation and split-database commits.
No offline data is opened, rewritten or uploaded. Back up the web data folder
with the server stopped before an update. Continue using the SAME --data path
(or default %LOCALAPPDATA%\AllCropCNWeb) to retain Phase 2 accounts.

Projects contain workbooks and optional project-wide schemes/settings/files.
Parties and layouts require a workbook. Every child lookup validates its owned
parent graph. Names and filenames are display values only, never disk paths.
Files retain exact bytes using canonical base64. They are stored, not parsed or
executed. PDF import/ledger population is Phase 4. Workbook fields in Phase 3
are metadata; this is not a replacement financial database schema.

Configurations are opaque draft dictionaries for future adapters. The review
console offers advanced JSON for these saved documents; the guided financial
settings editor is not migrated yet. Financial snapshots, receipts, allocations,
issue state and ledger entries have no generic write endpoint. Never hand an
unvalidated Phase 3 configuration directly to the engine in a later phase.

## API

All APIs require a live session, completed password change, view_workspace,
exact Host, no query parameters and existing same-origin guards. Mutations
require JSON, Origin and CSRF. No user/path selector is accepted.

- GET /api/data/{kind}: own active objects, with project/workbook scope metadata.
- POST /api/data/{kind}: {data, project?, workbook?}; server generates identity.
- GET /api/data/{kind}/{id}: own object and current revision.
- PATCH /api/data/{kind}/{id}: {revision, data}; full validated replacement.
- DELETE /api/data/{kind}/{id}: {revision}; archive only, never purge.
- GET /api/projects/{id}/export: versioned one-project backup.
- POST /api/projects/import: {backup}; creates a new independent project.
- GET /api/files/{id}/download: attachment bytes, export_print required.

Kinds: projects, workbooks, schemes, settings, parties, files, layouts.
PATCH cannot change ownership, parents, kind or status. Archive rejects active
children. No restore/purge endpoint is exposed. Backups include active documents
only, not archived objects. They are project interchange, not a full server
account disaster-recovery backup or an offline Update35.2 import format.

## Permission and transaction boundaries

Projects/workbooks/parties: edit_ledger. Schemes/settings: edit_schemes.
Files: import_statements. Layouts: view_workspace (nonfinancial preference).
Archive: delete_records, plus edit_schemes for schemes/settings. Export/download:
export_print. Import: import_statements AND edit_ledger AND each included kind's
write permission. Thus a scheme-bearing backup requires edit_schemes, even if
rates are unchanged. No administrator ledger bypass exists.

Every read/write/export resolves ownership in SQL. Mutations recheck current
session/permissions inside BEGIN IMMEDIATE on the same database as accounts,
serializing account revocation with writes. Stale revisions return 409 without
changing any data. Audit writes share the mutation transaction and log only
object IDs, kind and count, never payloads or file content. Imports validate the
entire graph, reject unknown top-level/document fields and remap every object ID.
All imported rows and audit commit together; an error leaves no partial project.
No account/session/role data is exported or accepted as project metadata.

## Layout preservation

Layout documents hold theme classic/studio, record_id, positions and locked.
Coordinates and unique card identities are validated. Separate workbook and
owner scope protects identical record IDs. Export/import preserves content and
coordinates exactly. The two existing financial interfaces and their existing
saved-layout implementation remain unchanged in offline_baseline; live online
allocation UI integration is Phase 5. Imports remap storage/parent IDs only;
record_id/card keys remain uninterpreted until the Phase 5 adapter.

## Limits and future work

Allowance remains metadata. No quota accounting/enforcement, automatic deletion,
temporary-file cleanup, hosting or mobile work. JSON transport limit is 16 MiB
for workspace requests, 16 KiB for account APIs. This is a request parser bound,
not a user storage allowance. The review picker permits files up to 10 MiB.
Large/multi-file project backups can exceed the import request limit; streaming
and reservation-aware upload handling belong to Phase 7. Unbounded listing is a
local-review limitation; pagination/operational scale checks remain future work.
The account database holds document content, so operator backups must protect
that file and must not be used as cross-user interchange exports.
