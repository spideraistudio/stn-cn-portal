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

# All Crop CN Web — Phase 7.0

Cumulative PC-only release with server-enforced per-user storage and safe
60-day temporary cleanup. Use Start_Web_Phase7_Windows.bat after backing up
stopped WEB data and extracting to a new folder. Keep your current login/data path.

Storage usage appears in Account and calculator navigation. Existing administrator
account controls set allowances. Encoded PDFs, saved payloads and archived data
count; shared DB overhead and external backups do not. A full allowance rejects
the entire change; existing work remains available. Raise allowance and retry.
Clean eligible temporary data on Account requires Delete records permission;
startup/daily cleanup never ages out saved work. Unknown legacy files are untouched.
See docs/PHASE7_STORAGE_SECURITY.md for details and verification limits.

Only Phase 2 has overall Windows acceptance. Specific mapping and latest CD-card
checks passed; Phases 3–6 and new Phase 7 Windows acceptance remain pending.
Run the seven workflow checks below plus usage, rejected upload/retry after quota
increase, and cleanup preservation. Earlier release notes follow as history;
Phase 7 hold statements below are superseded by this explicitly requested work.

# All Crop CN Web — Phase 6 finish and reports

PC-only local review, cumulative from corrected Phase 5. Keeps Classic Emerald,
Navy Studio, the existing forms/workflow, allocation diagrams, dragging,
cursor-focused zoom, saved layouts and the unchanged Update35.2 financial engine.

## Phase 6.3.2 — show pooled CD on product cards

After Allocate CD to crop / segment, its product cards now show their funding
shares instead of ₹0. Shares use regular net sold, matching the existing product
CD benefit attribution, and add up to the pooled allocation at displayed paise
precision. “Shared CD” identifies this display attribution; hovering shows direct
and shared amounts. The selected payment also highlights the covered products.

The saved CD allocation remains one segment row. No extra payment, product split,
benefit, eligibility rule or CN rounding is introduced. The crop total already
includes these shares. Preview excess remains available; unused saved CD can be
released through the existing controls. Both appearances, card positions and saved layouts remain in place.

Verify on Windows: select a receipt, click its crop under CD, Preview and Allocate
usable; check all relevant product cards, totals, reopening and both appearances.
Automated evidence is under verification/phase632_*. Windows acceptance remains
pending and Phase 7 remains on hold.

## Phase 6.3.1 — payment allocation save correction

Fixes the Windows feedback: allocating opening credit no longer raises “Source
and Year Link evidence cannot be replaced through Save”. Undated opening-credit
sources use the original shared credit cap; traced Year Link receipts keep their
protected amounts, original dates and evidence. Saved allocations survive reopen,
server restart, source refresh and independent project backup/import.

A failed save reports its error but no longer permanently rejects the save queue.
Correct a validation error and Save or navigate again to retry; unsaved edits are
retained. There is no data reset or migration. Update35.2 is unchanged.

Verified with real Linux Chromium allocation controls and backend security tests;
Windows acceptance remains pending. Phase 7 remains on hold.

## Phase 6.3 — the original offline interface

This release removes the extra web import wizard from the calculator. It uses
Update35.2's actual screens and layout, including the original five clickable
steps, inline mapping dialog, Parties, Bulk Import, Ledger Audit and Year Link.

**Select Party → Import Tally PDF → Check Ledger.** There is no additional
Products & Packing setup, Parties & Ledger Review screen, or source log panel.
New products are added from the original mapping dialog only when required.
Existing recognised products/saved mappings are reused. Scheme selection remains
in the original workflow. Normal financial/review guards still apply.

Previously imported source-only parties appear in the normal Parties list. Open
Party / Ledger reloads their saved vouchers. Both interfaces and saved layouts
remain available. The sidebar identifies this release as **Phase 6.3.2**.

Native Linux Chromium and backend tests are included; Windows acceptance remains
pending. Phase 7 storage/cleanup is still deferred.

## Windows update

1. Stop the existing web-server window and back up the WEB data folder.
2. Extract the complete ZIP into a NEW program folder.
3. Run Setup_PDF_Windows.bat if needed, then Start_Web_Phase6_Offline_Interface_Windows.bat.
4. Confirm the sidebar shows Phase 6.3.2. If it does not, close the old server and
   start this folder’s launcher again. Sign in at http://127.0.0.1:8787 using your existing account; open Calculator.

Default WEB data stays at %LOCALAPPDATA%\AllCropCNWeb. If you use a custom path,
keep the SAME path: python manage_web.py start-local --data YOUR_EXISTING_PATH.
Python 3.10+ is required. Do not bootstrap another administrator for an existing
installation. Do not overwrite the separate offline installation/data.
Local admin recovery instructions remain in docs/ADMIN_LOGIN_RECOVERY.txt.

## Continue a party

Select the saved project/workbook and open Parties, then Open Party / Ledger.
This uses the ordinary offline party directory and opens the saved vouchers.
New Calculation — name/address only deliberately starts an empty draft.

For a new single-party PDF, start a calculation and select Import Tally PDF; it
opens Check Ledger directly. Bulk Import PDFs keeps the original bulk screen and
Open Party result buttons. Repeat/changed statements receive explicit review;
they do not silently replace completed history or discard saved destinations.

If another tab changed source evidence, the original five screens still show
saved work with a source-review warning. Open updated ledger refreshes the owned
draft while retaining corrections/allocations for review. Completed/issued
calculations keep their frozen settings/results and use Create Revision.

## Mapping and schemes

Known products and saved printed-name/packing mappings are reused from the
user's own workbook. Use Check Ledger → Edit Product Mapping for unresolved
items; saved crop choices avoid duplicate names. Product mapping is separate
from scheme/segment assignment. Choose Scheme / Group or Create Scheme for This
Product uses the original controls. A new product has no inferred benefits or
billing terms. PDF rates are evidence only.

Mapping an existing identity requires Edit ledger. Creating a new product or
changing scheme terms requires Edit schemes as well. Users own their data;
administrator rights do not open another user's calculations. Date confirmation
remains in Settings; an unconfigured draft cannot be finalised.

## Finish, issue and reports

Complete Check Ledger, Assign Payments and Check Benefits, then Review & Finish.
All blocking issues must be resolved before finalisation. Finalise freezes the
calculation and settings. Mark issued records the CNs in this application; it does
not post them to Tally. Existing duplicate controls and separate rounding apply.
Create Revision retains the old frozen version and deducts previously issued CNs;
review the current ledger and payment destinations before finalising a revision.

Reports provides completed product totals, weighted NRV and CSV filters within the
selected project. Dashboard shows State → HQ → Party. NRV uses configured billing
less calculated scheme CN; freight/journal credits and requested-only adjustments
are excluded. Phase 4 Ledger Audit separately reviews posted CNs and source NRV.

Compact and detailed party prints, product CSV, report CSV, and workbook summary/
detailed printing are enabled with Export and print permission. In the Windows
print dialog choose Save as PDF when needed. Workbook printing selects one saved
version per party/season; drafts are explicitly provisional. Requested CN
adjustments remain display only and never alter issue totals or NRV.

Projects & workbooks supports independent project JSON export/import, now including
validated finalised/issued history. Importing completed history requires Finalise;
issued history also requires Issue CN, plus normal import/configuration rights.
The original project stays separate. Keep a stopped-server WEB data backup too.

## Windows checks for this release

1. Start New Calculation, import one PDF and confirm the original Check Ledger
   opens directly. There must be no separate Products & Packing, Parties & Ledger
   Review, or source setup/log screen. Click each of the five original tabs.
2. Check known mappings reuse automatically; use the original mapping dialog for
   an unresolved name, then choose its scheme/group separately.
3. On a party with opening credit, click Allocate available opening credit,
   choose the allocation type/amount and Save Draft. Check Back, Next and the five
   tabs respond. Restart, reopen the same party and verify vouchers, original
   dates, supply/returns/IPT, mapping and allocations. Reviewed Year Link dates
   must stay intact, and total allocations must stay within available credit.
4. Check the original Bulk Import progress/results and ordinary Open Party button.
   Check Ledger Audit categories and the April–March Year Link dialogs.
5. Finalise a valid calculation, print summary/detailed working and export CSV.
   Verify separate CN rounding, per-unit values, NRV and display-only requests.
6. Change live schemes: completed results must stay frozen. Recheck issue once,
   duplicate-issue blocking, revision/prior-issued values and independent project
   export/import. Revoke rights and verify server-side denials.
7. Recheck Classic Emerald/Navy Studio, diagrams, dragging, cursor-focused zoom
   and saved layouts. No administrator/account recreation is needed.

Only Phase 2 has overall Windows acceptance. Specific mapping checks passed;
overall Phases 3–6 Windows acceptance is pending. Native Linux Chromium checks
and backend results are in PHASE_HANDOFF.md and verification/phase631_*. Storage
and cleanup belong to Phase 7; hosting is Phase 8; mobile remains deferred.
