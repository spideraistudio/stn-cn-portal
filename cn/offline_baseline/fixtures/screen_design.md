# All-crop offline CN calculator — Phase 5 screen design

Date: 13 October 2026
Status: Phase 5 COMPLETE — user accepted the screens, navigation and additional Create New Scheme layout on 13 October 2026, stating that UI improvements can follow later. All 18 design recommendations are accepted. Visual styling can be refined later without reopening settled calculation rules. No production app, importer or calculation engine implemented in this phase.

## Authority and preserved limitations

Use All_Crop_CN_Phase_5_Handoff(1).md (libfile_44acd304e6348191b49a175c2258045d) together with this design. The latest authoritative corrections in that handoff override older appended material. Calculation-rule arithmetic and Saini reconciliation are complete. Bajra native Microsoft Excel recalculation remains pending; the available-engine changed-input test did not establish live recalculation. Source Excel formulas do not implement all amended business rules. Do not reopen confirmed calculation rules.

Preserve all crop/state/season/segment/product/packing mappings, separate benefit CNs, manual allocations and transfers, old-dues-first ABS treatment, original receipt dates, CD caps, cash restrictions, exact precision and separately rounded CNs. DAWAT 1 kg and 3 kg stay in separate segments. Settings are editable drafts with historical versions; there is no automatic state fallback or automatic within-season rate schedule.

## Accepted design principles

English only. Simple guided workflow with freely accessible tabs and completion indicators. Plain labels such as Money received, Amount still available and Party still owes. Detailed workings expand under Show calculation. Clean light theme, readable text, Indian rupee grouping, dates such as 08-Apr-2026. Colour always accompanied by status text. Back / Save Draft / Next throughout. Autosave after valid draft changes, visible saved time and manual Save Draft. Production autosave and persistence remain to be implemented and tested.

## Main navigation

Dashboard; Parties; Calculate CN; Settings; History. Backup/Restore accessed from Settings; summary/CN exports accessed from Review & Finish and saved records.

### Dashboard

Party search and New Calculation at top. Continue Draft shows party/location, season, last saved time and next unfinished step. Needs Review opens relevant unresolved items. Recent calculations display status and whether the shown balance is before or after proposed CN. Totals are derived from saved records, never invented dashboard statistics.

### Parties

Search name/location; season and status filters. Rows show party, location/state, season, draft/finalised/issued status, outstanding or credit and Open/Continue. Party detail preserves identity and source ledger history. Company address state defaults scheme state; documented seasonal override is available.

## Party calculation workspace

Party and season stay visible. Five guided tabs: Select Party; Check Ledger; Assign Payments; Check Benefits; Review & Finish. Tabs allow revisiting sections; unresolved prerequisites block finalisation, not draft viewing. Summary panel shows reconciled ledger outstanding before new CN, proposed rounded CN sum, final party outstanding or excess credit, unallocated money and review items. Allocation availability is not treated as a second accounting credit or deduction. Segment balance is labelled separately from overall party balance.

### 1. Select Party

Party search/select; season; default scheme state; documented override and reason. Import Tally PDF or Enter Manually. Missing production dates/settings remain visibly draft. No placeholder date can qualify transactions or enable finalisation.

### 2. Check Ledger / Tally import review

Accepted input family: text-based Tally PDFs using the company's consistent statement layout. Offline local extraction is planned. No cloud AI or internet is needed for the target format. Imported PDFs are not assumed correct without review and reconciliation. Scans, changed layouts and unsupported entries require a clear error/review path rather than guessing.

Top: number of unique product/packing variants, payment total, ledger outstanding, import status. Tabs:

- Products: source name, matched product, packing/unit, supplied quantity, returned quantity, net sold. Crop/segment grouping; cotton-only and whole-ledger product counts clearly distinguished. Kg/packet conversion visible; fractional-packet conflicts flagged.
- Payments: every original receipt date, amount, voucher/reference and source status. No forced ABS allocation.
- Other Ledger Entries: opening debit/credit, already-posted CNs, other-crop entries and traceable adjustments.

View details expands original voucher date/type/number, source rate and line amount. Preserve varying invoice rates per entry; never replace them with one guessed product rate. Product aliases saved in settings; unmatched product/packing requires mapping. Distinguish itemised sales-return credit notes from already-issued benefit CNs. Unknown classifications require review. Preserve all actual ledger entries, including entries outside selected CN eligibility, for accounting reconciliation.

Highlighted problems offer Fix this; source entry displayed alongside correction fields. Preserve original source amounts/dates; separately audit reviewed corrections and remarks. Source-date correction cannot silently gain eligibility. Review current/prior-season returns without matched supply. Match opening plus transaction totals against source closing. Block finalisation on unexplained mismatch.

Repeat imports show Already imported / New / Changed. Skip duplicates; compare changed entries with their preserved originals before accepting. Handle repeated headers/page totals without counting them as transactions. Page-spanning voucher items must retain their parent voucher and source traceability.

### 3. Assign Payments

Order: Check starting balance and old dues; ABS Allocation; CD Payment Allocation.

Starting balance plainly identifies Old outstanding to clear or Opening credit available. Show source receipt amount, old dues cleared, amount available afterward and remaining old dues. Clearing old dues is allocation metadata, not another ledger debit/deduction.

ABS: eligible receipts/opening credit shown with Available / Assigned / Unallocated. Select one source then Split this payment. Rows: crop, segment, product, assigned amount and remark. Show crop ABS period; extension approval and remark where required. Preserve original dates and restrictions. Product eligibility remains product-wise; no automatic reallocation. Used principal and excess ABS are visible in working; excess allocated ABS enters configured first CD slab without creating another receipt. Unallocated money earns no ABS benefit.

CD: choose receipt and manually split across crop/segment. Original date, source amount, available after old dues, assigned total, available remainder and destination rate visible. Chronological processing default. Transfer unused payment manually, retaining original date and destination rules. Net-rate/no applicable CD = 0%; money still settles balance. Show cap-limited eligible amount and excess available for manual reassignment. Ordinary receipts needing assignment must be assigned before finalisation.

Cash Scheme Split: separate panel for eligible product, cash supplied and returned quantities, assigned eligible payment, required advance and relevant dates. Show regular quantity remainder; never auto-assign remaining money. Cash return flag exposes editable additional deduction Rs/kg and required remark, including explicit zero. Show normal cash CN, additional deduction, floored final cash CN and excess deduction needing review. No automatic debit/recovery.

### 4. Check Benefits

Expandable card per crop/segment. Header: selected scheme, total segment CN and review status. Quantities: supplied, returned, net sold and units. Separate rows for Quantity, ABS, CD, Return and Extra, enabled as configured. Cash benefit shown separately when applicable.

For per-unit CN, show eligible quantity and Rs/kg or Rs/packet. Fixed extra shows tier name and rupee total; CD shows eligible payment and percent. Zero/disabled benefits explained but do not issue zero-value CNs. Total equals sum of individually rounded CNs.

Show calculation expands directly beneath the row: applied tier, product eligibility, payments/slabs, pre-CD deduction order, cap, full-precision result, rounding adjustment and rounded issued proposal. Monetary display uses two decimals; preserve additional precision internally and in explanatory cap working when necessary. Source links expose constituent transactions. Segment amount due or excess allocated payment shown distinctly; overall party balance in summary panel. View Settings exposes applicable version read-only; settings editing is in separate Settings area.

### 5. Review & Finish

List each separate segment/benefit CN with narration, crop, segment, season, constituent products as relevant, precise amount, rounding adjustment and rounded amount. Show ledger balance minus sum of proposed new CNs, final due/credit and unresolved items.

Needs correction blocks finish and offers Fix this; Information does not block by itself. Finish Calculation opens a confirmation of all CNs, totals and due/credit. Only after prerequisites pass freeze quantities, ledger snapshot, allocations, settings version and calculation version. Finalised record read-only. Mark CNs as Issued is separate from calculation finalisation; track issued party/crop/segment/season/benefit and prevent duplicate full issue. Create Revised Version preserves original version and proposes difference only for already-issued entitlement; negative adjustment requires review, not automatic posting.

Print/Export Summary and Separate CN Details planned; exports reflect rounded separate CNs and clearly distinguish draft/finalised/issued.

## Settings

Sections: Seasons; Products & Packing; State/Segment Mapping; Schemes & Rates; CN Narrations.

Preserve full handoff settings, including four regular combinations, separate manually chosen cash allocation, crop-season-state applicability, aliases, unit conversion, ABS and extended approvals, quantity and extra tiers, return threshold/rate, inclusive CD windows/caps/order, cash dates/restrictions, narration and rounding. DAWAT packing variants remain separate. Copy Previous Season creates editable draft and highlights fields to confirm; source version retained. Show overlap/gap/missing mapping and invalid unit errors. No silent fallback or mutation of issued rules.

## Additional accepted requirement: Create New Scheme

User confirmed on 13 October 2026: create schemes by selecting crop and enabling/disabling benefit types. This extends the initial four selectable regular combinations into a configurable new-scheme builder; the original confirmed schemes remain unchanged. New combinations need compatibility validation before production use; no new entitlement maths are implicitly approved by the screen controls.

Entry: Settings → Schemes & Rates → Create New Scheme (also exposed directly in the updated mockup for review). Fields: crop, state(s), season, scheme name, segment, products/packing, quantity unit. Each benefit can be included/removed using a labelled switch, preserving draft entries when disabled.

- ABS: booking dates/extended cutoff, token rate and unit (Rs/kg or Rs/packet), incentive CN rate and unit. Existing approval/manual product allocation safeguards retained.
- Quantity: add/remove arbitrary slab rows; quantity above and up-to boundaries; CN rate/unit; whole-quantity or progressive mode. Fixed trip/extra CN worth is configured separately to retain separate benefit CNs.
- Extra/tour: add/remove tiers; quantity boundaries; benefit name; CN worth as fixed rupee amount or unit rate. Highest qualifying tier, net-sold basis and zero-sales rule retained.
- CD: add/remove periods; inclusive start/end dates; percentage. Existing original-date rules, explicit zero periods, deduction order and cap retained.
- No/low return: maximum return percentage based on supplied quantity, bonus rate/unit applied to net sold quantity. Inclusive threshold retained.
- Net rate: billing/reference rate, net rate and unit. Incompatible benefit combinations require review; cash remains a separate manual allocation with its own restrictions, not a freely combined regular benefit.

Preview Scheme gives a plain-English summary of enabled components, entered rates/units, tiers and dates. Save Scheme Draft preserves the new setup without activating incomplete fields or changing existing/issued versions. Validation: required fields, nonnegative rates, proper range coverage/equality, no overlapping CD dates, unit conversion, configured state/season, product packing membership (especially DAWAT separation), and benefit compatibility. Retain the distinction between unlimited configurable rows and the agreed highest-tier/no-stacking rules.

Updated inline mockup starts on the scheme builder. Add/remove slab rows, benefit toggles, crop-dependent product choices and Preview Scheme are local design interactions only. Production persistence, scheme validation and calculator execution remain Phase 6 onward.

## History and backup/export

Search/filter party, season and crop. Show saved time, version, state/scheme version, status, CN total and due/credit with source snapshot. Compare changed inputs/settings/allocations and result differences. Read-only issued versions; separate revision/issue actions. Backup/Restore controls designed, including restore preview and confirmation before overwriting records. Backup, restore, imports, save/reopen, duplicate controls and exports remain implementation/testing work in Phases 6–8.

## Sample evidence used in screen design

### Saini (preserve approved final result)

Reconciled actual ledger outstanding Rs2,79,265. Separate rounded CN proposals: quantity Rs61,200; Foreign Couple extra Rs65,000; CD Rs10,530; ABS Rs0. Sum Rs1,36,730. Final outstanding Rs1,42,535; excess party credit Rs0. Receipt/old dues/posted return deductions are already included in ledger balance: subtract only proposed new CNs from it. Bajra segment due before September allocation Rs1,62,835; other-crop net Rs9,700; September actual receipt Rs30,000. Production September allocation still required. Do not invent exact dates absent from supplied handoff.

### Ashapura (import layout sample, not new CN entitlement calculation)

Source: Ledger_Statement - Ashapura Seeds, Chuda - 20261013 (1).pdf, libfile_bcbc679ca1708191b7f99a07454945db. Period 08-Apr-2026 through 13-Oct-2026.

| Cotton product / 475 g | Supplied packets | Returned packets | Net packets |
|---|---:|---:|---:|
| Advance | 1,500 | 1,313 | 187 |
| Agniveer | 2,525 | 680 | 1,845 |
| D551 | 375 | 53 | 322 |
| Dhanvarsha | 250 | 189 | 61 |
| Total | 4,650 | 2,235 | 2,415 |

8 unique products in whole statement: four cotton plus sesame, bajra, Res.Angur and soybean. Cotton billing Rs901/packet. Actual receipt Rs2,00,000 on 08-Apr-2026. Opening debit Rs89,909; invoices Rs43,32,150; posted returns Rs20,35,535; already-posted bajra CN Rs2,000. Closing Rs21,84,524 reconciles exactly. Sesame/bajra returns have no matching supply in this statement and require season classification. Additional product aliases/mappings need review. These are import review issues, not permission to alter confirmed cotton schemes.

## Accepted 18 recommendations

Dashboard search/actions; searchable/filterable party list; PDF and manual entry; three import tabs; original-source/correction comparison; duplicate-import review; starting balance then ABS/CD flow; per-payment split; separate cash panel; labelled blocking/information statuses; five settings sections; previous-season draft copy; autosave/manual save; finalisation confirmation; read-only final records/revision/separate issue; searchable version history/comparison; print/export/backup controls; light English interface with Indian amounts/dates. All accepted by user on 13 October 2026.

## Next action

Phase 5 layout and workflow acceptance is complete. Next: Phase 6 offline app implementation using the authoritative handoff and this accepted design. Visual UI refinement is deferred by the user. Do not claim importer, persistence, issue/export/backup or production validation has already been implemented. Bajra native Excel recalculation remains pending independently of screen-design completion.

## Ready-to-paste Phase 6 prompt

Start Phase 6 implementation of my offline all-crop CN calculator using All_Crop_CN_Phase_5_Handoff(1).md and All_Crop_CN_Phase_5_Screen_Design.md. Phase 5 screens/navigation and crop-based Create New Scheme builder are accepted; we will improve visual UI later. Preserve confirmed crop/state/season/segment/product/packing settings, separate benefit CNs, manual ABS/payment allocations and transfers, old-dues-first ABS eligibility, original receipt dates, payment conservation, CD caps and rounding. Preserve Saini final outstanding Rs1,42,535. Implement the simple English guided workflow, Tally PDF import review, manual entry, draft save/reopen, benefits working, party reconciliation, finalisation/version/issue controls and configurable scheme builder without copying known source Excel defects. Use Ashapura's supplied Tally PDF as a text-based import fixture; preserve original entries and distinguish posted benefit CNs from sales returns. Calculation-rule verification is complete; bajra native Excel recalculation remains pending. Do not claim production tests or native Excel verification are complete. Keep Phase 7 import/save/reopen testing and Phase 8 packaging/backup/export work clearly tracked, even where supporting functions are implemented earlier.
