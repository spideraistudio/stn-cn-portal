# UX Phase 4 — category-first ledger audit

24 October 2026. Cumulative SOURCE handoff from Phase 3. User requested Phase 4 in the same chat. No deployment, live migration, original Meet-Dev modification or final installation release. Windows acceptance remains pending.

## Delivered

- Ledger Audit now begins its results with period/party/voucher totals and pending versus reviewed counts, followed by collapsed finding-category cards. CN/NRV tables no longer precede the categories.
- Each category displays total findings, distinct parties (name/location/state), pending count and reviewed/not-applicable count. Expand the category, then a party group, then a finding to inspect its original evidence and review controls. Cross-party findings remain one finding containing all affected parties, never split or double-counted.
- Reviewed/not-applicable findings live in their own collapsed section within the category. Original reasons, timestamps, vouchers and View / change review remain available. Reopen for Review returns the finding to the pending group through the existing server operation. Empty/all-reviewed categories have explicit messages.
- Saved bulk-import findings use the same category/party/reviewed presentation and retain filename, season and checking-period context. Historical import occurrences are counted as historical findings, not silently deduplicated. Identical party names at different locations count separately.
- CN given/realised net rate remains available in a collapsed CN/NRV section. Its heading shows unmapped product and pending-CN-classification counts; direct mapping links inside it still work. Posted credits, freight/journal exclusions, stock timing, warnings and checking notes remain available. Coverage-warning counts are visible above the category cards.
- Native details/summary controls support keyboard disclosure. Focus styles and small-viewport layout use the existing Emerald/Navy theme colours. All categories, parties, individual findings and reviewed groups start collapsed; expansion state is transient and resets on rerender/workbook change.
- Billing Rate Audit remains an independent panel and operation with all Phase 3 state/unit/source-trace and save/recheck behavior unchanged. Phase 4 does not regroup billing rows or combine billing counts with ledger/CN/NRV counts.

## Implementation and preserved behavior

New presentation-only assets: cn/backend/cn_web/calculator_static/audit-categories.js and audit-categories.css. index.html loads them after the existing audit mapping adapter and before the independent billing adapter. Both the CN static allowlist (http_app.py) and combined gateway (integration/run_local.py) route the assets; a real-HTTP test exercises the gateway with no STN server available, proving no asset fallthrough.

No financial/audit detection algorithm, review identity, review save/reopen API, export payload, database schema, saved state, permission, storage rule or protected engine file changed. The existing review lookup uses exact evidence-derived review IDs; changed source/period cannot be hidden under a prior review. The existing finding/voucher renderers are reused, and grouping does not mutate report data. Export still contains all findings and current review dispositions, including collapsed items.

Tests: cn/tests/test_ux_phase4_ui.cjs and test_ux_phase4_http.py. The existing browser_audit_mapping.cjs now opens the CN/NRV disclosure before clicking an unmapped product. This browser harness was updated but not executed here because no Chromium executable is installed. No new Next/Mongo full-stack browser run or visual acceptance is claimed.

## Verification

See TEST_RESULTS.md and verification/ux_phase4_* for fresh executed evidence. Tests cover grouping/counts, escaping, closed disclosures, empty/all-reviewed groups, multi-party/location/import cases, no report mutation, actual gateway asset delivery, owned audit review/save/reopen, stale and foreign review rejection, preserved evidence, Phase 3 rates/states and original-bill comparisons, audit mapping, Phase 1/2 checks and storage ceilings. Protected baseline hashes remain identical.

An initial test harness attempted native-state as POST rather than the supported GET state read. The harness was corrected; application behavior was not relaxed.

## Windows acceptance — pending

1. Import a combined PDF and Run Ledger Checks. Confirm categories/counts appear before party or CN/NRV tables. Expand category → party → finding and inspect every voucher.
2. Mark one finding Not Applicable with a reason. Confirm pending decreases, reviewed increases, and the item moves to the collapsed reviewed section. Open it, verify its reason/evidence, and reopen it for review.
3. Repeat for multiple parties, identical names at different locations, cross-party duplicates and saved bulk-import histories. Keep historical occurrences visible with their period/file context.
4. Export while disclosures are closed; confirm reviewed and pending findings are both included. Recheck after source/period changes; stale review must not suppress a changed finding.
5. Expand CN/NRV, map an unmapped product and save/recheck. Verify original statement data, freight exclusions and NRV calculations are unchanged. Billing-only checking remains separate.
6. Check keyboard Enter/Space focus, Classic Emerald/Navy Studio, narrow desktop windows and Windows browser zoom. Check Phase 1/2 account flow and Phase 3 rate/unit/state flow.

The actual reported Phase 3 billing PDF/workbook was not supplied and remains pending alongside Windows acceptance. Continue with Phase 5 only using NEW_CHAT_PHASE5.txt. Final installation ZIP after Phase 5; no public deployment.
