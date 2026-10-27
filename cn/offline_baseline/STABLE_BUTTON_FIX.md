UPDATE28.1 — STABLE BUTTONS (2026-10-17)

Fixes the hover/press movement reported in the user's recording. A generic button hover transform replaced the radial diagram's centering transform, making the target move outside the cursor and snap back repeatedly. Removed button-box hover/press translations and scaling, including the sidebar nudge and reduced-motion override that displaced radial nodes. Hover color, border and glow feedback remain. Wheel zoom and drag-to-pan remain available.

Apply: close the calculator and its running console, extract this ZIP, run Update_CN.bat, select app.py from the existing calculator folder, then reopen normally. For an already-open browser tab, reload with Ctrl+F5.

This is the complete cumulative Update28 with the stable-button correction. The runtime change from the delivered Update28 is static/style.css only. Financial calculations, database handling, imports, allocation behavior and sharing code are unchanged.

Verification: the stylesheet from the delivered ZIP fails the stationary-control regression check; the corrected stylesheet passes. Two targeted CSS regression checks and the allocation/payment plus calendar/native-close UI/API suites pass. The prior full 288 Python tests, 8 UI/API suites and 11 updater checks remain documented. The updater checks are repeated for this package. No native browser executable is available here, so final Windows hover/click visual acceptance remains for the user.
