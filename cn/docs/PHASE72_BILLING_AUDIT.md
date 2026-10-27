# Phase 7.2 — selectable Billing Rate Audit

Cumulative from the fixed Phase 7.1 release. Prior Windows acceptance and account
checks are retained. New billing-audit changes require Windows acceptance.

Ledger Audit → Add PDFs (or include saved workbook ledgers) → Approved billing
rates → Run Billing Rate Audit only. Add earlier-year PDFs to check returns.
Approved rates use state, saved product, unit and inclusive effective dates.
Add a new period when rates change; do not overwrite the old season. Overlapping
periods for the same state/product are rejected. Rates are workbook-local and
separate from schemes. Editing rates requires Edit schemes permission.

Sales compare approved rates effective on their own dates. Returns compare the
actual original bill rate, even if that original sale was incorrectly billed.
Choose / split original bills lets you assign returned quantity across invoices.
The parser has no reliable original-bill-reference field; even a single candidate
requires confirmation. No FIFO or average is treated as proof. Missing source,
unmapped products, conflicting invoice lines and unavailable rates remain flagged.
Load all earlier returns too: quantity capacity is verified only within available
evidence; unresolved prior returns are explicitly indicated. Each split is checked
individually; offsetting differences cannot cancel. Unit conversion uses confirmed
product packing; amount differences are before separately posted taxes/discounts.

Review finding saves Mistake, Approved exception or Not applicable with a reason;
it does not hide the arithmetic finding. Changed evidence/rates invalidate displayed
review status. Original-bill choices and notes require Edit ledger. Evidence is
reparsed server-side, owner/workbook scoped, revision checked and protected against
deletion. Explicit project export/import retains rates, choices, notes and sources
in a separate project. Audit never edits vouchers, allocations, schemes or CNs.

Automated evidence: verification/billing_cumulative.txt (99 tests), billing_browser.txt
(real Linux Chromium billing UI), billing_offline_browser.txt (original workflow),
and billing_package.txt. Windows acceptance is not inferred from these checks.

Back up stopped WEB data, extract the complete ZIP to a new program folder and run
Start_Web_Phase7_2_Windows.bat with your existing data path/login. No public deployment.
Windows check: enter two seasonal rates; check a wrong sale; return old-season stock
at original and new rates; choose/split original bills; save a review; restart and
reopen. Confirm existing CNs/allocations remain unchanged.
