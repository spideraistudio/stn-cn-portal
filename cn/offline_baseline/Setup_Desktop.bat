@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Run this only from your EXISTING working calculator installation after applying the update.
 pause
 exit /b 1
)
echo Installing the optional desktop window. Internet is needed for this one-time setup.
".venv\Scripts\python.exe" -m pip install pywebview==6.2.1
if errorlevel 1 goto failed
echo Ready. Close your browser calculator/server first, then run Start_Desktop.bat.
echo WebView2 Runtime must be installed on Windows. Existing data stays in the same folder.
pause
exit /b 0
:failed
echo Desktop setup stopped. Your existing Start_Calculator.bat remains available.
pause
exit /b 1
