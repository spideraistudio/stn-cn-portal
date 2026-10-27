# Automatic ABS allocation — Update26

## Using it

In Assign Payments, use **Allocate ABS by crop · automatic products**. Choose the crop and receipt
or opening-credit source, enter the amount, then click **Preview distribution**. A single eligible
active segment/scheme is selected automatically. If several segments are eligible, choose the
intended destination; amounts are never silently moved across segments or DAWAT packings.

The existing product selector now has **All eligible products — automatic split**. Entering a
positive amount with that choice opens the same preview. To correct an existing blank-product
allocation, select its saved row and click **Preview automatic product split**. It pre-fills the
existing amount/source. No old draft is silently converted merely by opening it.

Review the proposed product amounts, token/excess breakdown, scheme ABS/CD totals and any remaining
review issues. Click **Apply split to draft** to save through the normal validated record path.
After applying, every row has an explicit product and can be edited manually. Choose an individual
product to continue making a purely manual ABS allocation.

## Distribution rules

1. Only active, mapped, positive regular-net products in the selected current scheme are eligible.
   Returns, period selection, IPT and cash/regular quantity splits come from the existing engine.
2. Remaining token requirement = regular eligible quantity in ABS units × token rate, less existing
   valid ABS allocated to that product. Existing manual allocations remain untouched.
3. If funds are insufficient, distribute proportionally to the remaining requirements, conserving
   the entered amount exactly with deterministic remainder handling. Existing token/rate precision
   is retained; benefit CNs still use the unchanged separate-rounding rules.
4. If funds exceed all remaining requirements, fully fund those requirements and carry the excess
   on the first displayed product's ABS row. The existing segment calculation pools that excess
   into its first configured CD slab; it does not become a new receipt or dated ordinary CD row.
   If every eligible product is already funded, the new amount is entirely excess.
5. All generated rows keep the same original receipt/opening source. Availability after old dues,
   shared-source caps, booking dates, extension approval/note and Year Link provenance still apply.
6. Previewing/cancelling makes no database changes. Apply rechecks record revision/settings version,
   protected original dates and all normal save limits. Finished/issued records require revision.
7. Preview ABS/CD figures are totals for the selected scheme AFTER the split, including existing
   allocations, not additional entitlement to add again. Other review issues remain blocking.

## Existing Giriraj case

The uploaded backup was inspected without modification. Its full ABS amount had a blank product.
A temporary preview distributes across eligible Advance, Agniveer, D551 and Dhanvarsha and produces
both ABS and excess-ABS CD. This does not resolve the unmatched 500-packet 25D51 return, other crop
scheme mappings or the ledger-confirmation review. The 25D51 zero-net row is excluded from automatic
funding. Do not treat preview amounts as an approved final entitlement before resolving those items.
No private record, uploaded backup or derived real-party fixture is included in the update.

## Verification and installation

231 Python tests passed (221 previous + 10 new distribution tests), including the earlier 360
seeded financial scenarios. Eight updater tests passed. Full UI/API logic, Payment Studio, complete
UI, calendar/native-close, July ABS rejection and automatic distribution smoke checks passed.
The new API/UI tests exercise preview safety, exact money conservation, source/date/extension and
manual allocation limits, multiple-segment rejection, save/reopen, stale previews and frozen guards.
Real Windows visual/dialog/EXE acceptance remains pending. Minor print/CSV rechecks remain deferred.

Export a fresh complete backup, close calculator/desktop/server windows, extract the COMPLETE ZIP
separately, run Update_CN.bat and choose app.py in the EXISTING source installation. Keep using
Start_Calculator.bat. Existing launchers/data/settings are preserved; the updater backs up first.
No source restore/reimport is needed. Existing Windows EXE needs rebuilding locally. No EXE included.
