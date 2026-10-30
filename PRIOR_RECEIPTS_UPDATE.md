# Public appearance consistency — 29 October 2026

Public information pages, administrator login, password recovery and their loading placeholders now share the homepage theme tokens. Legacy blue gradients, surfaces, borders, buttons and text are themed in Classic Emerald and Navy Studio. Authentication and calculations are unchanged. Native Windows acceptance remains pending.

# Credit reconciliation and optional STN fields — 29 October 2026

When reserving linked receipts, unused existing opening-credit sources are reduced to the unreserved balance. Allocated amounts are preserved; overlap with allocated amounts blocks linking with the exact amount and instructions to reduce/reassign existing splits first. Ledger balances and accounting entries are unchanged. Tested credit-opening and debit-opening cases.

STN business summary is optional, including blank or short text (maximum 5000 characters). Buyer required delivery date and final quotation date/time are optional. An omitted deadline keeps the requirement open until manually closed/cancelled. Populated dates must be valid and future; quotation deadline need not precede delivery. Supplier offers keep their own required validity/delivery dates, and buyer delivery caps apply only when the buyer specified a date. No live deployment or data migration performed. Windows/browser acceptance of these changes remains pending.

# Carried-credit conversion — 28 October 2026

In Assign Payments choose Allocate available opening credit. Select crop, ABS scheme, conversion date and amount. The chosen date must be in the scheme booking window and controls the applicable benefit slab. Original receipt/CN dates remain in statement evidence; no new ledger receipt is posted. Select a product and amount in the resulting ABS allocation. Remaining opening credit can be converted separately within its shared limit. Linked dated receipt reservations continue to use their original dates. Windows visual acceptance remains pending.

# Follow-up correction — 28 October 2026

Unused carried credit, including prior CN credit, is eligible for next-season ABS using the existing opening-credit allocation path. Prior dated receipt reservations retain actual booking dates. Total opening credit and its reserved/unreserved portions are displayed together. For Mahalaxmi the net opening is ₹10,00,000: ₹5,08,534 reserved receipt plus ₹4,91,466 other carried credit; neither is inserted as new ledger money.

Corrected the ABS save validator to recognise reserved receipt dates. Added Unlink previous year for imported drafts; allocations against linked receipts must be removed first. The current statement and opening balance stay intact. Successful imports close the import dialog and show a notification. Receipt-history saving no longer requires a separate review checkbox; amount, identity, provenance and duplicate-use validation remain enforced. Native Windows acceptance remains pending.

# Prior receipts inside Payment Allocation — 28 October 2026

This is the cumulative offline combined STN + All Crop CN application, based on branch `fix/combined-portal-production`, commit `aa4e8937c6d826e6567ef37c8d5b2c23878ef9eb`. This update is for owner acceptance on Windows, not internet deployment. It does not migrate or erase any data. The original Meet-Dev repository and current hosted website were not changed.

## Try the update

1. Follow `START_HERE_WINDOWS.md`. For an existing installation, stop all services and back up the complete `integration-data` directory, including its keys. Extract this package into a separate folder. Keep the old folder as rollback. Never run both copies against the same data directory. Do not initialise a new administrator over existing accounts.
2. Start the app normally and sign in. Open CN Calculator, the correct workbook and the current seller statement. Import the current PDF normally if it is not already saved.
3. Open **Assign Payments → Prior receipts & crop reservations → Add previous-year statement PDF**.
4. Choose the previous full April–March PDF. A combined-party PDF is supported if it contains exactly one matching prior ledger. The software reads the seller name, full address and location and compares them automatically with the saved current statement. No typing or manual identity override. Extraction line breaks and repeated whitespace are normalised; words, case and punctuation must match. Missing, different or ambiguous identities are blocked, as are different issuing companies, non-adjacent financial years and unreconciled boundary balances.
5. The receipt period initially covers January–March. Change the dates and refresh if December or another period is needed. Receipt references, original dates, amounts, earlier dues and available balances come from the PDFs. Earlier dues clear first. Later paddy/other-crop invoices do not consume a protected advance automatically.
6. Select the receipt(s), choose the reserved crop, and confirm the review. The amount is prefilled from the computed availability; reduce it only for a documented earlier use or a deliberately partial reservation. The current release reserves each selected prior receipt for one crop; its normal product/segment payment splits remain available inside that crop. It does not guess a crop from bank narration.
7. If a CN was earned before a receipt but posted later, expand **Late-posted CNs**. Select the affected original receipt, enter its actual earlier earning date and approval evidence, and refresh the working. The CN amount and posting date are read automatically. A PDF generally cannot prove the earning date; the software must not invent it.
8. Save the reviewed sources. Use the ordinary payment allocation controls to assign ABS/CD/Settlement under the selected scheme. This does not calculate ABS on a reservation alone: existing sold-quantity, token, scheme-date, product and benefit rules still apply.
9. Reopen the party, check saved amounts/dates, compare your known CN calculation, and test restart before accepting the update. Native Windows acceptance and verification with your actual statements remain pending.

## Agreed financial examples

Earlier dues ₹2,00,000, January receipt ₹3,00,000 and a verified ₹90,000 earlier-earned CN posted in February: ₹1,10,000 clears adjusted dues and ₹1,90,000 can be reserved for cotton. A later paddy invoice does not subtract from that cotton reservation. Without the CN approval, available January surplus is ₹1,00,000. With only ₹1,00,000 received, no surplus remains even after that CN adjustment.

Net ledger opening is not an available-advance test. Gross opening dues for ordinary current receipts are the net opening plus protected reservations, floored at zero. The reserved sources have already cleared their own earlier dues and do not clear those dues again. Protected and unreserved opening-credit sources cannot both claim the same balance. No receipt is inserted into the ledger twice; opening, closing and original voucher dates remain unchanged.

A saved reservation is crop-specific. Cross-crop ABS/CD use is blocked; an intentional Settlement needs a reason. To change a reservation already allocated, review/remove its existing allocations first. Current balances and formula results do not silently change old issued calculations; create an explicit revision.

The same receipt is checked across this owner's saved workbooks, including issued history. A new unissued revision cannot release an issued ancestor's locked amount. A late CN cannot be redirected to release a second receipt in another saved calculation. Independent project imports retain their evidence but cannot be used to finalise/issue duplicate protected receipt consumption. Separate user-owned installations cannot audit each other's unshared/offline data.

## Implementation and limits

The original `cn/offline_baseline` files are preserved byte-for-byte against the supplied manifest for all 133 public files; seven private fixture PDFs were intentionally absent from GitHub. Three baseline batch files needed their original CRLF line endings restored after Git text normalisation. An explicit `cn_web/financial_runtime/engine.py` extends the original engine only for protected receipt sources, original-date availability, gross dues and crop constraints. Its benefit formulas are otherwise unchanged. `prior_payments.py` handles canonical statement review, reservations and reuse checks. Account ownership, permissions, quota enforcement, saved payloads, clean-profile defaults and STN routes remain in the existing adapters.

The main Year Link navigation entry is moved into Assign Payments. Older Year Link records and their legacy review APIs remain readable. Existing legacy allocations are not silently replaced; the new flow requires their review/removal first. Unknown packet weights remain deferred and are never invented. Unsupported/scanned or unreconciled statements are not automatically approved.

Fresh executed results are in `verification/prior_receipts_*`; previous `full_audit_*` results remain historical and have not been relabelled as fresh. Windows installation still requires Node/Python and first-setup downloads, as explained in `START_HERE_WINDOWS.md`. This is not a self-contained EXE.
