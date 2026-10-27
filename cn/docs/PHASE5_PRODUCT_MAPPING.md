# Phase 5 PDF product mapping correction — 22 October 2026

This is a cumulative Phase 5 correction, not Phase 6 or Windows acceptance.

## Inspection of the actual implementations

The unchanged Update35.2 `offline_baseline/importer.py:product_suggestion` recognises
names/aliases and explicit kg/gm packing. Its parser retains printed item names,
quantities, units, rates, amounts and original voucher/receipt dates. The offline
`static/app.js` groups repeated printed names, saves aliases for future parties,
and creates unconfirmed "Awaiting scheme" placeholders for new products. It does
not derive scheme benefits from printed sale rates.

Before this correction the web LedgerService passed the workbook catalogue to
that same importer, but initialized every new ledger with empty mappings. Its
`effective` projection then discarded the parser's selected products in favour
of those empty mappings. Manual mapping applied only inside one statement; the
UI repeated controls for each voucher item. New product creation was separate.
The legacy calculator shortcut could also edit only its draft without updating
the authoritative saved PDF mapping.

## Current behaviour

- Import preview shows recognised versus unresolved item counts and saves nothing.
  Apply persists safe product identities as review metadata alongside the source.
- Recognition uses this user's selected workbook catalogue only. Case/whitespace
  variations and equivalent printed weight units are accepted when identity is
  unambiguous. Broad substring matches such as LEGEND PLUS against LEGEND remain
  suggestions requiring review. Distinct 14D14 / 14D14 Gold identities are kept.
- Prior saved mappings in active statements are reused for the same printed name,
  unit and detected packing. Two different saved choices for the same identity
  block automatic reuse. Superseded statement choices do not teach new imports.
  No mappings are read from another workbook, user, or administrator account.
- Reimporting identical PDFs is idempotent. Changed statements still require
  replacement review. Unchanged rows keep their prior decisions; newly recognised
  product identities can be filled without approving changed voucher amounts,
  classifications, stock seasons, or reconciliation.
- Older saved statements show a Reuse recognised item mappings button. It fills
  unresolved identities only; it never replaces a saved choice or mutates on GET.
- Review is grouped by printed name/unit/packing. Recognised rows are collapsed;
  unresolved rows show existing compatible products and their crop/segment/pack.
  Original voucher details, dates, quantities, amounts and printed rates remain
  visible below. No per-voucher mapping ticks are required.
- With Edit ledger + Edit schemes, Add / name new product creates the own-workbook
  catalogue product and its statement mapping atomically. Product name, crop,
  segment and packing are explicitly confirmed. Failure leaves no orphan product.
  Mapping to an existing product needs Edit ledger only. Edit schemes is still
  required for catalogue aliases, products, packing, scheme rates and benefits.
- Explicit printed packing conflicting with a selected product is rejected;
  create/select the correct packing variant. DAWAT 1 kg and 3 kg stay separate.
  Ambiguous or missing packing for a new name remains a user decision.
- For PDF-backed drafts, Check Ledger's Review saved PDF product mappings button
  opens the selected saved statement and season. Its legacy per-draft identity
  controls are disabled; Choose Scheme / Group remains available. Server Save
  rejects changes that would make source product/packing identities diverge.
  After source changes, Open in calculator creates a separate refreshed draft;
  earlier drafts and allocations remain saved under the existing staleness rule.
- If calculator settings were previously saved, use Settings → Load newly added
  source products / periods with Edit schemes. Existing schemes stay intact;
  new source groups begin with no confirmed billing rate or benefits. Configure
  and confirm real scheme terms yourself. PDF sale rates are evidence only.
- Existing project interchange includes the saved mapping metadata and source
  PDFs. An explicitly imported project is an independent copy; new statements
  can reuse that copy's validated mappings without sharing future changes.

## Security and compatibility

`resolve-mappings` and `mapping` run under a fresh session, view_workspace,
Edit ledger, owner/workbook lookup and revision check in one database transaction.
`new_product` additionally requires Edit schemes. All identifiers resolve under
that owner. Client-supplied owner fields and unsupported fields are rejected.
There is no public admin recovery endpoint. The supplied local recovery utility
is included unchanged; instructions are in `docs/ADMIN_LOGIN_RECOVERY.txt`.

No database schema or backup format change is needed: reuse is derived from the
existing validated per-ledger mappings. No stored source document is rewritten.
Original dates/rates/quantities, Update35.2 financial source, both appearances,
CSS, dragging/zoom/layout code, selector fixes, Phase 4 reviews/IPT/late Kharif and
April–March Year Link remain intact. Finalisation/reports remain Phase 6,
storage/cleanup Phase 7, hosting Phase 8; mobile is deferred. No public deployment.

## Verification and Windows checklist

See `verification/phase5_mapping_http.txt` for the cumulative HTTP suite,
`phase5_product_mapping_targeted.txt` for the five mapping-specific scenarios,
`phase5_mapping_ui.txt` for both production mapping-panel DOM model tests,
`phase5_mapping_selectors.txt`, `phase5_mapping_shell.txt`,
`phase5_mapping_zoom.txt`, `offline_mapping_regression.txt`,
`preservation_mapping.txt` and `phase5_mapping_package.txt`.

On Windows, stop the previous server, back up the existing WEB data folder,
extract the whole package into a NEW program folder and run
Start_Web_Phase5_Windows.bat with the same existing data location. Do not create
another administrator or replace the offline installation.

1. Sign in as a user; open the existing project/workbook. Import a known PDF.
   Confirm preview counts, cancel without writes, then preview/apply. Check
   original dates, printed rates/quantities and separate packing variants.
2. Map one new printed name; import another party using that same name. It should
   reuse the choice inside this workbook. Another workbook/user must not inherit it.
3. Check ambiguous names and conflicting packing. Only those need decisions.
   With both rights, create/name a product from its review row. Configure the
   actual scheme in Settings; no PDF rate or benefit is silently activated.
4. Revoke Edit schemes: existing-product mapping still works with Edit ledger;
   creating products or editing schemes is blocked. Revoke Edit ledger: mapping
   and reuse are blocked. Administrator privileges do not open user ledgers.
5. For older unmapped statements, use Reuse recognised item mappings. Open in
   calculator and confirm Check Ledger shows the saved identities. After changing
   source mapping, reopen and confirm the earlier draft is retained separately.
6. Verify selector persistence, empty-list guidance, working periods, April–March
   Year Link, both appearances, card dragging, cursor zoom and saved layouts.

Phase 2 alone has passed user Windows acceptance. Phases 3–5 remain pending.
Automated checks and ZIP integrity are not Windows/native-browser acceptance.

## Mapping action feedback correction — 22 October 2026

An empty catalogue now says No saved products in this workbook. If products
exist but no packet weight matches, the dropdown says No products with this
printed packing. The new-product editor opens automatically when no compatible
existing product is available. No default products or packing are invented.

Create product and save mapping validates product name, crop, segment/group and
a positive packet weight before sending. Missing values are explained beside
the button and the relevant input is focused. Saving status and server failures
are shown in the mapping row; a successful save reloads the statement and brings
the confirmation into view. Enter weights in kg, e.g. 0.475 for 475 g.

The production button callbacks are now exercised in both standalone and embedded
panels by tests/product_mapping_actions.cjs, including the actual request payload,
empty catalogue, missing field, API failure and retry. Five real authenticated
PDF-mapping HTTP tests were rerun successfully. Browser/Windows acceptance is
still pending; a Chromium installation was unavailable in this environment.

## Saved crop choices and optional segment — 22 October 2026

User confirmed recognised products appear after import, and new-product saving
and repeat-party mapping reuse passed their Windows checks. This is acceptance
of those specific mapping checks only; overall Phases 3–5 Windows acceptance
still remains pending.

Both product-entry forms now offer saved workbook crops, an explicit Add new
crop choice, crop-filtered saved segment choices, and No segment — assign when
building / choosing a scheme as the default. The lists combine the workbook's
source catalogue and its saved financial settings only, under the current owner.
They do not expose another workbook/user or activate arbitrary Phase 3 drafts.
Case/whitespace variants of an existing crop resolve to its saved spelling.
Server creation reuses a unique existing name/crop/packing identity even when
the optional segment selection differs, avoiding a duplicate product for each
state grouping. Existing overlapping catalogue variants require an explicit
existing-product choice; none are merged or renamed automatically.

No-segment products use the unchanged offline Awaiting scheme placeholder,
with needs_assignment=true, empty unconfirmed benefits and no billing rate.
Choose Scheme / Group or Create Scheme for This Product assigns the state/season
group to the calculation through the preserved product_assignments mechanism.
A different calculation can use a different compatible scheme/group without
changing the PDF identity or previous calculation. These assignment changes now
also require Edit schemes server-side, like scheme overrides. Existing saved
assignments remain usable for read-only calculation. UI explains that permission.

Existing source crop/packing/segment identities and all previous data stay intact.
There is no financial engine or schema change, and no inferred benefits/rates.
New tests cover crop/segment lists, case normalization, no-segment placeholders,
identity reuse, two independent scheme assignments and revocation/isolation.
See verification/phase5_crop_segment_http.txt (six scenarios),
phase5_crop_segment_full.txt (cumulative suite), and updated Node action/model
checks. Overall Windows rendering/acceptance remains pending.
