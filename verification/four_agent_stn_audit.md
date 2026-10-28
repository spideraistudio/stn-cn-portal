# STN audit — 28 October 2026

Scope: separate source copy and disposable local testing. No live data, GitHub changes or deployment.

- `node --import tsx --test tests/seed-trade.test.ts tests/seed-market-search.test.ts tests/case-numbers.test.tsx`: 12 passed, none failed/skipped. Raw record: verification/four_agent_stn_rules.txt.
- Covers search/filter/sort behavior, approved company state scope, own-request quote rejection, anonymous owner hiding, quantity conversions, deadlines, quotation validity and case-number history tests.
- Reviewed member API membership/category/password-change gates and coordinated full-stack coverage for ownership, grants, module revocation, seed request → quotation → selection/contact exchange → history.
- Expanded `integration/browser_stn_navigation.cjs` to 19 member/admin pages and 7 legacy aliases in each of Classic Emerald and Navy Studio. Checks HTTP success, expected destinations, theme, error-page content and uncaught browser errors.
- Browser script syntax passed. Runtime browser result must be taken from the root-coordinated full-stack log; this independent agent does not claim it passed before that run completes.
- Browser harness excludes Chromium `--single-process`, avoiding context-close crashes observed in the prior interrupted run. Opaque-origin localStorage access is guarded. Web security remains enabled.

No additional STN implementation defect confirmed by this independent review. This audit is not an exhaustive security certification. Windows acceptance and production hosting remain pending.
