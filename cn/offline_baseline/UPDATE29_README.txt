UPDATE29 — OPTIONAL NAVY STUDIO — 19 October 2026

Cumulative from accepted Update28.1. Classic Emerald is still the default.
Choose Interface -> Navy Studio in the top bar. Switch back whenever you want.
The new appearance covers Dashboard, Workbooks, Parties, Ledger Audit, Year Link,
Reports, Settings, History, calculation steps, forms and dialogs.

PAYMENT STUDIO
Available Payment remains fixed in the centre. Drag each scheme, crop or product
card separately with the mouse, like moving a folder. Dragging empty space does
not move the group. Cards stop at other cards, including the central payment hub.
Clicking still opens the existing allocation editor. Dragging changes no amounts.
Arrow keys move the focused card; Shift+Arrow uses a larger step.
Use the mouse wheel to zoom and Fit diagram to show all cards.
Click Save layout after arranging cards. Reset layout restores the default;
click Save layout afterwards if you want to keep the reset. Save the calculation
first if it has not been saved yet. Layouts are separate by project, workbook and
calculation. Appearance is saved on this PC and survives changing server ports.
Classic retains its original graph, zoom and background panning.

FINANCIAL PRESERVATION
Financial engine, stores, settings defaults, PDF readers, application workflow JS,
Cash quantity logic, ABS distribution, NRV, project sharing, cleanup and deletion
modules remain byte-identical to Update28.1. No database migration is introduced.
Appearance files ui-theme.json and ui-layouts.json are kept beside the relevant
project database, separate from financial settings. They are not included in
financial JSON/.cnwork exports; an in-place update preserves them and data backup
copies made by the updater include files under data/. Never silently evicts layouts.

TESTING
293 Python tests passed in the full run (includes initial 3 appearance tests).
Final appearance changes passed 4 targeted tests, including >40 saved parties.
All 8 existing UI/API regression suites passed. All 11 updater backup/rollback
checks passed. Native Chromium 153 browser tests passed for the eight main pages,
all five calculation steps, six Settings sections, stationary hover, independent
card drag, non-overlap, repeated collision attempts, unchanged financial record,
fixed hub during zoom, saved layout after reload, Classic/Studio switching,
product inspector, print selector hiding and 1366px viewport. No page JS errors.
Financial-module byte comparison and program/source package parity are verified.
Windows-specific installer, WebView2 appearance and physical printing require
checking on your PC; these were not executed in this Linux test environment.
Update28.1 button stability was already accepted by the user on Windows.

PHASE STATUS / RESUME
1 Baseline and persistent UI selector: COMPLETE.
2 Whole-app Navy styling and offline illustrations: COMPLETE.
3 Independent draggable cards and saved layouts: COMPLETE.
4 Automated/browser verification and cumulative packaging: COMPLETE.
Next: user Windows acceptance. Do not rebuild from older updates. Continue from
this source; read PHASE_PROGRESS.md, LATEST_HANDOFF.md, STABLE_BUTTON_FIX.md and
TEST_RESULTS.txt. Preserve both themes, financial rules, saved work and settings.
