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
