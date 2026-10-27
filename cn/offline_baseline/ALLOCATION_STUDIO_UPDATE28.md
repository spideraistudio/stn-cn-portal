# Update28 — payment and quantity allocation (held working update)

17 October 2026. Continues Update27. User asked to hold the file until remaining tasks are supplied.
No update was applied to the user's PC. No live database/settings/backup was changed or bundled.

## Confirmed Cash rule

User clarified: the ₹40,000 difference IS issued as CN, like Net Rate.
For 32D55 billed at ₹140/kg, ₹1,00,000 Cash booking at ₹100/kg funds 1,000 kg.
With 1,500 kg net sold, 1,000 kg Cash earns ₹40,000 Cash CN and the remaining 500 kg follows
its configured normal scheme. Cash quantity receives no regular ABS/Quantity/Extra/CD/Return
benefits. Remaining regular quantity receives no automatic ABS token assignment.
The test reference's normal scheme pays ₹10/kg quantity CN on 500 kg (₹5,000), giving ₹45,000
total CN and ₹65,000 outstanding from ₹1,10,000 ledger closing. These normal rates are test
settings, not a universal rule. Actual independent workbook settings remain authoritative.

## Workflow

- Central Money Allocation opens a read-only receipt breakdown: original dates, receipt amounts,
  old dues cleared, availability, allocated and remaining. Money is never counted twice.
- Four hubs: ABS, CD, Net Rate, Settlement. No separate Cash hub/panel. Net Rate includes Cash
  funding for presentation only; saved Cash allocation identities/calculation keys are preserved.
- All eligible crops/products/packings appear, using a dynamically sized canvas. Products have
  fixed-height cards, 130-pixel spacing, full-name tooltips, exact direct monetary totals and
  explicitly labelled scheme pools. Group-level pools are not falsely assigned to every product.
- Wheel zoom follows pointer; drag empty space to pan; Fit/Pause provided, no +/- zoom buttons.
  Graph navigation/zoom/pan does not mutate records. Data-based coordinates applied by trusted
  local JS keep the existing restrictive CSP. Crops have offline vector stickers/animation.
- Net Rate allocation type records source-money assignment to Net-only schemes, with no added
  payment CN, ABS or CD. Existing Net-price/Fixed-CN quantity maths is unchanged.
- Net Rate product -> Allocate Cash quantity. Choose funding row/source/amount and Cash supplied/
  returned quantities; optionally suggest quantity from total booked payment. Preview shows Cash
  CN, Cash net, regular net, funding and required advance. Apply explicitly saves the reviewed
  split and one funding row. Multi-source product funding edits preserve other rows.
- Cash returns retain explicit deduction-rate/remark rules; varying invoice values still need
  traceable value shares. Positive quantity/payment, conservation, whole packet units, dates,
  after-dues source caps, state/season/current scheme and configured rates are checked.
- Preview is read-only. Apply regenerates server plan; stale record/settings, cross-workbook,
  frozen/deleted, forged saved-original dates and changed asynchronous form inputs are guarded.
  Existing Cash keys, separate rounding and reporting attribution remain unchanged.

## Opening dues finding and fix

Previously the engine correctly reserved the entered `old_dues` amount in original-date order,
but fresh imports/bulk imports defaulted it to zero even with debit opening. Thus opening debit
alone did NOT guarantee clearance before scheme allocation. No live PC case is claimed inspected.

Fresh imports now propose the full positive opening debit for `old_dues` and require explicit
confirmation. Opening credit is never treated as debt. Existing drafts retain their financial
inputs/allocations; a prominent panel requires review when saved through the UI. Confirm full
opening or explain any excluded amount. A confirmed review is bound to opening and selected due;
changing either requires reconfirmation. If raising dues exceeds an already assigned source,
normal validation rejects it without moving money; reduce/review allocations first.

No automatic data migration/backfill. Previously completed snapshots remain authoritative.
Direct legacy records without the new review flag retain historical engine compatibility; the
normal UI opts current drafts into review on save. Server finalisation enforces the flag and
review for new imports/current UI-saved drafts. Dues reserve source availability only; proposed
CNs alone reduce the already-reconciled closing balance. Payments are not subtracted again.

## Verification and limits

253 Python test methods passed (244 prior + 8 new allocation tests + 1 scoped/auth HTTP test),
including existing 360 seeded numerical ABS/CD cases. Six UI/API suites passed. Targeted radial
UI suite rerun after final display/action adjustments passed. These are Node DOM/event harness
checks using the real isolated local API, not browser screenshots/Windows visual acceptance.
Nine updater safety tests passed, including new Cash-module removal on rollback.
Full compilation, JS syntax, source/runtime equality, manifest and ZIP integrity verified.
Actual browser/Windows graphics, mouse-wheel feel, native/EXE/print acceptance remain pending;
no Chromium binary was available here. Minor print/CSV PC rechecks remain user-deferred.

Cumulative backup-first updater preserves data/settings/launchers/.venv. It adds cash_quantity.py.
Hold delivery; continue further requested changes on this source rather than reverting to Update27.
