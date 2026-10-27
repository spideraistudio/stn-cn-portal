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
