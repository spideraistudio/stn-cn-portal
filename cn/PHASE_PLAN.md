# Phase 7.2.1 — map statement products directly from Ledger Audit

Cumulative from Phase 7.2 Billing Rate Audit. New changes require Windows checks;
earlier reported Windows acceptance is retained, never inferred for new features.

Run Ledger Checks now shows clickable unmapped source-product lines and mapping
links in NRV rows. Billing Rate Audit also links unmapped product lines to the
same mapping form. It loads the authoritative statement name, bill/date, quantity,
rate and amount. Printed packing is suggested only if explicit; missing packing
must be entered. Choose saved crop/product or name a new one. Segment/scheme is
chosen separately: creating a product adds only an unconfirmed empty placeholder,
with no billing rate or benefits inferred from the statement.

Save Mapping and recheck retains the audit page and reloads its report. The audit
path does not open/create a calculation draft or replace the current calculation.
It registers owned source evidence and uses the existing source mapping model;
normal imports and future audits reuse it. Mapping existing identities requires
Edit ledger; creating an identity also requires Edit schemes. Ownership,
workbook boundaries, revisions and server-reparsed evidence are enforced. Failed
saves roll back the catalogue, source and placeholder together. Sources remain
protected and explicit project export/import remains independent.

NRV resolves exact confirmed mapping even with overlapping product names. Its
web adapter uses private identity aliases only AFTER original printed-source
multiset deduplication; the preserved NRV functions and financial engine files
are unchanged. Returned source evidence retains the printed names and packing.
Original amounts/dates, tax/reconciliation warnings and CN exclusions remain.
Existing saved/frozen calculations are not recomputed or edited by audit mapping.
Any source-bound draft affected by a new mapping still needs normal source refresh.

COMMON_PORTAL_PROPOSAL.md records the requested shared CN/STN login, company
permissions/subscription model and researched Hostinger options. This is a proposal,
not implemented SSO or a hosting purchase/deployment. Current STN Meet-Dev uses
MongoDB; the earlier MariaDB deployment description must be checked against the
actual deployed version before integration. No STN repository writes were made.

Verification is recorded under verification/audit_mapping_*. Automated HTTP/model
checks, Linux Chromium and ZIP checks are distinct from actual Windows acceptance.
Windows: Ledger Audit → Add PDFs → Run Ledger Checks → click an unmapped product
line → confirm prefilled statement details → save mapping → check the refreshed
report. Repeat from Billing Rate Audit and after restart; confirm saved work/CNs
remain intact. Missing packing must remain blank until explicitly entered.

Back up stopped WEB data, extract the cumulative ZIP into a new folder and run
Start_Web_Phase7_2_1_Windows.bat with the same data path/login. No public deployment.

Earlier release documentation follows as history.

# Phase 7.2 — selectable Billing Rate Audit

Cumulative from the fixed Phase 7.1 release. Prior Windows acceptance and account
checks are retained. New billing-audit changes require Windows acceptance.

Ledger Audit → Add PDFs (or include saved workbook ledgers) → Approved billing
rates → Run Billing Rate Audit only. Add earlier-year PDFs to check returns.
Approved rates use state, saved product, unit and inclusive effective dates.
Add a new period when rates change; do not overwrite the old season. Overlapping
periods for the same state/product are rejected. Rates are workbook-local and
separate from schemes. Editing rates requires Edit schemes permission.

Sales compare approved rates effective on their own dates. Returns compare the
actual original bill rate, even if that original sale was incorrectly billed.
Choose / split original bills lets you assign returned quantity across invoices.
The parser has no reliable original-bill-reference field; even a single candidate
requires confirmation. No FIFO or average is treated as proof. Missing source,
unmapped products, conflicting invoice lines and unavailable rates remain flagged.
Load all earlier returns too: quantity capacity is verified only within available
evidence; unresolved prior returns are explicitly indicated. Each split is checked
individually; offsetting differences cannot cancel. Unit conversion uses confirmed
product packing; amount differences are before separately posted taxes/discounts.

Review finding saves Mistake, Approved exception or Not applicable with a reason;
it does not hide the arithmetic finding. Changed evidence/rates invalidate displayed
review status. Original-bill choices and notes require Edit ledger. Evidence is
reparsed server-side, owner/workbook scoped, revision checked and protected against
deletion. Explicit project export/import retains rates, choices, notes and sources
in a separate project. Audit never edits vouchers, allocations, schemes or CNs.

Automated evidence: verification/billing_cumulative.txt (99 tests), billing_browser.txt
(real Linux Chromium billing UI), billing_offline_browser.txt (original workflow),
and billing_package.txt. Windows acceptance is not inferred from these checks.

Back up stopped WEB data, extract the complete ZIP to a new program folder and run
Start_Web_Phase7_2_Windows.bat with your existing data path/login. No public deployment.
Windows check: enter two seasonal rates; check a wrong sale; return old-season stock
at original and new rates; choose/split original bills; save a review; restart and
reopen. Confirm existing CNs/allocations remain unchanged.

Earlier release documentation follows as history.

# All Crop CN — PC web application phased plan

Baseline: cumulative Update35.2, built from Update35.1. Existing offline Windows
installation stays independent. User acceptance on Windows is not inferred from
an automated test or the decision to begin online work.

| Phase | Deliverable | Acceptance before moving on |
|---|---|---|
| 1 — Foundation (complete) | Preserved engine/source, compatibility inventory, independent workspace mapping, non-destructive retention design and automated tests | Baseline hashes match; existing regression and isolation tests pass; architecture limitations recorded |
| 2 — Accounts and permissions (complete for account APIs) | Admin bootstrap; create/disable users; secure login/session/logout; reset credentials; per-user permission switches; account audit trail | Missing/expired session denied; disabled users blocked; permission changes take effect; direct API bypass tests pass |
| 3 — Independent workspaces (implemented; Windows acceptance pending) | Per-user projects, workbooks, settings, parties, layouts and files; safe backup/export/import; revision/concurrency checks | User A cannot read/write/export User B's data through any endpoint; no automatic merging; safe failed imports |
| 4 — Ledger and season workflow (implemented; Windows acceptance pending) | PDF single/bulk import, mapping, ledger audit, IPT, Year Link and season boundaries | Original dates retained; material/freight CN distinctions; late Kharif CN in Rabi statement tested before claiming support |
| 5 — PC calculation interface (implemented; Windows acceptance pending) | Both existing appearances, receipt workbench, reviewed ABS/CD/Cash allocation, independent dragging, cursor zoom, saved layouts | Preview/cancel never writes; amounts counted once; unused CD release and token-only preview retained; PC browser checks |
| 6 — Finish and reports (implemented; Windows acceptance pending) | Frozen history, separate rounding, finalisation/issue, requested-only adjustments, NRV, CSV and compact individual/workbook prints | Offline/online results agree; issued results stay frozen; reporting exclusions and print verification pass |
| 7 — Storage and operations | Configurable per-user allowance, usage meter, upload reservations, safe 60-day temporary cleanup, backups/restore and audit logs | Concurrent uploads cannot bypass quota; linked/saved records excluded; cleanup retry/failure and restore tests pass |
| 8 — Hosting and acceptance | Production Python service/database/files, TLS, private staging, security/regression checks, pilot accounts and deployment handoff | Real-user PC acceptance; backup restore demonstrated; isolation/permission tests pass in deployed environment |

Phases are cumulative. Keep code and findings in each phase handoff. A phase is
complete only for its stated deliverables; a foundation test is not production
security certification. Hosting configuration and external services may need
owner-provided access during Phase 8. Do not request credentials until concrete
configuration is ready.

## Confirmed product decisions

- Desktop/PC browser only for the initial version; no mobile view work now.
- Each user works independently, with their own saved work and schemes.
- Administrator creates/manages accounts, switches permissions and sets quotas.
- Sharing is explicit export/import into an independent workspace/project.
- Keep both Classic Emerald and Navy Studio and per-user saved layouts.
- Preserve financial maths, original receipt dates, separate CN rounding,
  frozen history and every confirmed feature from the cumulative baseline.
- Existing offline database files are never silently uploaded or overwritten.

## Working defaults that remain adjustable

- “Two months” means 60 days for the initial retention implementation.
- Cleanup applies only to inactive, unlinked cache, temporary previews and
  abandoned uploads. Creation AND last-use must predate the cutoff.
- Saved ledgers/source statements, issued/frozen CNs, schemes and backups are
  retained regardless of inactivity. Explicit deletion is a separate permission.
- No storage size is invented or enforced yet; administrator chooses it per user.
- Admin status does not automatically confer access to another user's ledgers.
  Any future support access must be explicit and audited.

## Planned server-enforced permissions

| Switch | What it controls |
|---|---|
| View workspace | Read only the user's own workspace |
| Edit schemes | Rates, slabs, benefits, products, packing and scheme settings |
| Import statements | Single/bulk PDF and saved statement re-read |
| Edit ledger | Manual entries, mapping, corrections, review classifications |
| Allocate payments | ABS/CD/Cash/settlement preview and apply/clear/release |
| Finalise calculations | Draft validation and frozen finalisation |
| Issue CN | Issue/revision workflow permitted by existing financial rules |
| Export and print | Own workspace exports, CSV, summary and detailed printing |
| Delete records | Soft delete/archive of own permitted objects |
| Permanently delete | Existing guarded purge rules; frozen/issued protection retained |
| Manage users | Account status, permissions, quota; no automatic ledger access |

Scheme-edit restrictions must cover alternate mutation routes too: workbook
imports, project imports, quick scheme creation, product mapping and Cash
configuration shortcuts. Hiding a button is insufficient. Read-only calculation
of an existing scheme remains available unless separately restricted.

## Phase 2 status

Accounts/login/admin controls and central permission enforcement implemented.
Only own-workspace metadata and account APIs are live in the LOCAL review
console; financial endpoints arrive in subsequent phases. No public deployment
or quota enforcement has occurred. See PHASE_HANDOFF.md for current evidence.

## Phase 3 status
Owned document storage, project interchange, file persistence and layout records
implemented for local review. See docs/PHASE3_WORKSPACES.md for the boundary
between stored drafts and later financial engine/UI integration.

## Phase 4 status
PDF import, typed catalogue/mapping, ledger audit/NA reviews, stock-season
classification and reviewed Year Link implemented for local PC review. Ledger
backups now include validated source provenance. Actual allocation/CN calculation
interface integration remains Phase 5; finalisation/issue/report UI is Phase 6.
See PHASE_HANDOFF.md and docs/PHASE4_LEDGER_SECURITY.md.

## Phase 5 status
The preserved Update35.2 shell, both appearances, financial builder and allocation
workbench now use authenticated, owned web calculator storage. Phase 4 source
forms mount inside that shell. Financial source is unchanged. Version 3 project
backups include calculator drafts and separate Classic/Navy layouts. Finalise,
issue, reporting/printing completion remains Phase 6. See
`docs/PHASE5_INTERFACE_SECURITY.md` for projection, permissions and limitations.
Phase 2 Windows acceptance is confirmed; Phases 3, 4 and 5 remain unconfirmed.

Phase 5 mapping correction reuses recognised own-workbook identities and saved
printed-name/packing mappings, groups unresolved reviews, and adds atomic
permission-checked product creation from source review. No scheme terms are
inferred from PDF sale rates. This does not advance Phase 6 or mark Windows
acceptance. See docs/PHASE5_PRODUCT_MAPPING.md.

## Phase 6 status
Finalise/issue/revise, frozen results and validated completed-history interchange,
NRV/CSV, compact/detailed individual and workbook print preparation are now
connected to authenticated owned web storage. Source parties appear directly in
Parties, and saved calculations reload from the backend with an explicit stale
evidence message. See PHASE_HANDOFF.md and docs/PHASE6_FINISH_SECURITY.md.
Starting Phase 6 does not accept Phases 3–5; overall Windows checks remain pending.

Phase 6 review correction: stale-source party redraws and save-guard scope fixed.
No Phase 7 implementation or Windows acceptance is implied. See PHASE_HANDOFF.md.

Phase 6.2 corrects the import-to-calculator transition, immediate source-directory
refresh, visible workflow navigation and saved/stale party detail views. Native
Linux Chromium flows pass, including server restart; Windows acceptance remains
pending. Phase 7 is still on hold. See the current PHASE_HANDOFF.md.

## Phase 6.3 interface correction
The Phase 6.2 alternate source/import screen was not accepted. The calculator
now uses the actual preserved offline page renderers and controls, with native
transport adapted behind them. No extra source setup/log page or disabled pseudo
steps belongs in the normal workflow. Phase 7 remains on hold. Windows acceptance
is still pending; see the current handoff for native Chromium/API evidence.

## Phase 6.3.1 Windows feedback correction

Opening-credit registration now saves as allocation metadata while dated Year
Link receipts stay immutable. Failed saves can retry after correction without
blocking the navigation queue. Original screens and all engine files remain
unchanged. Chromium/backend checks are recorded under verification/phase631_*.
Windows acceptance remains pending; Phase 7 has not started.

## Phase 6.3.2 Windows feedback correction

CD crop allocation is saved as before; product diagram cards now show the shared
funding attribution and selected-receipt highlighting. No change to Update35.2
or persisted allocations. See verification/phase632_*. Overall Windows acceptance
of Phases 3–6 remains pending. Phase 7 remains on hold.

## Phase 7.0 implementation status (23 October 2026)
Acceptance gaps reviewed; only Phase 2 overall Windows acceptance. Mapping and
latest CD cards passed specifically. Storage limits, usage display, serialized
transaction upload reservations, safe registered-temporary startup/daily/manual
cleanup and audit implemented; existing backup/import remains supported. See
docs/PHASE7_STORAGE_SECURITY.md. Prior Phase 7 holds above are historical.
No overall Windows acceptance inferred. Hosting Phase 8; mobile deferred.

## Phase 7.1 cumulative account hierarchy
User confirmed all remaining Phases 3–7 Windows checks. New superadmin/admin/user
hierarchy, scoped resets, default/delegated allowances, Navy-on-login and camera
panning implemented; new Windows checks pending. See PHASE71_ACCOUNTS_SECURITY.md.
Hosting not deployed. Do not request hosting credentials until a concrete private
deployment plan is ready; mobile deferred.
