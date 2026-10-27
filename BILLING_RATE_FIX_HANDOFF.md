# Billing Rate Audit correction — 25 October 2026

Cumulative from the intact STN_CN_UX5_Windows_Installation.zip supplied in this chat. Supersedes both earlier Billing_Audit_Fix_*_Candidate.zip packages. The source-integrity limitation is resolved: all 755 intact files from the earlier partial upload match this complete archive. The authoritative current proxy.ts and all five UX phases are preserved. No history-restored runtime files are used.

Start with BILLING_RATE_FIX_HANDOFF.md and START_HERE_WINDOWS.md. Native Windows acceptance and verification with the actual affected ledger PDF/workbook remain pending. That PDF was not supplied. No deployment, live migration or original Meet-Dev changes.

## Implemented behavior

- Default report: issue category → party (with location/state) → product/packing → affected entries. All levels start collapsed. Matching entries are available under “View all checked entries”. Unchecked comparisons are separated under “Checks requiring information”; they are never presented as matches.
- Earlier printed supply rates automatically compare against returns, normalized through confirmed product/packing and kg/packet units. The same low/high decisions used by the original Ledger Audit produce “Return rate above supply” and “Mixed supply rates — review return”. Regression tests compare both implementations on identical source evidence. No original invoice, FIFO or quantity consumption is inferred. A return with one distinct earlier rate can be compared without bill selection; multiple rates above/below the return show a range and possible-excess bounds. Ambiguous return rates above the lowest but within the highest rate require explicit original-bill selection. A single-rate return below supply is separately flagged. Existing explicit splits retain independent comparisons, quantity caps and stale-evidence checks.
- Confirmed code causes: returns previously ALWAYS skipped comparison until a bill was selected; approved ALL-state rates were accepted by validation but never matched a named statement state. The latter is reproduced and fixed, with an effective state-specific rate taking precedence over explicit ALL fallback. Both causes are verified in synthetic fixtures; neither is claimed as the diagnosis of the missing user's PDF.
- Mapping, saved packing, printed/approved units, statement state, approved effective dates, saved rate/product identity and each unchecked reason are visible in the row trace. No fuzzy mapping or state inference is introduced. Missing state can be resolved through authorised source correction or a deliberately approved ALL-state rate; workbook/scheme state is not silently substituted.
- Rate save rechecks from saved values; original-bill/review saves show a persistent refreshed-findings notice. Missing-product mapping controls remain available after those saves. Failed rechecks leave saved corrections intact and clear the stale report. Existing rate/config revision checks, ownership, permissions and source fingerprints remain.

## Fresh verification

After rebasing onto the intact Phase 5 archive, 16 targeted model/HTTP tests and all three controller checks passed again; all 140 baseline hashes match. This removes the archive-recovery limitation from the earlier candidates.

- 78 focused billing/model/mapping/native calculator/ledger/frozen finish HTTP tests passed. Counts overlap inherited scenarios.
- 2 additional real-HTTP PDF/save/review/recheck tests passed, including ALL fallback, corrected-rate reclassification, review invalidation, unchanged statement evidence and permissions.
- 332 original financial tests: 331 passed, one external-PDF-dependent skip.
- 24 portal/account tests and 1 storage-ceiling test passed.
- Three actual-controller VM checks passed: 502 entries with 500 matching rows hidden by default, category/party/product disclosure, unchecked section, escaping, all-entry disclosure, fresh report replacement, saved-but-failed recheck and inherited Phase 4 audit disclosures.
- All 140 protected Update35.2 files retain their original hashes.
- Changed Python/JavaScript syntax checked; ZIP integrity/member safety and runtime parity between deliverables checked.

Evidence: verification/billing_fix_*. Browser harness selectors were adapted to open the new disclosure before clicking; no fresh Chromium, Next build or full Mongo/STN journey was executed. Prior handoff build/browser results are historical. No Windows acceptance inferred.

## Changes

cn/backend/cn_web/billing_audit.py; cn/backend/cn_web/calculator_static/billing-audit.js; cn/backend/cn_web/native_interface.py (retain mapping actions after review/match refresh); billing tests and browser harnesses; release/provenance documentation. No financial settings, original dates, CN rounding, frozen history, private ownership, quota policy, STN permission/approval code or live branch changed by this fix.

## Acceptance still required

1. Supply the reported PDF and relevant approved-rate/mapping settings, using an authorised test copy. Verify its precise cause from the trace. A source package's synthetic fixture is not the reported PDF.
2. On a backed-up separate Windows test installation, verify the category → party → product disclosure, both themes, keyboard/zoom/printing, 1/3/4 kg packing, kg/packet units, state/date boundaries, missing mapping/state and explicit ALL fallback.
3. Change an approved sale rate and save: verify a fresh mismatch or match immediately, and confirm return comparisons still use printed earlier supplies. Test mixed rates, optional/required bill selection, reviewed findings, reload, permissions and frozen work retention.

The corrected Windows installation package uses the existing source-based Setup_Combined_Windows.bat flow and requires the documented Node/Python prerequisites. It is not a standalone EXE. Both cumulative packages include the complete source, historical Git bundle/patch and Windows setup scripts. The historical integration_changes.patch and integration-history.bundle predate this fix; the packaged source files are authoritative. The two ZIP contents are identical except PACKAGE_INFO.json, which describes the intended handoff role.
