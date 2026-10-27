# Core rules audit — Update25

Audit date: 16 October 2026. Baseline: delivered Update24 source.

## Result

The accepted reference calculations and main safeguards passed. Code review and targeted
counterexamples identified six additional gaps. This cumulative update fixes them without
modifying stored financial data, saved settings, original vouchers, allocations or issued totals.

## Confirmed findings and corrections

| Finding | Before | Update25 |
| --- | --- | --- |
| Net Price with different billing/quantity units | A 4 kg packet billed at ₹400, with a ₹80/kg net-price slab and 40 kg net sold, produced ₹12,800 CN. The correct CN is ₹800. | Convert configured billing to the calculation unit before subtracting the slab's net price. Same-unit Net Price and Fixed CN modes retain their rules. |
| Custom slab validation | An open-ended slab could be followed by another slab. Progressive bands could overlap and double-count quantity. Inclusive extra minimums could repeat or be unordered. | An open-ended slab must be last; inclusive extra minimums must increase and use consistent boundary semantics. Unknown quantity calculation modes are rejected. Existing valid highest-slab continuation is retained. |
| Cash minimum advance and settings | A negative configured advance could let a cash quantity earn CN without the required cash payment. Cash dates, rate units and negative CN rate lacked complete settings validation. | Positive cash advance, nonnegative CN rate, valid date range, eligible product list and kg/packet rate unit are validated. Invalid confirmed settings cannot be saved; invalid active draft schemes block finalisation. |
| Cash packet quantity split | Fractional packets could be entered in cash supplied/returned splits even though packet entries must be whole. | Fractional packet splits are rejected before save/calculation. Fractional weights remain supported when calculating in kg. |
| Frozen-result display | The calculate endpoint recomputed a completed record using its frozen settings but the current engine. An engine update could change its displayed result. | Finished/issued records return their authoritative stored result from the selected workbook. A client-supplied replacement result is ignored. Draft revisions still calculate normally. No historical result is rewritten. |
| State in reporting | An explicit scheme-state override was used by the calculation but could be grouped under the workbook's state in reports/dashboard. | Reporting follows the calculation's precedence: explicit scheme state, then workbook scheme state, then fallback metadata/address. HQ remains sourced from PDF Group. |

These are code-level findings. This audit did not establish that the user's live records contained
any of these configurations. Historical affected calculations are preserved; use a reviewed draft
revision if one needs correction. There is no automatic retrospective reissue or total replacement.

## Rules checked and evidence

| Core rule | Result | Evidence |
| --- | --- | --- |
| Saini outstanding stays ₹1,42,535 | Passed | Accepted synthetic-date Saini arithmetic regression: ledger ₹2,79,265 − Qty ₹61,200 − Extra ₹65,000 − CD ₹10,530. No real receipt dates invented. |
| ABS uses original receipt dates and configured booking period | Passed | Boundary tests and July type/source/add/save rejection; source dates not rewritten. |
| Extended ABS needs configured extension plus approval and remark | Passed | Extension/date boundary regression; checkbox alone cannot extend the configured period. |
| Opening credit is allocation metadata, not a second receipt | Passed | Mixed opening splits, cap, ledger conservation, save/reopen and Year Link tests. Undated opening-credit exception retained. |
| Old dues clear before payment becomes available | Passed | Source availability, combined allocation caps and old-dues boundary tests. |
| No double allocation or amount above source availability | Passed | Exact decimal split tests, multi-row caps, negative/nonfinite and atomic save rejection. |
| ABS is product-wise and capped by regular net sold quantity | Passed | Reference calculations and 180 generated ABS cases. Principal + excess = allocated token. |
| Eligible excess ABS enters the segment's first configured CD slab | Passed | Existing reference arithmetic and excess pool tests. Net/no-CD destinations remain 0% CD. |
| Ordinary CD follows original date; manual ordering is explicit | Passed | Every accepted crop's date boundaries, manual-order regression and original-date preservation tests. |
| Payment + CD cannot exceed remaining segment balance | Passed | 180 independently calculated generated cases covering 0–100% configured CD and small/large payments. |
| Sales returns reduce net sold; IPT in adds and IPT out reduces supply | Passed | Actual PDF fixtures, adjusted stock, return-bonus denominators, late IPT fingerprints/cutoffs and duplicate-issue safeguards. |
| Cash supplied/returned splits conserve physical quantity and payment coverage | Passed after fixes | Accepted cash reference, return deduction/floor, oversized split/value rejection, cash config and packet-integrality tests. |
| Quantity slabs, Extra and Return bonus retain accepted boundaries | Passed after validation fixes | Whole/progressive/highest-slab tests, SingleCross inclusive thresholds, zero sales and return-limit reference cases. |
| Separate half-up rupee rounding per CN | Passed | Accepted rounding case plus generated cases checking sum of separately rounded benefits and product attribution totals. |
| DAWAT 1 kg and 3 kg remain separate | Passed | Separate catalogue/mapping identities, scheme arithmetic and product/report packing groups. |
| NRV = configured billing − scheme CN per net sold unit | Passed | ₹901 − ₹115 = ₹786/packet reference, packet/kg conversions and weighted realisation/quantity tests. |
| Freight CN excluded from NRV; ledger CNs still affect actual ledger closing | Passed | Posted/freight journal and reporting regressions. |
| Requested CN changes stay outside actual CN, outstanding and NRV | Passed | Display-only save/finalise/issue and reporting tests. |
| Workbook settings/schemes/mappings and records stay independent | Passed | Private-store tests, 200-party bulk/resume and cross-workbook HTTP guards. |
| April–March Year Link retains original source provenance and caps | Passed | Adjacent-year reconciliation, confirmed unspent source, source tampering and duplicate reservation tests. |
| No duplicate CN issue; revisions preserve prior-issued entitlement | Passed | Stale-write/freeze/issue/revision and overlapping-workbook tests. |
| Backup/restore/restart preserve records and archived identities | Passed | Database/workbook restore, safety-copy, restart and updater rollback tests. |
| Import/audit reads preserve voucher evidence and classifications | Passed | Real PDF fixtures, duplicate import/correction, read-only audit and finding-review regressions. |

## Verification

- 221 Python test methods passed: 209 previous plus 12 audit tests.
- The audit tests include 360 deterministic generated financial scenarios, not 360 additional
  test methods: 180 CD cap calculations and 180 ABS principal/excess calculations.
- 8 backup-first updater tests passed, including rollback after a simulated replacement failure.
- Full UI/API logic, Payment Studio, complete software UI, calendar/native-close and ABS assignment
  smoke checks passed using isolated temporary stores and actual fixture PDFs.
- Python compilation, JavaScript syntax, ZIP integrity, file hashes and source/program runtime
  byte equality verified.

The source and fixture checks do not replace Windows acceptance of the locally rebuilt EXE,
visuals, native file dialogs or actual printing. Minor print/CSV PC rechecks remain deferred as
requested. This audit did not connect to or change the user's running PC installation.

## Apply safely

1. Export a fresh complete backup and keep it separately.
2. Close the calculator and its command/server/desktop windows.
3. Extract the complete Update25 ZIP separately and run `Update_CN.bat`.
4. Select `app.py` inside the existing working source installation.
5. Continue using the existing `Start_Calculator.bat`. Existing launchers are unchanged.

The updater backs up code and data before replacement. No reimport or restore is needed for the
normal source update. If using a Windows EXE, rebuild it locally from the updated source. No EXE,
live database, virtual environment or real user backup is bundled.
