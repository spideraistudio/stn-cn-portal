# Standalone Windows preview

The delivered ZIP contains source and build tools, not a compiled Windows EXE.
On Windows with Python installed, double-click Build_Windows.bat. The first build
needs internet to install build dependencies in a separate .build-venv. The working
.venv and Start_CN_Fixed.bat are untouched. Build output is dist/AllCropCN.

Keep the complete AllCropCN folder together, in a writable location such as Documents.
Run AllCropCN.exe; the local browser interface opens. Keep its console open while
working. The built app bundles Python/PDF dependencies and uses no internet at runtime.
Databases belong in data beside AllCropCN.exe, outside _internal. Never put it under
Program Files or copy only the EXE. Each launch selects a free local port; open only
one instance per data folder, and close the old instance before relaunching.

Migration test: export a fresh all-workbook backup from the existing calculator;
start the standalone preview in its separate folder and restore the backup there.
Check all workbooks/settings, source dates, allocations, frozen/issued histories,
PDF import, audit, year link, print and backup after restart. Keep the original app
and backup until these checks pass. Restore replaces the TEST copy's data.
Do not merge or copy a single private-workbook SQLite file into a different manifest.

Windows compilation, offline-on-a-clean-PC testing and visual acceptance remain pending.
This is an unsigned preview, not an installer or a certified standalone release.
