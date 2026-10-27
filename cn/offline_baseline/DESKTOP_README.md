# Own desktop window

After applying the update to your existing working source installation:

1. Export a fresh backup and close the old calculator tabs/server/desktop window.
2. Run `Setup_Desktop.bat` once with internet. It adds pinned pywebview 6.2.1 to the existing environment.
3. Run `Start_Desktop.bat`. It starts its own maximized window through Python's windowed launcher.

The source desktop uses the existing database/data folder. It does not restore, copy or reset data.
Its WebView2 engine has no normal browser tabs or address bar. Windows WebView2 Runtime and its
OS prerequisites must be available; they are not bundled. See https://pywebview.flowrl.com/guide/web_engine.html.
The old `Start_Calculator.bat` remains available. Do not run both sessions against the same source folder.

Close requests save the current party draft through the normal API before destroying the window.
Busy operations/failed saves keep it open. Settings still require their explicit Save buttons.
Downloads are enabled; native file export, printing, calendar layout and closing/restart need PC testing.

## Separate executable

`Build_Desktop_Windows.bat` builds an isolated `.desktop-build-venv` and outputs
`dist/AllCropCNDesktop/AllCropCNDesktop.exe`. Keep its whole folder. Export a fresh backup first;
restore it into that NEW copy and retain the old folder/backup. Runtime remains required.
No compiled EXE is included. Existing `Build_Windows.bat` remains the earlier browser-mode build.
