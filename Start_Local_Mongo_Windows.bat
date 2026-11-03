@echo off
cd /d "%~dp0"
if not exist "runtime\tools\integration\mongo_local.mjs" goto missing
node runtime\tools\integration\mongo_local.mjs
goto end
:missing
echo Run Setup_Combined_Windows.bat first to prepare the compact runtime.
:end
pause
