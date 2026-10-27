@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
 echo Run this from your EXISTING working calculator installation after applying the update.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -c "import webview" >nul 2>nul
if errorlevel 1 (
 echo Run Setup_Desktop.bat once, then open Start_Desktop.bat again.
 pause
 exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "%~dp0desktop_app.py"
exit /b 0
