UPDATE33 — WORKFLOW, CASH SHORTCUTS & WORKBOOK ATTENTION
20 October 2026. Cumulative from Update32. Windows acceptance pending.

SCOPE: User selected comparison recommendations 3, 4 and 5 only.
No new calculation explanations, zero-benefit narrative, revision comparison,
PDF diagnostics or alternative payment table are introduced in this update.

1. STEP STATUS AND NEXT ACTION
The existing five steps now show status: needs attention, complete, checks
passed, ready to review/finish, blocked or awaiting issue. These are derived
from the existing engine checks and saved status, not an employee approval.
A Next Action banner opens the relevant existing correction workflow.
Finalised/issued records route to Review & Finish and remain frozen.

2. REGULAR + CASH CONTROLS
Selected scheme cards in Select Party / Check Benefits now show whether Cash
is configured, with Configure Cash option / Edit Cash settings. This opens the
existing scheme builder directly at Benefits with Cash controls in view.
The scope notice explains that saving edits the workbook's scheme for its
active drafts. Completed calculations retain frozen settings. After saving
from this shortcut, return to the party's Check Benefits step.
Party allocation controls now say Allocate Cash quantity / Edit Cash quantity
and payment, and Remove party Cash allocation. All existing reviewed preview,
apply and removal behavior remains. No stock or payment is auto-allocated.
Cash removal still releases funding to unallocated; it does not move it to ABS.

3. WORKBOOK ATTENTION
Dashboard -> Work needing attention loads a read-only saved-work snapshot.
Filters: All, Product mapping, Ledger/party review, Payment allocation,
Calculation blocked, Ready to finish, Awaiting issue, Issued.
Open takes the employee to the current calculation's first relevant correction
or final review. One latest populated version per party/location/season is
shown, matching workbook print selection. Older versions remain in History.
Refresh attention list updates the snapshot. Stale responses after project or
workbook navigation are discarded. Deleted parties/other workbooks excluded.
Import history is separately expandable: failed and review attempts are shown
with their existing messages and Bulk Import/review links. Historical failures
may remain after successful retries; they are not counted as blocked parties.
No record, audit, setting, finalisation or issue writes occur during scanning.
No ledger balances or revised CN amounts are aggregated in the attention list.

PRESERVATION
Runtime changes only: static/app.js, static/scheme-options.js, static/style.css.
All Python modules, financial rules, settings defaults, PDF fixes, print logic,
workbook/project storage, launchers, theme/layout modules and both UI choices
remain. No database migrations, new financial fields or default-rate changes.
Updater is unchanged and backup-first. All saved data/settings are retained.

VERIFICATION
Eight existing UI/API suites passed, covering imports, workflow, allocations,
ABS, Cash, frozen histories, reporting, sharing, isolation and deletion.
Seven workbook snapshot/HTTP tests passed (read-only, frozen, deleted scope,
revision selection, missing results, stale selection and authentication).
Native Chromium: five synthetic parties, attention filters/deep links, unchanged
backup after refresh, Cash shortcut add/save/return without automatic allocations,
frozen CN Rs2000 retained, five badges, both themes and stable hover at 1366px.
No browser JS errors. Attention panel rendered and visually inspected.
Eleven updater preservation/backup/rollback checks passed.
Runtime module byte preservation and source/program parity verified.
Full Python financial suite was not rerun for these presentation-only changes;
Update32's 311-test result remains historical evidence, not a new Update33 run.
Windows/WebView2 execution and user acceptance remain pending.

INSTALL / CHECK
Close the calculator and its server console. Extract this whole ZIP, run
Update_CN.bat and select app.py from the EXISTING working calculator folder.
Reopen using your normal launcher; Ctrl+F5 if the browser shows cached UI.
Check Dashboard attention filters/Open; five-step next action; Check Benefits
Cash configuration and party allocation; one saved completed party unchanged.

RESUME
Implementation, targeted regression, native browser checks and packaging complete.
Continue cumulatively from Update33. Preserve all previous rules/features/data,
Classic Emerald and Navy Studio, saved layouts, and Update32 workbook printing.
