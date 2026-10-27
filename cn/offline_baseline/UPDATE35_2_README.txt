UPDATE35.2 - CURSOR-FOCUSED DIAGRAM ZOOM
21 October 2026. Cumulative from Update35.1. Windows acceptance pending.

CHANGE
In Payment Allocation, point at a card or diagram area and turn the mouse wheel.
Navy Studio now keeps the point under the cursor in place while zooming instead
of always zooming around the payment hub. The hub remains fixed in diagram
coordinates, but can move on screen as the view zooms towards another card.
Classic Emerald retains its existing cursor-focused scroll zoom.
Fit diagram restores the complete centred view. Reset layout also resets the
zoom focus. Dragging, collision checks, lock and saved card positions remain.
Zoom changes only the camera; it does not move individual saved cards.

INSTALL ON YOUR EXISTING WINDOWS CALCULATOR
1. Close the calculator AND its console window.
2. Extract this ENTIRE ZIP.
3. Run Update_CN.bat and select app.py in your existing working calculator folder.
4. Reopen with your normal launcher. Use Ctrl+F5 if old controls are cached.
The cumulative updater creates a safety backup and updates program files only.
Do not replace or remove your existing data folder. No earlier update is needed.

CHECK ON WINDOWS
Open Payment Allocation in Navy Studio. Point at an off-centre crop/product
card, wheel up then down: the point under the cursor should stay in place.
Try a second card, then Fit diagram. Check drag, lock and saved layout reload.
Switch to Classic Emerald and check wheel zoom and background panning.
Update35.1 remains included: Preview -> review -> Allocate usable saves;
Close/Cancel saves nothing. User Windows acceptance of both updates is pending.

PRESERVATION
Only static/studio.js, static/app.js (toolbar wording) and static/index.html
(asset refresh) changed at runtime from Update35.1. All Python/backend modules,
financial rules, receipt dates, separate CN rounding, frozen history, settings,
allocations, both interfaces and saved layout storage are unchanged. No database
migration. No online/mobile/accounts/storage-cleanup changes are included.

VERIFICATION THIS UPDATE
PASS: production Studio zoom/layout geometry harness: cursor anchors in all four
quadrants and centre, repeated zoom in/out, min/max clamps, Fit reset, redraw,
unchanged card coordinates/saved layout, Classic delegation. This is a simulated
geometry test, not a native browser or Windows test.
PASS: eight existing UI/API suites using an isolated temporary database.
PASS: thirteen updater backup/preservation/rollback tests.
PASS: two stable-control regression tests; JavaScript syntax checks.
PASS: only the three listed runtime files changed; source/program parity.
Full financial tests were not repeated because no financial module changed.
Historical Update35.1/35 test evidence remains below/in verification files.
A native Chromium download failed in this environment, so new native visual
verification was unavailable. Windows/WebView2/user acceptance remains pending.

