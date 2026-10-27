# All Crop CN Web — Phase 5 calculator interface

PC-only local review, cumulative from the supplied Phase 4 package.
**The calculator uses the preserved Update35.2 Classic Emerald and Navy Studio
interface.** The account console remains available for account administration.
No hosting, mobile work, storage enforcement or automatic cleanup is enabled.

## Windows setup

1. Stop the previous web server and back up the WEB data directory.
2. Extract the complete ZIP into a NEW program folder. Keep the offline
   installation and its data separate.
3. If needed, run `Setup_PDF_Windows.bat` once for the selected Python.
4. Run `Start_Web_Phase5_Windows.bat`. Open http://127.0.0.1:8787 and sign in
   with the existing account; choose **Open calculator**.
5. Direct calculator address: http://127.0.0.1:8787/calculator.

Existing default web data remains `%LOCALAPPDATA%\AllCropCNWeb`.
Custom-data installations must keep the SAME path:
`python manage_web.py start-local --data PATH`.
Python 3.10+ is required. Only a fresh installation needs
`Setup_Admin_Windows.bat`. No credentials or working user databases are bundled.
A project and workbook must already exist; create them in Projects & workbooks
if this is a fresh account. The original Workbooks screen can create additional
workbooks with state, season and independent scheme copies.

## Use the calculator

- Select a project/workbook in the original left navigation.
- Switch **Classic · Emerald / Navy Studio** in the original top bar.
- Open **Settings** to edit financial schemes with the original guided builder.
  Source catalogue products get unconfirmed, empty benefit groups; enter and
  confirm real rates, states, dates and benefits before relying on results.
  Phase 3 opaque scheme dictionaries are retained as drafts, not auto-activated.
- **Parties → Bulk Import PDFs** opens reviewed single/bulk import inside the
  same calculator shell. Choose Preview, review the batch, Apply or Cancel.
  Source products/periods and mapping/review forms use the Phase 4 services.
- Select a saved statement and season, then **Open in calculator**. This creates
  an owned draft and opens Check Ledger. Reopening unchanged evidence resumes
  its draft. Changed evidence creates a separate draft; earlier edits remain.
- If products/periods were added after financial setup, Settings →
  **Load newly added source products / periods** adds empty benefit groups.
- Continue through the original ledger, payment-allocation and benefit screens.
  Manual parties/entries and reviewed corrections remain available. Original
  posting dates cannot be rewritten. All payment eligibility uses receipt dates.
- Use the existing ABS/CD/Cash preview/apply controls, diagrams, independent card
  dragging, cursor-focused zoom, lock and Save layout. Merely selecting a node
  or cancelling a preview saves no financial changes.
- **Ledger Audit** and **Year Link** reuse Phase 4's forms/services within the
  calculator shell. Audits remain category-first. Year Link keeps original
  receipt dates and the opening-credit cap; it creates no automatic ABS booking.
- Use **Projects & workbooks** for web JSON project export/import. Version 3
  includes calculator drafts, settings history and layouts, plus source PDFs,
  mappings, reviews and Year Link. Import creates a separate project. Offline
  `.cnwork` or SQLite archive restoration is not enabled in this web phase.

Late Kharif CNs keep their posted dates and ledger credit during Rabi. Review
benefit season in the source forms. Stock benefits use explicit stock-season
reviews. The adapter includes reviewed late returns/IPT within cutoff without
moving any voucher or receipt date. See the Phase 5 security note for the exact
calculation projection and source-staleness rules.

## Acceptance checklist on Windows

1. Existing login, user rights and projects still work. User B cannot see A.
2. Both appearances match Update35.2; menus/forms, dragging and cursor zoom work.
   Save separate layouts for both appearances; reopen/restart and confirm them.
3. Import single/combined PDFs, cancel preview, apply and reimport a repeat.
   Open the reviewed statement from Parties and verify all ledger entries.
4. Confirm rates with the original scheme builder, then test ABS/CD/Cash previews,
   apply, unused CD release, token-only ABS and manual allocation. July receipts
   must not become ABS. Check original dates and amounts after allocation.
5. Review late Kharif CN/return/IPT while Rabi supply exists. Confirm each season's
   net sold, ledger closing, Year Link original dates and unspent opening cap.
6. Revoke Edit schemes: settings, quick creation and imports cannot bypass it.
   Revoke Allocate payments: direct saves and preview/apply routes must reject it.
7. Export/import a project, verify the independent copy, layouts and dates, then
   restart. Current work must remain separate.

Phase 2 Windows acceptance was confirmed by the user. Phase 3/4 Windows
acceptance remains unconfirmed. Phase 5 Windows/native-browser visual acceptance
is also pending. Automated verification is documented in `PHASE_HANDOFF.md`.

Finalisation, issue/revisions and reporting/print/export completion remain
**Phase 6**. Their preserved controls cannot issue/finalise through an offline
fallback. Saved baseline frozen history and financial source remain untouched.
Storage allowance enforcement and safe temporary cleanup are Phase 7; hosting
is Phase 8. No public deployment.

## Workbook / statement / season selection correction

The selected project and workbook are now remembered together. Create a workbook
through Workbooks → Create Workbook to save its working season in both calculation
and source-review screens. For an older workbook with an empty Working season
list, use Parties → Bulk Import PDFs → Working periods to add its actual season
name and dates. Do not create a second workbook merely to fill a season list.

Saved statement lists contain only PDFs whose preview was applied in the current
user's selected workbook. PDFs held only in the separate offline installation do
not appear automatically. Import the relevant PDFs in the web workbook.

Year Link requires two saved reports in that same workbook: the previous full
April–March financial year, and the following year (partial year allowed). Choose
previous first, then current; review the party and dates before saving. For
example, 1 April 2025–31 March 2026 and 1 April 2026–your statement's end date.
Empty lists now show the missing prerequisite. Financial calculations are unchanged.

Stop the previous server, extract this corrected package into a NEW program
folder, and run Start_Web_Phase5_Windows.bat using the same existing web data
location. Reopen /calculator. Do not bootstrap the administrator again.

## PDF product mapping update

Known products and previously saved printed-name mappings now reuse this user's
selected workbook catalogue on import. New, ambiguous or conflicting identities
remain for review in Parties → Bulk Import PDFs / Open imported ledger. Repeated
names are grouped; original printed names, rates, quantities and dates are kept.
For older unmapped statements, choose Reuse recognised item mappings.

Mapping existing products needs **Edit ledger** on your own login. Adding products
needs **Edit ledger + Edit schemes**; the administrator grants these permissions
without managing your workbook data. New product rows offer Add / name new product
and confirm crop, segment and packing. PDF rates do not create scheme benefits.
If financial settings already exist, load newly added source products in Settings
and configure the real rates/benefits. Details and PC checks:
`docs/PHASE5_PRODUCT_MAPPING.md`.

Check Ledger → Review saved PDF product mappings opens the authoritative saved
statement. After changing source mapping, reopen the calculation; the previous
draft remains saved. The attached local admin-recovery tools are included beside
manage_web.py, with instructions in docs/ADMIN_LOGIN_RECOVERY.txt.

If the product list is empty, use Add / name new product and fill all four
fields: product, crop, segment/group and packet weight in kg. Click Create
product and save mapping. Errors now appear beside that action; a successful
save displays confirmation. This works in Phase 5 with the required permissions.

Product entry now uses saved crop and segment dropdowns. Select + Add new crop
only when needed. Segment is optional: No segment leaves the product awaiting
a scheme; assign its final state/season group with Choose Scheme / Group or
Create Scheme for This Product. Choosing/changing that assignment requires
Edit schemes; it does not alter the product's original PDF identity.
