# STN search layout, scrolling and theme correction — 25 October 2026

Cumulative from STN_CN_Reference_UI_Windows_Installation.zip. This supersedes the dashboard layout described in STN_REFERENCE_DESIGN_HANDOFF.md. All billing corrections and UX phases 1–5 remain included. No deployment, live migration or original Meet-Dev changes.

## Final layout

The dashboard begins with the accepted large Verified network search panel from the user's screenshot: title and help text, category badge, persistent Seller GSTIN label, full-width input with search icon, Search seller button and decorative ring. The same SellerSearch component appears on Search sellers. Only its palette follows Classic Emerald / Navy Studio. Company membership information and workspace action cards follow the dashboard search.

Seed marketplace is removed from the dashboard. The complete marketplace, filters, requirement form, own requests/quotations, history and notification preference remain on Buy/Sell Requirements. The dashboard retains a direct action card and sidebar link to that page. The input-looking navigation link in the top chrome is removed; the actual search form is first in the dashboard content.

## Scrolling and contrast diagnosis

SellerSearch previously embedded ListFrame, a full-height component with negative margins and its own overflow area, inside a scrolling dashboard card. This created a second content scrollbar and clipped the search heading/help. It now renders its panel and result cards in normal document flow. Search sellers also opts into natural-height ReportShell content; the old forced full height caused overflowing results to consume the final page padding. Other full-height table pages retain their existing default layout. The workspace scroll area has bottom space so the last content can clear the fixed Appearance control.

The accepted search panel now has explicit, paired theme colours for heading, help, label, badge, input, placeholder, icon and enabled/disabled action. The shared form-padding rule had overridden the input's icon inset; its left padding is now explicit. Disabled/enabled Search colours switch together to prevent a low-contrast midpoint during the old colour transition. Sidebar active text and shared navigation colours are readable in both themes.

Navy Studio legacy utility colours now pair light text with dark tinted status surfaces. This covers neutral captions, blue links, green membership/approved states, amber warnings, rose disputes/errors, violet legal notices, pale overlay badges and field options. These overrides are scoped to STN; no CN styles or calculation files were changed.

## Verification

- TypeScript noEmit, targeted changed-component lint and combined Next production build pass. Full-project lint is not claimed: the workspace shell's three previously recorded set-state-in-effect findings remain outside this correction.
- Real Chromium rendered the actual WorkspaceShell, MemberDashboard, SellerSearch, ReportShell, appearance provider/control and sidebar. Backend responses and Next navigation were mocked with synthetic records. Both themes passed valid search submission, uppercase GSTIN handling, 16 result cards, empty/error states, stale-response rejection and result clearing after edits. The exact GSTIN-only endpoint, complete-GSTIN validation and private category scope are preserved.
- Search text, placeholder, category badge, enabled/disabled action and tested result status surfaces meet at least 4.5:1 measured contrast. Both pages have at most one content scroll owner, no document overflow, and reachable final content at 1440×900, 1152×720, 960×600, 720×450 and 390×844. The intermediate desktop sizes approximate browser zoom through CSS viewport size; native Windows zoom acceptance is still pending.
- Disabled dashboard search and administrator preview remain non-interactive in both themes.
- Marketplace browser regression passes multiword search, filters, kg/MT sorting, quotation quantity display, empty/reset and failure/retry at desktop/tablet/narrow widths. Eight focused search and existing trading-rule tests pass.
- All 140 protected CN baseline files match. Package comparison also verifies that no CN, integration or API source file changed in this release.

Evidence: verification/search_layout_*.txt. Reproduce from the package root after installation with:

    npx tsc --noEmit
    npm run build
    node tests/search-layout-browser.mjs
    node tests/reference-ui-browser.mjs
    node --import tsx --test tests/seed-market-search.test.ts tests/seed-trade.test.ts
    python cn/verify_baseline.py

Use NEXT_PUBLIC_COMMON_PORTAL=1 for the combined build (Windows setup configures it). Browser checks require Playwright Chromium or STN_BROWSER_EXECUTABLE. They use a single-process browser for constrained local test environments. Screenshots were inspected internally and are not packaged. No complete fresh Mongo sign-in/submission journey or native Windows acceptance is claimed. Earlier full-stack records remain historical. The original affected Billing Audit PDF/workbook verification remains separately pending.

## Run the update on Windows

Stop the old app and MongoDB cleanly. Back up the complete integration-data folder, including keys. Extract into a new app folder, copy the complete stopped integration-data folder, run Setup_Combined_Windows.bat, then Start_Local_Mongo_Windows.bat and Start_Combined_Windows.bat. Existing users must not recreate the admin. Open http://127.0.0.1:8787/portal and use existing credentials. See START_HERE_WINDOWS.md for full instructions and custom-path guidance.

Windows acceptance: compare both search pages to the supplied layout; switch themes; check input, focus, status text and dropdowns; search a real approved seller; scroll through long results to the final item; verify dashboard actions and Buy/Sell Requirements. Repeat at your usual browser zoom. Existing data, original receipt dates, separate rounding, frozen history, private ownership, permissions, storage ceilings and financial calculations remain governed by the cumulative preserved implementation.

Both delivered ZIPs contain the cumulative source and Windows scripts. Installed dependencies, build caches, browser binaries, credentials and user databases are excluded.
