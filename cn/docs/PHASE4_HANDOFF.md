# Phase 4 handoff — 22 October 2026

Implemented for local PC review, cumulative from Phase 3. Phase 2 was accepted on
Windows by the user. The user requested the next phase; this is not recorded as
Phase 3 or Phase 4 Windows acceptance. No public deployment or mobile work.

## Delivered

- Real preserved Tally text/detailed PDF adapters, single/combined/multiple PDFs.
- Preview/cancel writes nothing. Apply is atomic across source files, parties,
  ledgers and audit; exact repeats are idempotent; changed statements need explicit
  reviewed replacement. Earlier sources are immutable history.
- Workbook-local catalogue and period forms, source product/packing suggestions,
  existing-product mapping and stock/CN classifications with review reasons.
- Season stock summary: supply, return, IPT in/out, net supply, net sold and kg.
  Late IPT can be assigned once to the reviewed season within its cutoff.
- Late Kharif scheme CN/return review during Rabi; posting dates/balances stay
  unchanged and reviewed Kharif CNs are excluded from the Rabi scheme-CN list.
- Category-first baseline ledger audit, original-evidence not-applicable notes,
  freight/Journal/material distinctions and read-only baseline NRV analysis.
- Preserved April–March Year Link validation, explicit remaining original receipt
  amounts, opening-credit cap and original dates; no automatic ABS allocation.
- Ownership/session/permission/revision checks on every new API. Mutations
  reauthorize inside the account-database write boundary after PDF parsing.
- Version 2 project interchange includes ledger state and source files. Imports
  reparse source PDFs, validate reviews/mappings, rebuild year-link proof, remap
  all stored IDs and layout references, and create an independent project.
- PC forms linked from Accounts and My workspace; PDF setup and new launcher.

## Preservation and migration

All 140 Update35.2 files still match the baseline manifest. No financial engine,
original receipt date, separate CN rounding, issued/frozen history, offline data,
baseline appearance or baseline saved-layout file changed. Phase 3 data remains.
Startup adds only ledger_workspaces in the existing web-only SQLite database.
Linked PDFs cannot have their bytes changed/deleted through generic document
routes. Their names and party/workbook display metadata can still be edited.

## Verification

verification/phase4_final.txt: 45 tests passed in 61.532 seconds: all 37 cumulative
account/foundation/workspace tests and eight new real-HTTP ledger tests.
verification/phase4_ledger_release.txt: eight ledger tests passed in 27.452
seconds on the final targeted rerun after
small validation and reporting-label refinements. Baseline hash, Python compile,
JavaScript syntax and final ZIP integrity checks passed.

Coverage includes 49-party/329-voucher combined PDF import, preview cancellation,
failed batches, repeat/changed source handling, cross-user/admin denial, live
permission revocation during parsing, stale apply, source protection, packing
identity, season/late-CN/return/IPT separation, original receipt dates, Year Link
cap, audit NA evidence, independent project import, tampered-backup rejection,
Year Link/mapping/layout restoration and restart persistence. Fixtures include
preserved baseline PDFs and clearly synthetic Phase 4 PDFs. No live private
workbook, credentials or CN issue was used.

Native Chromium is unavailable here. No native-browser/Windows visual acceptance
or security certification is claimed. Full financial tests were not rerun because
all financial source is unchanged; baseline hash verification is current.

## Windows review

Stop the previous server; back up the WEB data directory. Extract the full ZIP
into a NEW program folder. Run Setup_PDF_Windows.bat if the selected Python lacks
pdfplumber. Run Start_Web_Phase4_Windows.bat. Existing default accounts/data are
reused; do not bootstrap an admin again. Custom --data users keep the SAME path.
Open http://127.0.0.1:8787 → Open Ledger & Seasons. Follow README acceptance checks.

## Boundaries and next phase

This phase reviews source ledgers/seasons; it does not calculate/finalise/issue
new CNs. Source amount/quantity corrections, manual entries, guided financial
settings and ABS/CD/Cash interfaces are next. Baseline financial UI/source remains
preserved; live online calculator interface integration is Phase 5.

Season tags are draft provenance metadata. The Phase 5 adapter must translate
these into compatible calculation inputs without rewriting original dates,
changing ledger balances or modifying the preserved engine. Preserve late-IPT,
source-conservation and issue-conflict checks. Do not infer successful Rabi CN
calculation from this phase's stock-summary tests alone.

Phase 3 opaque settings/schemes remain saved, but are not automatically promoted
into validated financial settings. The new typed catalogue has no benefit rates.
The next adapter must validate financial configuration and enforce scheme-edit
rights on every shortcut/import/mapping/configuration mutation.

Read docs/PHASE4_LEDGER_SECURITY.md before Phase 5. It documents current API
shapes, transaction/provenance boundaries, archive protections, backup format,
posting-date audit vs season review and parser limits. Historical handoffs are
retained under docs. Quotas remain metadata; safe temporary cleanup/enforcement
Phase 7. Hosting Phase 8. Mobile deferred. No public deployment.
