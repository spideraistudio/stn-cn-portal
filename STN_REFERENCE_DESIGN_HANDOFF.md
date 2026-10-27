# STN reference design and search — 25 October 2026

Cumulative release from STN_CN_Unified_UI_Windows_Installation.zip. Read this handoff before the older phase records. All five UX phases, billing audit corrections, quotation labels and Windows launch scripts remain included. No deployment, live migration or original Meet-Dev changes.

## Phase 1 — shared visual design: complete

Reference-led agriculture dashboard and seed marketplace: navy navigation, emerald actions, illustrated welcome area, crop artwork, real-data metric cards, clear request cards and a quotation guide. Consistent spacing, rounded panels and responsive layouts use the shared Classic Emerald / Navy Studio themes. Shared STN headers, forms, buttons and table styling retain the previous update. Other membership categories retain their existing dashboard workflow.

The artwork is decorative inline SVG. There are no external image requests. Production displays authenticated API data; synthetic records exist only in tests. A quote starts from a particular requirement so the required buyer terms and original request link remain intact. The design photo is a visual reference, not a literal copy of its example figures or shortcut form.

## Phase 2 — search and navigation: complete

Browse requirements, My requests, My quotations and History have distinct views. Search supports multiple case-insensitive words across visible crop, segment, description, buyer and delivery location. Crop, delivery-state and seed-type filters combine with newest, deadline and normalized kg/MT quantity sorting. Counts, clear/reset controls, empty results, 12-at-a-time Show more and load-error retry states are explicit. Published requests past the deadline show Deadline passed. My published requests includes expired published requests, which the buyer may still manage; eligible supplier browsing remains server-scoped.

Seller trust search retains the complete 15-character GSTIN rule and existing permissions. Editing the GSTIN clears the preceding result; an old in-flight response cannot populate the edited query. No partial seller directory or additional private search endpoint was introduced. Anonymous buyer names are still masked by the existing backend before search.

## Phase 3 — verification and packaging: complete; Windows acceptance pending

- TypeScript noEmit and combined Next production build passed. Targeted lint passed for the new marketplace/search files and changed member page, art, seller search and sidebar. The wider workspace shell retains three pre-existing set-state-in-effect lint errors outside this change; full-project lint is not claimed.
- Eight focused search and existing seed-trading rule tests passed.
- Real Chromium mounted the actual React marketplace with mocked API responses and production CSS. Both themes passed multiword search, location filters, quantity sorting, quotation history rendering, empty/reset, load failure/retry and width checks at 1440, 800 and 390 pixels. No uncaught page errors. The quotation card type is derived from the history endpoint's return type (offeredQuantity), not the raw quotation storage type (quantity).
- All 140 protected CN baseline files match. This update changes no CN financial files, server routes, database rules, statement evidence, receipt dates, separate rounding, frozen history, ownership, permissions or storage limits.

Evidence: verification/reference_ui_*. Browser checks are component-level with synthetic data, not a fresh complete Mongo/SQLite sign-in/submission journey. Previous full-stack records remain historical evidence. Browser screenshots were inspected internally and are not packaged. The reported real billing PDF case and native Windows acceptance remain pending.

Reproduce focused checks from the package root after installing dependencies:

    npx tsc --noEmit
    npm run build
    node --import tsx --test tests/seed-market-search.test.ts tests/seed-trade.test.ts
    node tests/reference-ui-browser.mjs
    python cn/verify_baseline.py

Build with NEXT_PUBLIC_COMMON_PORTAL=1 for the combined edition (Windows setup/launcher configures combined mode). The browser check requires an installed Playwright Chromium or STN_BROWSER_EXECUTABLE pointing to a compatible local Chromium. It uses a single-process browser for constrained test environments.

## Windows acceptance

Use START_HERE_WINDOWS.md. Preserve the complete stopped integration-data folder and its keys. Extract into a new app folder, run Setup_Combined_Windows.bat, then Start_Local_Mongo_Windows.bat and Start_Combined_Windows.bat. Existing users must not recreate the admin.

Check both themes, navigation, keyboard focus, search/filter/reset, empty/error states, long company names and narrow/zoomed windows. Use your actual member data to open/create requirements and submit/revise quotations; confirm the 21 persistent quote labels and read-only accepted quotations. Check supplier-state/anonymous access and seller GSTIN search. Verify existing CN workbooks and the reported billing case separately. Keep the prior folder as rollback.

Both deliverables contain the cumulative source and Windows setup scripts. Neither is a standalone EXE or includes installed dependencies, browser binaries, credentials or user databases.
