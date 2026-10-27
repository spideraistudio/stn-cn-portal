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
