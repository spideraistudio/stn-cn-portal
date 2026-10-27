UPDATE35.2 - CURSOR-FOCUSED DIAGRAM ZOOM
21 October 2026. Cumulative from Update35.1. Windows acceptance pending.

CHANGE
In Payment Allocation, point at a card or diagram area and turn the mouse wheel.
Navy Studio now keeps the point under the cursor in place while zooming instead
of always zooming around the payment hub. The hub remains fixed in diagram
coordinates, but can move on screen as the view zooms towards another card.
Classic Emerald retains its existing cursor-focused scroll zoom.
Fit diagram restores the complete centred view. Reset layout also resets the
zoom focus. Dragging, collision checks, lock and saved card positions remain.
Zoom changes only the camera; it does not move individual saved cards.

INSTALL ON YOUR EXISTING WINDOWS CALCULATOR
1. Close the calculator AND its console window.
2. Extract this ENTIRE ZIP.
3. Run Update_CN.bat and select app.py in your existing working calculator folder.
4. Reopen with your normal launcher. Use Ctrl+F5 if old controls are cached.
The cumulative updater creates a safety backup and updates program files only.
Do not replace or remove your existing data folder. No earlier update is needed.

CHECK ON WINDOWS
Open Payment Allocation in Navy Studio. Point at an off-centre crop/product
card, wheel up then down: the point under the cursor should stay in place.
Try a second card, then Fit diagram. Check drag, lock and saved layout reload.
Switch to Classic Emerald and check wheel zoom and background panning.
Update35.1 remains included: Preview -> review -> Allocate usable saves;
Close/Cancel saves nothing. User Windows acceptance of both updates is pending.

PRESERVATION
Only static/studio.js, static/app.js (toolbar wording) and static/index.html
(asset refresh) changed at runtime from Update35.1. All Python/backend modules,
financial rules, receipt dates, separate CN rounding, frozen history, settings,
allocations, both interfaces and saved layout storage are unchanged. No database
migration. No online/mobile/accounts/storage-cleanup changes are included.

VERIFICATION THIS UPDATE
PASS: production Studio zoom/layout geometry harness: cursor anchors in all four
quadrants and centre, repeated zoom in/out, min/max clamps, Fit reset, redraw,
unchanged card coordinates/saved layout, Classic delegation. This is a simulated
geometry test, not a native browser or Windows test.
PASS: eight existing UI/API suites using an isolated temporary database.
PASS: thirteen updater backup/preservation/rollback tests.
PASS: two stable-control regression tests; JavaScript syntax checks.
PASS: only the three listed runtime files changed; source/program parity.
Full financial tests were not repeated because no financial module changed.
Historical Update35.1/35 test evidence remains below/in verification files.
A native Chromium download failed in this environment, so new native visual
verification was unavailable. Windows/WebView2/user acceptance remains pending.


--- HISTORICAL EVIDENCE ---

UPDATE35.1 — ALLOCATION PREVIEW FEEDBACK
21 October 2026. Cumulative from Update35. Windows acceptance pending.

User screenshot: CD segment was not selected (Choose segment), amount offered
was Rs500,000, and receipt availability was Rs100,000. Preview correctly could
not allocate, but errors were sent to a page toast underneath the modal top
layer, so the dialog appeared unresponsive. Close correctly cancelled.

FIXES
Messages while a dialog is open now appear persistently INSIDE that dialog.
CD preview validates segment, receipt and positive amount; availability uses
the existing exact allocation limit check. Messages retain entered fields and
explain how to correct them. No allocation is saved on an invalid preview.
The preview button shows Preparing preview while processing, then re-enables
on errors. Successful preview explicitly says Review figures, then Allocate
usable to save. Cancel or Close saves no allocation. Navy action-bar contrast
is corrected and browser asset versions refreshed.

USE
1. Select a sold crop/segment/scheme from the dropdown.
2. Choose the receipt. Enter an amount within that receipt's remaining balance.
3. Preview allocation. Review usable funding, excess, date/rate and CN.
4. Click Allocate usable to save. For another segment, use another reviewed split.
The receipt's original date selects its configured CD rate; no date promotion.

VERIFICATION
Native Chromium reproduces missing segment and excessive amount, confirms each
message is visible inside the dialog, retains the input and offers no apply
button on invalid preview. Corrected inputs preview/apply successfully. The
complete Update35 release/segment/ABS workflow passes in both interfaces with
unchanged ledger dates, cancellation safety and no JavaScript errors.
Eight existing UI/API suites and thirteen updater checks passed for this fix.
Update35's 332 Python and five native suite results remain historical evidence;
no financial/backend module changed, so financial tests were not repeated.
Runtime parity/preservation and ZIP integrity verified. Windows acceptance pending.

PRESERVATION
Only static/app.js, static/payment-workbench.js, static/style.css and
static/index.html changed at runtime. All backend rules/modules, saved data,
settings, original dates, allocations, both themes and card controls retained.
No database migration. Cumulative backup-first updater included.

INSTALL
Close calculator AND its console. Extract whole ZIP. Run Update_CN.bat and
select app.py in your existing working calculator folder. Reopen normally;
Ctrl+F5 if needed. Existing saved data and settings are retained.


--- UPDATE35 HISTORY ---

UPDATE35 — CROP/SEGMENT ALLOCATION AND UNUSED CD RELEASE
21 October 2026. Cumulative from Update34.1. Windows acceptance pending.

HOW TO USE
Select a receipt in Payment entries & allocations. Click the Maize (or other
crop) card below ABS or CD, or use the prominent Allocate by crop / segment
buttons in the payment workbench. Multiple sold schemes require your choice;
SingleCross, DoubleCross and other schemes are never silently merged.

CD SEGMENT PREVIEW
Enter an amount to offer. Preview shows original receipt date, actual CD rate,
amount used, amount to save, excess left available and resulting CN. Products
covered by the segment and their existing displayed CD attribution are listed.
Apply allocates only the usable funding; excess stays with the same receipt
for another crop/segment or documented Settlement. CD continues to pool across
all eligible products of that segment. It is not duplicated per product and no
new product-wise CD limit is introduced. Product CN attribution remains the
engine's existing distribution of the separately rounded segment benefit.
If this receipt already funds CD in the same segment, its last processed split
is topped up; the same capacity is not funded twice via a new sorted row ID.
New rows follow the existing original-date processing rules; manual CD order
is respected with new rows appended after existing manual priorities. An earlier
receipt can affect a later receipt's unused amount; the preview warns about it.
A zero-rate receipt is shown explicitly and never promoted to a better slab.

UNUSED CD IS VISIBLE
Direct CD rows show allocated, actually used, unused, applicable rate and CN.
The receipt list also flags unused CD still assigned. Release unused opens a
preview and returns the releasable amount to the SAME receipt. Other splits,
receipt dates, ledger entries and rounded benefit entitlements are preserved.
Cancel applies nothing. A fraction of a paisa can remain assigned; retaining
up to the next paisa for ordinary rupee allocations preserves full entitlement.
Rows with no used funding are removed when release is confirmed. Reallocation
is a separate explicit choice; it does not move money automatically.

ABS PRODUCT DISTRIBUTION
Clicking the ABS crop or segment opens the existing reviewed automatic ABS
split. It uses regular net sold, packing, token rates and remaining product
capacity, with existing Cash quantities and ABS splits respected. The table
shows each product's requirement, proposed split and excess. Excess ABS keeps
its confirmed routing to that segment's FIRST CD slab. It is not treated as
unused direct CD or released by the new CD action.
When the offered ABS amount exceeds token requirements, an optional Preview
token requirement only button recalculates at the required token amount. Apply
that preview to leave the rest available for another explicit destination.

TESTED USER EXAMPLE (SYNTHETIC, REFERENCE SETTINGS)
Ranbanka 200 packets, 32D12 8 packets, Legend 15 packets at 4 kg = 892 kg.
At reference token Rs50/kg, total remaining ABS requirement is Rs44,600:
Ranbanka Rs40,000, 32D12 Rs1,600, Legend Rs3,000, assuming no returns/Cash/prior ABS.
An offered Rs100,000 ABS preview shows Rs55,400 excess; token-only preview leaves
that amount available instead. A May Rs100,000 CD receipt uses the existing
12% reference window against the combined eligible SingleCross balance; all
three products are shown, money counted once. Actual workbook rates prevail.

PRESERVATION / SECURITY
engine.py, store.py, settings.py, abs_distribution.py, cash_quantity.py,
importers, printing, existing themes/layout controls and financial rules are
unchanged from Update34.1. New server preview/apply reads the saved authoritative
draft, checks revision and settings/selection fingerprint, local authentication
and project/workbook scope. Frozen/deleted work cannot be modified. The updater
is backup-first; saved data/settings and all earlier features are preserved.
No database migration, date reconstruction or automatic cross-scheme transfer.
Both interfaces retain independent card-body dragging, fixed hub, collision
prevention, lock, reset, zoom and saved layouts. Inline editor contrast improved.

VERIFICATION
332 Python tests passed, including 13 new allocation/HTTP cases covering one-
packet caps, three-product pooling, readonly previews, release preservation,
old dues, original dates/zero rates, top-ups, stale/frozen/invalid inputs and scope.
Eight existing UI/API suites passed. Five native Chromium suites passed:
new crop/segment/release workflow, Update34 payment/Cash workflow, Studio drag,
regular Cash controls and Update33 workflow attention. Final new workflow rerun
includes both themes and final inline-editor styling; screenshots reviewed.
Thirteen updater backup/preservation/rollback checks passed. Runtime preservation,
source/program parity and ZIP integrity verified. Windows/WebView2 execution
and user acceptance of this update remain pending.

INSTALL
Close calculator and server console. Extract the whole ZIP. Run Update_CN.bat
and select app.py in your EXISTING working calculator folder. Reopen normally;
Ctrl+F5 if needed. For a fresh copy read source/START_HERE.txt. This ZIP contains
programs and tests, not your private saved work. Do not replace your data folder.

CONTINUE
Implementation complete. Read this handoff, STABLE_BUTTON_FIX.md and TEST_RESULTS.
Continue cumulatively from Update35 and preserve all confirmed rules and data.


--- UPDATE34.1 AND EARLIER HISTORY ---

UPDATE34.1 — DRAG CARDS FROM ANYWHERE
21 October 2026. Cumulative from Update34.

Fix: Update34 required the small Move handle. Cards now drag from their body,
text, icon or Move handle. Hold the left mouse button, move, then release.
A stationary click still opens allocation controls. Layout must be unlocked;
click Unlock layout if shown. The payment centre stays fixed, cards stop before
overlapping, and Save layout retains positions. Both interfaces are supported.
The handle is larger and browser assets have refreshed version identifiers.
No financial, storage or settings rules changed. Existing saved layouts remain.

Verification: native Chromium payment/drag and Studio compatibility suites;
whole-card movement, one card at a time, fixed hub, collision, click allocation,
lock, save/reload and financial preservation checked. Windows acceptance pending.
All Update34 test evidence remains historical in verification files.

Apply: close calculator and console; extract whole ZIP; run Update_CN.bat;
select app.py in the existing calculator folder; reopen; Ctrl+F5 if needed.
Next queued phase remains Maize small-product allocation usability.

--- UPDATE34 HISTORY ---
UPDATE34 — PAYMENT WORKBENCH AND INDEPENDENT CARD CONTROLS
21 October 2026. Cumulative from Update33. Windows acceptance pending.

PAYMENT WORKFLOW
Calculate CN -> Payment Allocation now starts with a receipt-wise workbench.
Select a payment to see its original date, available amount, assigned amount,
remaining amount and all its allocation splits together. Add allocation, Edit
and Remove are accessible beside the selected payment. Graph destinations
funded by that payment are highlighted; the graph still shows the whole party.
Assigned funding and benefit actually used are distinct figures.
The selected receipt is retained when adding allocations. An ineligible ABS
receipt is blocked rather than silently replaced by another receipt. Adding Cash
funding from a second receipt does not silently edit the first receipt's funding.
Existing automatic ABS distribution and reviewed Cash quantity workflows remain.

CLEAR AND START AGAIN
Remove one row, clear the selected payment, or clear all party allocations.
A read-only preview shows affected rows, released amounts and before/after CN.
Cancel changes nothing. Apply checks the saved revision and preview fingerprint.
Cash quantity and its funding are linked by scheme/product. Removing such a row
clears the entire linked Cash group, including funding from other receipts;
those additional rows are explicitly listed before confirmation. Released money
returns to unallocated, not automatically to ABS or another scheme. Original
ledger entries, receipt dates, opening dues and balances are retained. Frozen
and deleted records are protected. Normal save revision/audit behavior remains.

CARD CONTROLS — BOTH INTERFACES
Drag the visible Move handle to move one card independently. Clicking the card
still selects allocation controls. Cards cannot overlap; the payment hub stays
fixed. Lock/Unlock layout, Reset and Save layout are available. Positions and
lock state are saved separately for Classic and Navy. Existing Navy layout keys
are retained. Classic background pan/zoom and Navy hub-centred zoom remain.

PRESERVATION
No changes to engine.py, store.py, settings.py, cash_quantity.py or
abs_distribution.py. All previous financial rules, PDF fixes, compact individual
and workbook printing, project isolation, cleanup, guarded deletion, workflow
attention, both themes, saved work and settings remain. No database migration.
The cumulative updater makes a backup and replaces program files only.

VERIFICATION
319 Python tests passed, including allocation clearing, API scope/authentication,
Cash group release, stale/frozen guards, ledger preservation and UI preferences.
Eight existing UI/API suites passed. Four native Chromium suites cover payment
workbench, Cash controls, Studio controls and Update33 workflow compatibility.
Final payment/Studio rerun covers both themes after Classic pan preservation.
Twelve updater preservation, backup and rollback tests passed. Source/program
parity and unchanged calculation modules checked. Internal screenshots reviewed.
Windows launch/WebView2 and user acceptance of Update34 remain pending.

INSTALL ON EXISTING CALCULATOR
Close the calculator and its server console. Extract the entire ZIP, run
Update_CN.bat and select app.py in your EXISTING working calculator folder.
Reopen with your usual launcher; Ctrl+F5 if the browser has cached old controls.
Do not replace your data folder. For a fresh installation, use source/START_HERE.txt.

NEXT PHASE — MAIZE SMALL-PRODUCT ALLOCATION (NOT CHANGED HERE)
User scenario: Ranbanka 500 packets, 32D12 8 packets, Legend 2 packets.
Review how to show usable funding and unused allocation at scheme level so small
products do not require guesswork. Existing automatic ABS distribution already
splits across eligible products by remaining token capacity; CD already pools
by scheme. Confirm actual workbook rules/rates and quantity exclusions before
changing any financial behavior. Never duplicate a payment across products.

RESUME
Update34 implementation and automated checks complete. Continue cumulatively;
read this handoff, STABLE_BUTTON_FIX.md and TEST_RESULTS.txt. Preserve confirmed
rules, both interfaces, saved settings and data. Windows acceptance pending.


--- HISTORICAL UPDATE33 AND EARLIER NOTES ---

UPDATE33 — WORKFLOW, CASH SHORTCUTS & WORKBOOK ATTENTION
20 October 2026. Cumulative from Update32. Windows acceptance pending.

SCOPE: User selected comparison recommendations 3, 4 and 5 only.
No new calculation explanations, zero-benefit narrative, revision comparison,
PDF diagnostics or alternative payment table are introduced in this update.

1. STEP STATUS AND NEXT ACTION
The existing five steps now show status: needs attention, complete, checks
passed, ready to review/finish, blocked or awaiting issue. These are derived
from the existing engine checks and saved status, not an employee approval.
A Next Action banner opens the relevant existing correction workflow.
Finalised/issued records route to Review & Finish and remain frozen.

2. REGULAR + CASH CONTROLS
Selected scheme cards in Select Party / Check Benefits now show whether Cash
is configured, with Configure Cash option / Edit Cash settings. This opens the
existing scheme builder directly at Benefits with Cash controls in view.
The scope notice explains that saving edits the workbook's scheme for its
active drafts. Completed calculations retain frozen settings. After saving
from this shortcut, return to the party's Check Benefits step.
Party allocation controls now say Allocate Cash quantity / Edit Cash quantity
and payment, and Remove party Cash allocation. All existing reviewed preview,
apply and removal behavior remains. No stock or payment is auto-allocated.
Cash removal still releases funding to unallocated; it does not move it to ABS.

3. WORKBOOK ATTENTION
Dashboard -> Work needing attention loads a read-only saved-work snapshot.
Filters: All, Product mapping, Ledger/party review, Payment allocation,
Calculation blocked, Ready to finish, Awaiting issue, Issued.
Open takes the employee to the current calculation's first relevant correction
or final review. One latest populated version per party/location/season is
shown, matching workbook print selection. Older versions remain in History.
Refresh attention list updates the snapshot. Stale responses after project or
workbook navigation are discarded. Deleted parties/other workbooks excluded.
Import history is separately expandable: failed and review attempts are shown
with their existing messages and Bulk Import/review links. Historical failures
may remain after successful retries; they are not counted as blocked parties.
No record, audit, setting, finalisation or issue writes occur during scanning.
No ledger balances or revised CN amounts are aggregated in the attention list.

PRESERVATION
Runtime changes only: static/app.js, static/scheme-options.js, static/style.css.
All Python modules, financial rules, settings defaults, PDF fixes, print logic,
workbook/project storage, launchers, theme/layout modules and both UI choices
remain. No database migrations, new financial fields or default-rate changes.
Updater is unchanged and backup-first. All saved data/settings are retained.

VERIFICATION
Eight existing UI/API suites passed, covering imports, workflow, allocations,
ABS, Cash, frozen histories, reporting, sharing, isolation and deletion.
Seven workbook snapshot/HTTP tests passed (read-only, frozen, deleted scope,
revision selection, missing results, stale selection and authentication).
Native Chromium: five synthetic parties, attention filters/deep links, unchanged
backup after refresh, Cash shortcut add/save/return without automatic allocations,
frozen CN Rs2000 retained, five badges, both themes and stable hover at 1366px.
No browser JS errors. Attention panel rendered and visually inspected.
Eleven updater preservation/backup/rollback checks passed.
Runtime module byte preservation and source/program parity verified.
Full Python financial suite was not rerun for these presentation-only changes;
Update32's 311-test result remains historical evidence, not a new Update33 run.
Windows/WebView2 execution and user acceptance remain pending.

INSTALL / CHECK
Close the calculator and its server console. Extract this whole ZIP, run
Update_CN.bat and select app.py from the EXISTING working calculator folder.
Reopen using your normal launcher; Ctrl+F5 if the browser shows cached UI.
Check Dashboard attention filters/Open; five-step next action; Check Benefits
Cash configuration and party allocation; one saved completed party unchanged.

RESUME
Implementation, targeted regression, native browser checks and packaging complete.
Continue cumulatively from Update33. Preserve all previous rules/features/data,
Classic Emerald and Navy Studio, saved layouts, and Update32 workbook printing.

--- HISTORICAL UPDATE32 AND EARLIER ---

UPDATE32 — APPLIED-BENEFIT PRINT + WORKBOOK PRINTING
19 October 2026. Cumulative from Update31. All earlier financial rules, UI choices,
Cash controls and PDF header fixes retained. Windows acceptance pending.

INDIVIDUAL DETAILED WORKING
Review & Finish -> Print Detailed Working now contains:
* Compact product totals and only non-zero product benefit breakdowns.
* Only payable/applied benefit CNs, or previously issued/revised CN adjustments
  that must remain visible even when current entitlement is zero.
* Applied quantity/extra/net tier only, actual ABS product rows, used CD payment
  periods, Cash deduction/funding working, and qualifying return bonus working.
* Progressive quantities list only used bands, including the established highest
  rate continuation. No complete configured slab lists or recursive per-field
  configuration dumps for these current benefit formats.
* Actual precise CN, separate rounding, previous issue, proposed new amount,
  narration, totals and balance remain. Requested adjustments show only when
  present and stay display-only. Zero-CN products remain visible in product totals.
The supplied example has three products and one Rs30 Quantity CN: 12kg x Rs2.50.
An A4 Chromium layout reconstruction using those figures fits ONE page, down from
four. Two pages is a target for ordinary parties, not a hard clipping limit.
Large party reports naturally continue if required to preserve all applied work.
Normal Print Summary remains available with its existing content.

WORKBOOK PRINT
Workbooks -> each active workbook (also Existing calculations) has:
* Print Workbook Summary: one party-wise table with period, status, ledger,
  full CN entitlement, new CN and balance. No total of ledger balances across
  periods, to avoid counting the same balance repeatedly.
* Print All Parties' Detailed Working: the workbook index plus a fresh page for
  each selected party's compact applied working.
A selector allows all/some parties and one saved version per party+location+season.
Latest populated ledger is initially selected, so a newer empty draft does not
hide an imported ledger. Revisions are not added together. Different seasons
remain explicit. Deleted parties and other workbooks/projects are excluded.
Current open draft is saved first, like individual printing. Preview/rendering
then uses a read-only SQLite snapshot of saved records and settings. A changed
workbook invalidates the selection fingerprint. Completed results stay frozen
and are never recalculated; unavailable historical results are reported explicitly.
Draft/incomplete calculations are marked provisional. The print operation does
not finalise or issue CNs. Missing/error results are not silently shown as zero.
Use the print dialog -> Save as PDF to share. No messaging or online upload occurs.

VERIFICATION
311 Python tests passed (including actual Update31 PDF regression, six workbook
print snapshot/version/deletion/frozen tests and one authenticated/scope HTTP test).
Eight existing UI/API smoke suites passed with the print expectation updated.
Applied-print JS tests passed: zero omission, reversals, progressive used bands,
CD used rows, fixed Net CN, escaping and financial objects unchanged.
Native Chromium tests passed for the individual report and workbook selection,
all/none, two-party Summary Rs6000, combined Detail Rs2000 + Rs4000, correct
working, page boundaries and restoration of the active party globals.
A4 PDFs rendered and inspected. Individual example: one page. Two-party combined
working: index + one page per party (three pages). White print background and
readable text; no clipping. No private input PDFs or browser images bundled.
Eleven updater backup/rollback checks passed. Source/program parity checked.
The calculation engine and financial stores are byte-identical to Update31.

CONTINUATION
1 Individual compact applied working: COMPLETE.
2 Workbook Summary / all-party Detail + selection: COMPLETE.
3 Regression, browser/PDF verification and packaging: COMPLETE.
Next: user Windows acceptance. Continue cumulatively from Update32. Preserve
both UI options, saved positions/preferences/data/settings and all financial rules.
Read LATEST_HANDOFF.md, STABLE_BUTTON_FIX.md, TEST_RESULTS.txt and PHASE_PROGRESS.md.

--- HISTORICAL UPDATE31 AND EARLIER NOTES ---

UPDATE31 — TALLY CONTINUATION-HEADER PDF FIX
19 October 2026. Cumulative from Update30. Update29 was accepted on Windows;
Update30/new Update31 user acceptance remains pending.

CAUSE
The supplied two-page Tally ledger prints a full Ledger: party name on page 1,
but Ledger: party name : report-period Page N on its continuation. The old
first-page matcher captured the continuation suffix as part of a second party
name and split one ledger into two documents. This led to a missing closing
balance and/or a misleading combined-ledger/Bulk Import route.

FIX
Recognise the explicit Ledger: name : date-to-date [Page N] continuation form
before the full first-page header. Join same-party continuation pages. Actual
different parties and repeated full first-page headers retain their boundaries.
No broad fuzzy matching, amount inference, OCR or party merging introduced.
All Update30 changes (Regular + Cash controls and reviewed removal), both UIs,
card layouts, saved preferences, data and settings are retained.
The only runtime change from Update30 is tally_detailed.py header detection.

SUPPLIED PDF VERIFICATION
One complete party; 2 pages, 12 distinct vouchers, reconciled closing Rs602385.
Opening credit Rs552875; sales Rs2088000; receipt Rs100000 on 13 July 2026;
sales return Rs820840; four freight/expense Journal CNs totalling Rs11900.
Freight journals remain posted expense CNs; they are not material returns or
additional receipts. Bill references/carry totals are not counted as receipts.
Stock net: 32D55 1700 packets / 6800kg; 32D12 84 packets / 336kg; Ranbanka
60 packets / 240kg; 14D88 86 packets / 129kg; Redgram 114kg; Res.Angur 262kg;
Green Gram 11 packets / 22kg. Product matches depend on the actual workbook's
catalogue; unknown catalogue products still require explicit mapping.
Original dates, voucher amounts, source snapshots and saved-source re-read agree.
Both /api/import and /api/reparse checked using the actual supplied PDF; single
import returns one complete party, not the combined-ledger route. Preview/import
parsing alone does not create saved party records.

TESTS
304 Python tests passed, with CN_REGRESSION_PDF set to the supplied file. Includes
three header/boundary tests and an actual-PDF money/stock/reparse regression.
Existing 49-party / 69-page detailed PDF and other formats pass regression.
All eight existing UI/API smoke suites passed. Eleven updater backup/rollback
checks passed. Native UI unchanged, so new browser-layout checks were unnecessary.
The new private source PDF is not bundled. Its regression test is optional and
uses CN_REGRESSION_PDF when provided. Generic header tests are always included.
This fixes this explicit header family; other unsupported PDFs need inspection.

USE
Close calculator/server, extract ZIP, run Update_CN.bat, select app.py in the
existing working calculator folder, reopen normally. Reimport the original PDF
into the intended party/workbook and review the import preview before accepting.
If a previous attempt created an incomplete draft, inspect its existing entries
before accepting a reimport; never delete saved party work just to fix this issue.
No need to split/convert the PDF. Saved calculations are not silently rewritten.

RESUME
All implementation/testing/packaging phases complete. Windows acceptance pending.
Continue cumulatively from Update31, preserving all financial rules and existing
features. Read LATEST_HANDOFF.md, STABLE_BUTTON_FIX.md, TEST_RESULTS.txt and
PHASE_PROGRESS.md before future changes. The source and verification logs are
included in this package.

--- HISTORICAL UPDATE30 AND EARLIER NOTES ---

UPDATE30 — DOUBLECROSS REGULAR + CASH CONTROLS
19 October 2026. Cumulative from Update29, accepted by the user on Windows.

SCOPE
The user confirmed the two DoubleCross schemes mean Regular + Cash (32D55),
not two alternative saved regular setups being applied to the same stock.
The existing financial engine already supports Regular + Cash. No new maths,
default rates, product mappings or automatic stock/payment conversions introduced.

NEW CONTROLS
Calculate a party -> Check Benefits -> Regular + Cash schemes:
* Add Cash Scheme / Edit Cash Scheme opens the existing payment-and-quantity
  preview. Choose the quantity, original payment and amount explicitly, preview,
  then Apply reviewed split. Regular quantity is the remaining net stock.
* Remove Cash Scheme previews the changed CN total and quantity before removal.
  Cancel changes nothing. Confirm removes only that product's Cash split and
  its Cash funding rows together. Funding returns to unallocated payment and
  must be assigned explicitly before finalisation. ABS/CD rows are retained.
* Payment diagram's Cash removal link uses the same reviewed removal flow.
* Settings -> My Schemes -> Edit Rates & Slabs -> Benefits or Rates now includes
  Add Cash Scheme / Remove Cash Scheme, original payment dates, advance/payment
  rate, Cash CN rate, unit, and eligible products. Save Scheme commits settings.
  Use party removal to remove a Cash booking; removing Cash from Settings changes
  availability and may flag existing draft bookings for review. Frozen history
  retains its saved settings. Rates and slabs preview now also lists Cash.
Works in both Classic Emerald and Navy Studio.

VERIFIED SCENARIO — 32D55
Illustration using the existing configured DoubleCross reference, no returns,
no old dues, 10,000 kg supplied at Rs140/kg = Rs14,00,000 invoice.
Original receipts: 20 March Rs5,80,000; 10 May Rs20,000 (total Rs6,00,000).
User explicitly books 3,000 kg Cash using Rs3,00,000 of March receipt.
Cash payment rate Rs100/kg; Cash CN Rs40/kg -> Rs1,20,000 Cash CN.
Remaining 7,000 kg regular: highest quantity slab Rs20/kg -> Rs1,40,000 CN.
Rs2,80,000 remaining March receipt explicitly allocated to regular ABS:
token Rs40/kg covers 7,000 kg; ABS benefit Rs10/kg -> Rs70,000 CN.
Rs20,000 May payment explicitly allocated to regular CD at 12% -> Rs2,400 CN.
Total CN Rs3,32,400; ledger outstanding Rs8,00,000 -> final Rs4,67,600.
No overlapping quantities or reuse of money. Actual saved workbook rates govern.
If only Cash is funded, regular ABS is zero; remaining net stock can still earn
configured quantity benefits. No Cash quantity ever receives regular benefits.

REMOVAL / SAFEGUARDS
The scenario's Cash removal releases Rs3,00,000 once, retains regular funding,
restores 10,000 kg regular quantity and recalculates CN to Rs2,72,400. Unallocated
money blocks finalisation until reviewed. Preview never writes. Apply checks
record revision, settings version, draft/frozen status, auth and workbook scope.
Original receipt snapshots and ledger entries are retained.

VALIDATION
299 tests passed in full Python run, including five new scenario/removal tests.
One additional HTTP test passed: token, workbook scope, preview/apply and asset.
Eight existing UI/API smoke suites passed. Eleven updater rollback tests passed.
Native Chromium: both interfaces, add/edit/preview/apply, cancel removal,
confirm removal, funding release, ledger preservation, Cash settings add/remove/
edit/save. Update29 native browser coverage repeated for all eight routes,
five calculation steps, draggable cards, fixed hub, persistence and collisions.
Windows Update30 acceptance remains pending. Update29 already accepted.

CONTINUATION
All implementation phases complete; next action is Windows acceptance.
Retain both UIs, saved themes/layouts/data/settings and all confirmed financial
rules. Continue cumulatively from Update30. Read this file, LATEST_HANDOFF.md,
STABLE_BUTTON_FIX.md, TEST_RESULTS.txt and PHASE_PROGRESS.md.

--- HISTORICAL UPDATE29 AND EARLIER NOTES ---

UPDATE29 — OPTIONAL NAVY STUDIO — 19 October 2026

Cumulative from accepted Update28.1. Classic Emerald is still the default.
Choose Interface -> Navy Studio in the top bar. Switch back whenever you want.
The new appearance covers Dashboard, Workbooks, Parties, Ledger Audit, Year Link,
Reports, Settings, History, calculation steps, forms and dialogs.

PAYMENT STUDIO
Available Payment remains fixed in the centre. Drag each scheme, crop or product
card separately with the mouse, like moving a folder. Dragging empty space does
not move the group. Cards stop at other cards, including the central payment hub.
Clicking still opens the existing allocation editor. Dragging changes no amounts.
Arrow keys move the focused card; Shift+Arrow uses a larger step.
Use the mouse wheel to zoom and Fit diagram to show all cards.
Click Save layout after arranging cards. Reset layout restores the default;
click Save layout afterwards if you want to keep the reset. Save the calculation
first if it has not been saved yet. Layouts are separate by project, workbook and
calculation. Appearance is saved on this PC and survives changing server ports.
Classic retains its original graph, zoom and background panning.

FINANCIAL PRESERVATION
Financial engine, stores, settings defaults, PDF readers, application workflow JS,
Cash quantity logic, ABS distribution, NRV, project sharing, cleanup and deletion
modules remain byte-identical to Update28.1. No database migration is introduced.
Appearance files ui-theme.json and ui-layouts.json are kept beside the relevant
project database, separate from financial settings. They are not included in
financial JSON/.cnwork exports; an in-place update preserves them and data backup
copies made by the updater include files under data/. Never silently evicts layouts.

TESTING
293 Python tests passed in the full run (includes initial 3 appearance tests).
Final appearance changes passed 4 targeted tests, including >40 saved parties.
All 8 existing UI/API regression suites passed. All 11 updater backup/rollback
checks passed. Native Chromium 153 browser tests passed for the eight main pages,
all five calculation steps, six Settings sections, stationary hover, independent
card drag, non-overlap, repeated collision attempts, unchanged financial record,
fixed hub during zoom, saved layout after reload, Classic/Studio switching,
product inspector, print selector hiding and 1366px viewport. No page JS errors.
Financial-module byte comparison and program/source package parity are verified.
Windows-specific installer, WebView2 appearance and physical printing require
checking on your PC; these were not executed in this Linux test environment.
Update28.1 button stability was already accepted by the user on Windows.

PHASE STATUS / RESUME
1 Baseline and persistent UI selector: COMPLETE.
2 Whole-app Navy styling and offline illustrations: COMPLETE.
3 Independent draggable cards and saved layouts: COMPLETE.
4 Automated/browser verification and cumulative packaging: COMPLETE.
Next: user Windows acceptance. Do not rebuild from older updates. Continue from
this source; read PHASE_PROGRESS.md, LATEST_HANDOFF.md, STABLE_BUTTON_FIX.md and
TEST_RESULTS.txt. Preserve both themes, financial rules, saved work and settings.

## Historical Update28.1 and earlier notes

# Fresh complete Update28.1 package - 17 October 2026

User confirmed Update28.1 hover/click button stability works on Windows.
This is a fresh full installation package, not an incremental updater. Runtime code,
assets, settings defaults and original launchers remain byte-identical to Update28.1.
Added Install_CN.bat and START_HERE.txt. Install into a separate folder; transfer saved
work via a full backup, and export/import received projects individually. No user data
is bundled. Further updates must remain cumulative and preserve saved data/settings.
No compiled Windows installer/EXE has been built here. Other native acceptance limits
remain as previously documented. New setup batch needs Windows execution acceptance.

# Update28.1: button stability correction

Read STABLE_BUTTON_FIX.md. The user recorded radial buttons jumping on hover/click; global hover/press transforms overrode centering. Only runtime static/style.css changes. Stable-button CSS guards added; allocation and calendar checks passed. User has now requested and received the cumulative ZIP; deliver corrected ZIP for this bug.

# Current continuation — offline sharing and storage (2026-10-17)

The cumulative Update28 now adds `projects.py` and `maintenance.py`. Read OFFLINE_PROJECT_SHARING.md before changing sharing or deletion behavior. All received files open into a fresh isolated project root; imports never merge with My Work, even when record/workbook IDs match. All API routes use per-request X-CN-Project. Startup is My Work. Portable .cnwork exports include the whole selected project and its issued safeguards; completed snapshots stay frozen and are continued by revision. Exports include archived records; the preview states the scope.

Storage cleanup removes regenerable cache, compacts SQLite, and only removes recovery backups after explicit selection and typed confirmation. Permanent deletion requires already-archived targets, preview fingerprints and exact typed names. Issued/prior-issued histories and dependent records block party/workbook purge. Unused scheme purge preserves independent frozen snapshots.

User requested cumulative work to remain HELD: do not deliver any file until asked. The portable sharing feature exports files locally; no messages or files were sent to third parties. Tests use isolated data, not the user’s PC. Windows/browser visual acceptance and native EXE build acceptance remain pending.

The earlier implementation notes below are historical. Current verification is in TEST_RESULTS.txt and verification/sharing-*.txt.

---

# Update28 continuation — posted ledger CN/NRV — 17 October 2026 — STILL HELD

Latest addition: read LEDGER_POSTED_CN_NRV.md. User confirmed actual Tally-posted CNs only,
excluding Journal/freight and material returns. Material returns reduce sales once, not CN totals.
New Ledger Audit section: weighted crop and product/packing averages, party details, status and
source evidence; saved-bulk source-only combined check; conservative review instead of guessed
NRV. Manual product mapping is scoped to voucher evidence, not shared generic narration.
New runtime file ledger_nrv.py. Existing engine and financial calculation results are unchanged.
No delivery link: user has asked to hold files for further tasks. See TEST_RESULTS.txt for final
verification. Original allocation-studio changes remain cumulative below.

--- Allocation studio continuation ---

# Update28 — allocation studio — 17 October 2026 — DELIVERY HELD

Read ALLOCATION_STUDIO_UPDATE28.md first, then ABS_DISTRIBUTION.md and CORE_RULES_AUDIT.md.
User explicitly asked not to give the file yet; more tasks are coming. Continue this source.

User confirmed Cash difference is issued as CN: 1,000 kg × ₹40/kg = ₹40,000 Cash CN, with
remaining 500 kg following its normal scheme. No separate Cash hub/panel; integrate quantity
booking within Net Rate. Net Rate -> crops/products now visible; radial centre/payment source
breakdown, wheel zoom/pan, all product nodes with spacing, offline crop art, original dates.
Opening-debit imports now propose full old dues and require explicit review; existing inputs
are preserved until reviewed. Saved histories remain frozen. No PC installation was changed.

Verification: 253 Python tests, six UI/API suites plus final targeted radial rerun, nine updater
safety tests passed. No actual browser binary/Windows visual acceptance; print/CSV deferred.
Cumulative package is staged; no delivery link supplied. Preserve backup-first updater, original
Start_Calculator.bat and local Windows EXE rebuild flow. Additional runtime: cash_quantity.py.

--- Update27 and earlier handoffs (historical) ---

# Update27 — cumulative workflow audit — 16 October 2026

Continue from this source; do not rebuild from defaults. The input ZIP was named update 25(1).zip
but its latest content was Update26. Read WORKFLOW_AUDIT.md, ABS_DISTRIBUTION.md and
CORE_RULES_AUDIT.md. The full workflow was reviewed and regression-tested; the new findings and
limits are documented in WORKFLOW_AUDIT.md. TEST_RESULTS.txt records the completed runs.

Changes: missing Cash quantity-selection blockers; explicit multi-product Cash chooser and labels;
stale scheme allocation blockers; settings identity/unit validation; blank/invalid manual CD order;
server-owned frozen status/results and current-workbook draft settings; nonblank extended-ABS
remark; stale asynchronous ABS preview rejection and Apply input verification.

Preserved: all stored data (no migration), independent workbook settings/mappings, existing
allocations and original payment dates, separate rounding, NRV exclusions, display-only requests,
bulk import, ledger audit and April–March Year Link. Completed/issued results are not rewritten.
An explicit draft save strips only inappropriate frozen_settings/result cache fields; it retains
financial inputs. Existing invalid allocations remain visible for manual correction.

DELIVERY: one cumulative backup-first ZIP. Export fresh complete backup; close the app/server;
extract separately; run Update_CN.bat; choose app.py in the EXISTING installation; continue with
Start_Calculator.bat. Existing launchers/.venv/settings/databases are not replaced. Windows EXEs
are rebuilt locally; no binary, runtime database or private backup is bundled.

PC acceptance of Update26/27 remains pending. Minor print/CSV PC rechecks remain deferred.
No live PC records were inspected. Ask one important question at a time only when needed.

--- Previous handoff follows (historical statuses) ---

# Update26 — Approved crop-level ABS product distribution — 16 October 2026

USER APPROVAL
User requested crop-level default ABS rather than leaving a blank product with zero CN. Approved
single eligible segment selection, explicit selection when multiple destinations exist, automatic
allocation across eligible net-sold products with preview and subsequent manual editing.

IMPLEMENTED
Read ABS_DISTRIBUTION.md for usage and exact distribution rules. New abs_distribution.py computes
reviewed explicit product rows using the existing engine's regular-net quantities, remaining token
capacities after other ABS allocations and exact source-money conservation. Overflow stays on an
ABS product row and enters the chosen segment's first configured CD slab through unchanged maths.
No cross-segment or cross-packing auto assignment. No automatic financial changes on navigation.

New protected /api/abs-distribution-preview and /api/abs-distribution-apply routes are scoped to the
selected workbook. Store preserves saved immutable originals, checks revision/frozen/deleted guards
and current settings version, regenerates the plan, and saves through existing validation/audit.
UI offers crop-level entry, automatic-product choice, preview with token/excess per product and
scheme ABS/CD totals, explicit Apply, Cancel and manual row editing. Positive blank-product ABS
edits open the preview before mutating/saving the original allocation. CD-to-ABS conversion also
uses the preview when product is blank. Date/cap failures remain blocked. Existing saved blank
allocations are retained until explicit preview/apply. All unrelated issues remain visible.

REAL CASE
Giriraj in the uploaded Surendranagar workbook had Rs1579400 allocated as ABS with blank product.
Temporary read-only preview now yields eligible product splits and ABS/CD entitlement. No user
backup was changed or bundled. Unmatched 500-packet 25D51 return, unmapped Redgram/Gram schemes and
ledger confirmation remain unresolved; do not silently remove or disregard these review blockers.

VALIDATION
231 Python tests (221 prior + 10 distribution) passed, including 360 earlier financial cases;
8 updater safety/rollback tests passed; full UI/API and dedicated distribution smoke suites passed.
No changes to engine.py, reporting.py, year_link.py, parsing/audit maths, settings defaults, source
dates or original launchers. Saved finalised/issued snapshots remain authoritative per Update25.
Actual Windows GUI/native print/download/EXE testing not run. Prior deferred checks remain deferred.

DELIVERY
Cumulative source + program kit. Updater adds abs_distribution.py and replaces approved runtime
files only, backing up existing code/data before replacement. Fresh exported backup first; close
all source/desktop/server windows, extract separately, run Update_CN.bat, select existing app.py,
continue Start_Calculator.bat. Windows EXE must be rebuilt locally. No database or EXE is bundled.

--- Previous handoff follows ---

# Update25 — Core-rule audit and corrections — 16 October 2026

USER REQUEST
Check whether core rules, maths, limitations and logic still apply throughout the software.
Baseline was the delivered Update24 ZIP, extracted separately. Audit report: CORE_RULES_AUDIT.md.

RESULT
Accepted reference arithmetic and principal safeguards pass. Six additional gaps were confirmed
and fixed. No live database/settings/allocations or historical entitlement were migrated.

CHANGES
1. Net Price: convert configured billing to scheme quantity units before subtracting the net slab
   rate (slab prices are per calculation unit as labelled in the existing builder). Example:
   4 kg packet, billing Rs400/packet, net Rs80/kg, 40 kg sold => Rs800 CN, formerly Rs12800.
   Same-unit and Fixed CN behavior preserved. Net working now exposes normalized billing/unit.
2. Slabs: open-ended must be last, inclusive Extra minimums strictly increase and all rows share
   boundary semantics; invalid quantity calculation mode rejected. Valid highest-rate continuation
   and default Extra thresholds preserved. Existing invalid settings retained but cannot finalise.
3. Cash setup: positive advance, nonnegative CN, valid dates/unit and eligible products validated.
   Confirmed invalid settings rejected on save; invalid legacy active setup blocks finalisation.
4. Cash split packets: supplied/returned must be whole when scheme unit is packet. Kg calculations
   continue to accept fractional weights. Conservation and advance/return-deduction rules retained.
5. Frozen history: Store.calculate returns a deep copy of persisted result for finalised/issued
   records from the selected store, ignoring client-supplied result/entries. No recomputation on
   navigation/reopen. Draft revisions recompute with current settings and existing review gates.
   Persisted numbers retain their standard JSON string representation; Python test comparisons
   normalize numeric strings where appropriate. Historical wrong results are not silently replaced.
6. Reporting state: explicit scheme_state takes precedence over workbook_scheme_state, matching
   engine behavior. HQ still comes from PDF Group. NRV/freight/request and weighted reporting math
   unchanged; stored completed results remain the report's financial source.

PRESERVED
Update24 July ABS routing/save protection, original receipt dates, approved extensions and undated
opening-credit exception; independent stores/schemes/mappings; source caps/old dues; eligible ABS
excess entering first configured CD slab; separate CN rounding; DAWAT packing separation; Saini
Rs142535 outstanding; bulk import/audit; April–March Year Link; original launchers; offline assets.

VALIDATION
221 Python test methods passed (209 existing + 12 audit), including 360 deterministic generated
ABS/CD cases against independent numerical/conservation expectations. 8 updater rollback/safety
checks passed. Full UI/API logic, Payment Studio, complete UI, calendar/native-close and ABS smoke
checks passed. Source compilation, JS syntax, ZIP manifest/runtime-pair checks passed. See report.
Windows EXE/native GUI/printing not executed here. Prior PC UI23 acceptance remains pending and
minor print/CSV rechecks remain user-deferred. No claim of inspecting current live PC records.

INSTALL
Fresh complete backup first. Close all calculator/desktop/command/server windows. Extract full ZIP
separately, run Update_CN.bat, choose existing app.py. Updater backs up code/data before replacement.
Continue existing Start_Calculator.bat. No restore/reimport needed for normal source update.
Existing Windows EXE must be rebuilt locally; no Windows binary or live database is included.
Review an affected completed calculation through an explicit revision if correction is needed.

--- Previous update handoff follows ---

# Update24 — Block out-of-period ABS allocation — 16 October 2026

USER REPORT / ROOT CAUSE
July payment could be selected as ABS in Money Allocation. Existing compute already flagged
out-of-period ABS and excluded it from ABS benefit/finalisation, but UI routing and draft saves
only enforced money limits. This update closes that selection/save gap.

FIX
- Eligibility follows each independent scheme's configured ABS booking dates and immutable
  original receipt date. No hardcoded calendar month, date rewriting, or automatic CD reassignment.
- Add ABS selects an eligible source, preferring positive remaining availability. If none exists,
  it stops without changing the record or its scheme override. Out-of-period source options are
  disabled and labelled. Changing type/source/scheme/amount is checked before committing.
- Segment-wide scheme changes check all affected ABS sources before changing any allocation,
  cash split or override. UI graph navigation remains read-only.
- Store.save independently rejects new/retargeted invalid ABS assignments (including zero rows)
  and invalid increases, after preserving immutable originals and normal monetary limits.
- Existing invalid draft rows are retained with a visible correction warning, and can be saved
  unchanged, reduced, changed to CD/Settlement or removed. They cannot earn ABS or finalise under
  the existing computation checks. No automatic deletion, migration or modification of history.
- Existing undated opening-credit registration/draft setup remains available, even before a sold
  scheme is selected. Normal compute still requires eligible scheme/product for any ABS benefit.
  Dated opening-credit sources follow the same booking dates as ordinary receipts.
- Configured extension routing remains available as draft setup; extended ABS earns benefit only
  with the existing explicit approval AND remark. A checkbox alone cannot bypass extended_end.
- Engine benefit arithmetic, CD treatment of eligible excess ABS, NRV, freight, requested CNs,
  DAWAT separation, Saini outstanding, ledger audit and April–March Year Link are unchanged.

VALIDATION
209 Python tests passed (204 previous + 5 new ABS tests), 8 backup-first updater tests passed.
Full UI/API logic, complete UI, payment studio, calendar/native-close and dedicated ABS regression
smokes passed. New tests cover date boundaries, July/original-date rejection, extension approval,
undated/datetime opening credit, atomic save rejection, legacy-draft correction, zero rows,
UI type/source/add guards, eligible source selection, disabled options and save/reopen.
Final targeted ABS tests and smoke rerun after last guard adjustment. No real Windows GUI run.

INSTALL / ACCEPTANCE
Export a fresh backup, close calculator and server, extract this full cumulative ZIP separately,
run Update_CN.bat and select app.py in the EXISTING working source folder. Updater makes code/data
backup before replacing files. Keep using existing Start_Calculator.bat. Both original launchers
are unchanged. Existing EXE requires local rebuild; no Windows binary is included.
No live data is bundled. New ABS guard awaits user's PC acceptance. Prior UI23 native/download/
printing acceptance remains pending; minor print/CSV rechecks remain user-deferred.

--- Previous update handoff follows ---

# Update23 — Premium studio, native window, categories and HQ dashboard — 16 October 2026

USER REQUIREMENTS / CURRENT STATUS
User found the earlier UI too basic and asked for a broader typography/calendar/animation polish,
a launcher with its own window, category-first party-wise audit findings, and clarified HQ:
STATE -> HQ -> PARTY. HQ is the area/territory allocated within a state, printed as PDF Group.
This update implements these requests. Do not infer UI22 acceptance from this request.
User's minor print/CSV PC rechecks remain deferred. New desktop/download/print behaviour needs
real Windows acceptance. Existing Start_Calculator.bat/Start_CN_Fixed.bat remain unchanged.

VISUAL POLISH
Bundled Manrope variable font (SIL Open Font License included) served locally. Updated density,
font hierarchy, spacing, glass/layer contrast, right-editor styling, button interactions, crop
nodes, status cards and empty states. Animated connector glints, card entrances, restrained
hero float, hover/ripple effects; prefers-reduced-motion disables all motion. Financial figures
are never animated or counted up. All new styling is screen-only; print remains separately scoped.

CALENDAR
New external local polish.js progressively enhances date inputs with a styled month/year picker,
leap-day/min/max checks, Today/Clear, Escape/focus handling and keyboard day navigation.
Opening a calendar does NOT assign a date. Only explicit changed selection dispatches the same
normal change event; original ledger/payment rules still validate source edits. Disabled/read-only
inputs remain protected. Native typing remains available. Dates before 1900 are not offered by
picker; existing values are not rewritten. New calendar and native UI need Windows visual checks.

AUDIT FIX
Standalone audit already had finding categories. The remaining bulk-history section was organised
party-first. It is now category-first too: Possible duplicate sales return, Mixed rates, etc.,
then open to see the party/source-period evidence. Categories start closed. Posted CNs/source notes
and warnings are in a separate closed auxiliary section. Historical reports remain historical;
no weaker cross-party checks are manufactured, and no voucher/financial evidence is changed.
Not Applicable/reopen controls retain existing fingerprint-based metadata and review behaviour.

HQ DASHBOARD
New read-only territory.py and /api/territory-report reuse the existing completed-snapshot report.
HQ reads ONLY saved PDF Group headers, including structured detailed pages with original header
line bounds. No guess from town/address or ordinary voucher narration. Conflicting/missing evidence
is Unassigned HQ with a visible note. Real 49-party Surendranagar fixture verifies Group extraction.
Frozen sources/results read as stored; no parser changes, DB migrations or backfill writes.
Dashboard filters state/HQ/party/workbook/season/crop/product and expands State -> HQ -> Party,
with product/packing weighted NRV table. Distinct DAWAT packing groups retained. Overlap exclusions,
latest completed lineage, missing billing/old snapshot notices and freight/request exclusion come
from existing reporting. Full entitlement, not incremental issue. No ledger outstanding values
are summed across product rows. HQ filter cannot revive products already excluded as overlaps;
choose a workbook to review those cases. State is the completed reporting/scheme state.

OWN DESKTOP WINDOW (OPTIONAL SOURCE LAUNCHER + SEPARATE BUILD KIT)
- After applying source update in EXISTING working folder: Setup_Desktop.bat once (internet installs
  pinned pywebview 6.2.1 only), then Start_Desktop.bat. pythonw opens a native window with no normal
  browser tabs/address bar and no persistent command window. Existing source uses same app.py,
  SQLite stores, loopback/token API and data path. Close other source servers before starting.
- Requires Microsoft Edge WebView2 Runtime/.NET prerequisites on Windows; OS runtime NOT bundled.
  Desktop dependency installed once; no claim arbitrary PC is ready. Existing browser launcher still
  works; no automatic browser fallback. Error is shown if native launch cannot proceed.
- Local server uses a free port and shuts down with the window. Close requests flush current draft
  through normal save/API first; busy operations or failed saves keep window open with a message.
  No direct DB/file-editing bridge. Native downloads enabled. File/Blob export, Windows printing,
  closing/autosave and native build require PC acceptance; fake-shell tests are not Windows tests.
- Optional Build_Desktop_Windows.bat uses isolated .desktop-build-venv and creates
  source/dist/AllCropCNDesktop/AllCropCNDesktop.exe with icon/static/font assets. Fresh backup first,
  restore into that NEW separate executable copy; keep old folder/backup. WebView2 runtime remains
  required. Existing Build_Windows.bat still builds accepted browser-mode standalone as before.
- Desktop profile sits beside data/, not inside financial backup data tree. Selected workbook is
  browser-profile state; all actual saved workbooks stay in the existing SQLite stores.

CORE PRESERVATION
Engine, store, workbooks, settings, importer/tally reader, ledger-audit rules, reporting CSV/NRV,
Year Link, old Windows build and BOTH existing source launchers remain byte-identical to Update22.
app.py changes only add static font/icon/polish routes and read-only territory endpoint.
Existing independent schemes/mappings/allocations, original dates, per-CN rounding, DAWAT groups,
Saini Rs142535, bulk import and April-March Year Link retained. Requested CN changes remain
separate from actual CN and NRV. No live DB or user backup is bundled.

VALIDATION / LIMITS
See CURRENT_TEST_STATUS.txt for final checks. Original regressions plus new Group evidence,
read-only hierarchy/filter/weighted-packing, HTTP auth/font/assets and native-shell tests.
UI/API/payment smoke preserved. Additional calendar/desktop close tests and bulk category-default
checks pass; updater tests include rollback after a new font file fails, removing native helpers.
No real browser binary/Windows GUI available here. Manrope/font license is bundled; no runtime
internet font/assets. Native dependency first setup needs internet. No compiled Windows EXE here.
Do not claim native layout/print/export acceptance without user's Windows confirmation.

INSTALL (BACKUP FIRST)
Export fresh app backup separately. Close browser tabs AND all calculator command/desktop windows.
Extract complete ZIP separately. Run Update_CN.bat, choose app.py in EXISTING working folder.
Updater backs up code/main/private DBs before installing 21 files including new assets/desktop kit;
rollback tested. Original launchers and .venv are preserved (optional Setup_Desktop adds its package
only when user runs it). Reopen usual Start_Calculator.bat for browser; optional desktop as above.
Do not restore/reimport merely to install. source/ is continuation/build material, not live data.

Native docs: https://pywebview.flowrl.com/api/ and https://pywebview.flowrl.com/guide/web_engine.html
Font source/license: Google Fonts Manrope, https://github.com/google/fonts/tree/main/ofl/manrope
Older handoff retained below; current notes supersede older status.

---

# Update 22 — Approved connected allocation flow — 16 October 2026

CURRENT AUTHORISATION AND PRIORITY
User approved the standalone uniform-flow preview and explicitly asked to apply it to the
calculator. User supplied SmartFarm-style dashboard screenshot as an icon/card/animation reference,
not as a request to copy that app's data or controls. Recommended order: connected allocation and
icons first; detailed state/HQ/product-NRV dashboard next. HQ definition/mapping still needs ONE
important question. Dashboard phase is NOT implemented beyond the existing Update21 overview.
Update20 allocation/layout was accepted; do not infer full Update21 PC acceptance. Minor print/CSV
PC rechecks remain explicitly deferred. User uses existing Start_Calculator.bat.

IMPLEMENTED
Assign Payments replaces the nested tree with connected Benefit -> Crop -> Segment/packing nodes.
Uniform orthogonal buses/branches are drawn from actual DOM node positions; selected path is green.
Crops/schemes/segments come from this calculation's frozen/current settings and net-sold choices,
not hardcoded crops. Alternative schemes within the same segment/packing share one node and can
be chosen in the existing editor. Distinct DAWAT 1/3 kg group keys remain separate. All existing
saved allocations, including unavailable/unknown destinations, stay in a visible selection list.

Selecting nodes is view-only. It does not change schemes, money, dates, allocation values or CNs.
Adding a new allocation uses existing explicit scheme/add workflow with amount ZERO and source cap.
Existing allocations still use allocationRow and original change/save/remove/validation handlers.
Scheme changes preserve the established explicit override behaviour. Frozen edit guards retained.

Right editor supports drag resize, width slider, keyboard arrows/Home/End and collapse/reopen.
Width/selection are session UI state only. On smaller desktop widths the editor stacks below the
map. Resizing redraws lines, including after rerender; saved rows reopen collapsed editor.
Receipt sources/old-dues controls and detailed benefit/payment workings are accessible in collapsed
sections, reducing screen density without removing evidence or source-split controls.

Added local vector crop icons, small action pictograms and restrained selection/hover motion with
reduced-motion support. No external clipart/font/animation dependency, fake sample figures or
prototype-only sample rows added to the live calculator. The standalone preview stays separate.

PRESERVED
13 core/runtime/build/launcher files byte-identical to Update21. No backend, engine, DB schema,
parser, audit, reporting or Year Link changes. Existing CSS is retained; additions are screen-only.
Original dates, source amounts/caps, opening credit, independent workbook schemes/settings,
allocations, DAWAT separation, separate CN rounding, Saini Rs142535, bulk import and financial-year
link retained. NRV continues configured billing minus scheme-benefit CN per net sold kg/packet;
freight excluded. Requested CN adjustments remain display-only and outside actual CN and NRV.

VALIDATION
Existing full Node UI/API smoke, Payment Studio smoke and Complete UI smoke pass on connected UI.
Extended focused Payment Studio checks pass node-selection read-only comparison, separate DAWAT
keys, adjustable width without financial writes, SVG bus rendering/no NaN, preserved source dates,
source-cap rejection, zero-start destination addition, save/reopen and frozen add guards.
Seven updater backup/rollback tests pass and JS syntax passes. Core Python files unchanged from
Update21's 198-test passing baseline. No new full Python suite rerun for this frontend-only update.
No current live user DB/backup supplied; tests use temporary fixture/synthetic stores.
Real browser/Windows visual check remains pending (browser binary unavailable here).
No Windows EXE built here. Do not claim layout pixel-perfect browser certification.

INSTALL
Fresh app backup first, keep separately. Close calculator tabs AND command/server window. Extract
complete ZIP separately, run Update_CN.bat, choose app.py in EXISTING working installation, reopen
existing Start_Calculator.bat and fresh tab. Updater backs up changed code/main/private DBs first;
saved data/.venv/launchers preserved. Source update needs no restore or reimport.
EXE needs local rebuild: export latest backup, close old app, Build_Windows.bat, open NEW
source/dist/AllCropCN/AllCropCN.exe and restore into that separate copy; keep old folder/backup.

NEXT
User may inspect connected flow and icons. Before designing the detailed dashboard, establish what
HQ means/how parties are assigned, then use existing completed snapshot reporting rules. Do not
infer HQ from town/address or expose draft/revision overlaps as completed financial totals.

Older handoff retained below; current statements above override historical status.

---

# Update 21 — Entire-software emerald UI preview — 16 October 2026

CURRENT USER STEERING
Update 20 layout AND allocation interface were confirmed working on the user's PC, including
expand/edit/save/reopen/original payment date. Record Update 20 as accepted. User explicitly
DEFERRED minor print/CSV rechecks and requested UI work for the ENTIRE software. Continue UI
work without repeatedly returning to those deferred checks. Phase 7 and previous CSV/source
suggestions/audit-category features remain accepted. User consistently uses Start_Calculator.bat.

WHAT CHANGED
Frontend-only extension of accepted Update 20. Common emerald navigation with local SVG icons,
current-workbook topbar, scope chips, page mastheads, status pills, empty states, stronger forms,
upload areas, tables, settings cards, scheme wizard/dialog styling and a sticky workflow footer.
Applied to Dashboard, Workbooks, Parties, Bulk Import, Ledger Audit, Financial-Year Link, Reports,
Settings (schemes/periods/products/backup), History and every calculation step. Payment Studio
is retained. New five-step navigation has numbered markers and accessible current-step state.
The application remains local/offline; no downloaded font, image or runtime asset is required.

Dashboard: current-workbook party/draft/finalised/issued record COUNTS, recent calculations with
individual saved balances and working navigation actions. No balances/versions are summed.
Separate completed-report section is visibly ALL ACTIVE WORKBOOKS and uses the existing
read-only /api/report output (same overlap exclusions, missing-data notes and billing rules).
Its scheme CN figure is full entitlement, NOT incremental issue. Net realisation is known
configured billing only. Product/packing weighted NRV remains in Reports, not one mixed rate.
Freight and requested CN changes remain excluded from NRV. No automatic CN issue/changes.
Report loads in background without occupying apiBusy; ordinary save/calculation guards remain.
Dashboard sequence/page/workbook checks discard stale replies after navigation/workbook switch.

PRESERVATION
13 core/runtime/build/launcher files byte-identical to Update 20: app, engine, store, workbooks,
settings, importer, tally_detailed, ledger_audit, year_link, reporting, Windows build and BOTH
launchers. No DB migration or update to saved schemes/settings/allocations/source entries.
No receipt date changes, money transfers, parser expansion or recalculation of frozen history.
Accepted Update 20 stylesheet retained verbatim; new CSS is @media screen only. Existing
print summary/detail templates and styles are preserved. Existing exports stay functional.
Independent workbook settings, original source caps/dates, per-benefit rounding, DAWAT 1/3 kg
separation, Saini Rs142535, bulk import and April-March Year Link retained.

VALIDATION
198 Python tests pass. Existing Node UI/API smoke and focused Payment Studio smoke pass.
New Complete UI smoke covers all page routes/settings sections, retained import/audit/report/
backup controls, heading escaping, all five calculation steps, unchanged backup after page
rendering, original record unchanged by tab rendering, nonblocking dashboard report reads,
workbook switching during background load and stale reply rejection. Seven updater backup/
rollback tests pass; JS syntax passes. Tests use temporary stores, not user's live backup.
Native Windows/browser visual acceptance of Update 21 remains pending. Chromium is unavailable
here (earlier download failed); do not claim screenshots/rendered browser QA. No Windows EXE
built here. User's minor print/CSV PC rechecks remain explicitly deferred, not silently passed.

INSTALL
Export a fresh app backup and keep it outside the app folder. Close all calculator browser tabs
AND command/server window. Extract the COMPLETE update ZIP separately. Run Update_CN.bat and
select app.py from the EXISTING working installation. Code plus main/private DBs are backed up
before replacement; data, .venv and both working launchers are preserved. Reopen existing
Start_Calculator.bat and use its fresh browser tab. Do not restore or reimport merely to update.
Source/ is continuation/build material, never a replacement live data folder.
Standalone EXE embeds code: latest backup first, close old app, run included source/Build_Windows.bat,
launch NEW source/dist/AllCropCN/AllCropCN.exe and restore into that separate copy. Keep old EXE
folder and backup. No compiled EXE included. Source updater does not patch embedded EXE code.

NEXT
User can review the overall UI and request visual changes. Do not call Phase 8 fully accepted
until user confirms this broader UI. Defer previously requested print/CSV PC checks as instructed.
The concept image is a visual reference; this is a functioning UI implementation with real data,
not a guaranteed pixel-exact copy of image-generation mockups.

Older handoff retained below; this current status supersedes historical pending statements.

---

# Update 20 — Emerald Payment Studio preview — 16 October 2026

CURRENT ACCEPTANCE
Phase 7 accepted. User reports standalone build, offline operation, restore/restart and PDF printing passed.
Prior audit review/freight/navigation passed. User now accepted CSV exports, PDF packing/billing suggestions
and audit category grouping. Close those topics as complete; new Update 20 UI acceptance is pending.
User uses Start_Calculator.bat consistently. Preserve that working launcher. Their Windows EXE is built
locally; source updates require rebuilding the EXE. Ask only one important question at a time.

PDF INCIDENT CLOSED
The supplied Mahalaxmi PDF was a Statement - Selected Bills and Update 19 rejected it. User regenerated
the PDF and confirmed import works, then asked to leave this topic. No parser change is included.
Do not claim the earlier selected-bills report is now supported or a parser regression was established.

IMPLEMENTED
Screen-only glass/emerald styling across existing pages: dark sidebar, leaf mark, translucent cards,
clear tables, focus outlines, improved headings and Payment Studio. Uses local CSS/SVG and system fonts;
no network dependencies. Approved concept image is a reference, not a promised pixel-exact implementation.
No invented accounts, notifications, search or sample financial numbers have been added.

Assign Payments now has exact-decimal display totals for available registered sources after old dues,
allocated and remaining; unregistered opening credit is still registered explicitly through existing controls.
ABS/CD/Cash/Settlement expand to crop -> segment/packing -> saved scheme and allocation cards. Each card
selects a side editor with original source, type, scheme, ABS/Cash product, amount, limits, live benefit/slab
preview, approval/remark, remove and Save allocation. Save uses existing draft save, not a second financial
commit. Autosave stays active. Branch expansion and editor selection are session UI state only.
At narrower desktop widths the editor stacks below the tree so controls remain usable.

New destination allocation starts at zero with an existing source and the explicitly chosen saved scheme.
It uses the existing scheme override workflow; switching an alternative scheme for a segment affects that
segment's existing destinations as before. Original source money/dates and allocation amounts are untouched.
Existing unresolved/archived destinations remain visible for correction. Frozen records retain disabled edit
controls and the add handler refuses frozen writes. Original source splitting, opening-credit registration,
manual CD order, cash splits and Settlement remain available.

PRESERVED
Engine, store, workbooks, PDF readers, ledger audit rules, reporting, Year Link and both launchers are byte-
identical to Update 19. No database migrations, receipt-date edits, automatic allocation amounts or live data.
Independent workbook settings/schemes, product mappings, original allocations, DAWAT 1/3 kg identities,
separately rounded CNs, full-year ledgers, bulk import and April-March Year Link retained.
Saini control remains Rs142535. NRV = scheme billing less scheme-benefit CN per net sold unit; excludes
freight. Requested adjustments remain separate and do not change actual CN, outstanding or NRV.
Print/report templates and print CSS remain unchanged; new styling is @media screen only.

VALIDATION
See CURRENT_TEST_STATUS.txt for final recorded checks. Focused Payment Studio API/event/template tests
cover exact decimal totals, branch separation including DAWAT, unresolved saved rows, selection without
financial changes, over-allocation rejection, zero-initialised destination additions, original receipt dates,
save/reopen and frozen-add guard. Tests use temporary stores, not the user's live backup.
Linux browser download failed; no real-browser visual QA or native Windows EXE built here. User PC checks
are required before accepting this preview. No new runtime dependency required.

INSTALL FOR THIS USER
1. In current calculator, Settings -> Backup & Restore -> Download Backup. Keep it outside the app folder.
2. Close calculator browser tabs AND the calculator command window/server.
3. Extract the COMPLETE ZIP to a separate folder. Run Update_CN.bat and select app.py from the EXISTING
   working installation (not the new source folder). Updater backs up code and main/private DBs first,
   rolls code back on install failure and preserves data, .venv, settings and existing launchers.
4. Reopen your existing Start_Calculator.bat. Use its fresh browser tab. No restore/reimport is needed for
   a source update. The source folder is continuation/build material, not replacement live data.
5. If testing EXE separately: export latest backup from current app first, close it, build with included
   source/Build_Windows.bat, open the NEW dist/AllCropCN/AllCropCN.exe and restore into that separate copy.
   Keep the old EXE folder/backup. The source updater cannot patch an embedded EXE.

PC CHECKLIST
- Existing workbook/party opens with same entries, CN totals, outstanding and allocation values.
- Assign Payments: Available / Allocated / Remaining agree with source details after old dues.
- Expand ABS or CD -> crop -> segment; select saved allocation, review source/date and live slab.
- Add zero allocation in chosen segment; enter a within-limit amount, save/reopen. Excess is rejected.
- Separate DAWAT packing branches, optional Cash, Settlement and manual CD order still work.
- Frozen/issued record stays read-only. Summary CSV/NRV and PDF print still match prior values.
- Review readability on the user's desktop (100% and normal Windows scaling); new layout acceptance pending.

Historical handoff below is retained for evidence. Current acceptance above supersedes older pending notes.

---

# CSV exports source suggestions and audit categories — 16 October 2026

User PC acceptance: previous audit review/freight classification/Parties navigation update
checked and passed. Current requested changes implemented below; new Windows acceptance pending.

CSV EXPORTS
Review & Finish -> Export Product Summary (CSV), alongside existing JSON/print.
Reports -> filters for workbook/state/season/crop/segment/product/party -> Export Filtered Report
(CSV). This is a functional report view using existing styling, not the futuristic UI redesign.
Reports use latest completed (finalised/issued) frozen snapshot per lineage. Draft revisions do
not hide completed snapshots. Draft product export is allowed only when all calculation issues
are resolved. Existing frozen records are read from stored settings/results, not recomputed.
Older frozen snapshots without product breakdown are explicitly omitted/not reconstructed.

Rows include original invoice supply, IPT in/out separately, returns, net sold in scheme unit,
packets/kg, individual rounded benefit attribution, total CN, per-unit CN, configured billing,
NRV in both units and net realisation. NRV = configured scheme billing rate minus scheme-benefit
CN per net sold quantity. Full entitlement, not incremental revision issue. Freight and posted
ledger credits are not subtracted again. Requested adjustments have separate display-only columns
and never affect NRV. Source billing suggestions become rates only after normal scheme save/review.
Rates and totals use Decimal, CSV has UTF-8 BOM for Excel, quoted cells and formula-text protection.
No files are opened in Excel here; native CSV acceptance remains pending.

Weighted NRV grouped by crop/product/packing is sum of net realisation / sum net quantity, never
an average of party rates. Kg/packet columns remain separate; DAWAT packings stay separate.
No repeated ledger outstanding totals are summed across product rows. Archived parties/workbooks
excluded. Overlapping completed product/party/period/packing records across distinct lineages or
workbooks are excluded with a visible review note, not guessed/doubled. Filters apply before this
check, so explicitly choosing one workbook can resolve a cross-workbook overlap. Options remain
available for all completed rows. Older/missing reporting data has explicit notices. No auto issue.

PDF SETUP SUGGESTIONS
Product mapping retains detected explicit kg/g/gm packing suggestions, with extra source-name
fallback and editable confirmation. No unknown packet weight guessed from a bare quantity/rate.
Create Scheme for this Product reads only that product's selected-period sales item rates, never
returns/IPT/payment/journal amounts. Validates rate x quantity against printed item amount and
converts packet/kg rates with the reviewed packing. One unique rate prefills the NEW scheme;
mixed rates leave billing blank with explicit source-rate choices. Source unit is labelled.
Existing saved schemes/rates are never automatically rewritten. Missing rates stay manual.
Normal benefits/slabs/ABS/CD dates and confirmation still required.

AUDIT CATEGORIES
Finding categories replace direct party listing. Each closed expandable category shows type,
finding/party counts and Not Applicable count. Open category then finding to see parties/vouchers.
Exact cross-party return checks, payment evidence, saved review metadata, freight classification,
PDF source evidence, repeat-upload deduplication and JSON audit export remain unchanged.

PRESERVED
Engine, financial persistence, workbooks, parsers, ledger-audit rules, Year Link and working
Start_CN_Fixed.bat byte-identical to previous update. No DB migrations, auto-rate updates,
receipt date edits or CN/request logic changes. No live user databases/backup in deliverable.

VALIDATION
198 Python tests pass (11 new reporting/CSV/HTTP tests), expanded Node UI/API smoke including
unique/mixed source rate selection, closed categories, report filters and CSV download; 7 updater
backup/rollback tests including failure installing new reporting.py. JS syntax passes.
Original actual backup restored into isolated temporary store: report read leaves complete
backup data/settings/entries/allocations/issued histories unchanged; this older backup contains
no completed reportable rows. New completed scenarios tested synthetically. No Windows binary
built here. New visual/native CSV checks on user PC pending. Prior build/offline tests accepted.

INSTALL
SOURCE app: close server; extract complete ZIP; run Update_CN.bat -> EXISTING app.py; reopen
existing Start_CN_Fixed.bat. Backup-first updater now also installs reporting.py, preserving
all main/private DBs, launcher and .venv. Standalone EXE embeds code: export FRESH backup from
current EXE, close it, run included source/Build_Windows.bat, open NEW source/dist/AllCropCN/
AllCropCN.exe and restore fresh backup into that separate copy. Keep old EXE folder/backup.
No compiled EXE included. Do not replace live data with source folder.

STILL CONCEPTS
Futuristic glass/emerald redesign and expandable ABS/CD/crop/segment allocation interface remain
concepts; no broad UI redesign done here. Reports provide working exports/basic aggregation.

---

# Audit review controls freight classification and navigation — 16 October 2026

User requests implemented:
1. Audit findings have Mark Not Applicable, a required reason, saved timestamp and Reopen for
   Review. Evidence stays visible and counted. Report export includes current review decisions.
   Stored in selected workbook settings with existing version/stale-write guards and backups.
   Fingerprints bind exact voucher evidence, rule and checking period. Filename changes alone
   do not reset; changed financial evidence or group/period does. New workbook creation does
   not inherit finding dispositions from copied settings. Existing workbook data is untouched.
2. Posted CN audit views support Scheme benefit, Freight/transport, Other adjustment and
   Unclassified. Freight/Other do not require/display crop selectors. Explicit source narration
   containing freight/transport/courier suggests freight in audit; generic JOURNAL is not proof.
   User can override/save narration classification within the workbook. Saving freight/other
   removes that narration's prior crop mapping. Mapping/classification is audit metadata only;
   voucher kind/debit/credit, ledger/CNs/allocations/NRV calculations are not changed. Posted-CN
   listing is informational; duplicate reference/narration findings can still need review.
3. Bulk Import button moved from sidebar to Parties (opens the same bulk workflow).
4. Calculate CN duplicate sidebar removed; existing party record/new party actions still open
   the full calculation workflow. Parties stays highlighted in both internal screens.
5. Deleting schemes archives their settings; engine maths/workflow remain. New custom schemes
   need explicit supported benefits/rates/slabs/billing/state/period/dates, not retraining.

Previous strict cross-party-return audit, payment-reference evidence, period scoping and
repeat-upload deduplication all retained. No futuristic mockup UI or NRV dashboard implemented.
These remain the reviewed concepts. Existing UI and accepted Phase 7/standalone flows retained.
Engine, Store, import parsers, year link and Start_CN_Fixed.bat byte-identical to previous update.
Workbooks changes only clear review dispositions when creating a NEW independent workbook.
No migration, forced restore, live DB replacement or dependency changes.

Validation: 187 Python tests (including 8 new review/scope/backup/classification checks), extended
Node event/API smoke including mark/reopen/re-run, freight save/no crop and navigation, 6 updater
safety/rollback tests and JS syntax. Real Windows checks for these NEW controls remain pending.

INSTALL source app: close calculator/server, extract full ZIP, run Update_CN.bat, choose EXISTING
app.py, relaunch existing Start_CN_Fixed.bat. Backup-first updater preserves existing data/private
workbook DBs, .venv and launcher. Do not copy source over working data.
Standalone EXE embeds code and needs rebuild: export FRESH backup from current EXE first, close
it, run included source/Build_Windows.bat, launch NEW dist/AllCropCN/AllCropCN.exe and restore that
fresh backup into the new separate copy. Keep original EXE folder/backup. No compiled EXE here.

---

# Ledger Audit strict cross-party return check — 16 October 2026

User approved ONLY exact cross-party sales-return matches: same date, source product/packing,
unit, positive returned quantity and item amount. No weaker-match alerts. Compare all party
identities, including similar and completely different names. Exact name normalisation is
case/whitespace only; no fuzzy product aliases or guessed pack conversions. Explicit packing
metadata must also match when present. Item amount is compared, not unrelated voucher totals.
Incomplete/zero/negative item values do not qualify. IPT is never a return for this check.

Read-only audit now groups these matches across all supplied party PDFs. Repeated/overlapping
uploads retain existing multiset deduplication. Multiple identical lines in one voucher cannot
manufacture cross-party matches. Full voucher equality requires all source item signatures
with multiplicity plus debit/credit totals; this is an evidence badge on strict item findings,
not an additional weaker rule. Parties matched by normalised name/location, never fuzzy names.

Findings contain both/all party names, PDF filenames, original dates/references/items and
page/line evidence. UI renders comparison cards side by side when space permits, exact item
amounts and expandable complete voucher items. Warns Possible duplicate sales return; no
automatic correction/deletion/merge. Report JSON retains comparison evidence. Existing
payment reference checks remain unchanged: concrete transaction ID or exact descriptive
narration, including cross-party and different-date cases, never payment amount alone.

Run Ledger Audit, load ALL relevant PDFs together, choose period, Run Ledger Checks. Prior
saved bulk-import reports are historical; rerun standalone audit to compare across files.
No financial, payment, NRV, settings, allocation or database schema changes. The generated
futuristic UI mockups and workbook NRV dashboard remain concepts, not implemented here.

Windows acceptance recorded in chat after Phase 8 preview: source visual check; native build
and launch; restore/restart in standalone; offline PDF import/calculation; browser print/save
PDF all passed by user. Second-PC/no-Python test explicitly waived, not passed. Native EXE
was built by USER, not in this Linux environment. Current deliverable is source/updater/build
kit, not a Windows binary. Production source and EXE data folders remain separate.

Install SOURCE app: close all running apps; extract complete ZIP; run Update_CN.bat and choose
EXISTING source app.py; reopen Start_CN_Fixed.bat. Backup-first updater preserves all DBs.
For standalone EXE: updater cannot patch embedded executable. Export latest backup from the
CURRENT EXE, close it, build this ZIP's source/Build_Windows.bat, open newly built dist/AllCropCN/
AllCropCN.exe and restore the fresh backup into that separate copy. Keep old folder/backup.
No reimport/restore needed when using only source updater. No user data is bundled.

Validation: 10 new strict-return tests plus prior 169 Python regressions, extended Node UI/API
smoke, six updater safety/rollback tests and JS syntax. Synthetic exact matches tested;
user's newly observed real duplicate-return PDFs were not supplied in this chat.

---

# Phase 8 first preview — 15 October 2026

Phase 7 ACCEPTED by user on Windows in this conversation: checks 1–7, latest Year Link,
finalise/reopen, issue/reopen, separate revision draft, unchanged revision zero difference,
changed revision incremental difference with original issued unchanged, fresh backup preview,
restore into separate test copy, and native Microsoft Excel Bajra recalculation matching app.
This records user acceptance, not independent remote observation of their Windows machine.

Phase 8 IN PROGRESS. This first preview adds screen-only desktop styling, keyboard focus
indicators, updated phase/acceptance copy, frozen-runtime database separation and automatic
free-port binding for packaged builds. Source launcher behavior and explicit CN_DATA_PATH /
CN_PORT overrides remain supported. Store, engine, importer, workbook/year-link/audit modules
are byte-identical to accepted Phase 7. Print styles and all financial rules are unchanged.
Requested CN changes remain display-only. No live database is included or rewritten.

Build_Windows.bat creates a separate .build-venv and uses pinned PyInstaller 6.22.3 plus
existing PDF requirements. Output is dist/AllCropCN/AllCropCN.exe with bundled static assets,
Ashapura fixture and PDF libraries. Keep entire output folder. Data lives beside executable,
not under _internal. First build needs internet; intended built runtime works offline.
This archive DOES NOT contain a compiled Windows EXE. Native build/clean-PC offline tests,
visual review and wider Phase 8 PDF/CSV output polish remain pending. No signed installer.

Install visual/runtime update: close calculator; extract complete archive; run Update_CN.bat;
select EXISTING app.py; reopen existing Start_CN_Fixed.bat and fresh browser tab. Updater
preserves data/main/private workbook databases, launcher and .venv; backs up before replacing
code. source is continuation/build material, never a replacement for the live data folder.
For standalone build testing follow source/STANDALONE_README.md in a separate location.

Validation: 169 Python tests pass: original 167 regression tests plus two new simulated frozen-runtime tests (default
and overridden data paths, asset lookup and assigned port); Node UI/API smoke; six updater
safety tests; JS syntax. Actual 34.8 MiB backup isolated restore/navigation/HTTP preview passed:
336 records recognised and 300 private workbook records preserved exact monetary/entry data.
Native Windows build/visual tests remain pending; Chromium binary unavailable here.

---

# Phase 7 — actual Year Link Ledger Account PDF layout fix — 15 October 2026

USER STATUS
User reports acceptance checks 1–7 passed on Windows (saved data, late IPT, border imports,
delete/restore, workbook schemes/optional cash, audit mappings/progress and compact print).
Year Link failed with 'Load both financial years first' and briefly 'missing ledger markers'.
User supplied real PDFs for Sri Lakshmi Ganapathi Traders, Khammam:
- previous FY 1-Apr-2025 to 31-Mar-2026, 3 pages;
- current FY 1-Apr-2026 to 15-Oct-2026, 1 page.
Original PDFs were read locally, visually inspected and left unchanged. Exact copies are regression
fixtures khammam_previous_fy.pdf / khammam_current_fy.pdf. This cumulative ZIP retains the party
navigation fix, large-backup restore fix and all prior batches. No live user database is included.

CAUSE AND FIX
The native Tally heading is party name + 'Ledger Account', followed by an unprefixed date range.
Continuation pages have 'Party Ledger Account : <period> Page N'. These differ from both older
'Ledger Statement / For ...' and detailed group 'Ledger:' headers. Import routing fell through
to the legacy marker check and refused both files, leaving Year Link's arrays empty.
- Recognise native Ledger Account first/continuation headers and route through the existing
  geometry-based detailed adapter, not a separate guessed-text/OCR reader.
- Preserve table-column debit/credit interpretation, balancing-row inversion, omitted-zero opening
  validation, carry/final totals, inherited printed voucher dates, stable IDs and page/line evidence.
- Read address only below the party's Ledger Account heading. Both actual files correctly identify
  Telangana, not the issuer's Gujarat address. Native item layout already matches the detailed reader.
- Shared adapter means Year Link, single import, bulk import and audit all accept this native layout.
- Re-read saved source uses unchanged detailed format/schema; actual repeat imports are idempotent.

YEAR LINK LOADING / REVIEW UI
- Persistent PDF loading results identify role (previous/current), filename, success/party count or
  exact error. A toast is not the only surviving explanation for a failed PDF.
- Only successful party documents enter the matching arrays. Failed segments remain reported.
- Find Matching Parties is disabled until both roles contain successfully loaded documents.
  Programmatic guard explains which side is missing/failed and points to the loading results.
- Reselecting an already-loaded identical source skips it rather than manufacturing ambiguous matches.
  Changed PDFs remain distinct and require identity/source review as before.
- A zero opening-credit cap has a clear explanation: debit outstanding is not an unspent advance.
  Historical receipt rows remain visible for review, but unspent-registration inputs are disabled
  when the cap is zero. Saving the reconciliation without a carried source remains supported.
  Toast/linked-record text no longer claims available carried credit when none was registered.

REAL FILE CONTROLS (source-verified, not invented)
Previous FY: 22 vouchers, 15 physical item rows, 7 receipts totaling Rs275000; 6 sales, 2 returns,
6 posted CNs (including freight credit journals) and one IPT received. Missing printed opening is
validated as zero. Previous closing is debit Rs269180. Continuation carries/final totals reconcile.
Invoice 734 inherits 02-Dec-2025 from preceding voucher; receipt 2814 remains 02-Dec despite its
Cheque/DD date of 1-Dec. Jan30 invoice 803 is IPT received from Vishnu Seeds, Medru, counted once.
Current FY: opening debit Rs269180, 5 vouchers (3 genuine receipts totaling Rs130000, one sales
return Rs44149 with two physical items, and debit journal Rs25000). Closing debit Rs120031.
Sep28 journal 0156 retains its original Sep28 date, debit amount and required adjustment review;
its narration's older credit date never becomes a new receipt or a changed source eligibility date.
Actual pair matches party/location, prior closing = next opening, with opening-credit cap zero.
Saving a reviewed link adds NO opening-source money and changes NO current voucher. No ABS balance
is fabricated from historical receipts. Year Link does not silently copy prior stock into current
benefit calculations; legitimate returns without current-period supply still require stock review.

VALIDATION
167 Python calculator tests pass, including seven actual-native-layout/period/geometry/carry/date/
IPT/reparse/link tests and all prior regressions. Extended Node UI/event/API smoke uses both actual
PDF files through normal upload, failed-upload persistence/retry, repeat-file skip, matching,
reconciliation and link-save with exactly five current vouchers and zero extra receipt sources.
Six updater safety tests and JS syntax pass. Engine and working Start_CN_Fixed.bat are unchanged.
The actual 34.8 MiB backup still passes isolated restore/party navigation and HTTP restore-preview
checks: 336 preview records; all 300 workbook records retain exact entries/allocations/balances.
No PC live data or original uploaded file was modified. Windows acceptance of this Year Link fix
remains pending. Native Bajra Excel verification and remaining Phase 7 acceptance are still pending.
The earlier 'no real previous FY pair available' limitation is superseded for this supplied pair.

INSTALL / RETEST
Close calculator/server; extract full ZIP; run Update_CN.bat; select EXISTING app.py; reopen existing
Start_CN_Fixed.bat and use the fresh tab. Updater backs up code/main/private-workbook DBs first and
preserves data, .venv and launcher. Do not install the continuation source over working data.
Year Link -> choose previous PDF in Previous April–March -> current 26–27 PDF in Current year ->
check Previous: 1 / Current: 1 -> Find Matching Parties -> Review -> Reconcile and Review Receipts.
For this debit-opening pair, save only the reconciliation/review note with zero carried amounts.
Do not restore the backup or reimport saved parties merely to install this parser/UI correction.

---

# Phase 7 — saved-party ledger navigation fix and large-backup restore — 15 October 2026

LATEST USER ISSUE
Bulk-imported parties appeared in the list but opening/selecting a party seemed to show no entries.
User supplied All-Crop-CN-All-Workbooks-Backup.json (36,463,312 bytes / ~34.8 MiB). Unlike earlier
sessions, a live user backup IS NOW AVAILABLE and was inspected from the supplied local attachment.
Never overwrite it with a reproduction. Testing restored it into an isolated temporary database.

CONFIRMED CAUSE
The Select Party button and saved-party dropdown invoked startForParty: a fresh name/address-only
calculation with empty entries/allocations. That was deliberately implemented earlier, but is not
what the user expects when opening party details. The grouped list used the newest record, so a
new empty draft could hide the imported ledger as the default party action. openRecord also landed
on Step 1 Select Party rather than Step 2 Check Ledger, concealing entry details until another click.
Actual examples: active workbook test 3 has A K Traders (6 imported vouchers) and Adarsha (1 voucher),
each with a newer empty selected_party_id draft. Archived test state 2 has a similar 12-voucher case.
No importer data loss was found in those cases. Genuine source-only/no-voucher ledgers are separate.

FIX
- Party list primary action is Open Party / Ledger (N entries), opening the saved populated record.
- Group default prefers a voucher-containing calculation, then an imported source-only calculation,
  over newer name/address-only drafts. Saved Calculations still exposes every season/draft/version.
- Saved-party dropdown opens the existing saved ledger instead of silently starting an empty draft.
- Imported/populated records open directly at Check Ledger. Step Select Party remains available.
- Explicit New Calculation — name/address only is retained as a separate secondary action. It still
  does not reuse old receipts or allocations. No empty draft is deleted or silently filled/merged.
- Opening an old name-only empty draft shows a link to the saved voucher-containing ledger when
  available. A genuinely source-only imported record is labelled separately and asks for PDF review.
- No database migration, reimport or restore is needed to fix this navigation. No financial rules,
  source dates, opening/closing values, allocations, scheme settings or saved records are rewritten.

LARGE BACKUP RESTORE
The supplied backup also exceeded the server's 20 MB request limit. /api/restore now accepts up to
128 MB, including preview and confirm requests. All other API requests keep the 20 MB limit, local
host/session-token checks and prior restore validation/safety-backup behaviour. Actual full backup
was accepted for HTTP preview: 336 records. No restore confirmation was sent in that preview test.

ACTUAL-BACKUP EVIDENCE
Backup contains 36 Existing calculations records plus 79 + 52 + 169 = 300 workbook records.
The first two workbooks are already deleted/archived; they remain retained and were not restored
into the active list as part of the UI fix. The active workbook's two empty-versus-imported cases
were reproduced against a temporary restored copy with real UI functions/events/API. Primary list
and saved-party dropdown now open saved vouchers and Check Ledger. Empty-draft recovery link passed.
All 300 workbook records preserved exact entries, allocations, opening and closing values after
navigation in the isolated copy. Uploaded backup bytes were not modified. No user backup/database
is bundled in this update ZIP. Optional developer runner: tests/run_backup_navigation.py PATH.json.

VALIDATION
160 Python calculator tests pass; extended Node UI/event/API smoke passes new default navigation,
entry counts, empty-draft recovery, explicit fresh calculation and all previous flows. Actual backup
restoration/navigation and >20 MB HTTP restore preview checks pass. Final HTTP suite: 10 tests pass.
Six updater backup/data-preservation/rollback tests and JS syntax pass. Calculation engine and
Start_CN_Fixed.bat are byte-identical to the previous all-batches package. Real Windows acceptance,
a real historical prior/current FY pair and native Bajra Excel verification remain pending. Phase 7
is ongoing. User had confirmed saved-data preservation on PC before this navigation report.

INSTALL
Close calculator/server; extract full ZIP; run Update_CN.bat; select EXISTING app.py; relaunch existing
Start_CN_Fixed.bat. Open Parties -> Open Party / Ledger. It should open Check Ledger and existing
voucher rows. This cumulative package includes all previous batches and preserves DBs/workbooks,
.venv, launcher and issued-history controls. Do not replace live installation with the source folder.

---

# Phase 7 — all requested batches implemented — 15 October 2026

This cumulative package includes Batch 1 and the remaining requested batches. User requested ONE
final ZIP after all batches; this is that cumulative deliverable. Implementation is complete for
points 1–10 below. Phase 7 acceptance is NOT complete: live Windows/browser/print acceptance,
a real prior/current FY PDF pair and native Bajra Microsoft Excel verification remain pending.
No live user backup or previous-financial-year PDFs were supplied. Tests use isolated data.

1. LATE IPT
Retains Batch 1's explicit post-period IPT inclusion with a reason and cutoff validation. Original
posting dates, receipt dates, debit/credit and full ledger stay unchanged. In-period quantity
coverage includes later-posted IPT irrespective of order. Audit rates still compare invoices,
not IPT as invoices. Late review invalidates if physical source/period changes. Issued period
reuse controls remain. Check Ledger -> Late IPT / working-period review -> Include -> reason ->
save -> Confirm stock summary. This is not automatic date reassignment.

2. WORKBOOK DELETE + AUDIT LOADING
Workbooks has Delete Workbook, preview/confirmation, Deleted Workbooks and Restore. A JSON safety
snapshot is written under the existing data folder before deletion/restoration. Deletion is a
recoverable tombstone: DBs, settings, histories and issued controls remain. Stale previews are
rejected; Existing calculations cannot be deleted as a workbook. Archived workbooks are included
in all-workbook backups, restore and cross-workbook issue controls; get/open refuses until restore.
Ledger Audit displays loading immediately, an indeterminate parser progress bar, current filename,
completed-file count/percentage and a live elapsed timer. It never invents a per-page parse percent.
Final file results and errors remain separate. Year Link PDF loading also shows file/elapsed status.

3. WORKBOOK-SPECIFIC CN CROP MAPPINGS
Already-given CNs have a crop selector and Save Crop Mapping for the full normalised narration.
Stored under audit_crop_mappings in the selected workbook settings, including backup/versioning.
Mappings apply to future checks and old bulk-audit views, without changing voucher classifications,
source text or financial figures. All CNs can be explicitly mapped, not just unidentified ones.
No narration means no reusable narration map; the original source remains available for review.

4. COMPACT PRINT
Print Summary now prints one product row (net packet/kg, benefit amounts, total, per-unit rates),
a concise benefit/slab table, requests/reasons and entitlement/new-CN/balance totals. It omits repeated
per-receipt workings and all configured unused slabs. Print Detailed Working preserves the expanded
report separately. Existing frozen snapshots without product breakdown remain explicitly limited.
There is no guaranteed one-page limit for arbitrary product counts; real Windows print pagination
is not certified here. CN requests remain display-only and never alter issued/outstanding amounts.

5. BORDER-STATE IMPORTS
Retains Batch 1: different address states no longer reject single/bulk PDF imports. Actual address
is retained; selected workbook scheme state is separately stored and visibly displayed. Border
warnings are informational. Explicit manual scheme-state override still requires its existing note.

6. PRODUCT DELETE
Products & Packing has Delete Product / Restore Product. This archives IDs instead of erasing them,
so history and mappings survive. New PDF suggestions exclude archived products. Existing active
drafts using them flag restoration before finalisation; frozen snapshots remain unchanged.

7. CLEAR WORKBOOK-SCOPED SCHEMES
Settings prominently names the selected workbook and states that schemes/products belong only to
it. Sidebar workbook selection scopes the existing settings/API. No central scheme list is mixed
into a private workbook. Copies and edits remain independent.

8. SCHEME MATHS SURVIVES DELETION
Deleting schemes archives settings; engine code, supported benefit types and settled rules remain.
New schemes can still use ABS/CD/Quantity/Net/Extra/Return/Cash, with rates/dates/slabs configured
explicitly. No deleted scheme is automatically revived. Regression restores archived schemes and
verifies unchanged calculations. Deleted products may require explicit restoration or new products.

9. APRIL–MARCH FINANCIAL-YEAR LINK
New Year Link navigation loads multiple previous/current PDFs, including combined-party reports.
Matching uses party/location identity, not PDF order. Ambiguous/missing/location-different matches
require manual selection; differing identity/location requires an explicit review reason.
Previous report must cover full 1 April–31 March; current report must start the next 1 April (a
partial current-year end is allowed). Source voucher dates must fall inside their report dates.
Both ledgers must reconcile, and prior closing must equal current opening before registration.
Review shows January–March invoices, products, returns/IPT/CNs/receipts, source narration and
original receipts. User confirms ONLY the unspent amount per receipt after those purchases.
No FIFO attribution, automatic crop transfer, guessed original date or guessed ABS amount occurs.
Registration creates opening_sources allocation metadata retaining original receipt dates and
proof; it never adds old receipts to current ledger.entries. It shares the actual opening-credit
cap with existing sources and caps each traced receipt by original/confirmed unspent amount.
Optional replacement affects only explicitly selected unused undated opening registrations;
allocated registrations cannot be replaced silently. Changed traced amounts with allocations
require review/removal first. Frozen current records require a draft revision. Changed current
statements use ordinary import review before linking; existing workbooks are not overwritten.
The link/proofs/review note survive save/reopen/backup/freeze. Signatures bind physical prior
vouchers, amounts and original dates. Date/cap/proof edits invalidate source validation. Issue-time
checks reserve traced receipt allocations across other issued lineages/workbooks (including deleted
history), allowing partial splits within the confirmed pool and normal revisions of one lineage.
Bank UTRs/remaining-amount attestation still need source-document review; this is not automatic
proof that a particular receipt funded a particular purchase.

10. OPTIONAL CASH PANEL
Assign Payments defaults to Add Cash Scheme rather than displaying the editor for every party.
Adding shows the existing cash split controls. Existing splits or Cash allocations keep it visible.
Remove Cash Scheme panel is enabled only after cash splits/allocations are removed explicitly.
No quantities, source assignments or allocations are silently dropped.

PRESERVED
Original dates, full-year ledgers/selected stock periods, bulk/combined Tally support, IPT no-double-
counting, journal posted CNs, opening-credit caps, independent workbooks, DAWAT 1/3 kg separation,
per-benefit rounding, frozen/issue/revision safeguards, Saini Rs142535 and display-only CN requests.
Working Start_CN_Fixed.bat is byte-identical to the supplied version. No hosting/database service,
new Python dependency or standalone EXE is required.

VALIDATION
160 calculator Python tests pass, plus extended Node UI/event/API smoke and JS syntax. Six updater
backup/data-preservation/rollback tests pass, including failure adding the new year_link.py module.
Actual supplied combined PDF/import regressions remain covered (49 parties/329 vouchers), alongside
synthetic cross-year receipts/purchases and HTTP registration. No real historical FY pair or user's
live database was available. UI smoke is not a substitute for Windows/browser acceptance or native
Excel recalculation. Phase 7 remains ongoing until those acceptance checks are completed.

INSTALL
Close calculator/server, extract complete ZIP, run Update_CN.bat, select EXISTING app.py, relaunch
existing Start_CN_Fixed.bat and use the fresh tab. Updater backs up code + main/private workbook DBs
before installing eleven program files, including new year_link.py. DBs, launcher and .venv are not
replaced. Do not copy Current_Code_For_Next_Chat over live data. It is continuation source only.

---

# Phase 7 Batch 1 — late IPT and border-state imports — 15 October 2026

USER'S NEW REQUESTS / ACCEPTED BATCH ORDER
User authorised batch-wise work. This package completes development of Batch 1 only:
1. Late IPT handling (including return-before-IPT stock coverage).
5. Border-state parties may import despite address-state differences.
Still queued, NOT implemented in this batch:
- Batch 2: workbook deletion, product archive/delete, prominent workbook-scoped scheme lists,
  optional Add/Remove Cash Scheme panel. Deleting schemes must never delete engine maths/rules.
- Batch 3: immediate PDF audit loading/elapsed time/file progress (honest percentages only),
  workbook-specific saved CN narration-to-crop mappings, compact default print with optional details.
  User says current summary can span 12 pages and is too difficult; previous detailed print remains
  in this batch and is explicitly not yet simplified.
- Batch 4: April–March financial-year bulk-ledger linking regardless of party order, closing/opening
  reconciliation and traceable original-date ABS availability across January–March purchases.
  No guessed advances and no duplication of old receipts with opening credit. This is not implemented.

LATE IPT
- Period stock was already order-independent. Standalone audit now checks quantity coverage across
  the COMPLETE selected checking period: supply + IPT received - IPT given compared with actual
  returns. A later transfer within that period can explain an earlier return without a false
  return-without-supply warning. No earlier invoice rate becomes a timing/rate-coverage note;
  transfers do not become invoices for rate-excess comparisons. Genuine quantity shortages still flag.
- Check Ledger now has Late IPT / working-period review. Existing IPT received/given posted after
  the period end may be explicitly included with a reason, provided it is on/before cutoff.
  This uses the same voucher once for selected-period stock/benefits. Original source/physical dates,
  debit/credit, full ledger reconciliation, receipt sources and allocation dates are unchanged.
  After save/remove, stock confirmation is cleared and must be confirmed again.
- Reviews bind to season name + start/end + physical-voucher fingerprint. Period changes, source
  corrections or type changes invalidate the review; revised mapping identities alone do not.
  UI exposes Remove inclusion and Review period/cutoff. In-period IPT needs no extra review.
- Stock summaries, mapping lists, eligible allocation products, backend stock computation and
  cash input limits all use the reviewed stock scope. Save/reopen, backup/restore and frozen
  record guards retain the metadata. No automatic transfer of payment money occurs.
- Issue guards check whether the same IPT has already been included in a different issued period,
  within a store and across workbooks, including deleted issued history. This prevents using a
  reviewed late transfer again in its ordinary posting period. Normal revision lineage remains
  governed by existing prior-issued differences. This is not full cross-year advance reconstruction.

BORDER STATES
- Bulk and single import no longer reject a different statement address state. Existing identity,
  voucher, repeat-import review, source snapshots and category/state-specific scheme setup persist.
- New workbook drafts retain actual parsed address state and record workbook_scheme_state separately.
  Selected workbook scheme state is the default benefit state. Address differences show visible
  warnings on calculation and bulk results; they are informational and do not force scheme rates
  from the party's neighbouring state. Explicit manual scheme-state override still requires a reason.
- Saving/calculating workbook records tags workbook scheme state on the server. Existing finalised
  history is not rewritten or reissued. Existing records receive the field only when saved normally.

VALIDATION
148 Python tests pass, including new late-IPT order/period/review/cutoff/fingerprint/stale/frozen/
backup/issue-history and border-state controls, plus Saini Rs142535, separate DAWAT and rounding,
original receipt/allocation dates, real PDFs and all prior audit/workbook regressions.
Extended Node UI/event/API smoke passes real border import/address retention/workbook state and
late-IPT include/remove, original source conservation and stock display once, plus prior flows.
Five updater backup/data-preservation/rollback checks and JS syntax pass. Tests use isolated stores;
no live user database/backup was supplied. Windows/browser acceptance and native Bajra Excel remain
pending. Phase 7 remains ongoing. Do not claim queued Batches 2–4 are implemented.

INSTALL / TEST
Close calculator/server; extract full ZIP; run Update_CN.bat; select EXISTING app.py; relaunch existing
Start_CN_Fixed.bat. This cumulative update preserves all previous delivered code and backs up code,
main DB and private workbook DBs before replacement. No DB, .venv or launcher is replaced.
Check Ledger -> Late IPT / working-period review -> Include late IPT -> enter reason -> save ->
confirm stock summary. If posting is beyond cutoff, review cutoff explicitly first. For standalone
audit, select a period containing the transfer to assess full-period coverage; workbook CN review
assignments are not silently applied to independent PDF-only audits.
Re-select earlier failed border-state PDFs in Bulk Import to import them. Source address remains
visible and workbook schemes remain selected. Do not replace live installation with the source folder.

---

# Phase 7: standalone Ledger Audit, fresh imports after deletion, focused CN print — 15 October 2026

Latest user requirements implemented:
- New Ledger Audit navigation works independently of CN calculations/workbooks/scheme confirmation.
  Select explicit checking start/end, add multiple ordinary or combined-party Tally PDFs, Run Ledger
  Checks, inspect original page/line evidence and export the report as JSON. Session documents are
  held in memory only and are not saved as parties/calculations. No CN issue or ledger writes occur.
- Duplicate payment checks use a concrete NEFT/RTGS/IMPS/UPI reference (including same reference
  with different amounts) or exact non-generic narration with digits. NEVER warn from amount alone.
  Duplicate posted CN checks require same party, complete descriptive narration AND credit amount;
  generic CN labels are excluded. These remain review warnings, not proof of an accounting error.
- Overlapping/repeated PDFs use a multiset union of vouchers: reloading one PDF cannot manufacture
  a duplicate, but two truly repeated printed postings in a single document remain detectable.
- Posted CNs show party, date/reference, amount, narration and crop inferred only from recognised
  crop/product/alias text; otherwise explicitly unidentified. No guessed crop assignment.
- Product/packing/unit-specific return rate comparisons use earlier supplies within the checking
  period. Higher than every earlier rate is flagged; mixed rates show an uncertain range requiring
  original invoice review. No earlier matching supply produces a coverage review, not a fabricated
  excess. IPT does not become a sale for these comparisons. No FIFO or availability claim is made;
  displayed rate-difference values are potential comparisons, not approved recoveries.
- Normal workbook bulk imports also record period-specific, read-only per-party checks, show finding
  counts/links and expose reports under Ledger Audit. Comparing references across files/parties uses
  the separate audit with all PDFs loaded. Old import logs do not automatically acquire checks.
- Deleted party history no longer blocks creation/import of a NEW record with the same name/PDF.
  Bulk match/duplicate detection ignores deleted records. Archived records remain read-only and
  retained; issued-CN rows and duplicate-issue protections remain even after deleting/reimporting.
- Print Summary uses a dedicated print-only report with party/location/state/season/status,
  product/benefit CN amounts, totals and per-packet/per-kg rates, requested changes and notes,
  separately rounded CNs/proposed issue amounts, configured slabs and calculation working. It
  excludes stock/payment/allocation screens and form controls. Missing older frozen breakdowns
  remain explicitly unavailable; frozen history is not recalculated to invent detail.
- Calculation engine and Start_CN_Fixed.bat are byte-identical to the supplied version. No changes
  to Saini Rs142535, separate DAWAT segments, independent workbooks, original receipt dates,
  allocation caps, requested-change isolation, full-year ledgers, IPT or CN rounding rules.

VALIDATION
138 calculator Python regression tests pass; an additional cross-layout numerical-precision
audit deduplication test also passes. Node event/API smoke covers standalone duplicate uploads, no
calculation writes, independent audit UI, dedicated print contents, unchanged results and all prior
flows. Five updater backup/preservation/rollback tests pass. JS syntax passes. Actual 49-party /
329-voucher combined PDF exercised, repeat load does not add vouchers/findings. No user live backup
was supplied; all database tests use isolated data. Real Windows/browser print-layout acceptance
and native Bajra Microsoft Excel verification remain pending. Phase 7 is ongoing.

INSTALL
Close calculator/server; extract the COMPLETE update ZIP; run Update_CN.bat; choose EXISTING app.py;
relaunch existing Start_CN_Fixed.bat. Updater backs up all data/private workbook stores and changed
code first; installs ten program files including new ledger_audit.py and static/index.html. It does
not replace any database, launcher or .venv. Do not install Current_Code_For_Next_Chat over live data.

---

# Phase 7: Combined detailed Tally group-ledger PDF — 15 October 2026

User supplied Surendranagar.pdf from another Tally export/print layout and requested working
import support. This update extends the latest workbook build; all prior rules/data remain.

ACTUAL FILE VERIFIED
69 pages, 49 separate party ledgers, 329 vouchers and 341 product item rows. All 49 closing
balances reconcile, including five net credit balances and a fully settled zero ledger with
no printed closing-balance row. There are no missing-item/carry/closing mismatches in this file.
Reference catalogue still has unmatched products; these remain normal mapping work for the user.

IMPLEMENTATION
- New tally_detailed.py reads the detailed Group/Ledger report. Debit/Credit column geometry
  determines money direction, not the Dr/Cr label attached to the counter-account. Opening and
  balancing closing entries have the appropriate separate sign interpretation. Header/footer
  totals independently check running debit/credit accumulations.
- Party headers split the combined PDF; continuation headers retain the same party. Stored
  sources contain only that party's structured pages, original physical page/line numbers,
  raw text and independent source hashes, plus the parent PDF hash. No cross-party voucher pool.
- Real voucher rows are distinguished from cheque/bank details, Agst Ref/New Ref, ledger-account
  breakdowns, Brought Forward/Carried Over and balancing totals. These never become extra receipts
  or stock. Printed dates carry forward only within the same ledger for Tally's omitted-repeat
  date convention, including across continuation pages; the date_inherited flag records this.
  A first voucher without a preceding printed date is refused rather than assigned a guessed date.
- Quantity lines support the detailed quantity / unit / rate-per-unit / item-amount layout,
  including three-decimal packet displays and bags/kg. Voucher/item subtotals are checked.
- Wrapped GOODS RECIVED/RECEIVED FROM and DISPATCH/DESPATCH TO narrations preserve full other-party
  names and classify the same existing voucher as IPT In/Out once. Conflicting/undirected IPT
  retains manual classification. Credit-side non-stock freight journals remain already-posted CNs.
- Explicit opening/closing credit signs are retained. Omitted zero opening is identified in the
  source metadata; omitted zero closing is accepted only when actual printed final debit/credit
  totals are equal and match all accumulated postings. Inactive opening-only ledgers are supported.
- importer.import_pdf_documents returns one or several party documents. Existing single-party
  import_pdf contract remains; requesting a combined file through it gives a clear Bulk Import
  instruction. The app /api/import previews combined files; the ordinary PDF picker automatically
  routes such a file into bulk import in the selected workbook. Existing calculations/legacy mode
  asks for a workbook first. Bulk Import directly accepts one combined PDF or mixed PDF/folder lists.
- Each party gets its own saved draft/import result. A failed party segment can be logged without
  stopping other parsed parties. Changed existing parties retain the explicit review workflow.
  All prior workbook isolation, caps, original dates and no-auto-issue rules remain in force.
- Cross-layout voucher IDs retain date/header-kind/reference identities. Duplicate comparison
  normalises numerical display precision without rounding significant digits. Intraday running
  balances are presentation/order metadata, not a changed voucher: the exports list some same-day
  vouchers in a different order. Date, type, reference, actual debit/credit and physical item
  quantities/rates/amounts still detect real changes. Printed balances remain independently checked.
- Check Ledger re-read supports the stored detailed-source format without needing the original PDF
  again. After a reviewed newer statement import, latest_statement_source points to the accepted
  source while immutable first record.source and original voucher snapshots remain intact. This
  prevents re-reading an older first PDF from resetting a newer statement's closing balance.

CONTROLS
Ashapura: supply 4650 packets, IPT out 125, net supply 4525, actual return 2110, net sold 2415.
Its updated full ledger closes Rs1591149 after posted CNs 919 (Rs50000) and 1258 (Rs543375).
Compared with the earlier 13-voucher PDF, exactly those two CNs are New; the other 13 are Already
Imported, not new/doubled vouchers. Receipt remains Rs200000 on 08-Apr-2026, counted once.
Krishna Trading: supply 3250, IPT in 175, IPT out 10, net supply 3415, return 1505, net sold 1910.
Closing Rs1683058. All 14 vouchers match the earlier PDF despite same-day presentation order and
2-versus-3 decimal quantity displays. Both 14-Aug transfer directions and ordinary returns stay
separate. Other controls include Umiya opening credit Rs215700, Giriraj closing credit
Rs645172.22 and Chandrakant's zero closing with freight journal Rs17299.

VALIDATION
126 Python tests pass, including 11 new actual-file/group/column/date/carry/credit/zero/batch/
reparse/duplicate and partial-failure checks, plus every prior regression. The actual combined
file imports 49 drafts, then a second import skips all 49. Extended Node UI/event/API tests
verify the ordinary PDF picker routes to batch import; in a workbook with an existing Ashapura
draft, 48 new parties are created and one existing party is held for review. Only the two real
new posted CNs are accepted, original source snapshots/receipt date retained, queue resolved, and
latest detailed source re-read returns the updated closing without doubling anything. JS syntax
passes. Five updater tests pass, including rollback of newly added modules if the last copy fails.
Saini Rs142535, separate DAWAT, separate CN rounding, allocation/opening-credit controls, workbook
isolation and display-only product CN requests are unchanged. Full real Windows/browser acceptance
and native Bajra Excel recalculation remain pending. No live app backup was supplied; tests used
isolated databases. Phase 7 remains ongoing. This is text-based layout support, not generic OCR.

INSTALL / USE
Close calculator/server; extract ZIP; run Update_CN.bat; choose EXISTING app.py; relaunch existing
Start_CN_Fixed.bat. Updater backs up first, replaces eight program files and adds tally_detailed.py.
Saved database, workbook stores, .venv and launcher are not replaced. No new dependency required.
Select/create the Gujarat workbook -> Bulk Import -> choose working period -> select Surendranagar.pdf.
Review any new mappings and existing-party updates as usual. Combined import creates drafts only.

---

# Phase 7 expansion: Workbooks, annual ledgers, bulk import and product CN review — 15 October 2026

User approved implementation after analysis and one proportional-benefit allocation decision.
Workbooks/projects have independent schemes, rates and party records; full-year PDFs must be
retained while a selected working period drives stock benefits. Bulk import creates party
drafts. Review & Finish shows product totals and CN per packet/kg. Per-unit increase/decrease
requests are display-only and must not change calculated/issued CN or outstanding.

IMPLEMENTATION
- workbooks.py manages a manifest table in the original SQLite database plus private stores
  under data/workbooks/<uuid>.sqlite3. Existing calculations/schemes/history stay in the
  original database, selected as 'legacy'. No old records are silently moved or converted.
- Workbook creation collects name, explicit state, period name, stock start/end and cutoff.
  It copies an independent catalogue/scheme snapshot from the chosen workbook, or retains
  products/groups with blank benefit setup. No parties/payments/issued records are copied.
  Copied schemes are marked unconfirmed; source rates/dates remain for explicit review.
  DAWAT product/segment identities stay distinct within each separate workbook namespace.
- Every API request carries X-CN-Workbook. Records/settings/party operations/import/finalise
  and issue resolve the selected private store. Mismatched record workbook tags are refused.
  Switching flushes drafts and resets working UI state; switching is refused while an API
  request/save/calculation or bulk import is in progress to avoid mixing scopes.
- New workbook records use annual_ledger=true. Complete source vouchers, original payment
  dates, opening and full statement closing stay intact. Stock outside the selected period
  is omitted from benefits without a generic outside-season blocker; retained postings still
  reconcile the full ledger. Mapping/stock summaries also show selected-period stock.
  Legacy records retain their previous conservative season-boundary handling.
- All original receipt sources remain available for explicit allocation. Earlier ABS receipts
  keep original eligibility dates. Payments after the selected cutoff cannot earn ABS/CD/Cash
  benefits; documented Settlement remains available. Confirmed old-dues allocation rules and
  original opening-credit cap are unchanged. Prior-season money still requires explicit
  allocation/Settlement; there is no guessed seasonal receipt or automatic payment transfer.
  Final outstanding is full-statement closing minus proposed new period CNs, not a fabricated
  season-only ledger closing. If a current-period return has no matching period supply, the
  existing unmatched-return guard still applies.
- Bulk Import accepts many selected PDFs or a folder and sends one PDF per request. Each
  successful party draft is saved immediately; failed files are logged and do not stop later
  files. Stop finishes the current file; re-select files to resume with existing imports skipped.
  Duplicate checks include source hashes and actual voucher content, so even the same PDF can
  offer review when an older parser classified IPT differently. Updated statements never
  silently overwrite saved parties: parsed documents are retained in a persistent review queue.
  Review Updated Statement opens the matching record (or creates a draft revision for an issued
  record) and presents the normal New/Changed import review. Accepted changes preserve immutable
  originals, receipt IDs/dates and allocations. Successfully reviewed queues become Reviewed.
  Ambiguous party matches and state mismatches are surfaced; no guessed merge or new empty party.
- Product_CNs output attributes each existing separately rounded benefit CN across products.
  Shared Net/Quantity/Extra/Return/CD benefits use regular net sold quantity in that segment's
  unit; ABS follows its product-specific eligible CN; Cash follows its product. Deterministic
  largest-remainder whole-rupee attribution preserves each original rounded benefit total
  exactly. This does not recalculate/round a new grand total. Product rates divide total
  attributed CN by actual product net packets/kg, including its cash and regular quantities.
- Review & Finish leads with product total, per-packet and per-kg rates; detailed scheme/slab
  working stays under Check Benefits. Original separate benefit narrations and proposed issue
  differences remain available in a collapsed details section. For revisions, product totals
  are full current entitlement; proposed new CNs still subtract earlier issued amounts.
- cn_requests holds product request direction, rate, unit and note. Backend produces display-only
  deltas/requested totals in product_CNs. Actual CNs, proposals, rounding, issue tables and final
  outstanding never use these adjustments. Negative requested totals show a request warning and
  do not create a negative issued CN. Notes survive save/reopen/freeze/issue/backup and JSON export.
- Issuing across overlapping workbooks additionally checks previously issued matching party/
  benefit periods. Existing within-store duplicate/negative revision/frozen-state guards remain.
- All-workbooks backup includes original data, each private store, metadata and bulk review logs.
  Composite format is all-crop-cn-workbooks-backup version 1. Old all-crop-cn-backup files remain
  restorable into Existing calculations only. Restore validates all components and creates a full
  safety backup; failed multi-store restoration attempts roll back to that backup.

VALIDATION
115 Python tests pass, including all prior Saini Rs142535, separate DAWAT, separate rounding,
IPT/return, opening-credit, allocation/date, lifecycle/frozen and HTTP regressions. New tests cover
private stores/settings, period stock versus full ledger, earlier ABS dates, cutoff guard,
actual-PDF bulk imports, persistent failed/pending imports, old-parser same-PDF repair, composite
backup/restore, product-benefit conservation, direct ABS/Cash attribution, request-only save/issue
and cross-workbook overlapping issue rejection. A 200-party synthetic batch simulation verifies
independent drafts, persistence and second-pass duplicate skipping (actual PDF parser separately
exercised on supplied fixtures; this is not 200 distinct real-world PDF layout certification).
Extended Node UI/event/API smoke passes workspace switching, bulk success/failure/resume, private
scheme edits, per-unit/product views, display-only requests through finalise/issue, pending bulk
review resolution and unchanged source snapshots. JS syntax passes. Four updater tests pass,
including new module installation and nested workbook DB backup/preservation.

LIMITS / CONTINUATION
No exported live user app backup was supplied; tests use isolated data. No browser binary was
available, so real Windows/browser acceptance remains pending. Phase 7 is ongoing, and native
Bajra Microsoft Excel recalculation remains pending independently. PDF support is still the
conservative text Tally adapter; scanned/unrecognised layouts fail per file for manual handling.
No standalone EXE, new external dependency, hosting or database service is required.

INSTALL
Close calculator/server; extract complete ZIP; run Update_CN.bat; choose existing app.py; launch
existing Start_CN_Fixed.bat. Updater backs up first and replaces seven program files, adding
workbooks.py; DB/.venv/launchers are not replaced. Startup only adds required manifest/import-log
schema. New workbook files are created only when the user creates a workbook.
Use Workbooks -> Create Workbook -> review/confirm own schemes -> Bulk Import -> open party drafts.
Keep Current_Code_For_Next_Chat with this handoff for continuation. Do not use it as an empty
replacement installation over the working data folder.

---

# Phase 7: IPT narration import and stock summary — 15 October 2026

Latest user instructions: inspect both supplied 14-Aug transfer ledgers; detect IPT in/out;
ensure no duplication with supply; show Supply / IPT In / IPT Out / Net Supply / Sales
Return / Net Sold clearly; remove routine per-voucher verification ticks; explain mapping
persistence. This section supersedes earlier per-entry and mapping-confirmation requirements.

Changes:
- Narrations GOODS RECIVED/RECEIVED FROM, GOODS DISPATCH/DESPATCH TO and explicit directional
  IPT identify the existing voucher as ipt_in or ipt_out. Source invoice/Credit Note family
  still determines the original stable ID. No extra vouchers/receipts are created. Actual
  posted debit/credit, dates and quantities stay unchanged. Conflicting/undirected IPT remains
  unknown with classification required; missing item details still block finalisation.
- Header Sales Return markers cannot turn a transfer into an actual unsold return: final
  narration classification runs once per voucher. IPT expected item value uses abs(debit-credit).
- Stock Summary above Check Ledger, Check Benefits and Review & Finish: crop/unit cards and
  product rows with Supply, IPT In, IPT Out, Net Supply, Sales Return and Net Sold. Net columns
  highlighted. Raw statement figures include outside-season entries with an explicit caption;
  engine still blocks season exceptions. Kg/packet columns never mixed; product/packing rows
  retain identities. Unknown classifications and documented exclusions are made visible.
- Routine voucher reviewed and mapping confirmed checkboxes removed from UI and those flags no
  longer block calculation. Known product IDs require no extra tick; missing/ambiguous product
  mappings still block. Single Confirm Stock Summary remains, and changes invalidate it.
  Unknown classifications, source correction reasons, reconciliation, allocation limits,
  invalid packing/quantities/settings, changed re-import approval and frozen-record controls remain.
- Existing manual-original capture also works when one overall stock summary is confirmed;
  prior snapshots remain immutable. Legacy review flags remain stored without forced migration.
- Save Mapping persists catalogue crop/product/packing and the exact source product name as a
  ledger alias even for an existing product. Future party imports can reuse it. Scheme/group
  assignment and payment allocations stay per calculation; no automatic global scheme choice.

Verified cotton packet totals:
Party       Supply IPT_In IPT_Out Net_Supply Actual_Return Net_Sold
Ashapura    4650   0      125     4525       2110          2415
Krishna     3250   175    10      3415       1505          1910
Shared Ashapura->Krishna transfer is 125 Agniveer packets / Rs112625 on 14-Aug-2026.
Krishna also receives 50 packets from Giriraj and sends 10 Dhanvarsha packets to Jay Bhole.
Ashapura ledger Rs2184524 and Krishna ledger Rs1683058 still reconcile. Original 08-Apr
Ashapura receipt Rs200000 unchanged. Transfer vouchers never become payment sources.

Validation: 100 Python tests, JS syntax and extended Node UI/event/API tests pass. New checks
cover actual PDF directions/parties, product/crop stock conservation and engine totals, zero
routine-tick blockers, required exception blockers, old-draft Changed replacement on same IDs,
immutable snapshots/money/dates, second re-read Already Imported, and mapping reuse for another
party. 3 installer tests pass including CSS backup/rollback and data/environment preservation.
No browser binary available: full real Windows/browser acceptance remains pending. No live user
app backup supplied; all testing used isolated databases. Native Bajra Excel recalculation still
pending independently. Saini Rs142535 and separate DAWAT/rounding controls pass. Phase 7 ongoing.

Install: close calculator; extract complete ZIP; run Update_CN.bat; select EXISTING app.py;
launch existing Start_CN_Fixed.bat. This updater now backs up/replaces six program files,
including static/style.css, and never replaces DB/.venv/launchers. Existing drafts: use Check
Ledger -> Re-read Statement and accept Changed IPT entries; no New duplicate should appear.
Do not replace the existing installation with Current_Code_For_Next_Chat.

---

# Phase 7: Journal expense CNs and readable payment benefits — 14 October 2026

Latest user instructions: journals represent already-given freight/expense CNs;
show the scheme/slab where payment earns a benefit; make existing opening credit
available for ABS (default), CD or documented Settlement with a strict shared cap.

Changes:
- Credit-side, non-stock Journal vouchers import as posted_cn with a freight/expense
  label. Their amounts remain in ledger once; they are not receipts, new CNs or stock
  returns. Debit journals and journals with stock/IPT indicators still need review.
  Original journal IDs retained for re-read matching; original saved snapshots unchanged.
  Existing drafts: Check Ledger -> Re-read Statement and explicitly accept/review Changed
  journals. Repeat import is idempotent. Sales-return/IPT classification remains available.
- Assign Payments has per-row ABS/CD benefit previews and named scheme tables: qualifying
  quantity/tour/return rules, ABS eligible quantity/token/rate/excess, original-date CD slab
  number/window/percent/eligible payment/precise CN/unused payment, and separately rounded
  benefit totals. Progressive quantity rates are listed. No raw JSON in payment working.
  ABS product working is explicitly combined across allocations for that product; it must
  not be read as a per-receipt CN. CD unused is still assigned until manually reduced.
- Opening credit panel shows actual credit, allocated amount and remaining amount.
  Allocate available opening credit registers only the exact unregistered balance as
  allocation metadata, then creates a zero-amount ABS row for explicit scheme/product/amount
  selection. Existing credit sources are reused. No automatic money transfer or added receipt.
  Receipt-source splits default CD; opening-source splits default ABS. All allocation types
  share the backend Decimal cap; registration uses exact decimal arithmetic in UI too.
  Undated opening credit keeps existing 0% direct-CD rule; excess ABS uses first CD slab.
- New result fields describe working only. Math, dates, independent DAWAT groups, rounding,
  original snapshots, saved custom schemes and Saini Rs 142535 regression are preserved.

Validation: 92 Python tests, JS syntax, extended Node UI/event/API checks including credit
cap/default/reuse/save-reopen/zero-stop and readable slab preview, plus 3 updater tests pass.
Maharashtra still reconciles Rs 602385; posted Journal credits Rs 11900 and returns unchanged.
No live exported app backup was present in supplied update 7.zip, so tests use isolated data.
Full real Windows/browser acceptance and native Bajra Excel recalculation remain pending.
Phase 7 remains ongoing. Do not claim these app tests certify Excel.

Installation: close calculator; extract complete update; double-click Update_CN.bat;
select app.py in existing working installation; relaunch existing Start_CN_Fixed.bat.
Updater backs up code/data first and replaces only app.py, engine.py, importer.py,
store.py, static/app.js. Database, .venv, launchers and settings are not replaced.

---

# Phase 7: returns, IPT, payment remainder and review links — 14 October 2026

Latest user confirmation: adjusted supply = invoice supply + IPT received - IPT given;
net sold = adjusted supply - actual unsold returns. IPT given is separate from returns.
Quantity tiers use net sold; return percentage uses adjusted supply. Transfers never
create receipts. Actual source debit/credit postings govern ledger and item values.

Actual Maharashtra statement: opening credit Rs 552875, invoices Rs 2088000,
receipt Rs 100000 on 13-Jul-2026, four journal credits Rs 11900, sales return
Rs 820840 on 01-Sep-2026. Closing reconciles Rs 602385. Twelve vouchers; return
six item rows; packet totals 3320 supplied - 1003 returned = 2317 net.
The Credit Note header plus separate SALES RETURN marker is now recognized.
Journals are retained with explicit classification required. No rates/mappings invented.
September stock outside a confirmed August-end season now blocks finalisation for
season review, instead of being silently omitted. Source dates stay unchanged.

Assign Payments shows and blocks Next/later tabs for any remaining source money,
including registered opening-credit sources. Explicit Settlement remains available.
Final issues are clickable, opening voucher/item, allocation, scheme or season review.
Voucher popup offers Sales Return, IPT Received, IPT Given, Posted CN and Other
Adjustment, with documented review. Manual rows can be deleted in drafts; imported
rows are protected with documented Exclude available. No automatic money/date edit.

Check Ledger -> Re-read Saved Statement repairs old saved drafts with source.text:
explicitly review Changed return/New journals. Receipt IDs and allocations retained;
legacy parser IDs accepted. Original snapshots remain immutable. latest_import_source
holds the accepted parser baseline separately; declined Changed rows block finish.
If incomplete scheme rates prevent calculation, ledger/source remainder stays visible.

Verification: 86 Python tests, JS syntax, extended Node UI/event/API runtime checks,
3 installer backup/rollback tests pass. Covers actual PDF, IPT tier/return separation,
conservation caps, September flags, manual deletion, source correction/repeat import,
and payment remainder under incomplete rates. Prior Saini Rs 142535, separate DAWAT,
separate rounding and allocation cap controls pass. No live DB backup supplied.
Full Windows/real-browser acceptance and Bajra native Excel recalculation pending.
Phase 7 remains in testing. Installer preserves SQLite closing-handle fix, backs up
first and changes only five program files; DB/.venv/launcher untouched.

# Editable import mapping, per-product scheme groups and fixed CN — 14 October 2026

Implements the user's six latest requested changes:
1. Crop column has + Add / Name New Crop and an inline mapping form. It registers
   the crop with a product/packing entry without forcing the user to invent a segment.
2. Product column shows/edit-selects product names only via a name input with catalogue
   suggestions. Group/segment is chosen separately via Choose Scheme / Group.
3. Packing kg per packet is editable. A correction resolves an existing matching
   variant or creates a separate catalogue variant, preserving existing product IDs,
   packing and prior saved/frozen calculations. Confirm the corrected mapping.
4. Net Rate offers two explicit modes: existing invoice-minus-net-price slabs (default
   for old saved schemes) and Fixed CN per packet/kg. New placeholder-product scheme
   flow defaults its new Net setup to Fixed CN per packet. The fixed formula uses NET
   sold quantity converted to the selected benefit unit; it does not change source
   invoices. Redgram 27D27 example: 100 net packets at Rs 20 CN/packet gives Rs 2,000;
   gross Rs 15,000 leaves Rs 13,000 before receipts/other posted items.
5. Party name/locality/state/address suggestions are parsed only from the recipient
   header/address, not the issuing company's state. Ambiguous/missing state stays blank.
   Established saved-party locality/identity is not silently overwritten; selected or
   populated profiles are preserved and the statement address is shown for review.
6. Check Benefits/party scheme cards flag unmapped statement items and products awaiting
   a scheme, with Map Crop/Product or Choose Scheme/Group actions. User can choose a
   compatible saved crop/packing/season scheme or create one and name the group.

Implementation/data preservation:
- New inline products use neutral mapping-placeholder base schemes, hidden from normal
  scheme selectors and with no automatic benefit. needs_assignment blocks entitlement
  until the user explicitly assigns a real scheme.
- Per-calculation product_assignments maps catalogue product IDs to scheme IDs. Effective
  settings are deep-copied for working calculation; catalogue/base group identities remain
  unchanged. Existing products may be assigned to another compatible group for this
  calculation without altering other parties or frozen results. Crop and packing must
  match; alternative group-scheme overrides must stay within that group.
- New schemes created from the mapping flow use record_product_scheme, allow naming the
  group and selecting same-crop/same-packing products, and assign selected products to
  the new scheme in the current draft. Rates/dates/states still require confirmation.
- After a group change, mismatched ABS/Cash destinations and CD destinations without
  mapped group sales are flagged for review. Money is not automatically transferred;
  original receipt IDs, amounts, dates and source voucher snapshots are preserved.
- Optional JSON fields require no SQL schema change. Old Net schemes keep price mode;
  frozen settings remain immutable; allocation limits, rounding, DAWAT and Saini controls
  remain in force. Existing backup format and recovery features are retained.

Validation:
72 Python tests pass, including 12 new fixed-CN/unit/return/zero/missing-rate, record
assignment/freeze, group compatibility and recipient-address checks, plus previous
60 arithmetic/import/lifecycle/backup/HTTP regressions. Extended UI/event/API smoke
passes inline Redgram creation, pure product name and editable packing, scheme flags,
new scheme/group selection, fixed CN save/use, packing variant preservation, profile
fill, source money/date preservation and previous features. JS syntax passes.
Three installer tests pass for closed backup handles, unchanged database/environment/
launcher and rollback after a partial copy. Full real Windows/browser acceptance
remains pending. No exported live app backup has been supplied; tests use isolated data.

User confirmed previous party/scheme/mapping update installed and launched. Earlier
PC confirmations include new-crop setup, sold-only allocation choices and excessive
payment rejection. Phase 7 remains underway. Native Bajra Excel recalculation is still
pending; app tests do not certify Excel. Saini control remains Rs 1,42,535 outstanding.

---

# Party/scheme management and import suggestions — 14 October 2026

Current feature update, built on the working custom-crops update:
- Parties is now a grouped searchable party list (name + location), with Select Party
  for a fresh calculation, Open Latest and Saved Calculations. Step 1 has a saved-party
  dropdown and searchable picker. Selection copies only name/location/state; it never
  reuses receipt money or old allocations. Switching to another saved record or starting
  a new calculation saves a non-empty draft first.
- Delete Party previews all saved seasons/versions and issued-record count. Confirmation
  moves the party's records to Deleted Parties; Restore restores them. JSON tombstone
  metadata and revision updates preserve source entries, settings snapshots, results,
  issued duplicate-control rows and audit. No hard deletion or database-schema change.
  Stale previews are rejected using record/revision fingerprints. Deleted parties cannot
  be edited, issued, revised or recreated before restoration.
- My Schemes has a saved-scheme selector, Delete Scheme and Deleted Schemes/Restore.
  Scheme IDs/rates/product links remain stored; tombstones are excluded from new choices.
  Drafts using a deleted scheme require restoring it or selecting an active alternative.
  Finalised/issued frozen snapshots retain their original results. Raw removal of existing
  scheme IDs is rejected. Settings version guards prevent stale deletion/restoration.
- PDF items now carry suggestion metadata (product, crop, group, catalogue packing,
  detected statement packing, alternatives and reason). Unique name/packing matches are
  preselected; ambiguous/no-match products stay unresolved. Check Ledger shows an editable
  grouped mapping summary with Correct checkboxes and supplied/returned/net quantities.
  Changing crop/product applies explicitly to matching raw item names/units. For identical
  names requiring different mappings, individual voucher rows have Mapping correct checks.
  Original quantities, invoice values, dates and source snapshots are preserved.
- Freshly imported suggestions require confirmation before affected finalisation. Older
  records without the new mapping flag remain compatible. Mapping metadata is separated
  from physical-source corrections; changed physical source data still requires a reason.
  Repeat-import comparison uses source voucher values, ignoring changing catalogue hints,
  preventing false Changed/doubled vouchers when suggestions change.
- Importing another party's statement into an existing populated calculation is refused.
  With a different selected party but no entries, it asks whether to start a fresh calculation
  for the statement party, preserving the previous saved draft.

Validation: 60 Python tests passed, including new party/scheme lifecycle, stale-session,
HTTP, frozen-history/issued-control, backup restore, suggestion ambiguity/packing/aliases,
repeat-import and physical-source correction checks. Extended JS runtime/event/API smoke
passed selection, delete/restore, mapping correction/confirmation and unchanged monetary
source fields, plus all previous guards/custom-crop flows. JS syntax passed. Full real-browser
acceptance remains pending because this environment has no browser binary. No live exported
user backup has been provided; tests use isolated fixture/synthetic data.
Updater retains the working V2 SQLite-handle fix and now updates/backups importer.py too.
Three updater tests cover closed handles, data/environment/launcher preservation, safe
backup failure and rollback after partial program copying. No replacement database included.

PC-confirmed to date: fixed launcher/PDF import; earlier Ashapura controls and old-dues
clearance; V2 update; excessive payment rejection; custom crop flow; sold-only allocation
choices. Phase 7 remains underway; Saini arithmetic remains Rs 1,42,535 and native Bajra
Excel recalculation stays pending. Separate rounding, DAWAT groups and original dates remain.

---

# Custom crops update — 14 October 2026

Latest user steering: add arbitrary crops, their own segments/packing groups,
products and schemes. Implemented Add New Crop and Add Segment / Packing Group
in Settings → Products & Packing; Add New Crop also appears under My Schemes.
The flow collects crop/group name, kg per packet, kg/packet calculation unit, first
product, optional ledger aliases, scheme name and season. Save & Set Up Scheme
persists the group/product plus a neutral scheme draft and opens the existing scheme
wizard. No benefits/rates/dates/states from another crop are inherited. Existing
product IDs, settings and records are preserved. More products use Add New Product;
more schemes use Create New Scheme. Custom crop choices now derive from the saved
catalogue in both crop filters and the scheme wizard, with no fixed four-crop list.
Duplicate crop/group names, invalid packing and missing required fields are rejected.
Distinct packing groups retain distinct segment IDs, including existing DAWAT groups.

Validation: existing 47 Python tests pass; extended JS runtime/event/API smoke passed
new crop form/save, second packing group, duplicate/packing guards, dynamic scheme
choices, unchanged existing product/record data and a synthetic Wheat CN calculation
(100 kg, Rs 1/kg Quantity CN → Rs 100 CN, Rs 900 final balance from Rs 1,000 sales).
No live user data was used for these synthetic tests. Full new-flow Windows/browser
acceptance remains pending. No browser binary is installed here.

User confirmed V2 updater installed successfully on Windows and excessive payment
allocation is rejected. Updated packaging retains V2's contextlib.closing fix for
WinError 32: both SQLite backup handles close before the snapshot rename. Existing
Start_CN_Fixed.bat stays untouched. Product-editor acceptance led to this crop request;
original sold-only allocation selector acceptance is still pending on the user's PC.
Phase 7 stays underway; Bajra native Excel recalculation remains pending. No exported
live app backup has been received, so actual custom scheme settings remain on the PC.

---

# Phase 7 safety and product-editor update — 14 October 2026

This update continues the supplied latest source, retaining the confirmed rules below.
Phase 7 remains underway; Bajra native Excel recalculation is still pending.

## Latest changes
- Added exact Decimal input-limit validation before saving and calculating: aggregate
  all ABS/CD/Cash/Settlement assignments by source, subtract confirmed old dues first,
  reject excessive/negative/nonfinite amounts, duplicate source/allocation identities,
  opening sources beyond actual opening credit, and impossible cash quantity/value splits.
- Invalid legacy drafts retain saved inputs and visible source availability, but expose
  no CN preview and cannot be finalised until corrected. Installation does not rewrite them.
- UI rejects excessive allocation edits and source reassignment, keeps the previous value,
  and displays the remaining maximum for each row. Exact decimal split comparisons are used.
  Changes to source receipt amounts, old dues, cash splits and opening source additions also
  validate before acceptance. Backend independently checks every save and calculation.
- Products & Packing now has Add New Product / Edit Product forms. Existing IDs, crop,
  segment, packing and base scheme stay fixed. Renaming retains the previous name as a
  ledger alias and updates applicable cash-product names. New products join their base
  scheme; other saved schemes require explicit product selection in the scheme wizard.
- ABS/CD choices are filtered to mapped products with positive net sales in the selected
  season, including saved custom schemes covering those products. ABS/Cash products are
  filtered individually. Existing unavailable selections remain labelled for review;
  allocations are not silently deleted. Settlement retains broader documented choices.
- Provided Update_CN.bat + apply_update.py: choose existing app.py, back up changed code
  and data, replace only app.py, engine.py, store.py and static/app.js, preserve .venv,
  database and existing Start_CN_Fixed.bat. Close calculator windows before applying.

## Validation and limits
47 Python tests pass, including original 39 regressions, arithmetic/persistence input
limits and HTTP rejection. Extended JS runtime/template/event smoke passes for amount
reversion, combined caps, sold-only choices, product add/edit and DAWAT identities.
JS syntax passes. Updater tested in an isolated existing installation: database bytes,
.venv marker and launcher unchanged, old program files backed up, SQLite snapshot valid.
The new Windows batch wrapper itself has not been run on Windows here. Real Chromium
click-through was attempted but unavailable because no Chromium binary is installed.
Full Windows/browser acceptance remains pending; do not describe Phase 7 as complete.
Saini synthetic-date control still yields Rs 1,42,535 outstanding. All separate CN
rounding and prior rule/date tests pass. No native Excel testing was performed.

## Supplied data
The user's uploaded ZIP contained source and fixtures only: no live database, exported
app backup or custom test scheme. None was guessed or reconstructed. Their actual data
stays in their existing PC folder; an exported backup is needed to reproduce it here.

The update ZIP also contains Current_Code_For_Next_Chat with full updated source,
fixtures and handoff (no runtime data or .venv). Use this handoff first in the next chat.

---

# All-crop offline CN calculator — latest continuation handoff

Date: 14 October 2026. This file supersedes outdated implementation/UI status in the bundled Phase 6 handoff and README. Latest business-rule corrections in fixtures/confirmed_handoff.md remain authoritative over its historical appended sections.

## Current task and status

Phase 6 development build implemented. Phase 7 testing is underway on the user's Windows PC; it is not complete. The user now wants further improvements and will describe them in the new chat. Continue modifying this supplied code; do not start again or reopen settled entitlement rules. Ask one important question at a time only when necessary.

## Latest code included

Python local server, SQLite draft/history/audit storage, text Tally PDF adapter, manual vouchers/items, old-dues clearance, manual ABS/CD/cash/settlement allocations, benefit engine, per-CN rounding, reconciliation, finalisation/issue/revision guards, settings versions, backup/restore and print/JSON export.

Latest UI updates are already included:
- Settings divided into My Schemes, Seasons, Products & Packing, Backup & Restore.
- Four-step scheme wizard: Crop & Products → Choose Benefits → Rates & Slabs → Review & Save.
- Existing product/packing group is selected; user does not need to invent a new segment for a scheme based on existing products. DAWAT packing groups remain separate.
- Benefit cards and labelled unit dropdowns. Enable/disable retains entered settings. Arbitrary slab/period rows; separate Net scheme; Cash remains separately restricted.
- Save Scheme saves directly; Save as Draft allows unfinished settings. No raw scheme JSON in the ordinary wizard. Advanced catalogue editor remains available separately.
- Party cards show mapped crop/segments and chosen schemes; Change Scheme shows saved alternatives for the same group/season.
- Allocation selector now shows SAVED SCHEME NAME followed by crop/segment. Selecting a matching scheme sets the group's calculation override and updates its previous destination allocations without changing receipt dates, amounts or product booking quantities. Settlement selection does not change benefit setup.
- Separate label Amount to allocate (₹); CD processing-order field only visible with manual order enabled.
- Product selection required for ABS/Cash only; CD/Settlement have no product selector.

## User-PC verification in this chat

User confirmed:
1. PDF import worked after launching through Start_CN_Fixed.bat.
2. Ashapura product-wise supplied, returned and net sold quantities are correct.
3. Receipt ₹2,00,000 with original date 08-Apr-2026 is correct.
4. Opening outstanding ₹89,909; closing ₹21,84,524; reconciliation difference zero are correct.
5. With confirmed old dues ₹89,909, the receipt clears those dues and leaves ₹1,10,091 available, with zero old dues remaining.
6. User installed the simplified UI update and latest allocation-selector fix. User created a test scheme on THEIR PC. Its actual name/rates/products are not present in this code ZIP; retrieve them from the user's exported backup, not from guesses.

A test split of ₹50,000 Premium + ₹60,091 Deluxe was suggested only as a test example. Do not treat it as a permanent accounting instruction or a verified final allocation/CD output. Finalisation/issue/revision/export/restore and all real-account scenarios remain to be verified on the PC.

## Windows/PDF launch issue

The PDF dependencies were installed in the user's .venv (pdfplumber 0.11.9). Initial repair script stopped before checking the import. Start_CN_Fixed.bat successfully verified and launched the right Python on a fresh local port. After UI updates an older browser/server session again showed the generic missing-PDF message; using Start_CN_Fixed.bat and the new browser tab resolved it. Do not repeatedly ask the user to reinstall dependencies that already work. The user's working .venv/data reside in their existing extracted calculator folder.

Bundled Start_CN_Fixed.bat is the tested-on-user-PC launcher from this chat. It asks for app.py, verifies .venv import with actual diagnostic output, and opens the app on a fresh local port. Start_Calculator.bat also uses .venv and a fresh port, but the user should use the known-working fixed launcher when troubleshooting. Keep app instances/windows/tabs distinct. No standalone Windows EXE/installer was built.

## Calculations and settings to preserve

- Actual ledger balance already includes opening balance, receipts (ordinary and ABS), posted sales returns and already-posted CNs. Subtract only proposed new CNs once. No second payment/principal deduction.
- Old dues are allocation metadata; clear before ABS entitlement. Source original dates/amounts stay preserved. Document source corrections; original dates still govern eligibility.
- Product-wise ABS eligibility min(net sold, allocated token/token rate). Proportional booked quantity from money allowed; physical fractional packet entries forbidden.
- Used principal + allocated excess equals allocated token money. Excess ABS enters the same segment's first CD slab, without creating another receipt. No automatic product/segment money transfer.
- Ordinary original dates govern destination CD; net-rate/no applicable CD = 0%. Pre-CD benefit/principal deductions and payment-plus-CD cap retain full decimal precision. Manual order does not alter dates.
- Separate segment/benefit CNs; each rounds nearest ₹1, half up; total is sum of separate rounded CNs, never grand-total rounding.
- Both quantity and fixed highest extra CN for Bajra, plus ABS/CD. Zero sales gets no extra; return benefit disabled. Latest handoff top corrections override older no-extra bajra appendix.
- Saini approved control: ledger ₹2,79,265; quantity ₹61,200; Foreign Couple extra ₹65,000; ABS zero; CD precise ₹10,530.45 → ₹10,530; total ₹1,36,730; final outstanding ₹1,42,535. The independent test uses explicitly synthetic representative dates; actual missing receipt dates and September allocation must not be invented.
- Cotton Premium net only; Deluxe regular benefits. Inclusive no/low-return qualification includes 0% and exact threshold. Maize extra uses net sold, not ABS booked quantity.
- DAWAT 1 kg and 3 kg have independent product/segment identities, settings, allocations and CNs. Do not pool them.
- Cash advance based on cash supplied quantity; cash supplied/returned split conserves actual quantities. Extra return deduction per kg requires rate and remark (zero allowed); CN floors at zero; excess is review, no automatic recovery. Actual varying invoice-rate cash splits require documented value shares.
- Explicit state/season setup, no automatic state fallback. Missing rates/dates stay missing and block affected finalisation. Existing numerical references are drafts until production settings are confirmed.
- Finalised/issued snapshots are frozen. Duplicate full issue blocked. Revisions propose differences from prior issued totals; negative changes require review. Revised ledger must include earlier posted CNs.

## Verification evidence and pending work

Latest Python suite: 39 tests passed, including Saini, corrected bajra cap, separate DAWAT, CD/date/slab boundaries, cash, payment conservation, save/reopen/stale writes, frozen settings, duplicate issue, revision decreases, backup/restore, HTTP and custom-scheme calculation override. JS syntax passes; runtime/template smoke covers wizard save, named allocation options, amount/order labels, scheme destination changes and preserved source entries. These are not equivalent to complete real-browser acceptance.

Ashapura fixture automatically reconciles: 13 vouchers, 20 item lines, 8 unique product names, invoices ₹43,32,150, posted returns ₹20,35,535, receipt ₹2,00,000, posted bajra benefit CN ₹2,000, opening ₹89,909, closing ₹21,84,524. Cotton totals 4,650 supplied / 2,235 returned / 2,415 net packets. Unmatched other crops and returns without matching supply require review/classification.

Still pending:
- Full Phase 7 Windows/browser click-through, custom schemes, all allocation paths, save/reopen/crash behaviour, finalisation/issue/revisions and more real ledgers.
- Broader changed-layout/scanned/page-spanning PDF testing; current adapter is conservative text Tally, not universal PDF/OCR.
- Historical advance reconstruction beyond net opening credit intake: not automated. Review a documented source model rather than adding a second receipt.
- Phase 8 standalone EXE/offline dependency bundling and polished PDF/CSV outputs; current export JSON + browser print; backup/restore needs larger/corrupt-data drills.
- Bajra native Excel recalculation remains pending independently of app tests. No source formula repairs/native Excel certification.

## Data and continuation

This ZIP has SOURCE CODE AND FIXTURES, NOT the user's live database or their custom test scheme. Do not overwrite their data/.venv folders with a new empty working copy. Ask the user to export Settings → Backup & Restore → Download Backup and attach it when testing their actual scheme. Materialise/inspect the backup without posting/issuing real CNs. Work in a separate local data path for reproductions. Deliver in-place safe updates with backups and simple Windows launch instructions; avoid repeated setup commands.

For user improvements, inspect this latest implementation, apply requested changes, run relevant checks, package a clear update and retain all confirmed accounting controls. The user finds scheme/segment and payment controls confusing; prefer clear labels and simple guided flows.
