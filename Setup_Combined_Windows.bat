@echo off
setlocal
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 goto node_missing
where npm >nul 2>nul
if errorlevel 1 goto node_missing
node -e "const [m,n]=process.versions.node.split('.').map(Number);process.exit((m===22&&n>=17)||m>=24?0:1)"
if errorlevel 1 goto node_missing
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 goto python_missing
call npm ci --ignore-scripts
if errorlevel 1 goto failed
python -m pip install -r cn\offline_baseline\requirements.txt
if errorlevel 1 goto failed
set NEXT_PUBLIC_COMMON_PORTAL=1
call npm run build
if errorlevel 1 goto failed
echo.
echo Setup complete. Read START_HERE_WINDOWS.md.
echo For an existing installation, retain the complete stopped integration-data folder.
echo For a fresh installation only, run Setup_Combined_Admin_Windows.bat once.
echo Start_Local_Mongo_Windows.bat must stay open before Start_Combined_Windows.bat.
echo Open http://127.0.0.1:8787/portal in your browser.
goto end
:node_missing
echo Install Node.js 22.17 or newer 22.x, or Node.js 24+, including npm.
echo Close and reopen this window after installing, then run setup again.
goto end
:python_missing
echo Python 3.10 or newer is required. Install it with Add Python to PATH enabled.
echo Close and reopen this window after installing, then run setup again.
goto end
:failed
echo Setup failed. Read the error above. Do not delete or recreate your saved data.
:end
pause
endlocal
