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

# Phase 7.1 — superadmin, delegated admins and navigation

Cumulative from Phase 7. User confirmed all remaining Phases 3–7 Windows checks;
Phase 2 was already accepted. The NEW Phase 7.1 changes still need Windows checks.

Implemented: original operator becomes superadmin; create admins with 1 GiB own
storage, five user slots and 250 MiB per-user defaults/ceiling; superadmin controls
limits, grants and assignment. Scoped admin user management/reset and live grant
ceilings are enforced server-side. Independent ownership and quotas remain.
Existing users/credentials/quotas/work survive; legacy users stay under superadmin
until explicitly assigned. No reset or data import is needed to upgrade.

Password resets revoke target sessions and force a temporary-password change.
Superadmin recovery uses the protected local operator tool with verified backup.
New login starts Navy Studio; Classic remains selectable within the session.
Empty-canvas left dragging pans Navy while zoomed without moving cards or money.

Stop server, back up WEB data, extract the complete ZIP to a NEW program folder,
run Start_Web_Phase7_1_Windows.bat with the SAME data path/login. Check Phase 7.1
in the calculator sidebar. Read docs/PHASE71_ACCOUNTS_SECURITY.md and its targeted
Windows checklist. No public deployment; hosting preparation remains Phase 8.

Earlier release notes follow as history; old pending-acceptance statements below
are superseded by the user's confirmations recorded above.

# Phase 7.0 — cumulative storage and operations

23 October 2026. Read docs/PHASE7_STORAGE_SECURITY.md for accounting, transaction
reservations, cleanup exclusions, tests and limitations.

Acceptance reviewed first: user confirmed latest CD-card Windows check passed;
specific mapping checks passed. Retain 6.3.1 opening-credit Save/navigation.
Only Phase 2 has overall Windows acceptance. Phases 3–6 checklist remains open.
No unresolved reported defect is silently marked accepted.

Server-side exact logical-byte limits cover all retained payload writes, including
PDF/bulk imports and project restore; concurrent writers reserve through SQLite
BEGIN IMMEDIATE. Failure rolls back the entire operation. Existing over-limit
work is retained and readable/exportable; reductions are allowed. Account and
calculator show usage. Existing admin controls configure per-user allowances.

Safe 60-day cleanup touches only explicitly registered unlinked/inactive/unprotected
temporary blobs. Saved/linked PDFs, workbooks, allocations, frozen history and
recovery data are never aged out. Existing loose caches are not scanned/deleted.
Startup/daily maintenance and own-permission manual cleanup are audited.

Back up stopped WEB data; extract full ZIP into a NEW folder. Start using
Start_Web_Phase7_Windows.bat with the SAME data path/login. Do not reset admin
or clear saved data. Check quota before new imports; encoded PDFs and retained
snapshots count. If full, increase allowance through existing admin controls.
Re-run README Windows workflow checks plus quota rejection/retry, usage display
and temporary cleanup. Automated evidence is under verification/phase7_*;
Windows acceptance is pending. No public deployment; hosting Phase 8, mobile deferred.

Earlier handoff follows as historical context (its Phase 7 hold is superseded).

# Phase 6.3.2 — reflect pooled CD funding on product cards

23 October 2026. Cumulative patch from Phase 6.3.1. Phase 7 is on hold.
Read PHASE_PLAN.md, README.md and docs/PHASE6_FINISH_SECURITY.md first.

User clarified that CD crop allocation saves correctly, but only CD/crop cards
show money; product cards stay at zero. The diagram read only a.product-specific
rows, while reviewed CD crop allocation intentionally persists one segment pool.

The diagram now adds a display share of pooled CD to each eligible product card,
weighted by positive regular_net from canonical result.product_CNs, the same
basis as the unchanged engine's product CD benefit attribution. Largest-remainder
paise attribution keeps displayed shares equal to the displayed segment pool;
stable product IDs break ties. Direct product assignments remain included once,
other allocation types/schemes are excluded, and no weight yields no fabricated
share. CD CN and unused funding continue to come from the engine. This display
never writes allocations, source data, schemes, dates, calculations or history.

Shared CD labels and full hover amounts distinguish attribution from saved direct
splits. Selected receipt highlighting extends to products covered by pooled CD.
A scoped CD card stylesheet fits the labels inside existing card dimensions;
layout keys, positions, dragging, zoom and existing styles are preserved.

Changed web app.js only at allocationStudio product rendering/footnote; the
original intake/ledger/mapping/payment forms and financial assets remain intact.
New cd-card-display.js/css are served from the fixed app asset list.
The 6.3.1 opening-credit save and retry correction remains cumulative.

Verification: phase632_card_model.txt (exact attribution, fractions/large amounts,
no mutation); phase632_cd_cards_browser.txt (actual crop click/preview/apply,
three products, matching totals, both themes/card fit/highlighting, read-only
rendering, party reopen/server restart, capped one-packet excess); calculator
and native HTTP regression reports; original full-screen browser parity and
opening-credit regression; baseline hashes and cursor zoom checks. The targeted
CD-card run uses normal motion; the broader legacy journey uses reduced motion
after headless click-stability timeouts. This is not Windows animation acceptance. Internal
synthetic screenshots are not included in the deliverable. See phase632_package.

Stop the old server, back up WEB data, extract the whole ZIP into a new folder,
run Start_Web_Phase6_Offline_Interface_Windows.bat and confirm Phase 6.3.2. Keep
your existing login/data path and workbook. No admin reset or migration. Windows
acceptance of Phases 3–6 remains pending; Phase 2 alone passed overall Windows
acceptance. No storage cleanup, mobile work, hosting or deployment.

Prior cumulative handoff follows.

# Phase 6.3.1 — opening-credit allocation correction

22 October 2026. Cumulative patch to Phase 6.3. Phase 7 remains on hold.
Read PHASE_PLAN.md, README.md and docs/PHASE6_FINISH_SECURITY.md first.

Windows feedback: payment allocation reports “Source and Year Link evidence
cannot be replaced through Save” and blocks subsequent actions. The original
Allocate available opening credit action appends an undated opening_sources row;
the web Save guard incorrectly rejected every change to that list. Its rejected
saveQueue also prevented actions from reaching the next retry.

The web guard now separates ordinary undated opening-credit allocation metadata
from immutable traced Year Link receipts. Opening sources require Allocate
payments permission; the unchanged engine validates the combined credit cap,
source identities and shared allocation limits. Dates/signatures/carried amounts
cannot be forged through Save. prior_year_link, source, lineage and prior_issued
remain protected. Project validation/rebinding and native source refresh retain
manual sources alongside reviewed Year Link sources. No financial engine change.

The bridge reports a save failure to its caller while settling the queue, allowing
a corrected retained draft to retry through normal Save/navigation. Failed saves
are never presented as saved and drafts are not discarded.

Verification: verification/phase631_allocation_browser.txt exercises the actual
opening-credit button and Settlement/amount controls, Save, all five tabs, Parties
reopen, a deliberate dated-source rejection/retry, and a real server restart.
phase631_offline_browser.txt reruns original import/mapping/bulk/audit/Year Link,
renderer parity and source-only party opening. Backend tests cover rights,
over-cap credit, fabricated/modified traced sources, source refresh and project
transfer. Baseline hashes remain identical. See phase631_* reports.

Stop the old server; back up WEB data; extract the new complete ZIP to a new
program folder; run Start_Web_Phase6_Offline_Interface_Windows.bat. Use the same
existing WEB data path and login. Confirm Phase 6.3.1 in the sidebar. Reopen the
saved party and retry the allocation. Do not clear data or recreate an admin.
Actual Windows acceptance of Phases 3–6 remains pending. Only Phase 2 passed
Windows acceptance; selected PDF mappings passed. No hosting/mobile/deployment.

The Phase 6.3 original-screen handoff follows for cumulative context.

# Phase 6.3 handoff — restore the actual offline interface

22 October 2026. Cumulative from Phase 6.2. Phase 7 is NOT started.
Read PHASE_PLAN.md, README.md and docs/PHASE6_FINISH_SECURITY.md first.
Phase 2 passed Windows acceptance. Specific PDF mapping checks passed, but overall
Phases 3–6 Windows acceptance remains pending. No hosting or public deployment.

## Correct interpretation of the user's requirement

The user explicitly wants the Update35.2 interface/layout/workflow, not a similar
web interface with another import wizard. The Phase 6.2 extra source screen was
not accepted. It showed setup sections/logs and disabled pseudo-step buttons.
That screen is no longer used by the calculator. Do not bring it back.

## Implementation

- The actual preserved Select Party, Check Ledger, Assign Payments, Check
  Benefits, Review & Finish, mapping dialog, Parties, Bulk Import, Ledger Audit
  and Year Link renderers are used directly. The bridge does not replace these
  pages or disable the five step tabs. Original Next/review/payment guards remain.
- Single PDF selection on Select Party saves authoritative source evidence and
  opens the original Check Ledger. No extra preview/apply/setup/log screen.
  Products are mapped inline or through the original Edit Product Mapping dialog;
  new products are added there only when needed. Segment assignment stays with
  scheme selection; an unmapped new product has no inferred scheme benefits.
- Original bulk progress/results and Open Party controls, original audit upload/
  category view, and original Year Link upload/reconciliation dialogs are wired
  to authenticated owned backend actions instead of alternate page mounts.
- Previously saved source-only imports appear in the ordinary Parties list and
  open their vouchers without a separate PDF-party directory. Native transport
  is installed BEFORE initial state loading, including after server restart.
- Inline product mapping is atomic over saved source mappings, catalogue identity
  and the current draft, with existing-product versus new-product permissions.
  Existing entries/dates/manual corrections/allocations are preserved. Known
  mappings and saved crop names are reused; no pricing is inferred from the PDF.
- Source review changes retain the original calculation screens and five tabs.
  A clearly marked stale snapshot is read-only and blocks financial transitions
  until its owned source is refreshed. Source refresh retains unchanged reviewed
  rows, manual rows, allocations and lineage/prior-issued controls. A financial
  source replacement leaves the prior saved draft intact and requires review.
- Date confirmation uses original Settings/working-period controls. PDFs may be
  saved as drafts before season dates are configured, exactly as offline; missing
  confirmed dates still block finalisation. No production dates are invented.
- Original backup and editable project export/import controls use validated web
  project archives. Import creates an independent project, never merges work.
  Native Year Link reparses owned PDFs, retains original receipt dates/caps and
  preserves existing draft allocations. Completed records require revision.
- Phase 6 canonical print/report/CSV and frozen issue protections remain active.
  Storage/cleanup actions still belong to Phase 7. No offline DB is accessed.

## Source changes

- backend/cn_web/native_interface.py: scoped native-screen orchestration,
  source-backed imports/mapping/audit/Year Link, independent project transfer.
- calculator_service.py/http_app.py: native-action routing, owned state, existing
  bulk history, and unconfigured-season draft projection (not finalisation).
- calculator_static/web-bridge.js: transport/canonical record adapter, not pages.
- calculator_static/app.js: only initial bootstrap is deferred until the bridge
  is installed; original page renderers are unchanged. index.html no longer
  mounts the alternate source-panel script. Static advanced legacy ledger files
  and their existing APIs remain preserved for compatibility. Account/workspace
  navigation now leads to the original calculator, not the superseded console.
- Existing CSS, payment workbench, original baseline engine and all 140 baseline
  files remain byte-identical. Both appearances, diagrams, dragging, cursor zoom,
  saved layouts, separate rounding, IPT, Year Link and frozen history remain.

## Verification evidence

- verification/phase63_offline_browser.txt: actual Linux Chromium; exact renderer
  function comparisons to the offline source; both appearances; all five original
  tabs clicked; inline mapping; ordinary party reopen; real server restart/fresh
  browser context with exact voucher/date/mapping/allocation retention; original
  Bulk Import, Ledger Audit and Year Link flows; first-load source-only party
  compatibility. No uncaught page errors or failed workflow APIs.
- verification/phase63_full_web.txt: cumulative backend HTTP/security suite.
- verification/phase63_native_http.txt: native transport tests, including source
  ownership, live permissions/CSRF, no date edits, atomic new mapping permission
  failures, existing mapping reuse without scheme rights, placeholder schemes,
  repeat/bulk imports, changed source/late IPT, canonical audit/year evidence and
  independent project interchange. Browser-supplied source arithmetic is ignored.
- verification/phase63_offline_regression.txt: unchanged offline-engine suite.
- Transport model, baseline hashes, JS/Python compilation, zoom geometry and ZIP
  extraction/startup checks are retained under verification/phase63_*.
- Linux Chromium testing is not Windows acceptance. A visual comparison was made
  on synthetic data only; internal screenshots are not included in the package.

## Windows update and acceptance

Stop the previous server and back up WEB data. Extract to a new program folder;
run Start_Web_Phase6_Offline_Interface_Windows.bat. Keep the existing login and
WEB data path. Confirm the sidebar says Phase 6.3. The standalone offline install
stays separate. Do not recreate an administrator or clear workbooks/data.

Check: New Calculation → Import Tally PDF → original Check Ledger; click all five
original tabs; map any unresolved product within Check Ledger; reopen a saved
party after restart; check the original bulk/audit/Year Link screens. Review the
README checklist. Keep Phase 7 on hold until Windows feedback is addressed.

Previous unaccepted workaround: docs/PHASE62_HANDOFF.md.
