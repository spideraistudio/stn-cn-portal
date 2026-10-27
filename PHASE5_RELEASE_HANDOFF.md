# UX Phase 5 — unified appearance and Windows installation package

25 October 2026. Cumulative from STN_CN_UX_Phase4_Source_Handoff.zip. All five UX phases implemented. Final local-PC installation package and complete source are supplied; native Windows acceptance remains pending. No deployment, live migration, remote push or original Meet-Dev modification.

## Appearance

- Portal, Account & Settings and combined STN now offer Classic Emerald / Navy Studio. Combined STN admin/member routes no longer force light mode. Standalone STN retains its prior light/dark behavior.
- Shared browser-local key `stn-cn-theme` contains only `classic` or `studio`. The same local address shares the choice across portal, STN and CN. Native CN keeps its accepted layout, diagrams, controls and existing user-preference endpoint. A browser-local choice takes precedence on entry; without one, CN can load its saved server preference. CN's own selector still saves that preference, and only a successful save publishes the browser-local choice. No account/financial write is added by the portal/STN appearance control.
- Shared tokens cover backgrounds, text, forms, borders, buttons, sidebar and key legacy STN surfaces. Both theme screenshots were inspected with synthetic data; a hard-coded light dashboard surface causing low Navy contrast was corrected. Logo/semantic status colours remain. CN billing's include-saved checkbox was aligned with its label without changing behavior.
- Source changes are limited to theme assets, their static/gateway allowlists, static page inclusion, CN appearance bridge, Next theme provider/toggle/layout, Windows setup and test/docs. No protected engine, financial settings, receipt, frozen history, ownership, permission, STN approval/category or storage-policy code changed.

## Packaging and setup

Read START_HERE_WINDOWS.md before installation. The final Windows ZIP is source-based with setup/launch scripts, not a standalone EXE. Node.js, Python and internet are needed for first installation/Mongo download. It excludes installed dependencies, Linux browser/build output, test databases and secret files. The complete cumulative source handoff is also supplied separately.

Setup_Combined_Windows.bat now checks Node/Python prerequisites, installs locked dependencies and builds the combined UI. It no longer requires installing Playwright browsers for ordinary use. Existing Mongo, admin and app launchers remain. Back up the complete stopped integration-data folder and keys together; never bootstrap a second admin for existing data. No automated data migration is included.

## Executed verification

See TEST_RESULTS.md and verification/ux_phase5_* for results. Actual disposable MongoDB/SQLite/Python gateway/Next/Chromium combined journey passed: signup approval, scoped resets, effective viewport sizes, shared login/module switching, both appearance selections, seed trading, seller report/search, exact ₹38,561 CN fixture, source PDF workflow, private ownership including denial to platform admin, frozen history, export/import, separate accounting, revocation, restart and logout.

New Chromium check passed Phase 4 category/party/finding disclosure, keyboard-reviewed disclosure, mark/reopen, unchanged voucher evidence, exports including reviewed findings and both CN themes. Existing billing, direct audit mapping and original five-step/Year Link/restart browser journeys passed. Source baseline: all 140 protected files unchanged. Production build, TypeScript and changed-file ESLint passed. Original financial tests: 332 run, 331 passed, one external-PDF-dependent skip.

The complete CN HTTP suite initially ran 118 tests: 117 passed, one old form-inventory assertion failed because it predated the already-present combined STN/CN access checkboxes. Only the expected create-user fields were corrected; the failing test passed in a targeted rerun. The original failure log remains retained. No application validation was weakened.

Browser extraction first failed on unsupported archive chown in this Linux environment; the same bundled Chromium/fonts were extracted without applying archive ownership. No browser security bypass was enabled. Internal screenshots contain synthetic data and are not included in the deliverables.

## Remaining acceptance and boundaries

- Actual Windows install/start/stop, native browser zoom/keyboard/printing and the user's real saved-data copy remain unaccepted until the user tests them.
- The actual PDF/workbook from the Phase 3 billing complaint was not supplied. The explicit kg/packet mismatch path was reproduced and fixed, but that unseen case remains to be verified.
- Full browser checks cover the recorded synthetic journeys, not exhaustive every inherited STN moderation/legal/governance route.
- No live legacy STN account/database migration or production backup recovery was rehearsed. Hosting, TLS, production supervision, concurrency/capacity and cutover remain a separate authorised project.

Use the Windows acceptance checklist in START_HERE_WINDOWS.md and retain all earlier financial rules. Report failures with the exact screen/action/error and synthetic or authorised evidence; do not delete/recreate accounts or overwrite saved databases as a workaround.
