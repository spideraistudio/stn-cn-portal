# Public visitor website and registration UI — 26 October 2026

Cumulative from STN_CN_Case_Numbers_Rate_Precision_Source_Handoff (1).zip. The user confirmed that preceding update works on their Windows PC. This new public UI still requires Windows acceptance. No deployment, live migration or original Meet-Dev repository changes.

## Inspection and routing

The visitor landing page formerly described STN only. The existing registration endpoint creates a pending company application, not credentials. Approval and individual module/permission grants remain in the unified administrator action. Anonymous registration does not provide a signed-in approval-status API or public application lookup; no such lookup was introduced.

In combined mode, the gateway owns / and /portal (shared sign-in/module selection), sends /stn to the Next homepage, and redirects /login and /admin-login to /portal. /join remains the public company application. The existing /home logo route formerly returned anonymous visitors to /, which in combined mode sent them back to sign-in. It now returns anonymous combined visitors to /stn. Existing authenticated member/admin destinations and standalone anonymous / destination are preserved. Direct /stn still follows existing authenticated homepage redirects.

## Delivered changes

- Homepage: consistent STN + All Crop CN branding, explanations of both tools, applicable access/privacy wording, registration and login actions, and the application → review → credentials sequence. Unsupported marketing/security guarantees were removed from this page. Uses the accepted Classic Emerald / Navy Studio palettes.
- Registration: company, responsible contact and registered location sections; persistent labels, required fields, GSTIN/mobile/email/PIN guidance and native constraint validation; accessible completion progress and submission status. All existing companyName, gstin, category, otherCategory, responsiblePersonName, mobileNumber, email, state, district, pincode, taluka, address and website honeypot fields retain their API names. Existing LocationFields and server location validation are reused.
- Submitting disables editable fieldsets and the action, with a synchronous guard against repeated submit events. Network/non-JSON/validation/duplicate/rate-limit errors leave entered values in place and focus the feedback. Switching business category retains a typed other-category value on the current page, but omits it from agriculture requests. No sensitive form draft is saved to local storage. Values are not promised to survive closing/reloading the page.
- Success: explicit application-received / approval-pending screen, with review and manual credential steps, correction/follow-up guidance and contact/login/home actions. It reflects the successful submission in this page session; it is not a live status tracker. It does not imply immediate access or send credentials.
- Login: shared portal adds registration, pending-review guidance and public-home links, a keyboard skip link, visible focus, fixed action geometry and login-in-progress/double-submit protection. Authentication endpoints, redirects, module selection and forced-password-change behavior are unchanged. Standalone STN login also receives the public styling, and its password reveal is keyboard reachable; standalone authentication was not separately exercised end to end.
- Public footer: combined branding and readable paired text colours. Public CSS is scoped to public surfaces; member dashboard/search, Buy/Sell, financial pages and their workflows remain intact.

## Fresh verification

| Check | Result | Record |
|---|---|---|
| TypeScript / changed-source ESLint | Passed; no lint errors | verification/public_ui_typecheck.txt, public_ui_lint.txt |
| Combined Next production build | Passed; final frontend built and served by full-stack runner | verification/public_ui_build.txt; public_ui_full_stack_server.txt |
| Actual production public pages through gateway in Chromium | Passed both themes; homepage, registration, pending/success and shared login; no uncaught page errors | verification/public_ui_full_stack.txt |
| Layout/access | No horizontal document overflow at 1440×900, 1152×720, 960×600, 720×450 and 390×844 for homepage; registration also checked from 1152 down; keyboard submit/link/focus and stable hover geometry passed | same record |
| Text contrast | Measured ≥4.5:1 for tested public headings, body/help text, labels, controls, errors, links and footer after theme settles, both themes | same record |
| Error/retry UX | Invalid formats, category retention, delayed duplicate-submit guard, non-JSON and 429 failure retention/focus passed | same record; failure responses deliberately mocked |
| Real registration lifecycle | Actual browser submits application to Mongo pending, with no credentials; duplicate returns error, retains form, leaves exactly one application; actual unified platform approval grants modules; actual shared login forces password change | same record; synthetic records and disposable data only |
| Broad real-service regression | Passed shared account/role scopes, staff permissions, seed trading/privacy, case-number history/review, original PDF/CN journey, exact ₹38,561 fixture, frozen work, independent exports, accounting, revocation, restart and scoped resets | same record |
| Case-number and seed tests | 12 passed | verification/public_ui_node_tests.txt |
| Billing precision/rate regressions | 28 passed (includes inherited overlapping tests) | verification/public_ui_billing_tests.txt |
| Original financial suite | 332 run: 331 passed; one external-PDF-dependent skip | verification/public_ui_engine_tests.txt |
| Protected baseline | All 140 files match | verification/public_ui_baseline.txt |
| Archive/source integrity | Original source files retained; all API/lib/db and financial engine sources unchanged; new artifacts exclude runtime caches, private data and dependencies | verification/public_ui_package.txt |

Screenshots of both theme homepages, application form/error and pending screen were inspected internally. They are excluded from the packages. Initial browser execution required a valid local font configuration; early harness failures involved font-runtime startup, awaiting React focus effects and an already-used synthetic GSTIN. These were corrected in the test environment/harness. Contrast assertions wait for the inherited theme transition to settle. The final full-stack record is a complete passing run. CSS viewport checks approximate zoom; native Windows browser zoom is not certified.

The preceding case-number/rate precision work is retained byte-for-byte, including all financial source and stored-data contracts. This UI phase does not rerun the prior private Amreli PDF comparison, modify approved rates, migrate saved work, alter quotas or grant permissions from public requests. Earlier handoffs and verification logs remain historical.

## Windows installation and acceptance

Both release ZIPs include complete cumulative source and Windows setup/launch scripts. The Windows package installs dependencies and builds locally; it is not a standalone EXE. Read START_HERE_WINDOWS.md. Stop the existing app and MongoDB cleanly; back up the COMPLETE integration-data folder including keys; extract to a fresh app folder and copy the complete stopped data folder. Run Setup_Combined_Windows.bat, then Start_Local_Mongo_Windows.bat and Start_Combined_Windows.bat. Keep existing credentials; do not recreate the admin.

Open http://127.0.0.1:8787/home for the visitor website, /join for registration, and /portal for the shared account. Use a signed-out/private window to inspect visitor routing. A real submission creates a pending application in your own local test installation, so use deliberate test-company details.

Check both themes at your usual browser zoom: navigation and footer, stable buttons, tab/focus order, labels and dropdowns, PIN/state/district errors, retained details after duplicate/failed submissions, success/pending guidance, and company approval with chosen permissions. Verify the issued login requires password change and opens only permitted modules. Reopen existing CN work and STN records, including temporary/permanent history and billing audits. Windows acceptance of these new pages remains pending until the user tests them.

## Reproduce

After dependency installation: npx tsc --noEmit; targeted ESLint on changed TSX/route files; build with NEXT_PUBLIC_COMMON_PORTAL=1; run the three Node test files case-numbers.test.tsx, seed-market-search.test.ts and seed-trade.test.ts; run the recorded Python suites; run python cn/verify_baseline.py. Start a disposable MongoDB using STN_DISPOSABLE_MONGO=1, then python integration/full_stack_test.py. It invokes integration/browser_public.mjs against the actual production/gateway services before the existing regression journey. Chromium requires Playwright's installed browser, or CN_BROWSER_EXECUTABLE plus appropriate runtime libraries/fonts in constrained Linux environments. CN_BROWSER_SINGLE_PROCESS=1 is supported by the inherited Linux harness. No real user database is needed or modified.
