# All-crop CN — Phase 4 final verification and Phase 5 handoff

Date: 13 October 2026

Status: confirmed-rule arithmetic, boundary tests and Saini real-party reconciliation passed. Artifact Tool recalculation was attempted across all source workbooks; the bajra changed-input check did not update its dependent output, so full workbook recalculation verification is incomplete. Microsoft Excel-native verification remains unperformed because Microsoft Excel is not available in this environment. No source workbooks were modified and no CN was issued. Proceeding to screen design is supported; do not claim native Excel certification or app implementation/testing is complete.

## Authoritative corrections after the earlier handoff

Latest user-confirmed rules override conflicting older reports and source formulas.

Bajra has BOTH quantity CN and a separate fixed extra-benefit CN. Use combined segment net sold kg; apply the selected quantity rate to the entire net sold quantity and only the highest qualifying extra tier. Zero sales gives zero CN. Return benefit remains disabled.

| Net sold kg | Quantity CN Rs/kg | Separate extra CN Rs | Benefit |
|---|---:|---:|---|
| Above 0 through 330 | 16 | 15,000 | Ranthambore |
| Above 330 through 630 | 20 | 25,000 | Ujjain |
| Above 630 through 1,050 | 25 | 35,000 | Kashmir Single |
| Above 1,050 through 1,650 | 27 | 55,000 | Thailand Couple |
| Above 1,650, including beyond old top threshold | 32 | 65,000 | Foreign Couple |

For decimal kg, above 1,650 selects Foreign Couple; there is no uncovered interval between 1,650 and 1,651.

Billing Rs400 per 1.5kg packet; ABS token Rs50/kg and incentive Rs10/kg. Product-wise ABS eligibility remains min(net sold, allocated token/token rate). Deduct quantity CN, extra CN, ABS CN and used token principal before CD. Only allocated excess ABS enters the first 7% CD pool. Ordinary payments retain original dates: through 30 June 2026 7%, through 15 July 5%, through 31 July 3%, thereafter 0%.

DAWAT inherits bajra's numerical QUANTITY thresholds/rates only, not its added fixed tour CN. Both DAWAT packing segments remain separate, without extra or return benefits. All other crop rates and mappings remain as recorded in the earlier handoff.

## ABS workflow decisions

Crop-wise normal booking period and extended acceptance cutoff are editable per season. Extended-period ABS requires approval per party and a remark. Keep original receipt dates. Clear old outstanding before allocating remaining funds manually to crop, segment and product ABS. Unallocated money stays visible and earns no ABS benefit. Bajra's latest confirmed acceptance is January through March at the latest; Saini June receipts do not qualify as ABS. Do not reuse the earlier generic February example as a crop rule.

## Saini real-party verification

User confirmed no transactions 1–9 April and no January–March ABS advances outside the statement. Use the agreed old-dues treatment of the Rs49,565 opening debit. The actual ledger includes other crops and all actual receipts, including Rs30,000 in September.

| Accounting control | Rs |
|---|---:|
| Opening debit | 49,565 |
| Invoice debits | 7,89,000 |
| Posted sales-return credits | (2,69,300) |
| Actual receipts | (2,90,000) |
| Reconciled closing debit before new CN | 2,79,265 |
| Quantity CN: 1,912.5kg × Rs32 | 61,200 |
| Foreign Couple extra CN | 65,000 |
| ABS CN | 0 |
| CD precise: (50,435 + 1,00,000) × 7% | 10,530.45 |
| Issued-proposal CD, rounded separately | 10,530 |
| Total proposed new CN | 1,36,730 |
| Final outstanding after proposed CN | 1,42,535 |
| Excess party credit | 0 |

Bajra net billing Rs5,10,000. Before CD: 5,10,000 − 61,200 − 65,000 = Rs3,83,800. First 7% pool Rs1,50,435 is below 3,83,800/1.07; all qualifies. After payment and precise CD: Rs2,22,834.55. August Rs60,000 at 0% leaves Rs1,62,834.55. Rounded accounting balance Rs1,62,835 plus other-crop net Rs9,700 less September receipt Rs30,000 = Rs1,42,535. No receipt or old-dues clearance is deducted twice. September allocation remains a production input, without extra CD in this example.

## Additional corrected bajra cap case

Synthetic supply 400kg, return 40kg, ABS allocation Rs30,000; ordinary payments Rs30,000 at 7% and Rs30,000 at 5%. Net billing Rs96,000; quantity CN Rs7,200; extra CN Rs25,000; ABS CN Rs3,600; used principal Rs18,000; excess ABS Rs12,000. Pre-CD balance Rs42,200. First pool Rs42,000 is capped to 42,200/1.07; precise CD Rs2,760.74766355, rounded Rs2,761. Second pool earns zero additional CD. Total rounded CN Rs38,561; actual receipts Rs90,000; final credit Rs32,561. This replaces the obsolete no-extra bajra synthetic case in the earlier handoff.

## Verification performed

- 213 assertions passed, zero failures. Includes boundary fixtures, configured-crop examples, corrected bajra/Saini, ABS excess, CD caps, cash supply-based eligibility, return deductions and separate CN rounding. Selected checks intentionally reproduce known source defects; passing those checks does not mean the source business rule is correct.
- Whole-workbook recalculation was invoked in disposable copies; source hashes remain unchanged. Matching existing cached values alone does not prove active recalculation.
- Numeric populated outputs matched existing cached values within tolerance; no formula errors were found. Maize blank-string outputs export as empty cells; no previously nonblank formula result was lost.

| Source | Formula cells | Nonblank recalculated outputs | Formula errors | Populated cached differences |
|---|---:|---:|---:|---:|
| GJ cotton customized.xlsx | 7,616 | 7,616 | 0 | 0 |
| MAIZE all type CN -V5.xlsx | 154,001 | 3,320 | 0 | 0 |
| RJ_Bajra_ABS_Credit_Note_Calculator_v6.xlsx | 16,014 | 16,014 | 0 | 0 |

Matching caches shows engine consistency, not agreement with all amended business rules. Source Excel formulas still differ from the agreed specification:

- Cotton excludes zero returns and exactly 10% from return bonus; the confirmed rule includes both. It awards Rs3,950 extra at zero sales; the confirmed rule awards zero.
- Maize tour eligibility uses ABS-eligible quantity rather than net sold quantity; automatic transfer and pooled product ABS must be replaced with manual transfer and product-wise eligibility.
- Bajra does not implement the final separate fixed extra CN and agreed full pre-CD deduction order. Source results must not be used unchanged as production entitlement calculations.

## Remaining checks and setup

Changed-input probes updated cotton extra CN to Rs15,000 and maize tour CN to Rs25,000 as expected. Bajra input B3 was changed to 750 packets, for which source formulas imply pre-payment balance Rs2,90,000, but the engine returned the old Rs1,34,750. A separate override attempt also retained the old output. Therefore the available engine did not establish live bajra recalculation; this must be resolved or checked in native Excel before full Phase 4 sign-off. This failure is separate from the 213 passing independent arithmetic checks.

Microsoft Excel-native recalculation remains unperformed. Artifact Tool recalculation is not Microsoft Excel-native validation. Source spreadsheet compatibility remains a recorded limitation; no source formula repairs were requested.

Before live finalisation, enter/approve season, applicable state settings and crop-wise ABS periods/cutoffs; retain draft status if missing. These are editable production settings rather than unanswered numerical rates. Software validation, import, allocations, version freeze, duplicate issue prevention, save/reopen, backup and exports require later implementation and testing.

## Final payment clarification confirmed by the user

All actual ordinary receipts and ABS token payments reduce outstanding once. Eligible ABS CN is a separate additional deduction. Used ABS principal plus allocated excess ABS equals allocated token money; moving excess into CD does not create another receipt. When starting from actual reconciled ledger closing balance, receipts, opening balance and posted sales-return credits are already included: subtract only proposed new CNs. Never deduct receipts or used token principal again from that closing balance.

Saini direct check: Rs5,10,000 bajra net billing − Rs50,435 − Rs1,00,000 − Rs60,000 − Rs61,200 quantity CN − Rs65,000 extra CN − Rs10,530 CD = Rs1,62,835 bajra due. Add other crops Rs9,700 and deduct September receipt Rs30,000: final party due Rs1,42,535. The Rs49,565 old debit was cleared from the original first Rs1,00,000 receipt; the remaining Rs50,435 is used above.

## Phase 5 scope and completion

Design screens and navigation for the offline calculator before implementation. Show: dashboard; parties and source ledger/import review; crop/state/season/segment/product/packing/scheme settings; receipt and opening-credit allocation with old-dues clearance and extension approvals; sales and returns; calculation working and separate benefit CNs; party reconciliation and due/credit; review flags and finalisation; saved calculation versions and issue history. Future backup/export controls can be designed without claiming implementation.

Use editable draft settings for missing production dates; show prerequisites before finalisation. Keep original source amounts/dates separate from allocations, with clear available/used/unallocated amounts. Show ledger closing balance minus proposed CN as the accounting result and segment workings separately. Never count a payment again when using the ledger closing balance. Design both kg and packet entry, separate DAWAT packing segments, and manual cash-return deduction/remark resolution.

Phase 5 completion means the screen layout, field placement, navigation and sample interactions have been reviewed and accepted. It does not mean Phase 6 app implementation, Phase 7 import/save/reopen tests or Phase 8 packaging are complete. Ask one material design question at a time; do not reopen confirmed rates.

## Phase 5 prompt

Start Phase 5 screen design for my offline all-crop CN calculator using the attached handoff. Phase 4 calculation rules, boundary tests and Saini reconciliation are complete; bajra native Excel recalculation remains pending. Work on screen design now, preserving that limitation. This file contains the latest authoritative corrections and the earlier full handoff appended below; use both, with the latest corrections taking precedence. This report supersedes all prior bajra benefit interpretations and Saini totals. Preserve separate segment/benefit CNs, manual allocation and transfers, old-dues-first ABS eligibility, configurable crop/season/state/product mappings, original receipt dates, CD caps and exact precision with separate rounding. Show source ledger, segment balances, party due/credit and unresolved inputs clearly. Build screen design before Phase 6 app coding. Do not claim the original Excel source formulas implement the amended rules. Native Excel validation remains unperformed; available-engine and confirmed-rule tests are recorded here.

## Assertion evidence

| Check | Actual | Expected | Result |
|---|---|---|---|
| Cotton whole-quantity slab at 0 | 150 | 150 | PASS |
| Cotton whole-quantity slab at 299 | 150 | 150 | PASS |
| Cotton whole-quantity slab at 300 | 150 | 150 | PASS |
| Cotton whole-quantity slab at 301 | 175 | 175 | PASS |
| Cotton whole-quantity slab at 499 | 175 | 175 | PASS |
| Cotton whole-quantity slab at 500 | 175 | 175 | PASS |
| Cotton whole-quantity slab at 501 | 200 | 200 | PASS |
| Cotton whole-quantity slab at 999 | 200 | 200 | PASS |
| Cotton whole-quantity slab at 1000 | 200 | 200 | PASS |
| Cotton whole-quantity slab at 1001 | 225 | 225 | PASS |
| Cotton whole-quantity slab at 10000 | 225 | 225 | PASS |
| SingleCross whole-quantity slab at 0 | 2.5 | 2.5 | PASS |
| SingleCross whole-quantity slab at 199.99 | 2.5 | 2.5 | PASS |
| SingleCross whole-quantity slab at 200 | 2.5 | 2.5 | PASS |
| SingleCross whole-quantity slab at 200.01 | 5 | 5 | PASS |
| SingleCross whole-quantity slab at 500 | 5 | 5 | PASS |
| SingleCross whole-quantity slab at 500.01 | 7 | 7 | PASS |
| SingleCross whole-quantity slab at 1200 | 7 | 7 | PASS |
| SingleCross whole-quantity slab at 1200.01 | 10 | 10 | PASS |
| SingleCross whole-quantity slab at 2500 | 10 | 10 | PASS |
| SingleCross whole-quantity slab at 2500.01 | 15 | 15 | PASS |
| SingleCross whole-quantity slab at 5000 | 15 | 15 | PASS |
| SingleCross whole-quantity slab at 5001 | 15 | 15 | PASS |
| DoubleCross whole-quantity slab at 500 | 10 | 10 | PASS |
| DoubleCross whole-quantity slab at 500.01 | 15 | 15 | PASS |
| DoubleCross whole-quantity slab at 1500 | 15 | 15 | PASS |
| DoubleCross whole-quantity slab at 1500.01 | 20 | 20 | PASS |
| DoubleCross whole-quantity slab at 2500 | 20 | 20 | PASS |
| DoubleCross whole-quantity slab at 2501 | 20 | 20 | PASS |
| Bajra partial whole-quantity slab at 330 | 16 | 16 | PASS |
| Bajra partial whole-quantity slab at 330.01 | 20 | 20 | PASS |
| Bajra partial whole-quantity slab at 630 | 20 | 20 | PASS |
| Bajra partial whole-quantity slab at 630.01 | 25 | 25 | PASS |
| Bajra partial whole-quantity slab at 1050 | 25 | 25 | PASS |
| Bajra partial whole-quantity slab at 1050.01 | 27 | 27 | PASS |
| Bajra partial whole-quantity slab at 1650 | 27 | 27 | PASS |
| Bajra partial whole-quantity slab at 1650.01 | 32 | 32 | PASS |
| Bajra partial whole-quantity slab at 10000 | 32 | 32 | PASS |
| Cotton extra at 0 | 0 | 0 | PASS |
| Cotton extra at 300 | 3950 | 3950 | PASS |
| Cotton extra at 301 | 15000 | 15000 | PASS |
| Cotton extra at 500 | 15000 | 15000 | PASS |
| Cotton extra at 501 | 17500 | 17500 | PASS |
| Cotton extra at 1000 | 17500 | 17500 | PASS |
| Cotton extra at 1001 | 50000 | 50000 | PASS |
| SingleCross extra at 0 | 0 | 0 | PASS |
| SingleCross extra at 1499 | 0 | 0 | PASS |
| SingleCross extra at 1500 | 25000 | 25000 | PASS |
| SingleCross extra at 2999 | 25000 | 25000 | PASS |
| SingleCross extra at 3000 | 50000 | 50000 | PASS |
| SingleCross extra at 5001 | 50000 | 50000 | PASS |
| Proportional cotton ABS eligible | 100.4 | 100.4 | PASS |
| Proportional cotton ABS CN | 2510.0 | 2510 | PASS |
| Proportional cotton ABS excess | 0.0 | 0 | PASS |
| Product A eligible | 400 | 400 | PASS |
| Product B eligible | 400 | 400 | PASS |
| Product A excess stays available within segment | 10000 | 10000 | PASS |
| Old dues cleared once | 50000 | 50000 | PASS |
| Receipt remaining for ABS after old dues | 100000 | 100000 | PASS |
| Insufficient receipt leaves old dues | 50000 | 50000 | PASS |
| Cotton representative Quantity | 180000 | 180000 | PASS |
| Cotton representative ABS | 18500 | 18500 | PASS |
| Cotton representative Extra | 17500 | 17500 | PASS |
| Cotton representative Return | 9000 | 9000 | PASS |
| Cotton representative CD | 21200.00 | 21200 | PASS |
| Cotton pre CD | 400900 | 400900 | PASS |
| Cotton total CN | 246200 | 246200 | PASS |
| Cotton final due, reconciled ledger only | 64700 | 64700 | PASS |
| SingleCross representative Quantity | 15000 | 15000 | PASS |
| SingleCross representative ABS | 10000 | 10000 | PASS |
| SingleCross representative Extra | 25000 | 25000 | PASS |
| SingleCross representative Return | 3750.0 | 3750 | PASS |
| SingleCross cap handworked CD | 39537 | 39537 | PASS |
| SingleCross product-wise excess | 25000 | 25000 | PASS |
| SingleCross total CN | 93287 | 93287 | PASS |
| SingleCross final party credit | -143287 | -143287 | PASS |
| No ABS still gets extra | 25000 | 25000 | PASS |
| No ABS no ABS CN | 0 | 0 | PASS |
| DoubleCross representative Quantity | 38000 | 38000 | PASS |
| DoubleCross representative ABS | 19000 | 19000 | PASS |
| DoubleCross representative Extra | 0 | 0 | PASS |
| DoubleCross representative Return | 0 | 0 | PASS |
| DoubleCross representative CD | 6880.00 | 6880 | PASS |
| DoubleCross CN total | 63880 | 63880 | PASS |
| DoubleCross final due | 52120 | 52120 | PASS |
| Return threshold 0/1000 | True | True | PASS |
| Return threshold 100/1000 | True | True | PASS |
| Return threshold 101/1000 | False | False | PASS |
| Return threshold 0/0 | False | False | PASS |
| Combined return qualification uses 8%, not product B 20% | 0.08 | 0.08 | PASS |
| Payment cap used | 1E+2 | 100 | PASS |
| Payment cap CD | 8 | 8 | PASS |
| Payment cap unused stays credit | 100 | 100 | PASS |
| Zero balance no CD | 0 | 0 | PASS |
| Zero-rate payment settles balance | 60 | 60 | PASS |
| Cotton CD boundary 2026-06-15 | 0.08 | 0.08 | PASS |
| Cotton CD boundary 2026-06-16 | 0.04 | 0.04 | PASS |
| Cotton CD boundary 2026-07-15 | 0.04 | 0.04 | PASS |
| Cotton CD boundary 2026-07-16 | 0.02 | 0.02 | PASS |
| Cotton CD boundary 2026-07-30 | 0.02 | 0.02 | PASS |
| Cotton CD boundary 2026-07-31 | 0 | 0 | PASS |
| Maize CD boundary 2026-06-15 | 0.12 | 0.12 | PASS |
| Maize CD boundary 2026-06-16 | 0.08 | 0.08 | PASS |
| Maize CD boundary 2026-06-30 | 0.08 | 0.08 | PASS |
| Maize CD boundary 2026-07-01 | 0.05 | 0.05 | PASS |
| Maize CD boundary 2026-07-15 | 0.05 | 0.05 | PASS |
| Maize CD boundary 2026-07-16 | 0.02 | 0.02 | PASS |
| Maize CD boundary 2026-07-30 | 0.02 | 0.02 | PASS |
| Maize CD boundary 2026-07-31 | 0 | 0 | PASS |
| Bajra CD boundary 2026-06-30 | 0.07 | 0.07 | PASS |
| Bajra CD boundary 2026-07-01 | 0.05 | 0.05 | PASS |
| Bajra CD boundary 2026-07-15 | 0.05 | 0.05 | PASS |
| Bajra CD boundary 2026-07-16 | 0.03 | 0.03 | PASS |
| Bajra CD boundary 2026-07-31 | 0.03 | 0.03 | PASS |
| Bajra CD boundary 2026-08-01 | 0 | 0 | PASS |
| Cotton to maize transfer on 1 July uses destination 5% | 0.05 | 0.05 | PASS |
| Cash date 2026-03-11 | False | False | PASS |
| Cash date 2026-03-12 | True | True | PASS |
| Cash date 2026-03-31 | True | True | PASS |
| Cash date 2026-04-01 | False | False | PASS |
| Cash representative required_advance | 300000 | 300000 | PASS |
| Cash representative net | 2900 | 2900 | PASS |
| Cash representative normal_CN | 116000 | 116000 | PASS |
| Cash representative deduction | 3000 | 3000 | PASS |
| Cash representative final_CN | 113000 | 113000 | PASS |
| Net-basis advance 290000 is insufficient | False | False | PASS |
| User-confirmed 20000 less 3000 | 17000 | 17000 | PASS |
| Cash CN zero floor | 0 | 0 | PASS |
| Cash excess deduction review | 1000 | 1000 | PASS |
| Explicit zero return deduction | 20000 | 20000 | PASS |
| Cash plus regular supplied conservation | 10000 | 10000 | PASS |
| Cash plus regular returned conservation | 500 | 500 | PASS |
| Cash plus regular net conservation | 9500 | 9500 | PASS |
| Rounding half rupee upwards | 101 | 101 | PASS |
| Separate rounding sum | 30 | 30 | PASS |
| Grand total rounding differs and is not issue total | 31 | 31 | PASS |
| Ledger due 80000 less CN 30000 | 50000 | 50000 | PASS |
| CN greater than due creates credit | -10000 | -10000 | PASS |
| Revised CN proposal only difference | 2000 | 2000 | PASS |
| Revised lower CN requires review | -2000 | -2000 | PASS |
| Cotton kg converts to whole packets | 1E+2 | 100 | PASS |
| Fractional packet conversion flagged | True | True | PASS |
| DAWAT one and three kg variants remain separate | True | True | PASS |
| Cotton cached row4 M | 4325 | 4325 | PASS |
| Cotton cached row4 Q | 25950 | 25950 | PASS |
| Cotton cached row4 R | 3950 | 3950 | PASS |
| Cotton cached row4 O | 0 | 0 | PASS |
| Cotton cached row4 CD rounded | 5807 | 5807 | PASS |
| Cotton cached row4 total | 40032 | 40032 | PASS |
| Updated cotton principal already included | 78398 | 78398 | PASS |
| Source unchanged GJ cotton customized.xlsx | 10afe662df9ed3870aab150b5bc42639671cec100e82f2901a311a606ecf7cfb | 10afe662df9ed3870aab150b5bc42639671cec100e82f2901a311a606ecf7cfb | PASS |
| Source unchanged MAIZE all type CN -V5.xlsx | c510fa87fd3c1bc94d426a76b4cc94525a6d1627ce6640edae643db123d4b09a | c510fa87fd3c1bc94d426a76b4cc94525a6d1627ce6640edae643db123d4b09a | PASS |
| Source unchanged RJ_Bajra_ABS_Credit_Note_Calculator_v6.xlsx | 5dac72471a085393448c780531701f2a3ff65773f5b37761871d80cb6d9f1654 | 5dac72471a085393448c780531701f2a3ff65773f5b37761871d80cb6d9f1654 | PASS |
| Source formula Cotton at exact 10% excludes return CN (known override) | 0 | 0 | PASS |
| Source formula Cotton at zero return excludes return CN (known override) | 0 | 0 | PASS |
| Source formula Cotton zero sales extra 3950 (known override) | 3950 | 3950 | PASS |
| Selected source Cotton formula chain total reproduces 40032 | 40032 | 40032 | PASS |
| Selected source Cotton formula chain pre-CD balance reproduces 78398 | 78398 | 78398 | PASS |
| Source formula maize no ABS tour 0 (known override) | 0 | 0 | PASS |
| Source formula maize pooled ABS eligible 1500 (product-wise override) | 1500 | 1500 | PASS |
| Source formula automatically transfers 20000 (manual-choice override) | 20000 | 20000 | PASS |
| Bajra source pre-payment balance only deducts ABS CN | 134750 | 134750 | PASS |
| Final bajra quantity rate 0 | 16 | 16 | PASS |
| Final bajra separate extra 0 | 0 | 0 | PASS |
| Final bajra quantity rate 0.01 | 16 | 16 | PASS |
| Final bajra separate extra 0.01 | 15000 | 15000 | PASS |
| Final bajra quantity rate 330 | 16 | 16 | PASS |
| Final bajra separate extra 330 | 15000 | 15000 | PASS |
| Final bajra quantity rate 330.01 | 20 | 20 | PASS |
| Final bajra separate extra 330.01 | 25000 | 25000 | PASS |
| Final bajra quantity rate 630 | 20 | 20 | PASS |
| Final bajra separate extra 630 | 25000 | 25000 | PASS |
| Final bajra quantity rate 630.01 | 25 | 25 | PASS |
| Final bajra separate extra 630.01 | 35000 | 35000 | PASS |
| Final bajra quantity rate 1050 | 25 | 25 | PASS |
| Final bajra separate extra 1050 | 35000 | 35000 | PASS |
| Final bajra quantity rate 1050.01 | 27 | 27 | PASS |
| Final bajra separate extra 1050.01 | 55000 | 55000 | PASS |
| Final bajra quantity rate 1650 | 27 | 27 | PASS |
| Final bajra separate extra 1650 | 55000 | 55000 | PASS |
| Final bajra quantity rate 1650.01 | 32 | 32 | PASS |
| Final bajra separate extra 1650.01 | 65000 | 65000 | PASS |
| Final bajra quantity rate 1651 | 32 | 32 | PASS |
| Final bajra separate extra 1651 | 65000 | 65000 | PASS |
| Final bajra quantity rate 10000 | 32 | 32 | PASS |
| Final bajra separate extra 10000 | 65000 | 65000 | PASS |
| Corrected bajra preCD all benefits | 42200.00000000000000000000000000000000001 | 42200 | PASS |
| Corrected bajra cap CD rounded | 2761 | 2761 | PASS |
| Corrected bajra quantity once | 7200 | 7200 | PASS |
| Corrected bajra extra once | 25000 | 25000 | PASS |
| Corrected bajra total | 38561 | 38561 | PASS |
| Corrected bajra final credit | -32561 | -32561 | PASS |
| Saini preCD | 383800.0000000000000000000000000000000001 | 383800 | PASS |
| Saini qualifying payment full | 150435 | 150435 | PASS |
| Saini CD precise | 10530.45 | 10530.45 | PASS |
| Saini total new CN | 136730 | 136730 | PASS |
| Saini ledger closes | 279265 | 279265 | PASS |
| Saini final due | 142535 | 142535 | PASS |
| Saini other crops and September bridge | 142535.0000000000000000000000000000000001 | 142535 | PASS |
| Purnima final configured total | 63880 | 63880 | PASS |
| DAWAT 1kg final configured total | 34298 | 34298 | PASS |
| DAWAT 3kg final configured total | 34298 | 34298 | PASS |
| Research Paddy final configured total | 3500 | 3500 | PASS |
| Premium final rate 0 | 700 | 700 | PASS |
| Premium final rate 300 | 700 | 700 | PASS |
| Premium final rate 301 | 675 | 675 | PASS |
| Premium final rate 500 | 675 | 675 | PASS |
| Premium final rate 501 | 650 | 650 | PASS |
| Premium final rate 1000 | 650 | 650 | PASS |
| Premium final rate 1001 | 625 | 625 | PASS |
| Premium final rate 2500 | 625 | 625 | PASS |
| Premium final rate 2501 | 625 | 625 | PASS |
| Premium 400 final CN | 90400 | 90400 | PASS |


---

# Earlier complete settings and handoff (historical; latest corrections above override conflicts)

# All-crop CN — Phase 4 updated settings and verification

Date: 13 October 2026

Status: initial numerical rates supplied; representative arithmetic checked. Phase 4 remains open for initial season/date/state setup and real-ledger/full workbook verification. No app code or source Excel changes.

## Decisions after the first Phase 4 report

- Both Gujarat cotton categories bill at Rs901 per 475g packet.
- Premium is net-rate-only, using combined segment net sold packets. Whole-quantity net prices: up to 300 Rs700/packet; above 300 through 500 Rs675; above 500 through 1,000 Rs650; above 1,000 through 2,500 Rs625. Highest rate continues beyond 2,500. Zero sales → zero CN. Net-rate adjustment CN = net packets × (901 − qualifying net rate), separate Premium narration. No ABS/CD/extra/return stacking for this scheme.
- Deluxe extra rupee totals confirmed: positive net sales up to 300 packets Rs3,950; above 300 through 500 Rs15,000; above 500 through 1,000 Rs17,500; above 1,000 Rs50,000. These are converted gift/tour values, not additional physical entitlements to count twice. Zero sales gives zero extra; highest qualifying tier only.
- Bajra corrected: the Rs16/20/25/27/32 per kg bands are converted gift/tour **Benefit Slab CN**, not a separate quantity CN plus extra CN. Apply to the entire eligible net sold quantity once. Thresholds up to 330/630/1,050/1,650 kg; above 1,650 Rs32/kg, including beyond 9,999. Gives Benefit Slab CN + ABS CN + CD CN; no return benefit. This overrides the original mandatory-quantity-plus-extra interpretation of Scheme 3.
- Purnima / Threeway Cross bills Rs160/kg. Other regular scheme settings follow DoubleCross: token Rs40/kg, ABS Rs10/kg, quantity rates Rs10/15/20 per kg at 500/1,500/above; maize CD dates/rates; 4kg packing; no extra or return. Separate segment calculation and CN. Inheriting regular settings does not grant cash eligibility.
- DAWAT 1kg and 3kg variants: billing Rs300/kg; token Rs100/kg; ABS Rs25/kg; **quantity CN** uses bajra's numerical thresholds/rates once; CD follows cotton's 8/4/2/0% dates. No extra or return benefit. Same numerical rates, but separate segments, allocations, calculations and CN identities; do not pool packing variants.
- Research Paddy / Janki Gold, Karina, Karishma: billing Rs70/kg; token Rs25/kg; ABS Rs2.50/kg; **quantity CN disabled**; CD follows cotton for now; 10kg packing; no extra/return. ABS remains product-wise.
- Future-year crop settings and mappings must be editable: crop/segment/product/packing/state/season assignments, scheme applicability and rates. Copy prior season into a new draft; preserve historical identities, versions and issued snapshots. User clarified that individual benefits must support enabled/disabled states, since bajra and Research Paddy do not fit rigid mandatory component combinations. Do not treat disabled benefit as missing data or invent a required rate.

## Newly checked sample arithmetic

| Synthetic case | Benefit/quantity CN | ABS CN | CD CN rounded | Total new CN | Final balance |
|---|---:|---:|---:|---:|---|
| Premium, 400 packets | 90,400 net-rate adjustment | — | — | 90,400 | Depends on actual ledger |
| Corrected bajra, 360kg net | 7,200 benefit slab | 3,600 | 4,000 | 14,800 | 8,800 credit |
| Purnima, 1,900kg net | 38,000 quantity | 19,000 | 6,880 | 63,880 | 90,120 due |
| DAWAT 1kg, 630kg net | 12,600 quantity | 15,750 | 5,948 | 34,298 | 5,298 credit |
| DAWAT 3kg, separate 630kg net | 12,600 quantity | 15,750 | 5,948 | 34,298 | 5,298 credit |
| Research Paddy, 1,000kg net | Disabled | 1,500 | 2,400 | 3,900 | 6,100 due |

### Inputs and reconciliation

Bajra: supplied 400kg, returned 40kg; ABS allocation Rs30,000; ordinary receipts Rs30,000 in 7% and Rs30,000 in 5%. Billing Rs96,000 (400/1.5 per kg), used principal Rs18,000, excess Rs12,000, ABS CN Rs3,600 and benefit CN Rs7,200. Pre-CD Rs67,200. First pool Rs42,000 gives CD Rs2,940 and remaining Rs22,260. Second eligible payment capped at Rs21,200 gives CD Rs1,060; unused Rs8,800. Total CN Rs14,800. Actual receipts Rs90,000 counted once; ledger before CN Rs6,000; final Rs8,800 credit.

Purnima: supplied 2,000kg, returned 100kg; ABS Rs1,00,000; ordinary receipt Rs50,000 in maize's 8% window. Billing Rs3,04,000, used token Rs76,000, excess Rs24,000; benefit CN Rs38,000, ABS Rs19,000. CD Rs2,880 + Rs4,000. Actual receipts Rs1,50,000; ledger Rs1,54,000 before CN; final Rs90,120 due.

Each DAWAT example separately uses kg mode: supplied 700kg, returned 70kg, ABS Rs70,000; ordinary receipts Rs50,000 in 8% and Rs40,000 in 4%. Used principal Rs63,000, excess Rs7,000. Pre-CD Rs97,650. First pool Rs57,000, CD Rs4,560, remaining Rs36,090. Second used payment Rs36,090/1.04; CD Rs1,388.076923… Total precise CD Rs5,948.076923… rounds to Rs5,948. Billing Rs1,89,000 less actual receipts Rs1,60,000 gives Rs29,000 before CN; final credit Rs5,298. A 700kg input is not a whole number of 3kg packets; this example uses permitted kg mode, not fractional packet entry.

Research Paddy: Janki Gold supply 600kg, no return, ABS Rs20,000; Karina supply 400kg, no return, ABS zero; Karishma zero. Product-wise eligibility 600kg, principal Rs15,000, ABS CN Rs1,500, excess Rs5,000. Ordinary receipts Rs10,000 in 8% and Rs30,000 in 4%; pre-CD Rs53,500. First pool Rs15,000 gives Rs1,200 CD; second Rs30,000 gives Rs1,200. Billing Rs70,000, actual receipts Rs60,000, ledger Rs10,000 before CN; final Rs6,100 due.

## Remaining setup and verification

- Initial calculation season, end/cutoff, ABS eligibility dates and numerical state authorization remain incomplete. Cotton Premium/Deluxe mappings are Gujarat; other crop catalogue mappings cover all states, but numerical rates do not auto-apply across states without confirmation.
- Shared CD reference dates remain 2026 as inherited, not automatic future-year dates.
- Need full Excel-native recalculation and real imported ledger test; Saini needs 1–9 April entries or explicit confirmation none.
- Software enforcement (validation, mapping isolation, conservation, manual allocations, historical freeze, duplicate issues, save/reopen) waits for implementation.
- This is arithmetic verification in disposable scripts and selected formula evaluation; no finished offline app or universal workbook certification.

Next ask one setup decision at a time, beginning with which season/dates this initial configuration should cover. Then confirm ABS advance eligibility and state authorization. Preserve settings above and appendices; do not reopen settled rates.

## Evidence

Final run: 198 assertions passed, including prior arithmetic and selected-source checks. Counts include individual fixtures and known source mismatch reproduction; they do not represent complete app tests.

| # | Check | Actual | Expected | Result |
|---:|---|---|---|---|
| 1 | Cotton whole-quantity slab at 0 | 150 | 150 | PASS |
| 2 | Cotton whole-quantity slab at 299 | 150 | 150 | PASS |
| 3 | Cotton whole-quantity slab at 300 | 150 | 150 | PASS |
| 4 | Cotton whole-quantity slab at 301 | 175 | 175 | PASS |
| 5 | Cotton whole-quantity slab at 499 | 175 | 175 | PASS |
| 6 | Cotton whole-quantity slab at 500 | 175 | 175 | PASS |
| 7 | Cotton whole-quantity slab at 501 | 200 | 200 | PASS |
| 8 | Cotton whole-quantity slab at 999 | 200 | 200 | PASS |
| 9 | Cotton whole-quantity slab at 1000 | 200 | 200 | PASS |
| 10 | Cotton whole-quantity slab at 1001 | 225 | 225 | PASS |
| 11 | Cotton whole-quantity slab at 10000 | 225 | 225 | PASS |
| 12 | SingleCross whole-quantity slab at 0 | 2.5 | 2.5 | PASS |
| 13 | SingleCross whole-quantity slab at 199.99 | 2.5 | 2.5 | PASS |
| 14 | SingleCross whole-quantity slab at 200 | 2.5 | 2.5 | PASS |
| 15 | SingleCross whole-quantity slab at 200.01 | 5 | 5 | PASS |
| 16 | SingleCross whole-quantity slab at 500 | 5 | 5 | PASS |
| 17 | SingleCross whole-quantity slab at 500.01 | 7 | 7 | PASS |
| 18 | SingleCross whole-quantity slab at 1200 | 7 | 7 | PASS |
| 19 | SingleCross whole-quantity slab at 1200.01 | 10 | 10 | PASS |
| 20 | SingleCross whole-quantity slab at 2500 | 10 | 10 | PASS |
| 21 | SingleCross whole-quantity slab at 2500.01 | 15 | 15 | PASS |
| 22 | SingleCross whole-quantity slab at 5000 | 15 | 15 | PASS |
| 23 | SingleCross whole-quantity slab at 5001 | 15 | 15 | PASS |
| 24 | DoubleCross whole-quantity slab at 500 | 10 | 10 | PASS |
| 25 | DoubleCross whole-quantity slab at 500.01 | 15 | 15 | PASS |
| 26 | DoubleCross whole-quantity slab at 1500 | 15 | 15 | PASS |
| 27 | DoubleCross whole-quantity slab at 1500.01 | 20 | 20 | PASS |
| 28 | DoubleCross whole-quantity slab at 2500 | 20 | 20 | PASS |
| 29 | DoubleCross whole-quantity slab at 2501 | 20 | 20 | PASS |
| 30 | Bajra partial whole-quantity slab at 330 | 16 | 16 | PASS |
| 31 | Bajra partial whole-quantity slab at 330.01 | 20 | 20 | PASS |
| 32 | Bajra partial whole-quantity slab at 630 | 20 | 20 | PASS |
| 33 | Bajra partial whole-quantity slab at 630.01 | 25 | 25 | PASS |
| 34 | Bajra partial whole-quantity slab at 1050 | 25 | 25 | PASS |
| 35 | Bajra partial whole-quantity slab at 1050.01 | 27 | 27 | PASS |
| 36 | Bajra partial whole-quantity slab at 1650 | 27 | 27 | PASS |
| 37 | Bajra partial whole-quantity slab at 1650.01 | 32 | 32 | PASS |
| 38 | Bajra partial whole-quantity slab at 10000 | 32 | 32 | PASS |
| 39 | Cotton extra at 0 | 0 | 0 | PASS |
| 40 | Cotton extra at 300 | 3950 | 3950 | PASS |
| 41 | Cotton extra at 301 | 15000 | 15000 | PASS |
| 42 | Cotton extra at 500 | 15000 | 15000 | PASS |
| 43 | Cotton extra at 501 | 17500 | 17500 | PASS |
| 44 | Cotton extra at 1000 | 17500 | 17500 | PASS |
| 45 | Cotton extra at 1001 | 50000 | 50000 | PASS |
| 46 | SingleCross extra at 0 | 0 | 0 | PASS |
| 47 | SingleCross extra at 1499 | 0 | 0 | PASS |
| 48 | SingleCross extra at 1500 | 25000 | 25000 | PASS |
| 49 | SingleCross extra at 2999 | 25000 | 25000 | PASS |
| 50 | SingleCross extra at 3000 | 50000 | 50000 | PASS |
| 51 | SingleCross extra at 5001 | 50000 | 50000 | PASS |
| 52 | Proportional cotton ABS eligible | 100.4 | 100.4 | PASS |
| 53 | Proportional cotton ABS CN | 2510.0 | 2510 | PASS |
| 54 | Proportional cotton ABS excess | 0.0 | 0 | PASS |
| 55 | Product A eligible | 400 | 400 | PASS |
| 56 | Product B eligible | 400 | 400 | PASS |
| 57 | Product A excess stays available within segment | 10000 | 10000 | PASS |
| 58 | Old dues cleared once | 50000 | 50000 | PASS |
| 59 | Receipt remaining for ABS after old dues | 100000 | 100000 | PASS |
| 60 | Insufficient receipt leaves old dues | 50000 | 50000 | PASS |
| 61 | Cotton representative Quantity | 180000 | 180000 | PASS |
| 62 | Cotton representative ABS | 18500 | 18500 | PASS |
| 63 | Cotton representative Extra | 17500 | 17500 | PASS |
| 64 | Cotton representative Return | 9000 | 9000 | PASS |
| 65 | Cotton representative CD | 21200.00 | 21200 | PASS |
| 66 | Cotton pre CD | 400900 | 400900 | PASS |
| 67 | Cotton total CN | 246200 | 246200 | PASS |
| 68 | Cotton final due, reconciled ledger only | 64700 | 64700 | PASS |
| 69 | SingleCross representative Quantity | 15000 | 15000 | PASS |
| 70 | SingleCross representative ABS | 10000 | 10000 | PASS |
| 71 | SingleCross representative Extra | 25000 | 25000 | PASS |
| 72 | SingleCross representative Return | 3750.0 | 3750 | PASS |
| 73 | SingleCross cap handworked CD | 39537 | 39537 | PASS |
| 74 | SingleCross product-wise excess | 25000 | 25000 | PASS |
| 75 | SingleCross total CN | 93287 | 93287 | PASS |
| 76 | SingleCross final party credit | -143287 | -143287 | PASS |
| 77 | No ABS still gets extra | 25000 | 25000 | PASS |
| 78 | No ABS no ABS CN | 0 | 0 | PASS |
| 79 | DoubleCross representative Quantity | 38000 | 38000 | PASS |
| 80 | DoubleCross representative ABS | 19000 | 19000 | PASS |
| 81 | DoubleCross representative Extra | 0 | 0 | PASS |
| 82 | DoubleCross representative Return | 0 | 0 | PASS |
| 83 | DoubleCross representative CD | 6880.00 | 6880 | PASS |
| 84 | DoubleCross CN total | 63880 | 63880 | PASS |
| 85 | DoubleCross final due | 52120 | 52120 | PASS |
| 86 | Return threshold 0/1000 | True | True | PASS |
| 87 | Return threshold 100/1000 | True | True | PASS |
| 88 | Return threshold 101/1000 | False | False | PASS |
| 89 | Return threshold 0/0 | False | False | PASS |
| 90 | Combined return qualification uses 8%, not product B 20% | 0.08 | 0.08 | PASS |
| 91 | Payment cap used | 1E+2 | 100 | PASS |
| 92 | Payment cap CD | 8 | 8 | PASS |
| 93 | Payment cap unused stays credit | 100 | 100 | PASS |
| 94 | Zero balance no CD | 0 | 0 | PASS |
| 95 | Zero-rate payment settles balance | 60 | 60 | PASS |
| 96 | Cotton CD boundary 2026-06-15 | 0.08 | 0.08 | PASS |
| 97 | Cotton CD boundary 2026-06-16 | 0.04 | 0.04 | PASS |
| 98 | Cotton CD boundary 2026-07-15 | 0.04 | 0.04 | PASS |
| 99 | Cotton CD boundary 2026-07-16 | 0.02 | 0.02 | PASS |
| 100 | Cotton CD boundary 2026-07-30 | 0.02 | 0.02 | PASS |
| 101 | Cotton CD boundary 2026-07-31 | 0 | 0 | PASS |
| 102 | Maize CD boundary 2026-06-15 | 0.12 | 0.12 | PASS |
| 103 | Maize CD boundary 2026-06-16 | 0.08 | 0.08 | PASS |
| 104 | Maize CD boundary 2026-06-30 | 0.08 | 0.08 | PASS |
| 105 | Maize CD boundary 2026-07-01 | 0.05 | 0.05 | PASS |
| 106 | Maize CD boundary 2026-07-15 | 0.05 | 0.05 | PASS |
| 107 | Maize CD boundary 2026-07-16 | 0.02 | 0.02 | PASS |
| 108 | Maize CD boundary 2026-07-30 | 0.02 | 0.02 | PASS |
| 109 | Maize CD boundary 2026-07-31 | 0 | 0 | PASS |
| 110 | Bajra CD boundary 2026-06-30 | 0.07 | 0.07 | PASS |
| 111 | Bajra CD boundary 2026-07-01 | 0.05 | 0.05 | PASS |
| 112 | Bajra CD boundary 2026-07-15 | 0.05 | 0.05 | PASS |
| 113 | Bajra CD boundary 2026-07-16 | 0.03 | 0.03 | PASS |
| 114 | Bajra CD boundary 2026-07-31 | 0.03 | 0.03 | PASS |
| 115 | Bajra CD boundary 2026-08-01 | 0 | 0 | PASS |
| 116 | Cotton to maize transfer on 1 July uses destination 5% | 0.05 | 0.05 | PASS |
| 117 | Cash date 2026-03-11 | False | False | PASS |
| 118 | Cash date 2026-03-12 | True | True | PASS |
| 119 | Cash date 2026-03-31 | True | True | PASS |
| 120 | Cash date 2026-04-01 | False | False | PASS |
| 121 | Cash representative required_advance | 300000 | 300000 | PASS |
| 122 | Cash representative net | 2900 | 2900 | PASS |
| 123 | Cash representative normal_CN | 116000 | 116000 | PASS |
| 124 | Cash representative deduction | 3000 | 3000 | PASS |
| 125 | Cash representative final_CN | 113000 | 113000 | PASS |
| 126 | Net-basis advance 290000 is insufficient | False | False | PASS |
| 127 | User-confirmed 20000 less 3000 | 17000 | 17000 | PASS |
| 128 | Cash CN zero floor | 0 | 0 | PASS |
| 129 | Cash excess deduction review | 1000 | 1000 | PASS |
| 130 | Explicit zero return deduction | 20000 | 20000 | PASS |
| 131 | Cash plus regular supplied conservation | 10000 | 10000 | PASS |
| 132 | Cash plus regular returned conservation | 500 | 500 | PASS |
| 133 | Cash plus regular net conservation | 9500 | 9500 | PASS |
| 134 | Rounding half rupee upwards | 101 | 101 | PASS |
| 135 | Separate rounding sum | 30 | 30 | PASS |
| 136 | Grand total rounding differs and is not issue total | 31 | 31 | PASS |
| 137 | Ledger due 80000 less CN 30000 | 50000 | 50000 | PASS |
| 138 | CN greater than due creates credit | -10000 | -10000 | PASS |
| 139 | Revised CN proposal only difference | 2000 | 2000 | PASS |
| 140 | Revised lower CN requires review | -2000 | -2000 | PASS |
| 141 | Cotton kg converts to whole packets | 1E+2 | 100 | PASS |
| 142 | Fractional packet conversion flagged | True | True | PASS |
| 143 | DAWAT one and three kg variants remain separate | True | True | PASS |
| 144 | Cotton cached row4 M | 4325 | 4325 | PASS |
| 145 | Cotton cached row4 Q | 25950 | 25950 | PASS |
| 146 | Cotton cached row4 R | 3950 | 3950 | PASS |
| 147 | Cotton cached row4 O | 0 | 0 | PASS |
| 148 | Cotton cached row4 CD rounded | 5807 | 5807 | PASS |
| 149 | Cotton cached row4 total | 40032 | 40032 | PASS |
| 150 | Updated cotton principal already included | 78398 | 78398 | PASS |
| 151 | Source unchanged GJ cotton customized.xlsx | 10afe662df9ed3870aab150b5bc42639671cec100e82f2901a311a606ecf7cfb | 10afe662df9ed3870aab150b5bc42639671cec100e82f2901a311a606ecf7cfb | PASS |
| 152 | Source unchanged MAIZE all type CN -V5.xlsx | c510fa87fd3c1bc94d426a76b4cc94525a6d1627ce6640edae643db123d4b09a | c510fa87fd3c1bc94d426a76b4cc94525a6d1627ce6640edae643db123d4b09a | PASS |
| 153 | Source unchanged RJ_Bajra_ABS_Credit_Note_Calculator_v6.xlsx | 5dac72471a085393448c780531701f2a3ff65773f5b37761871d80cb6d9f1654 | 5dac72471a085393448c780531701f2a3ff65773f5b37761871d80cb6d9f1654 | PASS |
| 154 | Source formula Cotton at exact 10% excludes return CN (known override) | 0 | 0 | PASS |
| 155 | Source formula Cotton at zero return excludes return CN (known override) | 0 | 0 | PASS |
| 156 | Source formula Cotton zero sales extra 3950 (known override) | 3950 | 3950 | PASS |
| 157 | Selected source Cotton formula chain total reproduces 40032 | 40032 | 40032 | PASS |
| 158 | Selected source Cotton formula chain pre-CD balance reproduces 78398 | 78398 | 78398 | PASS |
| 159 | Source formula maize no ABS tour 0 (known override) | 0 | 0 | PASS |
| 160 | Source formula maize pooled ABS eligible 1500 (product-wise override) | 1500 | 1500 | PASS |
| 161 | Source formula automatically transfers 20000 (manual-choice override) | 20000 | 20000 | PASS |
| 162 | Bajra source pre-payment balance only deducts ABS CN | 134750 | 134750 | PASS |
| 163 | Premium net rate at 0 | 700 | 700 | PASS |
| 164 | Premium net rate at 300 | 700 | 700 | PASS |
| 165 | Premium net rate at 301 | 675 | 675 | PASS |
| 166 | Premium net rate at 500 | 675 | 675 | PASS |
| 167 | Premium net rate at 501 | 650 | 650 | PASS |
| 168 | Premium net rate at 1000 | 650 | 650 | PASS |
| 169 | Premium net rate at 1001 | 625 | 625 | PASS |
| 170 | Premium net rate at 2500 | 625 | 625 | PASS |
| 171 | Premium net rate at 2501 | 625 | 625 | PASS |
| 172 | Premium 400 packets CN | 90400 | 90400 | PASS |
| 173 | Premium zero packets no CN | 0 | 0 | PASS |
| 174 | Corrected bajra Benefit Slab | 7200 | 7200 | PASS |
| 175 | Corrected bajra ABS | 3600 | 3600 | PASS |
| 176 | Corrected bajra CD | 4000.000000000000000000000000000000000000 | 4000 | PASS |
| 177 | Corrected bajra Extra | 0 | 0 | PASS |
| 178 | Corrected bajra Return | 0 | 0 | PASS |
| 179 | Bajra ABS excess enters first CD pool | 42000 | 42000 | PASS |
| 180 | Bajra second payment capped | 21200.00000000000000000000000000000000001 | 21200 | PASS |
| 181 | Bajra new CN counted once | 14800 | 14800 | PASS |
| 182 | Bajra final credit | -8799.99999999999999999999999999999999999 | -8800 | PASS |
| 183 | Purnima billing at 160/kg | 154000 | 154000 | PASS |
| 184 | Purnima CN same sample quantities as DoubleCross | 63880 | 63880 | PASS |
| 185 | Purnima final due | 90120 | 90120 | PASS |
| 186 | DAWAT 630kg quantity CN | 12600 | 12600 | PASS |
| 187 | DAWAT ABS CN | 15750 | 15750 | PASS |
| 188 | DAWAT excess first CD pool | 57000 | 57000 | PASS |
| 189 | DAWAT rounded CD | 5948 | 5948 | PASS |
| 190 | DAWAT total CN | 34298 | 34298 | PASS |
| 191 | DAWAT final credit | -5298 | -5298 | PASS |
| 192 | DAWAT 3kg same kg settings independent result | 34298 | 34298 | PASS |
| 193 | Research product-wise eligible not pooled | 1500.0 | 1500 | PASS |
| 194 | Research disabled quantity CN | 0 | 0 | PASS |
| 195 | Research excess ABS | 5000 | 5000 | PASS |
| 196 | Research CD | 2400.00 | 2400 | PASS |
| 197 | Research total CN | 3900 | 3900 | PASS |
| 198 | Research final due | 6100 | 6100 | PASS |

---

# Earlier Phase 4 report and inherited handoffs

# All-crop offline CN calculator — Phase 4 verification progress

Date: 13 October 2026

**Status: configured representative calculations and selected boundaries verified. Phase 4 remains open.** Required initial settings are incomplete. No app code or source workbook changes were made.

## New decisions

1. Cash advance eligibility is based on **cash supplied quantity**. Cash supply 3,000 kg, return 100 kg and required advance Rs100/kg requires Rs3,00,000, not Rs2,90,000. Cash CN uses net sold quantity, followed by the separate manual return deduction.
2. Proportional ABS entitlement derived from money is allowed. Rs25,100 / Rs250 token = 100.4 booked packets. With sufficient net sales, ABS CN at Rs25/packet is Rs2,510; used principal is Rs25,100, excess zero. Actual supplied/returned packet entries must remain whole packets.
3. Assistant-selected treatment under the user's instruction to choose what is best: kg entered in packet mode must convert to whole packets. Otherwise flag for correction or explicit kg-mode selection. No silent floor, ceiling or quantity loss. Convert rates and thresholds consistently when units change.

These supplement Phase 3. Keep settled rules; ask one unresolved decision at a time.

## Method and limits

- Independent Decimal arithmetic, 40-digit working precision, and explicit expected fixtures.
- **162 assertions passed** in the final run. This includes individual amounts, dates and source-identity checks, not that many complete accounts.
- Selected original formulas evaluated with a limited independent evaluator and disposable in-memory overrides. Supported scalar arithmetic/references and IF/MIN/MAX/SUM/AND/OR/ROUND/N. This is **not full native Excel recalculation**.
- One current populated cotton row was reproduced against cached values as a reference comparison. Cached values alone were not treated as proof of recalculation.
- Sources opened read-only; SHA-256 confirmed unchanged bytes.
- Inputs below are synthetic. Scheme dates/state authorization are test assumptions only. All-state catalogue mappings do not authorize all-state numerical rates.
- No app exists yet. Validation, duplicate issue controls, snapshots, import reconciliation, chronological/manual allocation and save/reopen remain implementation acceptance requirements, not verified software features.
- Positive half-rupee rounding uses ROUND-compatible half-up behavior. Round each separate benefit CN and sum those amounts; preserve full internal precision.

## Representative results

Amounts in Rs. Zero benefits are visible explanations, not zero-value issued CNs.

| Case | Net sold | Quantity CN | ABS CN | Extra CN | Return CN | CD CN rounded | Total new CN | Synthetic final balance |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Cotton Deluxe, provisional | 900 packets | 1,80,000 | 18,500 | 17,500 | 9,000 | 21,200 | **2,46,200** | 64,700 due |
| Maize SingleCross | 1,500 kg | 15,000 | 10,000 | 25,000 | 3,750 | 39,537 | **93,287** | 1,43,287 credit |
| SingleCross, no ABS/receipts | 1,500 kg | 15,000 | 0 | 25,000 | 3,750 | 0 | **43,750** | 4,81,250 due |
| Maize DoubleCross | 1,900 kg | 38,000 | 19,000 | 0 | 0 | 6,880 | **63,880** | 52,120 due |
| Cash with returns | 2,900 kg | — | — | — | — | — | **1,13,000 cash CN** | 7,000 credit in isolated example below |

### Cotton Deluxe: product-wise booking and inclusive 10% return

| Product | Supply packets | Return packets | Net packets | ABS allocation | Eligible packets | Used principal | Excess |
|---|---:|---:|---:|---:|---:|---:|---:|
| D551 | 600 | 60 | 540 | 1,50,000 | 540 | 1,35,000 | 15,000 |
| Dhanvarsha | 400 | 40 | 360 | 50,000 | 200 | 50,000 | 0 |
| Total | 1,000 | 100 | 900 | 2,00,000 | 740 | 1,85,000 | 15,000 |

Net sales: 900 × Rs901 = Rs8,10,900.
Quantity CN: 900 × Rs200 = Rs1,80,000.
ABS CN: 740 × Rs25 = Rs18,500. No automatic booking transfer to Dhanvarsha.
Provisional extra: Rs17,500. Returns: 100 / 1,000 = exactly 10%, so return CN = 900 × Rs10 = Rs9,000.

Pre-CD balance = 8,10,900 − 1,80,000 − 18,500 − 17,500 − 9,000 − 1,85,000 = **Rs4,00,900**.

Ordinary payments are Rs2,00,000 in the 8% window and Rs1,00,000 in the 4% window. Excess ABS Rs15,000 enters the first pool. CD = 2,15,000 × 8% + 1,00,000 × 4% = **Rs21,200**.

Actual receipts = Rs2,00,000 ABS + Rs3,00,000 ordinary = Rs5,00,000, counted once. Ledger before proposed CN = Rs3,10,900; less Rs2,46,200 new CN leaves **Rs64,700 due**. Do not deduct used token principal again from this ledger.

### SingleCross: product-wise ABS, extra and payment cap

32D12 supply 1,000 kg, zero return, ABS allocation Rs75,000; Legend supply 500 kg, zero return, ABS allocation zero. Token Rs50/kg and ABS benefit Rs10/kg.

32D12 books 1,500 kg but qualifies on 1,000 kg; used principal Rs50,000, excess Rs25,000. Legend gets no ABS benefit automatically.

Billing Rs5,25,000; quantity CN Rs15,000; ABS Rs10,000; extra Rs25,000; no-return CN = 1,500 / 4 × Rs10 = Rs3,750. Pre-CD balance **Rs4,21,250**.

Ordinary receipts Rs2,00,000 in the 12% window and Rs3,00,000 in the 8% window.
First pool includes excess ABS: Rs2,25,000; CD Rs27,000; balance Rs1,69,250.
Second used payment capped at 1,69,250 / 1.08 = Rs1,56,712.962962…; CD Rs12,537.037037…; remaining eligible balance zero.

Precise CD Rs39,537.037037… rounds to separate CD CN **Rs39,537**. Total CN **Rs93,287**.
Unused payment Rs1,43,287.037037… earns no more CD. Actual receipts Rs5,75,000 against billing Rs5,25,000; final ledger credit after rounded new CN is **Rs1,43,287**.

With the same 1,500 kg sales and no ABS or receipts, extra still equals Rs25,000; total CN Rs43,750. Extra eligibility does not require ABS booking.

### DoubleCross

32D55 supply 2,000 kg, return 100 kg, net 1,900 kg; ABS allocation Rs1,00,000; ordinary receipt Rs50,000 in 8% window.
Billing Rs2,66,000; quantity CN Rs38,000; ABS CN Rs19,000; used token Rs76,000; excess Rs24,000; pre-CD balance Rs1,33,000.
CD = 24,000 × 12% + 50,000 × 8% = Rs6,880. Scheme 2 gives no extra/return CN.
New CN **Rs63,880**. Synthetic ledger before CN Rs1,16,000; final **Rs52,120 due**.

### Cash return and split

Cash supply 3,000 kg, return 100 kg, net 2,900 kg. Required eligible advance **Rs3,00,000**.
Normal cash CN = 2,900 × Rs40 = Rs1,16,000.
Chosen deduction = 100 × Rs30 = Rs3,000.
Final cash CN **Rs1,13,000**.

If isolated actual cash receipts equal Rs3,00,000, net billing Rs4,06,000 gives Rs1,06,000 before CN; less Rs1,13,000 CN gives **Rs7,000 credit**. Sales-return ledger value is included once.

Total product supply 10,000 kg and return 500 kg can split into cash 3,000/100 and regular 7,000/400, giving net 2,900 + 6,600 = 9,500 kg. This does not automatically allocate money to regular ABS.

Other checked examples: normal cash CN Rs20,000 minus Rs3,000 = Rs17,000; normal Rs2,000 minus Rs3,000 = zero CN with Rs1,000 review flag. Explicit zero deduction is allowed with remark; remark enforcement is not yet software-tested.

## Source differences and overrides

| Source / example cell | Source behavior | Required agreed behavior |
|---|---|---|
| Customized cotton, Cotton CN!V4/X4 | Deducts principal and uses payment-plus-CD cap | Already correct here; historical principal-omission finding must not be applied to this updated source |
| Customized cotton, Cotton CN!O4 | 0 < return% < 10% | Inclusive 0% through 10%, complete season data required |
| Customized cotton, Cotton CN!R4 | Zero net sales still yields Rs3,950 extra | Zero sales → zero extra; positive bands provisional |
| Customized cotton, Cotton CN!AI4 | Rounds combined total | Round each separate benefit CN |
| Customized cotton, Cotton CN!AK4/AL4 | Working balances/unused pools | Actual reconciled ledger owns final due/credit |
| Maize, SingleCross!K12 | Tour uses ABS-eligible U12 | Tour uses net sold quantity, even without ABS |
| Maize, SingleCross!U12 | Segment-pooled booking/sales | Product-wise ABS eligibility |
| Maize, regular N12/O12 | Automatic transfer at 0% CD | Manual choice, original date, destination window or applicable 0% |
| Maize, dashboard!B12 | Blocks positive unallocated advance | Visible unallocated credit allowed; no forced ABS allocation |
| Maize, dashboard!I12/Q12 and regular Q12 | One cash quantity, all returns to regular | Separate cash supplied/returned and regular supplied/returned |
| Maize cash sheet | No separate return adjustment | Net-sales cash CN, manual deduction, zero floor/review |
| Maize regular C12 | Grand-total rounding | Separate benefit CN rounding |
| Bajra, Data!O3 | Gross less ABS CN only | Deduct used principal and all active non-CD CNs before CD |
| Bajra, Data!T3 | Payment capped by balance alone | Payment ≤ balance / (1 + CD rate) |
| Bajra return formula | Active strict-threshold benefit | Disabled under selected Scheme 3 |

Selected source formulas reproduced cotton row 4 total **Rs40,032** and pre-CD balance **Rs78,398**. For its isolated inputs, independently reconciled credit after separate CN rounding is Rs9,159; source unused pool Rs9,159.259259… is unrounded working. This row does not test return threshold equality.

## Coverage

Checked: whole-quantity tier equalities and next quantities; highest rate continuation; extra boundaries and zero sales; no-return/exact 10%/above-threshold and zero-supply arithmetic; product-wise and proportional ABS; old-dues arithmetic; CD date boundaries/cap/zero-rate settlement; cash eligibility date edges, supply basis, return adjustment and zero floor; separate rounding; ledger subtraction and revision differences; exact packet conversion and fractional-conversion detection.

DAWAT packing identities remain separate in the specification. No actual database or segment storage was tested. Negative/missing inputs and cash/regular quantity/payment conservation require real application validation after coding.

## Still open

1. Premium: fixed versus quantity-tiered net rate, actual rates and billing-to-net CN treatment.
2. Purnima: billing/reference, token/ABS, tiers, CD and eligibility dates.
3. Separate DAWAT 1 kg, DAWAT 3 kg and Research Paddy numerical settings.
4. Bajra active extra tiers/amounts. Only known isolated boundaries tested; full Scheme 3 blocked, not zero-filled.
5. Initial state/season numerical authorization and missing advance/cutoff dates.
6. Customized cotton extra bands need confirmation before production.
7. Full native Excel recalculation and broader formula drift/error scans.
8. Real ledger/import: Saini starts 10 April; obtain 1–9 April entries or confirmation none.
9. Software acceptance: blank versus zero, negative blocking, quantity/payment conservation, chronology/manual order, transfer restrictions, issue identity, historical snapshots, save/reopen.
10. If an actual cash-advance refund/reallocation scenario arises, review how it changes eligible advance. Supplied-quantity basis is settled.

Multiple return-benefit tiers remain unspecified; do not invent stacking.

## Next action and continuation prompt

Ask one decision at a time, starting with **cotton Premium: fixed rate or quantity-based tiers?** Then collect its rates and settlement/CN treatment. Keep other unconfigured settings as drafts.

Continue Phase 4 using this report and appended Phase 3/2/1 handoff. Preserve confirmed rules, supplied-quantity cash advance, proportional derived ABS packet entitlement and whole-packet conversion validation. Configured sample arithmetic and selected source formulas were checked; do not claim all Phase 4 or Excel/app certification complete. Missing rates stay unconfigured. No app coding or source Excel changes yet.

After Phase 4: Phase 5 screen design; Phase 6 offline implementation; Phase 7 real-account/import/save/reopen testing; Phase 8 packaging, backup/restore, exports and instructions.

## Source fingerprints

- GJ cotton customized.xlsx: SHA-256 10afe662df9ed3870aab150b5bc42639671cec100e82f2901a311a606ecf7cfb
- MAIZE all type CN -V5.xlsx: SHA-256 c510fa87fd3c1bc94d426a76b4cc94525a6d1627ce6640edae643db123d4b09a
- RJ_Bajra_ABS_Credit_Note_Calculator_v6.xlsx: SHA-256 5dac72471a085393448c780531701f2a3ff65773f5b37761871d80cb6d9f1654

Library identities are retained in the appended handoff. Original handoff was not replaced.

## Assertion evidence

A PASS for a known source mismatch means the source behavior was reproduced, not approved for implementation.

| # | Check | Actual | Expected | Result |
|---:|---|---|---|---|
| 1 | Cotton whole-quantity slab at 0 | 150 | 150 | PASS |
| 2 | Cotton whole-quantity slab at 299 | 150 | 150 | PASS |
| 3 | Cotton whole-quantity slab at 300 | 150 | 150 | PASS |
| 4 | Cotton whole-quantity slab at 301 | 175 | 175 | PASS |
| 5 | Cotton whole-quantity slab at 499 | 175 | 175 | PASS |
| 6 | Cotton whole-quantity slab at 500 | 175 | 175 | PASS |
| 7 | Cotton whole-quantity slab at 501 | 200 | 200 | PASS |
| 8 | Cotton whole-quantity slab at 999 | 200 | 200 | PASS |
| 9 | Cotton whole-quantity slab at 1000 | 200 | 200 | PASS |
| 10 | Cotton whole-quantity slab at 1001 | 225 | 225 | PASS |
| 11 | Cotton whole-quantity slab at 10000 | 225 | 225 | PASS |
| 12 | SingleCross whole-quantity slab at 0 | 2.5 | 2.5 | PASS |
| 13 | SingleCross whole-quantity slab at 199.99 | 2.5 | 2.5 | PASS |
| 14 | SingleCross whole-quantity slab at 200 | 2.5 | 2.5 | PASS |
| 15 | SingleCross whole-quantity slab at 200.01 | 5 | 5 | PASS |
| 16 | SingleCross whole-quantity slab at 500 | 5 | 5 | PASS |
| 17 | SingleCross whole-quantity slab at 500.01 | 7 | 7 | PASS |
| 18 | SingleCross whole-quantity slab at 1200 | 7 | 7 | PASS |
| 19 | SingleCross whole-quantity slab at 1200.01 | 10 | 10 | PASS |
| 20 | SingleCross whole-quantity slab at 2500 | 10 | 10 | PASS |
| 21 | SingleCross whole-quantity slab at 2500.01 | 15 | 15 | PASS |
| 22 | SingleCross whole-quantity slab at 5000 | 15 | 15 | PASS |
| 23 | SingleCross whole-quantity slab at 5001 | 15 | 15 | PASS |
| 24 | DoubleCross whole-quantity slab at 500 | 10 | 10 | PASS |
| 25 | DoubleCross whole-quantity slab at 500.01 | 15 | 15 | PASS |
| 26 | DoubleCross whole-quantity slab at 1500 | 15 | 15 | PASS |
| 27 | DoubleCross whole-quantity slab at 1500.01 | 20 | 20 | PASS |
| 28 | DoubleCross whole-quantity slab at 2500 | 20 | 20 | PASS |
| 29 | DoubleCross whole-quantity slab at 2501 | 20 | 20 | PASS |
| 30 | Bajra partial whole-quantity slab at 330 | 16 | 16 | PASS |
| 31 | Bajra partial whole-quantity slab at 330.01 | 20 | 20 | PASS |
| 32 | Bajra partial whole-quantity slab at 630 | 20 | 20 | PASS |
| 33 | Bajra partial whole-quantity slab at 630.01 | 25 | 25 | PASS |
| 34 | Bajra partial whole-quantity slab at 1050 | 25 | 25 | PASS |
| 35 | Bajra partial whole-quantity slab at 1050.01 | 27 | 27 | PASS |
| 36 | Bajra partial whole-quantity slab at 1650 | 27 | 27 | PASS |
| 37 | Bajra partial whole-quantity slab at 1650.01 | 32 | 32 | PASS |
| 38 | Bajra partial whole-quantity slab at 10000 | 32 | 32 | PASS |
| 39 | Cotton extra at 0 | 0 | 0 | PASS |
| 40 | Cotton extra at 300 | 3950 | 3950 | PASS |
| 41 | Cotton extra at 301 | 15000 | 15000 | PASS |
| 42 | Cotton extra at 500 | 15000 | 15000 | PASS |
| 43 | Cotton extra at 501 | 17500 | 17500 | PASS |
| 44 | Cotton extra at 1000 | 17500 | 17500 | PASS |
| 45 | Cotton extra at 1001 | 50000 | 50000 | PASS |
| 46 | SingleCross extra at 0 | 0 | 0 | PASS |
| 47 | SingleCross extra at 1499 | 0 | 0 | PASS |
| 48 | SingleCross extra at 1500 | 25000 | 25000 | PASS |
| 49 | SingleCross extra at 2999 | 25000 | 25000 | PASS |
| 50 | SingleCross extra at 3000 | 50000 | 50000 | PASS |
| 51 | SingleCross extra at 5001 | 50000 | 50000 | PASS |
| 52 | Proportional cotton ABS eligible | 100.4 | 100.4 | PASS |
| 53 | Proportional cotton ABS CN | 2510.0 | 2510 | PASS |
| 54 | Proportional cotton ABS excess | 0.0 | 0 | PASS |
| 55 | Product A eligible | 400 | 400 | PASS |
| 56 | Product B eligible | 400 | 400 | PASS |
| 57 | Product A excess stays available within segment | 10000 | 10000 | PASS |
| 58 | Old dues cleared once | 50000 | 50000 | PASS |
| 59 | Receipt remaining for ABS after old dues | 100000 | 100000 | PASS |
| 60 | Insufficient receipt leaves old dues | 50000 | 50000 | PASS |
| 61 | Cotton representative Quantity | 180000 | 180000 | PASS |
| 62 | Cotton representative ABS | 18500 | 18500 | PASS |
| 63 | Cotton representative Extra | 17500 | 17500 | PASS |
| 64 | Cotton representative Return | 9000 | 9000 | PASS |
| 65 | Cotton representative CD | 21200.00 | 21200 | PASS |
| 66 | Cotton pre CD | 400900 | 400900 | PASS |
| 67 | Cotton total CN | 246200 | 246200 | PASS |
| 68 | Cotton final due, reconciled ledger only | 64700 | 64700 | PASS |
| 69 | SingleCross representative Quantity | 15000 | 15000 | PASS |
| 70 | SingleCross representative ABS | 10000 | 10000 | PASS |
| 71 | SingleCross representative Extra | 25000 | 25000 | PASS |
| 72 | SingleCross representative Return | 3750.0 | 3750 | PASS |
| 73 | SingleCross cap handworked CD | 39537 | 39537 | PASS |
| 74 | SingleCross product-wise excess | 25000 | 25000 | PASS |
| 75 | SingleCross total CN | 93287 | 93287 | PASS |
| 76 | SingleCross final party credit | -143287 | -143287 | PASS |
| 77 | No ABS still gets extra | 25000 | 25000 | PASS |
| 78 | No ABS no ABS CN | 0 | 0 | PASS |
| 79 | DoubleCross representative Quantity | 38000 | 38000 | PASS |
| 80 | DoubleCross representative ABS | 19000 | 19000 | PASS |
| 81 | DoubleCross representative Extra | 0 | 0 | PASS |
| 82 | DoubleCross representative Return | 0 | 0 | PASS |
| 83 | DoubleCross representative CD | 6880.00 | 6880 | PASS |
| 84 | DoubleCross CN total | 63880 | 63880 | PASS |
| 85 | DoubleCross final due | 52120 | 52120 | PASS |
| 86 | Return threshold 0/1000 | True | True | PASS |
| 87 | Return threshold 100/1000 | True | True | PASS |
| 88 | Return threshold 101/1000 | False | False | PASS |
| 89 | Return threshold 0/0 | False | False | PASS |
| 90 | Combined return qualification uses 8%, not product B 20% | 0.08 | 0.08 | PASS |
| 91 | Payment cap used | 1E+2 | 100 | PASS |
| 92 | Payment cap CD | 8 | 8 | PASS |
| 93 | Payment cap unused stays credit | 100 | 100 | PASS |
| 94 | Zero balance no CD | 0 | 0 | PASS |
| 95 | Zero-rate payment settles balance | 60 | 60 | PASS |
| 96 | Cotton CD boundary 2026-06-15 | 0.08 | 0.08 | PASS |
| 97 | Cotton CD boundary 2026-06-16 | 0.04 | 0.04 | PASS |
| 98 | Cotton CD boundary 2026-07-15 | 0.04 | 0.04 | PASS |
| 99 | Cotton CD boundary 2026-07-16 | 0.02 | 0.02 | PASS |
| 100 | Cotton CD boundary 2026-07-30 | 0.02 | 0.02 | PASS |
| 101 | Cotton CD boundary 2026-07-31 | 0 | 0 | PASS |
| 102 | Maize CD boundary 2026-06-15 | 0.12 | 0.12 | PASS |
| 103 | Maize CD boundary 2026-06-16 | 0.08 | 0.08 | PASS |
| 104 | Maize CD boundary 2026-06-30 | 0.08 | 0.08 | PASS |
| 105 | Maize CD boundary 2026-07-01 | 0.05 | 0.05 | PASS |
| 106 | Maize CD boundary 2026-07-15 | 0.05 | 0.05 | PASS |
| 107 | Maize CD boundary 2026-07-16 | 0.02 | 0.02 | PASS |
| 108 | Maize CD boundary 2026-07-30 | 0.02 | 0.02 | PASS |
| 109 | Maize CD boundary 2026-07-31 | 0 | 0 | PASS |
| 110 | Bajra CD boundary 2026-06-30 | 0.07 | 0.07 | PASS |
| 111 | Bajra CD boundary 2026-07-01 | 0.05 | 0.05 | PASS |
| 112 | Bajra CD boundary 2026-07-15 | 0.05 | 0.05 | PASS |
| 113 | Bajra CD boundary 2026-07-16 | 0.03 | 0.03 | PASS |
| 114 | Bajra CD boundary 2026-07-31 | 0.03 | 0.03 | PASS |
| 115 | Bajra CD boundary 2026-08-01 | 0 | 0 | PASS |
| 116 | Cotton to maize transfer on 1 July uses destination 5% | 0.05 | 0.05 | PASS |
| 117 | Cash date 2026-03-11 | False | False | PASS |
| 118 | Cash date 2026-03-12 | True | True | PASS |
| 119 | Cash date 2026-03-31 | True | True | PASS |
| 120 | Cash date 2026-04-01 | False | False | PASS |
| 121 | Cash representative required_advance | 300000 | 300000 | PASS |
| 122 | Cash representative net | 2900 | 2900 | PASS |
| 123 | Cash representative normal_CN | 116000 | 116000 | PASS |
| 124 | Cash representative deduction | 3000 | 3000 | PASS |
| 125 | Cash representative final_CN | 113000 | 113000 | PASS |
| 126 | Net-basis advance 290000 is insufficient | False | False | PASS |
| 127 | User-confirmed 20000 less 3000 | 17000 | 17000 | PASS |
| 128 | Cash CN zero floor | 0 | 0 | PASS |
| 129 | Cash excess deduction review | 1000 | 1000 | PASS |
| 130 | Explicit zero return deduction | 20000 | 20000 | PASS |
| 131 | Cash plus regular supplied conservation | 10000 | 10000 | PASS |
| 132 | Cash plus regular returned conservation | 500 | 500 | PASS |
| 133 | Cash plus regular net conservation | 9500 | 9500 | PASS |
| 134 | Rounding half rupee upwards | 101 | 101 | PASS |
| 135 | Separate rounding sum | 30 | 30 | PASS |
| 136 | Grand total rounding differs and is not issue total | 31 | 31 | PASS |
| 137 | Ledger due 80000 less CN 30000 | 50000 | 50000 | PASS |
| 138 | CN greater than due creates credit | -10000 | -10000 | PASS |
| 139 | Revised CN proposal only difference | 2000 | 2000 | PASS |
| 140 | Revised lower CN requires review | -2000 | -2000 | PASS |
| 141 | Cotton kg converts to whole packets | 1E+2 | 100 | PASS |
| 142 | Fractional packet conversion flagged | True | True | PASS |
| 143 | DAWAT one and three kg variants remain separate | True | True | PASS |
| 144 | Cotton cached row4 M | 4325 | 4325 | PASS |
| 145 | Cotton cached row4 Q | 25950 | 25950 | PASS |
| 146 | Cotton cached row4 R | 3950 | 3950 | PASS |
| 147 | Cotton cached row4 O | 0 | 0 | PASS |
| 148 | Cotton cached row4 CD rounded | 5807 | 5807 | PASS |
| 149 | Cotton cached row4 total | 40032 | 40032 | PASS |
| 150 | Updated cotton principal already included | 78398 | 78398 | PASS |
| 151 | Source unchanged GJ cotton customized.xlsx | 10afe662df9ed3870aab150b5bc42639671cec100e82f2901a311a606ecf7cfb | 10afe662df9ed3870aab150b5bc42639671cec100e82f2901a311a606ecf7cfb | PASS |
| 152 | Source unchanged MAIZE all type CN -V5.xlsx | c510fa87fd3c1bc94d426a76b4cc94525a6d1627ce6640edae643db123d4b09a | c510fa87fd3c1bc94d426a76b4cc94525a6d1627ce6640edae643db123d4b09a | PASS |
| 153 | Source unchanged RJ_Bajra_ABS_Credit_Note_Calculator_v6.xlsx | 5dac72471a085393448c780531701f2a3ff65773f5b37761871d80cb6d9f1654 | 5dac72471a085393448c780531701f2a3ff65773f5b37761871d80cb6d9f1654 | PASS |
| 154 | Source formula Cotton at exact 10% excludes return CN (known override) | 0 | 0 | PASS |
| 155 | Source formula Cotton at zero return excludes return CN (known override) | 0 | 0 | PASS |
| 156 | Source formula Cotton zero sales extra 3950 (known override) | 3950 | 3950 | PASS |
| 157 | Selected source Cotton formula chain total reproduces 40032 | 40032 | 40032 | PASS |
| 158 | Selected source Cotton formula chain pre-CD balance reproduces 78398 | 78398 | 78398 | PASS |
| 159 | Source formula maize no ABS tour 0 (known override) | 0 | 0 | PASS |
| 160 | Source formula maize pooled ABS eligible 1500 (product-wise override) | 1500 | 1500 | PASS |
| 161 | Source formula automatically transfers 20000 (manual-choice override) | 20000 | 20000 | PASS |
| 162 | Bajra source pre-payment balance only deducts ABS CN | 134750 | 134750 | PASS |

---

# Inherited Phase 3 handoff, unchanged

# All-crop offline CN calculator — Phase 3 handoff

Date: 13 October 2026
Status: Phase 3 settings structure and initial mappings agreed. Initial numerical configuration is incomplete; provisional choices are identified below. Next: Phase 4 representative calculations, boundary tests and source formula verification. No app code written; no source Excel files changed. Read-only workbook inspection is not recalculation certification.

## Next-chat instructions

Preserve all agreed rules. Phase 3 decisions override conflicting earlier settings; Phase 2 overrides the historical Phase 1 appendix. Read this handoff with the appended Phase 2 handoff, which includes Phase 1 details. Do not reopen settled questions. Ask one decision at a time unless the user requests a batch. Do not start app coding or modify source workbooks during Phase 4 without new authorization. Test in disposable working copies or independent calculations.

## 1. Mapping and scheme structure

- Hierarchy: Crop -> Segment -> Product. No subsegment level.
- Mapping can differ by state and season; each product-and-packing variant belongs to one segment for that state/season. DAWAT is the explicit packing-variant exception to one product/segment membership.
- Segment names are editable, including bajra's currently unnamed single segment. Preserve stable identities when labels change.
- All products within a segment use the SAME scheme combination. The briefly discussed different schemes within a segment was withdrawn by the user.
- One segment can use different schemes/rates in different states and seasons.
- Party address state is the default scheme state; allow a documented override for the selected season.
- No automatic fallback state scheme: an applicable state must have configured settings before its calculation can be finalised.
- Maize, bajra and paddy mappings apply to all states initially. This is not approval to reuse source numerical rates in every state. Explicit state configuration is still required.
- Eligible products are selected in settings. Imported names/codes have editable aliases; unmatched names require manual mapping before finalisation. DAWAT aliases must identify packing size.
- Copy previous-season mappings/settings into a new editable draft, then confirm. Keep historical versions.

## 2. Four selectable regular scheme combinations

1. Net rate only.
2. ABS + Quantity + CD.
3. ABS + Quantity + CD + Extra benefit.
4. ABS + Quantity + CD + Extra benefit + No/low sales-return benefit.

Cash is NOT a fifth selectable scheme combination. It is a separate manually chosen cash allocation of the same eligible product alongside its regular allocation, with separate cash settings and restrictions inherited from Phase 2.

## 3. Confirmed initial catalogue and scheme selections

| Crop / state applicability | Segment | Products | Packet size | Regular scheme |
|---|---|---|---|---|
| Cotton / Gujarat | Premium | 25D51, Advance, Agniveer | 475 g = 0.475 kg | 1 |
| Cotton / Gujarat | Deluxe | D551, Dhanvarsha | 475 g = 0.475 kg | 4 |
| Bajra / all states | User-editable name, not yet named | 14D88, 14D99, 14D14, 14D14 Gold, 14D41 | 1.5 kg | 3 |
| Maize / all states | SingleCross | 32D12, Legend, Ranbanka | 4 kg each | 4 |
| Maize / all states | DoubleCross | 32D55 | 4 kg | 2 |
| Maize / all states | Threeway Cross | Purnima | 4 kg | 2 |
| Paddy / all states | Hybrid Paddy—1 kg (editable label) | DAWAT, 1 kg variant | 1 kg | 2 |
| Paddy / all states | Hybrid Paddy—3 kg (editable label) | DAWAT, 3 kg variant | 3 kg | 2 |
| Paddy / all states | Research Paddy | Janki Gold, Karina, Karishma | 10 kg each | 2 |

DAWAT's 1 kg and 3 kg variants MUST remain in different segments, with separate settings, calculations and CNs. Do not pool them into one Hybrid Paddy calculation group.

## 4. Editable settings and fixed safeguards

| Setting area | Agreed specification |
|---|---|
| Seasons and dates | Separate editable season boundaries, sales/return transaction eligibility, ABS advance eligibility, CD windows, calculation cutoff and scheme validity. Preserve Phase 0 season workflow. |
| Within-season rules | No effective rate changes partway through a season. Draft setup is editable; retain audited corrections and historical versions without silently changing issued calculations. A new version is not permission for an automatic mid-season rate schedule. |
| Units | Each segment can select kg or packet calculation. Product packet sizes govern conversion. DAWAT segments also offer kg/packet selection. Rates and thresholds must show their units and convert consistently. |
| Fractions | Fractional kg allowed; fractional packets prohibited. Do not silently round an invalid packet input. Validate conversion to a packet calculation unit and flag incompatible quantities for review. Exact treatment of a fractional-kg remainder in packet mode needs a Phase 4 check/clarification if encountered; no invented floor/ceiling rule. |
| ABS | Token and ABS benefit rates are common within the segment, not different product-wise. Eligibility and booking allocations remain product-wise. |
| Segment benefits | Quantity tiers, CD rates/balance/cap, return qualification and extra tiers use the segment scope. |
| Quantity mode | Editable whole-quantity or progressive-band mode. Current schemes use whole-quantity; highest rate continues above top threshold. |
| Extra benefit | Net-sold-quantity tiers, highest qualifying tier only. Support fixed rupee total, rupees/kg and rupees/packet. A per-unit rate applies to the segment's ENTIRE eligible net sold quantity. No ABS booking is required. |
| Return benefit | Editable no-return/low-return threshold, benefit amount and unit. Qualification at or below threshold; use returned/supplied quantities. Scheme 4 enables this benefit. Multiple return-benefit tier combination was not explicitly settled; do not assume stacking. |
| CD | Editable inclusive windows/rates, deduction order, cap method and excess-ABS treatment. Current rules retain deductions-before-CD, payment-plus-CD cap and excess ABS in first slab. Explicit 0% periods prevent gaps being treated as intended ineligibility. |
| Cash settings | Select eligible products by state/season; editable dates, required advance per kg/packet, billing/reference rate and cash CN rate. Block insufficient eligible payment or supply until resolved. |
| CN narration | Editable templates identifying party, crop, segment, season, benefit type and calculation details; constituent products listed as relevant. |
| Rounding | Current confirmed choice: nearest Rs1 for each separate CN; show adjustment and reconcile sum of rounded CNs. No other precision option was selected in Phase 3. Retain full internal precision and two-decimal money display. |
| Zero benefit | Show zero in working/explanation; do not issue a Rs0 CN. Outstanding review flags still block finalisation. |
| History | Remarks and previous versions retained for rule/mapping edits; finalised/issued records retain original settings and inputs. |

Settings flexibility must not allow duplicate money/quantity, source-date edits to gain eligibility, bypassing reconciliation, negative cash CN, automatic recoveries, or automatic benefit-related transfers.

## 5. Cash/regular quantity allocation

- Enter cash SUPPLIED quantity and cash RETURNED quantity separately for an eligible product.
- Cash net sold = cash supplied minus cash returned.
- Regular supplied = total product supplied minus cash supplied.
- Regular returned = total product returned minus cash returned.
- Regular net sold = regular supplied minus regular returned.
- Validate nonnegative components, returns not exceeding relevant supply, and reconciliation of both allocations to actual product totals.
- Example: total supply 10,000 kg, returns 500 kg; cash supply 3,000 kg, cash returns 100 kg => cash net 2,900 kg; regular supply 7,000 kg, returns 400 kg, net 6,600 kg.
- This quantity remainder does NOT automatically allocate any remaining payment/ABS money. User chooses money allocation; unallocated money remains visible credit.
- Cash quantities stay outside regular ABS/quantity/CD/extra/return calculations. Count each transaction, quantity and payment once.
- Flag cash returns. Additional manual deduction = flagged return kg x entered Rs/kg, with remarks; explicit zero rate allowed with remark. Deduct AFTER normal cash CN on net sold quantity. Floor final cash CN at zero; excess deduction requires review, not an automatic debit.
- Preserve source cash transfer restrictions. Regular transfers retain original dates and destination CD rules; cash has no automatic transfers.

## 6. Read-only source settings extracted

These are source starting values, not proof of correct formulas or approval for every state/season. Latest scheme enablement above controls whether a source benefit is active.

### Updated Gujarat cotton reference

User supplied `GJ cotton customized.xlsx` and instructed using it for cotton. It has `Cotton CN` (formula working) and `Sheet1` (static results), not explicitly labelled Premium/Deluxe schemes.

User authorised choosing a suitable testing arrangement. Provisional decision communicated: apply customized workbook numerical settings to Gujarat Deluxe, Scheme 4; retain Premium net-rate-only with rate pending. This is a TEST assignment, not evidence of the workbook's original product scope.

- Billing: Rs901/packet.
- ABS token: Rs250/packet; ABS benefit: Rs25/packet.
- Quantity CN upper-inclusive bands: up to 300 packets Rs150/packet; above 300 through 500 Rs175; above 500 through 1,000 Rs200; above 1,000 Rs225. Rate applies to entire eligible net sold quantity.
- Customized extra totals for the same bands: Rs3,950 / Rs15,000 / Rs17,500 / Rs50,000. These bands are provisional TEST settings. Do not replace them with old tour minima silently. At zero net sales, extra is zero, overriding the source formula's Rs3,950 output.
- CD percentages: 8%, 4%, 2%, 0%. Customized working labels do not specify dates. Earlier confirmed cotton dates remain the starting reference: eligible payments through 15 June 2026 at 8%; 16 June–15 July at 4%; 16–30 July at 2%; 31 July onward 0%. Eligibility start remains governed by season/advance settings.
- Return benefit Rs10/packet with threshold 10%. Preserve agreed inclusive qualification 0% through 10%, overriding customized formula `0 < return% < 10%`.
- Separate CN rounding overrides source grand-total-only rounding. Use actual ledger reconciliation rather than treating source outstanding cells as authoritative.
- Earlier Premium source net-price bands (Rs700/675/650/625) were NOT approved as the new net-rate-only setting. Premium rate and net-rate settlement/CN presentation remain pending; do not guess.

### Bajra source starting values

`RJ_Bajra_ABS_Credit_Note_Calculator_v6.xlsx`, Assumptions:
- Billing Rs400 per 1.5 kg packet.
- Token Rs50/kg; ABS benefit Rs10/kg.
- Upper-inclusive quantity CN bands: <=330 kg Rs16/kg; >330–630 Rs20; >630–1,050 Rs25; >1,050–1,650 Rs27; >1,650 Rs32. Highest rate continues beyond source 9,999 marker.
- CD: eligible through 30 June 2026 7%; 1–15 July 5%; 16–31 July 3%; 1 August onward 0%.
- Source lists tour names but no separate extra-CN rupee values. Those values and independent eligibility thresholds remain missing; do not infer them from quantity-slab labels.
- Source return bonus Rs10/kg at 10% is DISABLED under user-selected Scheme 3.
- Source is Rajasthan-oriented; all-state catalogue coverage does not approve its rates for every state.

### Maize source starting values

`MAIZE all type CN -V5.xlsx`:
- SingleCross billing Rs350/kg, token Rs50/kg, ABS benefit Rs10/kg; packet 4 kg.
- SingleCross quantity CN: <=200 kg Rs2.50/kg; >200–500 Rs5; >500–1,200 Rs7; >1,200–2,500 Rs10; >2,500 Rs15 (continues beyond 5,000).
- SingleCross extra: >=1,500 net sold kg Rs25,000; >=3,000 Rs50,000; highest only. NET SOLD replaces the source ABS-eligible basis.
- SingleCross no-return starting benefit Rs10 per 4 kg packet, threshold 0%, editable under Scheme 4.
- DoubleCross/32D55 billing Rs140/kg, token Rs40/kg, ABS Rs10/kg.
- DoubleCross quantity CN: <=500 kg Rs10/kg; >500–1,500 Rs15; >1,500 Rs20 (continues beyond 2,500). No extra/return benefit under Scheme 2.
- Both source regular segments CD: eligible through 15 June 2026 12%; 16–30 June 8%; 1–15 July 5%; 16–30 July 2%; 31 July onward 0%.
- Cash 32D55 starting reference: billing Rs140/kg; cash CN Rs40/kg; required advance Rs100/kg; eligibility 12–31 March 2026 inclusive. Cash return process is replaced by agreed Phase 2 manual deduction handling.
- Do not copy automatic source transfers or aggregate segment ABS eligibility; confirmed manual transfers and product-wise eligibility override them.
- Purnima and all paddy numerical settings have no reviewed source and remain missing.

## 7. Missing configuration / outstanding interpretation

Missing is NOT zero. Block affected finalisation when required active settings are absent; other fully configured test cases can proceed.

1. Premium net rate, whether it is fixed or tiered, and billing-to-net-rate CN treatment.
2. Purnima billing/reference rate, token/ABS rates, quantity tiers, CD windows and eligibility dates.
3. Paddy settings separately for DAWAT 1 kg, DAWAT 3 kg and Research Paddy: billing/reference, ABS, quantity and CD settings/dates.
4. Bajra extra benefit amounts and eligibility tiers; user-defined segment name remains editable, not forced to Hybrid Bajra.
5. Explicit initial state/season numerical configurations and actual season/cutoff/ABS windows where no authoritative dates are available.
6. Confirm provisional customized Deluxe extra bands when moving beyond testing. Zero-sales exclusion is retained.
7. Packet-mode handling of fractional kg that does not convert to whole packets; no silent rounding or loss of quantity. Fractional derived ABS booked quantity also needs distinction from prohibited fractional packet entry; do not floor money allocation without an agreed rule.
8. Confirm cash advance eligibility basis against supplied vs net sold quantity when cash returns occur if a test exposes ambiguity. Do not invent how refunded/retained cash advance changes eligibility.

## 8. Phase 4 work

- Test representative configured cotton Deluxe, maize SingleCross/DoubleCross and cash cases; missing extra settings must be resolved or explicitly excluded from incomplete bajra cases.
- Compare source results to independent expected calculations, preserving confirmed overrides. No native formula recalculation or boundary certification has yet been done.
- Verify blank vs zero, missing/negative quantities/rates, supply/return conservation, packet/kg conversion, slab equalities and highest-rate continuation.
- Verify product-wise ABS booking/eligibility under common segment rates, segment excess pooling, old-dues clearing, opening-credit allocations, no duplicate receipt/ledger reduction.
- Verify CD exact date boundaries, excess ABS first slab, chronological/manual order, cap payment + CD <= remaining eligible balance, date-preserving regular transfers, no applicable slab 0%, cash restrictions.
- Verify segment return %, no-return and exact threshold equality; zero-sales and incomplete supply must not gain benefits.
- Verify cash/regular split, cash eligibility, deduction after normal net-sales CN, zero floor and excess-deduction review.
- Verify full precision, separate nearest-Rs1 CN rounding, sum reconciliation, prior issued CN identity, revised difference proposals, frozen historical snapshots.
- Final party balance = actual reconciled ledger balance minus proposed new CN once. Segment balances are benefit working, not a second party ledger.
- Saini ledger begins 10 April; obtain 1–9 April transactions or explicit confirmation none before a full-season ledger test.

## 9. File identities

- This handoff's inherited Phase 2 attachment: All_Crop_CN_Phase_2_Handoff(1).md — libfile_745e604d165481918a6a631ed569678d.
- Customized cotton: GJ cotton customized.xlsx — libfile_fd091f6270f081918e1f0721c6e58d4f.
- Original cotton: GJ_Cotton_ABS_Credit_Note_Calculator_v9.xlsx — libfile_a649e94755388191b7369d94c10ba165.
- Bajra: RJ_Bajra_ABS_Credit_Note_Calculator_v6.xlsx — libfile_98f9da21b5008191ae6a222d66d59247.
- Maize: MAIZE all type CN -V5.xlsx — libfile_d444224757fc81918ebd3f4639a853dc.
- Phase 0: All_Crop_CN_Phase_0_Handoff(2).md — libfile_c3f2a5ef9c9c819181441b5f31adff9f.
- Flowchart: all crop CN working flowchart.xlsx — libfile_f98c5f5e6af48191a501713699094467.
- Saini ledger: Ledger_Statement - Saini Krishi Yantra,Shri Madhopur,Sikar - 20261003.pdf — libfile_3b0ad16b22a4819194b86b8cd679b715.

## 10. Remaining phases

4. Representative calculations, boundary testing and source formula verification.
5. Screen design.
6. Offline app implementation.
7. Real-account/import/save/reopen testing.
8. Packaging, backup/restore, exports and instructions.

## Ready-to-paste prompt

Start Phase 4 of my all-crop offline CN calculator using this Phase 3 handoff and its appended Phase 2/1 rules. Preserve all confirmed settings, state/season mappings, four scheme combinations, product-wise ABS and segment benefit calculations, separate DAWAT packing segments and manual cash/regular allocations. Use customized cotton Deluxe settings only as the labelled provisional test reference. Verify representative calculations and boundaries against independent expected results. Mark missing rates as unconfigured, not zero, and do not invent values. Ask one unresolved decision at a time unless I request a batch. No app coding or source Excel changes yet.

---

## Appendix: Phase 2 and historical Phase 1 handoff

The original supplied handoff follows unchanged. Phase 3 content above supersedes conflicts; Phase 2 supersedes its historical Phase 1 appendix.

# All-crop offline CN calculator — Phase 2 handoff

Date: 13 October 2026
Status: Phase 2 business-rule clarification complete. Next: Phase 3 settings specification and product mapping. No app code written and no source Excel files modified. Formula recalculation and boundary verification remain pending.

## Instructions for the next chat
Preserve confirmed decisions. Do not reopen settled questions unnecessarily. Define editable settings before coding. Ask one decision at a time with a small example unless the user requests a batch of questions. Source workbooks are starting examples, not universal scheme rules. The appended Phase 1 handoff supplies earlier calculation details; Phase 2 below overrides conflicts.

## Objective and inherited Phase 0 rules
Offline multi-crop CN calculator with accounting/Excel imports and manual input. Preserve original transactions; audit corrections and allocations. Rates depend on party state. Seasons and cutoff dates are selectable: current seasons April–August and October–January/February. Season 1 starts 1 April. CN is issued once after a season is complete; issue date does not determine transaction eligibility.
Use selected-season net sold quantity only for benefit eligibility. Distinguish sales-return CN from scheme-benefit CN. Final ledger balance includes all posted transactions once. Earlier-season issued CN is outside current-season benefit entitlement but its ledger effect remains included once.
Phase 0's exceptional prior-season return proposal is outside the user's current workflow: user says this does not occur. Do not add automatic prior-benefit recovery or silently change inherited rules if such data later appears; seek review then.

## Phase 2 confirmed rules

### 1. Old dues, opening balances and earlier advances
- Old outstanding must be cleared before money qualifies for ABS. Old dues Rs100,000 + ABS receipt Rs200,000 => Rs100,000 clears dues and Rs100,000 is available for ABS. Old dues Rs200,000 + receipt Rs150,000 => no ABS; Rs50,000 old dues remain.
- Show old dues cleared and available ABS separately. The old-dues amount is confirmed manually; do not add it as a second debit or deduct the receipt twice.
- Regular CN working uses selected-season net sold quantity converted to value; do not impose a universal old-dues allocation requirement on regular quantity-based benefits.
- No prior pending CN exists in the current business workflow. Do not create a pending-prior-CN calculation requirement.
- Eligible pre-season advances already reflected in opening balance can be identified and manually allocated to ABS; they do not reduce ledger balance again.
- Opening party credit can qualify for manual ABS allocation without an original receipt date. Apply selected scheme ABS rules. Excess ABS enters that segment's first CD slab without requiring an original receipt date.
- Unallocated opening credit stays visible as party credit and earns no ABS benefit. No forced ABS allocation.

### 2. Allocation hierarchy and conservation
- Manual allocation hierarchy: Crop -> Segment -> Product. Product mappings will be defined later.
- Product ABS eligibility stays product-wise: min(booked quantity, product net sold quantity). Do not automatically move product A's booking to product B.
- Example: Rs50/kg token; A allocation Rs30,000 books 600kg, net sold 400kg => eligible 400kg and Rs10,000 excess. B allocation Rs20,000 books 400kg, net sold 600kg => eligible 400kg. Reallocation requires a manual choice.
- Product excess ABS combines within its segment and enters that segment's first CD slab, subject to the segment cap. This is the current Phase 2 rule; keep future scheme settings configurable.
- Ordinary CD-period receipts must be assigned to a crop/segment before finalisation. This requirement does not force all money into ABS.
- If an assigned payment exceeds the segment's eligible balance, the remainder stays visible as party credit, earning no further CD unless manually allocated elsewhere.
- Draft ABS allocations may be revised; recalculate ABS, excess and CD and retain allocation history.
- Receipts and credit cannot be allocated or counted twice. Source dates and amounts remain traceable.

### 3. Manual payment transfers and CD
- Allow manual transfer of unused payment to a chosen crop/segment. Retain original receipt date and use the destination's CD slab covering that date. Example: July cotton payment excess transferred to maize uses maize's July slab if one exists.
- Destination net-rate scheme or no applicable CD slab => 0% CD; transferred money still settles balance.
- This explicitly supersedes Phase 1's blanket 0% rule for regular-maize transfers when a destination CD slab applies. Transfers generate no new ABS benefit; cash-scheme restrictions remain.
- Default payment processing order is chronological by original receipt date; also provide manual allocation. Manual choices cannot change receipt dates, duplicate money or bypass caps/scheme restrictions.
- CD calculation/cap is segment-wise using combined eligible balance and allocated payments, not separate product caps.
- Shared fixed tour/extra benefit is deducted at segment level; no artificial product split is needed for segment CD balance. Product ABS eligibility stays product-wise.
- Keep segment balances and overall party balance visible. Cotton credit Rs20,000 and maize due Rs50,000 => overall party due Rs30,000. Benefit-related reallocations remain manual.

### 4. CN scope, return benefits and rounding
- Current issue mode: segment-wise. Separate CN/narration for each applicable benefit: quantity/slab, ABS, CD, return, tour/extra. Do not combine all benefits into a single indistinguishable CN.
- Products in the same segment jointly determine quantity tier; one quantity CN for the segment lists constituent products.
- ABS calculates product eligibility individually, then issues one segment ABS CN.
- Tour/extra is one segment total, not distributed between products for current issue mode.
- Return qualification is segment-wise: sum selected-season returned quantity / sum selected-season supplied quantity, using matching units. Eligible return benefit is one segment CN. Threshold/rate remain editable.
- Example: A supplied 600kg, returned zero; B supplied 400kg, returned 80kg => segment return 8%. Use segment threshold, not B's separate 20%.
- Phase 1 allowed segment-wise and product-wise issue options. Phase 2 chooses segment-wise for now; product-wise future mode must not be claimed fully specified or completed. Shared-benefit product splitting can be specified when needed.
- Keep calculation precision; round each separate issued CN nearest Rs1, show rounding adjustment, and reconcile using the sum of rounded CN amounts. Do not independently round a grand total and create a mismatch.

### 5. Cash-scheme returns
- Flag sales-return quantity against cash-scheme supply.
- User chooses an editable additional CN deduction rate per kg, with remarks; no permanently fixed deduction rate.
- Deduction = flagged return kg x entered Rs/kg.
- Apply this as an additional adjustment AFTER normal cash CN has been calculated on net sold quantity. User explicitly confirms cash CN Rs20,000 minus additional deduction Rs3,000 => final cash CN Rs17,000.
- Sales-return ledger value is already posted separately and is not deducted again in ledger reconciliation.
- Require explicit rate entry to resolve every cash-return flag before finalisation; Rs0/kg is allowed with a remark.
- Final cash CN cannot become negative. Cash CN Rs2,000 minus deduction Rs3,000 => issue Rs0 and flag remaining Rs1,000 for review; do not create an automatic recovery/debit adjustment.

### 6. Ledger reconciliation, finalisation and versions
- Final party balance = reconciled actual ledger balance minus proposed new seasonal CN once. Actual balance already includes opening debit/credit, actual sales/returns, receipts and previously posted CN once.
- Example: ledger due Rs80,000; new CN Rs30,000 => final due Rs50,000.
- Issue full eligible CN even if it exceeds dues: ledger due Rs20,000; new CN Rs30,000 => party credit Rs10,000, available for future business.
- Compare imported balance with opening-plus-transactions reconciliation. Show discrepancy; block finalisation until corrected or explained by a traceable adjustment. Preserve source records.
- User's current workflow finalises net sales and then calculates/issues CN together; no separate changing-balance workflow is needed now. Freeze net quantity, ledger snapshot, allocations, rule version and calculation at finalisation.
- Mark issued CN by party, crop, segment, season and benefit type, preventing duplicate full issue for the same entitlement. Scheme CN is normally issued once after season completion; there is no routine partial-issue workflow.
- Changed rates/inputs produce a new saved calculation version, preserving the earlier one and its rules.
- If CN was already issued, show only the difference as a proposed adjustment for review. Issued Rs30,000, revised Rs32,000 => proposed additional Rs2,000; revised Rs28,000 => proposed Rs2,000 decrease/recovery adjustment, not an automatic transaction.

## Phase 3 scope
Define editable settings and mapping structure, not app coding:
- Party/state, crop, segment, product and product-to-segment assignments.
- Season start/end, transaction eligibility, calculation cutoff and scheme validity.
- Scheme type including ABS, regular CD, net-rate and separate cash schemes.
- Kg/packet units, packet size, conversion and fractional quantity restrictions.
- Token rates, ABS benefits, quantity tiers and whole-quantity/progressive modes.
- CD windows, rates, cap/order, excess ABS first-slab treatment and transfer rules.
- Return threshold/rate, segment scope, extra/tour tiers and applicability/combination rules.
- Segment CN narration, rounding and editable cash-return deduction entries.
- Historical rule versions, draft/manual allocations, finalisation and issued-status controls.
Use cotton, bajra and maize settings as initial examples. Future paddy Research/Hybrid and maize SingleCross/DoubleCross are mapping examples, not a locked complete catalogue. Do not invent rates or mappings.

## Files and prior handoffs
- Phase 0: All_Crop_CN_Phase_0_Handoff(2).md — libfile_c3f2a5ef9c9c819181441b5f31adff9f
- Phase 1: All_Crop_CN_Phase_1_Handoff(1).md — libfile_e25d6f024bac8191954c7633bb0ec1b2
- all crop CN working flowchart.xlsx — libfile_f98c5f5e6af48191a501713699094467
- MAIZE all type CN -V5.xlsx — libfile_d444224757fc81918ebd3f4639a853dc
- GJ_Cotton_ABS_Credit_Note_Calculator_v9.xlsx — libfile_a649e94755388191b7369d94c10ba165
- RJ_Bajra_ABS_Credit_Note_Calculator_v6.xlsx — libfile_98f9da21b5008191ae6a222d66d59247
- Ledger_Statement - Saini Krishi Yantra,Shri Madhopur,Sikar - 20261003.pdf — libfile_3b0ad16b22a4819194b86b8cd679b715
Saini ledger starts 10 April; obtain 1–9 April entries or explicit confirmation of none before full-season testing.

## Remaining phases
3 editable settings specification and mappings.
4 representative calculations, boundary tests and source formula verification.
5 screen design.
6 offline app implementation.
7 real-account/import/save/reopen testing.
8 packaging, backup/restore, exports and instructions.

## Ready-to-paste new-chat prompt
Start Phase 3 of my all-crop offline CN calculator using this handoff. Phase 2 decisions supersede conflicting earlier rules. Define editable crop/state/segment/product/season/scheme settings and product mappings while preserving the confirmed calculation, allocation, segment CN and reconciliation rules. Ask one decision at a time with a small example; give a batch only when I request it. Do not start app coding or modify source Excel files yet. The Phase 1 handoff is appended for calculation details; retrieve original workbooks only when needed.

---

# Appendix: Phase 1 handoff as received (historical; Phase 2 overrides conflicts)

# All-crop offline CN calculator — Phase 1 handoff
Date: 13 October 2026
Status: Phase 1 business-rule clarification complete for the items discussed. Read-only formula inspection; full recalculation, boundary tests and certification remain pending. No app code written; source workbooks unchanged.
Use together with All_Crop_CN_Phase_0_Handoff(2).md; Phase 0 remains authoritative for workflow, imports, seasons and ledger handling. Decisions below supersede conflicting source formulas.

## Objective
Offline multi-crop CN calculator with editable crop/product/state/segment/season/scheme settings. Work one phase per chat. Reuse sound Excel maths; do not copy confirmed defects.

## Confirmed Phase 1 rules
1. ABS: allocated token amount / token rate = booked quantity. Eligible quantity = min(booked quantity, net sold quantity), in matching units. ABS CN = eligible quantity × benefit rate. Used token principal = eligible quantity × token rate. Excess ABS = allocated token minus used principal.
2. Receipts are recorded once. Used token principal reduces outstanding once; only excess enters the selected scheme's payment pool. Unallocated advance is distinct from excess within an allocated scheme, stays visible, and earns no ABS benefit. No automatic ABS allocation.
3. Cotton and bajra source settlement formulas omit used token principal. Correct future specification. Regular maize already deducts it.
4. Return % = current-season returned quantity / current-season supplied quantity × 100, matching units, for every crop. Do not include prior-season returns automatically. Missing/zero supplied quantity or unresolved return data requires review; do not award a bonus from incomplete data.
5. Return-benefit threshold and amount editable by crop/product/scheme. Qualify at or below threshold: 10% qualifies for a 10% limit; 0% represents no-return. Benefit rate unit selectable as Rs/kg or Rs/packet, applied to net sold quantity. Cotton's current Rs10/packet and bajra's Rs10/kg are starting settings. Maize SingleCross's existing no-return starting setting is Rs10 per 4kg packet; user wants it editable.
6. Return benefit always recalculates with quantities; no fixed sample-row return amounts. Cotton Data W2–W8 have hardcoded values (W4 Rs17,500); later rows have formulas. Do not preserve these sample constants as automatic business rules.
7. Current cotton, bajra and regular maize schemes: before CD, deduct all applicable quantity CN, ABS CN, return bonus, tour/extra-benefit CN and used ABS principal from net sales value. This is the user's clarified decision, replacing differing existing order. Final ledger reconciliation must not deduct these twice.
8. Current schemes cap eligible payment so payment + its CD does not exceed remaining eligible balance: eligible payment = min(available qualifying payment, remaining eligible balance / (1 + CD rate)). Extra actual payment remains credit without more CD. Both calculation order and cap are scheme settings, not universal laws; future net-rate or other schemes may differ.
9. Cotton current inclusive CD windows: eligible payments up to 15 June 2026 = 8%; 16 June–15 July = 4%; 16–30 July = 2%; 31 July onward = 0%. Earlier eligible payments belong to first window. Earliest eligibility date remains governed by season/advance rules.
10. CD window inclusive start/end dates and percentages editable crop-wise and scheme-wise for each season. Flag overlaps and uncovered dates. Excess ABS CD rate/window configurable by scheme.
11. Kg and packet entry/calculation options both supported, selectable by need. Editable packet size; token rates, benefit rates and thresholds show units. Convert quantities to a common unit. Whole-packet/fractional restrictions are configurable; no particular restriction was selected.
12. Keep full precision during calculation; money displayed to two decimals. Current final CN rounded nearest Rs1; visible rounding adjustment. Rounding editable by scheme. With separate CNs, precise rounding/distribution reconciliation remains to define.
13. Current quantity slabs choose a rate using total eligible net sold quantity and apply that rate to the entire eligible quantity, not progressive bands. Future settings allow either whole-quantity or band-by-band calculation.
14. Highest slab rate continues above top threshold for current cotton, bajra and maize.
15. Regular maize 32D55 ↔ SingleCross credit transfers become manual: user selects amount/destination. Current transferred amount earns 0% CD and no new ABS benefit. Cash segment remains separate under source restrictions.
16. Return against 32D55 cash supply flags the account and blocks finalisation until resolved. Resolution process remains to define; do not silently remove it.
17. Only highest qualifying tour/extra tier applies in current schemes; lower tiers are not added.
18. Tour/extra benefit tier eligibility uses net sold quantity, not ABS-eligible quantity. No ABS booking is required. This specifically changes maize SingleCross source tour basis from ABS-eligible kg to net sold kg.
19. Product-to-segment assignments editable. Examples: maize SingleCross and DoubleCross; paddy Research and Hybrid. These examples are not a locked complete catalogue.
20. Quantity tier uses combined net sold quantity of all products assigned to the same segment, converted to a common unit. Avoid pooling mutually exclusive scheme quantities twice; detailed scope is Phase 2/3.
21. Each applicable benefit must have separate CN/narration: quantity/slab CN, ABS CN, CD CN, return CN, tour/extra CN as enabled. User did not approve universal stacking for every future scheme; keep applicability/combination rules scheme-specific. Existing cash scheme remains separate.
22. Both issue modes: segment-wise (one CN per benefit covering that segment) and product-wise (one per product/benefit, with segment quantity determining slab). Issue mode must not change total benefit. Product-wise split of shared CD/fixed tour benefit remains Phase 2.

## Source workbook starting settings
- Cotton: Premium/Delux slabs; Rs250/packet token; Rs25/packet ABS; 8/4/2/0% CD; return and extra benefits. Labels/rules changed above override source.
- Bajra: 1.5kg packet; Rs50/kg token; Rs10/kg ABS; quantity/tour slab; 7/5/3/0% CD. Calculation order, CD cap, inclusive return threshold changed above override source.
- Maize: regular 32D55 (Rs40/kg token, Rs10/kg ABS); combined SingleCross 32D12/Ranbanka/Legend (Rs50/kg token, Rs10/kg ABS); 12/8/5/2/0% CD. 32D55 cash: Rs140/kg billed, Rs40/kg cash CN, Rs100/kg eligible advance 12–31 March 2026; no other benefits or regular transfers under existing scheme.
- Do not assume the label 32D55 is a permanently fixed product-to-segment mapping; assignments are editable.

## Sources and identities
- Phase 0 handoff: libfile_c3f2a5ef9c9c819181441b5f31adff9f
- Flowchart: all crop CN working flowchart.xlsx — libfile_f98c5f5e6af48191a501713699094467
- MAIZE all type CN -V5.xlsx — libfile_d444224757fc81918ebd3f4639a853dc
- GJ_Cotton_ABS_Credit_Note_Calculator_v9.xlsx — libfile_a649e94755388191b7369d94c10ba165
- RJ_Bajra_ABS_Credit_Note_Calculator_v6.xlsx — libfile_98f9da21b5008191ae6a222d66d59247
- Ledger_Statement - Saini Krishi Yantra,Shri Madhopur,Sikar - 20261003.pdf — libfile_3b0ad16b22a4819194b86b8cd679b715

## Phase 2 — next work, not decided
- Opening debit/credit; prior dues; pending earlier CN and already-issued scheme CN.
- Eligible advances before season start, especially those already reflected in opening balance; no double deductions.
- Receipt allocations across crops/segments/products/schemes and old dues; allocation conservation; visible unallocated amounts.
- Product-wise split of CD, fixed tour/extra benefit, ABS and shared amounts; segment/product rounding reconciliation.
- Separate sales-return CN, issued scheme CN and proposed new scheme CN; benefit-specific reconciliation to avoid duplicate issue.
- Returns without invoice links: current/prior-season classification and flagged cash return resolution. No recovery of prior benefits for negligible late returns per Phase 0.
- Final outstanding and credit; preserve source transactions and audit manual corrections/allocations.
- What happens on scheme/input changes after a saved or finalised result; preserve historical rule versions.

## Remaining verification
Full workbook recalculation was not performed. Verify missing/negative inputs, units, fractional quantities, threshold equality, date boundaries, quantities beyond top slabs, allocation conservation, no-return missing data, cash eligibility, issued-CN matching and rounding in Phase 4.
Saini sample ledger begins 10 April: obtain 1–9 April entries or explicit confirmation of none before a full-season test.
Future scheme patterns beyond the three samples must be supported without treating current source rules as universal.

## Remaining phases
2 allocations/opening dues/pending CN/reconciliation.
3 editable settings specification.
4 representative/boundary calculation verification.
5 screen design.
6 offline app implementation.
7 real-account/import/save/reopen testing.
8 packaging, backup/restore, exports/instructions.

## Ready-to-paste next-chat prompt
Start Phase 2 of my all-crop offline CN calculator using the attached Phase 0 and Phase 1 handoffs. Preserve the decisions already agreed. Finalise old outstanding, prior pending and already-issued CN, eligible earlier advances, manual payment/ABS allocations across crops and segments, product-wise distribution of shared CN, and final ledger reconciliation. Use the referenced source calculators and Saini ledger when needed. Ask one decision at a time with a small example. No app coding or changes to source Excel files yet.

