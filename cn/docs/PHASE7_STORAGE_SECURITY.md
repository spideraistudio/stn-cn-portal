# Phase 7.0 — storage and operations

23 October 2026. Local PC release; no hosting or mobile changes.

## Acceptance review before implementation

The latest CD product-card Windows check is passed (user confirmation). The
specific mapping checks remain passed. Phase 6.3.1 opening-credit Save/navigation
is retained. Only Phase 2 has overall Windows acceptance. No new unresolved defect
was supplied; Phases 3–6 still need the README Windows checklist. Beginning this
requested work does not accept those phases or claim Windows verification.

## Accounting and reservation

Administrator-configured allowance is now enforced for every account SQLite
transaction, across document CRUD, PDF/bulk/source imports, independent project
restore/import, calculator saves, history, settings and layouts. Logical usage is
UTF-8 payload bytes across workspace_documents, ledger_workspaces and
calculator_workspaces plus registered temporary blob bytes and link metadata.
Base64 PDFs count at their actual stored encoded size. Archived/soft-deleted
records still count. Shared database pages/indexes/WAL, session/security audit,
program files and external operator backups are not charged to users. This is
logical retained storage, not a physical disk-space guarantee.

BEGIN IMMEDIATE acquires an exclusive writer reservation before inspecting usage
or changing data. A commit checks exact resulting retained bytes against the
current allowance while still holding that reservation. Other workers/processes
cannot spend this capacity concurrently. This deliberately uses transaction
reservations rather than expiring upload leases. Crashes roll back automatically.
Validation/parse failures and quota failures leave no partial saved source,
calculation, project or audit writes. Existing bounded JSON/decompression limits
remain; request/parse memory is not user disk storage. The local server continues
to serialize requests; tests also exercise a threaded HTTP server and independent
SQLite writer connections. No new arbitrary file-path upload endpoint exists.

Lowering an allowance never deletes data. Existing over-limit data can be read,
exported and reduced; growth is refused with HTTP 413 and an actionable message.
The account screen and calculator sidebar show used/allowed MiB. The account
screen refreshes usage on refresh/sign-in; calculator usage refreshes when its
navigation redraws. Administrators use existing account allowance controls.

## Cleanup boundary

Only storage_temporary registry blobs can be age-cleaned. They must be a known
cache, temporary_preview or abandoned_upload category, inactive, unprotected,
unlinked and BOTH created and last used strictly older than 60 days. Saved
PDFs, linked evidence, allocations, workbooks, history, schemes, recovery data and
backups are outside this table and cannot be selected. Unknown loose files and
legacy caches are intentionally untouched; no filesystem walk or unlink occurs.
Current PDF previews are in-memory responses and do not need disk cleanup.
Future durable caches must use this trusted server registry and mark links,
protection and active use in the same write transaction before handing out data.
No browser API may register arbitrary temporary paths or reclassify saved files.

Local launcher cleanup runs at startup and once per 24 hours while running;
manual POST /api/storage/cleanup requires live own-workspace Delete records
permission and CSRF. The account page offers this action. Automatic maintenance
is a trusted server operation across registered temporary objects, without
opening user ledgers. Removal and per-object audit commit atomically. A failure
rolls back; retry is idempotent. Background cleanup failure keeps the server
available and retries after 60 seconds; malformed/unknown metadata is retained. Logical bytes are released; SQLite may retain
free pages for reuse (no disruptive automatic VACUUM).

## Recovery and verification

Keep the existing stopped-server WEB folder backup procedure and validated
independent project export/import. No financial data migration. Quota rejection
rolls restore back atomically; raise the allowance and retry. Existing frozen
history proof, ownership, permissions and original engine validation are retained.
This release adds no automated physical whole-server backup service. Shared DB
payload scans under the writer lock favor correctness over throughput for this
local PC stage; production optimization belongs to Phase 8.

See verification/phase7_* for actual new test output. Earlier phase632/631 browser
reports are prior evidence, not fresh Windows acceptance. The unchanged baseline
hash check is rerun. Windows acceptance of this release is still required.
