# UX Phase 3 — billing rate trace, recorded states and save/recheck

24 October 2026. Cumulative SOURCE handoff from the attached Phase 2 ZIP. No deployment, live migration, original Meet-Dev modification or final installation release. Windows acceptance remains pending.

## Reproduction and diagnosis

No affected real-user PDF or private workbook is present in the source handoff. This phase reproduces a concrete UI path to a false rate mismatch; it does not claim to have reproduced the user's exact unseen statement.

Trace before changing behavior:

1. Authoritative statement items are reparsed from owned uploaded files or loaded from the scoped saved ledger. Printed quantity, unit, rate, amount, date and reference remain evidence.
2. The workbook catalogue supplies product identity and kg per packet; source-name packing compatibility is checked by product_mapping. Existing product/packing edits remain guarded; this phase does not relax those guards.
3. CN schemes use their own billing/billing_unit, season and states. Approved billing audit rates are stored separately in billing_audit.rates with state/product, inclusive dates and explicit unit. Saving a scheme is not approval to change an invoice audit rate.
4. Sales compare the approved rate converted using saved packing to the statement unit. Returns compare explicitly selected original printed bills, even across seasons; no FIFO/current-scheme substitution.
5. Before this fix, Add rate/Add all saved products silently set unit=packet. For 4 kg packing, entering a known ₹300/kg rate stored ₹300/packet. A correct 10-packet sale at ₹1,200/packet then showed a ₹9,000 mismatch. Explicitly saving the approved rate as ₹300/kg gives zero difference. Model regression reproduces both outcomes and verifies unchanged statement evidence and original-bill returns.
6. Saving approved rates previously discarded the displayed report without rechecking. The default run instructions then reappeared, with no persistent distinction between saved and checked.

## Delivered

- New approved-rate rows require a deliberate per-kg/per-packet selection; no default unit. Existing stored rates/units remain intact until explicitly edited. The form explains the 4 kg conversion and separates CN scheme settings from approved invoice rates.
- Audit lines show expected-rate unit, saved packing and the exact approved state/date/unit comparison basis. Return lines explicitly describe the selected-original-bill basis. Saved CN scheme rates are visible as reference only in the dialog.
- Recorded-state chooser in the approved-rate editor and its Add rows control. Choices come from the currently authorised workbook's rates, uploaded statement references, saved ledgers, workbook metadata, records and scheme states. The separate New state field appears only after choosing Enter a new state. Case/whitespace equivalents reuse recorded labels for new/edited rates; exact existing rows preserve their stored spelling. No fuzzy state merge, global-company enumeration, bulk data normalization or migration. Distinct historical misspellings remain distinct and can be reviewed explicitly.
- Save approved rates and recheck persists via the existing revision/permission checks, clears stale results and runs a fresh audit. Persistent status distinguishes successful recheck from saved-but-recheck-failed; failure leaves saved changes intact and offers the normal retry action. Manual run failure does not claim a save occurred. Source/date/include-saved fingerprints prevent an old in-flight result replacing a newer selection.
- Existing mapping save/recheck triggers a billing recheck with explicit completion status. Original-bill selections and review saves retain their existing server-returned fresh reports.

No financial formula, statement correction rule, catalogue packing guard, account schema, quota policy, original receipt date, frozen result, theme/layout, STN approval/category gate or Phase 1/2 component changed. All 140 protected Update35.2 files match. No stored states are rewritten on read. Foreign workbook/file references fail ownership checks.

## Files

Production changes: cn/backend/cn_web/billing_audit.py, native_interface.py, calculator_static/billing-audit.js.
Tests: cn/tests/test_ux_phase3.py and test_ux_phase3_ui.cjs. Existing browser_billing.cjs selectors now use the recorded-state dropdown and explicit unit. That browser harness was updated but not run in this environment (no Chromium executable installed).
Fresh evidence is verification/ux_phase3_*. Prior verification is historical. See root TEST_RESULTS.md for actual executed checks and limitations.

## Windows acceptance — pending

1. Repeat with the actual reported PDF/workbook. Record printed rate/unit, saved product packing, scheme billing/unit, approved audit rate/unit/state/period and resulting finding. Do not assume the synthetic reproduction explains every variation.
2. Test 1 kg, 3 kg and 4 kg packs, per kg and per packet, both themes. No new row should choose a unit silently. Correct only the intended approved rate/unit; save and confirm the audit refreshes.
3. Keep earlier approved periods and explicitly choose original bills for later returns. A current-season rate change must not replace the original sale's rate.
4. Select recorded states, add a genuinely new state, and test case/spacing reuse. Existing source labels and saved state rows must remain unchanged. Test a second user's workbook for isolation.
5. Test stale revision rejection, failed save and failed recheck separately. A failed save must not claim success; a saved correction with failed recheck must remain saved and clearly offer retry.
6. Reopen and confirm saved rates/reviews, mappings, schemes, receipts, frozen work and Phase 1/2 workflow. Native Windows/browser zoom and printing are not certified here.

Next: Phase 4 only, using NEW_CHAT_PHASE4.txt. Final installation ZIP after Phase 5.
