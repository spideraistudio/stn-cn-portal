# Update27 — workflow audit and corrections

Baseline: Update26 from the uploaded `update 25(1).zip`. Read the latest handoff,
ABS_DISTRIBUTION.md and CORE_RULES_AUDIT.md before work. The original 231 Python tests passed.
No live PC database was supplied or changed. Reproductions use isolated synthetic records and
the supplied PDF fixtures. This is a cumulative source update, not a new installation.

## Reproduced gaps and fixes

| Area | Reproduction / previous behavior | Correction |
| --- | --- | --- |
| Cash quantity selection | A valid 12 March cash payment of Rs10,000 for 100 kg of 32D55 could finalise with no cash split, producing only regular benefit. A zero-quantity placeholder also failed to warn. | Positive Cash allocations require a positive supplied-quantity split for that product. The issue points to Assign Payments. No quantity is guessed. A valid 100 kg cash split retains Rs4,000 Cash CN. |
| Cash editing | Add Cash always picked the first eligible product, and quantity rows did not identify their product/scheme. | Multiple available products get an explicit chooser; existing split products are excluded from new choices. Every split shows its product and scheme. One remaining eligible product can still be selected directly. |
| Changed scheme destinations | A scheme override left Rs30,000 ABS assigned to the old scheme as excess; finalisation could pass with missing benefits. | Positive benefit allocations left against an overridden scheme, or ABS/Cash against a product's wrong destination, block finalisation and point to payments. Money is not moved automatically. Unknown products cannot silently become excess ABS. |
| Scheme/season identity | Duplicate scheme IDs or duplicate season names could be saved, with dictionary/first-match selection hiding an entry. | Settings save rejects duplicate/missing identities atomically. Existing stores are not migrated. |
| Scheme units | Invalid billing, ABS, return or extra units passed scheme validation, then failed later during calculation. | Scheme validation checks units and rejects unknown benefit names. Existing valid units and arithmetic remain unchanged. |
| Manual CD order | Clearing an order produced an `int('')` calculation error. Negative/fractional/text orders could be saved. | Blank means 0, as for an omitted order. Invalid orders receive a clear validation error before save. Valid ordering keeps original dates and existing tie-breaking. |
| Frozen history / draft settings | Changing the client status of a saved completed record to draft caused recomputation. A draft could carry an obsolete frozen-settings/result object. | Stored status and stored result own completed history, including product CSV. Drafts use the current selected workbook settings and discard stale snapshot metadata on explicit save. Entries, allocations and mappings are retained. |
| Extension approval | A whitespace-only remark passed manual extended ABS approval while automatic distribution rejected it. | Both require a nonblank remark. No booking window or original date changes. |
| ABS preview timing | An input edit during an outstanding preview request could pair the old preview with new Apply inputs. | Stale responses are discarded. Apply re-reads the form and requires the exact previewed inputs, even without a change event. Existing revision/settings-version guards remain. |

The new Python reproduction suite failed on the old code and passes with these corrections.
The asynchronous UI regressions cover the delayed-preview and missing-change-event cases.
Do not infer that these configurations occurred in the user's actual saved work.

## Workflow coverage

| Workflow | Evidence / outcome |
| --- | --- |
| Import, product mapping and physical quantities | Existing fixture tests and UI/API tests cover normal and detailed Tally PDFs, bulk/resume, repeated and corrected imports, sales returns, IPT, manual items and period filtering. Existing results retained. |
| Workbook settings | Independent schemes/mappings, custom crop/packing setup, archive/restore and settings versions pass. New identity/unit checks run before committing settings. |
| Payments | Source caps, old dues, original dates, July ABS rejection, extension approval, opening-credit metadata, proportional ABS preview/manual edits, insufficient funding, excess into first CD slab and scheme-change review covered. |
| Calculation | Accepted Saini Rs1,42,535 outstanding; separate half-up rounding; cash/regular conservation; quantity, extra, return and Net Price units; 360 existing seeded ABS/CD scenarios retained. |
| Review, finalise, issue, revise | Missing Cash split and stale scheme destinations block finalisation. Frozen history is authoritative. Existing duplicate-issue, revision-difference and cross-workbook guards pass. |
| Reports and requests | Existing NRV unit conversion, freight/posted-CN exclusion, display-only CN requests and frozen product reporting regressions retained. PC print/CSV rechecks remain deferred. |
| Ledger audit and Year Link | Existing read-only audits, classifications, finding reviews and April–March matching/source provenance regressions retained. |
| Persistence and updater | Save/reopen, bulk data, backup/restore, workbook independence and backup-first updater tests cover unchanged data, both existing launchers, nested workbook databases, backup failure and replacement rollback. |

## PC acceptance still pending

1. Export a fresh complete backup, install using READ_ME_FIRST.txt, and reopen a saved party
   with Start_Calculator.bat. Confirm its entries, original dates and allocations remain.
2. Preview an automatic ABS split; change its amount; preview again before Apply. Reopen the
   saved record and confirm explicit product rows remain manually editable.
3. For Cash, choose a product, enter its supplied/returned quantities and confirm the expected
   CN. A payment with no quantity split should point you back to Assign Payments.
4. Open a completed record and confirm its stored totals remain unchanged. Use a revision
   only if intentionally correcting history.

Real Windows dialogs, browser visual acceptance and locally rebuilt Windows EXEs were not run
here. Minor print/CSV PC rechecks remain deferred. Text PDF fixtures are not proof of universal
PDF/OCR support. See TEST_RESULTS.txt for the final automated run counts.
