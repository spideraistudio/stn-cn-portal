# STN interface and quotation form update — 25 October 2026

Cumulative from the corrected Billing Audit installation. Preserves all five UX phases, the billing fixes, existing CN engine, data ownership, permissions and storage rules. No deployment or database migration.

STN now uses the shared Emerald/Navy palette with a layered workspace background, rounded translucent headers, larger page titles, improved forms/tables, a dashboard welcome panel and icon action cards. Hover feedback stays in place. Entry animation is short and respects reduced motion. Page descriptions can wrap instead of being truncated.

The supplier quotation form has 21 persistent, associated field labels and four numbered sections: Product & quantity, Price & quality, Delivery & payment, Reports & validity. Date and unit meanings remain visible after entry. Saving disables the submit button and displays progress; network errors preserve entries and explain how to retry. Positive price/quantity and nonnegative integer credit-day constraints supplement existing server validation. No quotation field name, payload, supplier privacy rule, approval or contact-sharing rule changed.

Validation: TypeScript noEmit and combined production build passed; actual React markup rendered and all 21 named fields checked for label association; five seed-trading rule tests passed; all 140 protected baseline files match. Evidence: verification/stn_ui_*. Chromium could not remain running in this environment; the unsuccessful browser attempt is retained. Visual/interactive Windows acceptance is pending. These checks do not claim end-to-end quote submission, moderation or all admin routes were tested.

Windows acceptance: back up the stopped integration-data folder and keys; use the existing setup instructions. Test member/admin screens in Classic Emerald and Navy Studio, keyboard focus, narrow windows, quotation entry/revision, submission failure/retry, required dates and price units. Keep accepted quotations locked and verify buyer/supplier permissions. The actual affected billing PDF remains to be verified separately.

Changed application files: app/globals.css, components/workspace-shell.tsx, components/member-dashboard.tsx, components/seed-trading-detail.tsx. No changes to financial or backend business logic.
