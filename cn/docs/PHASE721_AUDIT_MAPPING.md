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
