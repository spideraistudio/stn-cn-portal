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
