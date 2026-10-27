# Ledger checks — actual posted scheme CN and NRV

17 October 2026. Added cumulatively to the held Update28 source. Delivery remains on hold.

## Confirmed scope

User selected CNs actually posted in imported Tally ledgers, not calculator-proposed or app-issued
CNs. User explicitly excluded journals, freight CNs and CNs representing returned material.
Material return quantity/value reduces net sales once; it is never deducted a second time as a
scheme benefit. No source vouchers, allocations, settings of schemes, calculation results,
financial snapshots, posted amounts or original dates are rewritten by this report.

## Use

Ledger Audit -> choose checking dates -> upload one or more PDFs/combined-party PDF -> Run Ledger
Checks. The new top section shows:
- Weighted crop averages across included parties.
- Weighted product/packing averages wherever product attribution is supported.
- Party-wise crop and product/packing detail, with per-kg and per-packet NRV.
- CN given / No scheme CN found / Needs review, with included/pending/excluded voucher evidence.

For ledgers already imported through Parties -> Bulk Import, use Check saved bulk ledgers · CN &
NRV. It reads the selected workbook's saved imported source entries, chooses the latest active
version of an imported lineage, deduplicates overlaps, excludes manual entries without PDF
provenance and preserves current calculations. No reimport is required merely to run this check.
Older stored import-audit snapshots remain historical; the combined check recomputes source-only
statistics using the current workbook's audit mappings. Audit JSON export includes the new report.

## Formula and units

Net sales value = printed product invoice amounts minus printed material return amounts.
Net quantity = invoice quantity minus returned quantity. IPT and receipts are not invoice sales.
NRV = (net sales value minus eligible posted scheme CN) / net sold quantity.
Product/packing conversion uses unambiguous source/catalogue evidence. No production scheme
activation or configured billing/CN rates are required to analyse actual posted ledger figures.

Weighted averages divide total realisation by total net quantity; they never average party rates.
Per-packet crop averages are withheld when packing differs or is unknown across groups. Distinct
DAWAT 1 kg / 3 kg product identities remain separate; crop per-kg NRV may still be available.
Currency display rounds only for presentation; source values and rate calculations retain Decimal
precision. This report does not change the calculator's separate benefit rounding or its existing
configured-billing-based NRV report.

## CN identification and review

- Only positive financial scheme credit-note postings are included. Original Journal evidence and
  freight/transport/courier evidence remain excluded even if someone labels them as scheme CN.
- Financial benefit wording and unambiguous crop/product narration can identify a CN automatically.
  Otherwise confirm its classification and crop. Generic/unclassified credits never silently become
  a zero CN. A debit/zero scheme CN or reversal needs explicit review instead of guessed netting.
- Optional product mapping applies to THIS voucher's party, date, reference, source amounts and
  item/narration evidence. It is not reused across other parties or generic DAWAT narrations.
  Crop/classification narration mappings retain the existing workbook-only reuse behaviour.
- A crop-only CN supports crop NRV. Its amount is not arbitrarily split across products; affected
  product rates remain unavailable until source evidence supports a product assignment.
- A credit note with quantity/material lines needs explicit financial-scheme classification and
  crop/product mapping before those lines may be treated as benefit reference quantities. Definite
  material returns remain returns, regardless of a scheme label. Material-return classification
  with missing quantities leaves a review item rather than inventing a stock quantity.
- Source item/voucher value mismatches, missing quantities/units, returns above supply, CNs without
  matching sales, unresolved credits, negative realisation and conflicting overlapping voucher
  versions suppress affected rates. Repeated actual postings within one ledger remain distinct;
  repeated uploads of the same evidence do not multiply the figures.
- Missing/failed files and source-coverage warnings withhold full crop/product averages. Individual
  complete party rows can remain available. Credit-only parties and unknown crop CNs are not
  silently dropped from a combined average.

No scheme CN found means no identifiable scheme CN in the uploaded/selected period. It does NOT
establish that CN is owed, absent in another period or absent from an omitted/unreadable ledger.
NRV unavailable is displayed as a dash with the reason, never as ₹0.

## Verification

Synthetic accepted reference: sales ₹1,40,000 / 1,000 kg; material returns ₹14,000 / 100 kg;
posted scheme CN ₹18,000 => net value ₹1,26,000; after-CN value ₹1,08,000 / 900 kg = ₹120/kg.
At 4 kg packing, this is ₹480/packet. Extra journal/freight credits do not change that result.
Unequal-party quantities verify weighted rather than simple-mean NRV. Tests also cover packing
separation, crop-only fallback, voucher-scoped mappings, no source/record writes, date filtering,
unknown credits, value/quantity gaps, overlap conflicts and saved-bulk source-only recomputation.

See TEST_RESULTS.txt for the final cumulative test counts. UI/API tests use a Node DOM/event
harness with the real isolated local API, not a browser/Windows visual acceptance test. Windows
checks and previously deferred minor print/CSV rechecks remain pending. Keep the file held until
user requests delivery after remaining tasks.
