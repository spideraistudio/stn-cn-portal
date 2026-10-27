@echo off
setlocal
cd /d "%~dp0"
echo All Crop CN Calculator - Complete Update35.1
echo This installs dependencies in THIS folder only. Existing installations are untouched.
echo Internet is required for first setup. Python must already be installed.
echo.
if not exist "app.py" goto missing
if exist ".venv\Scripts\python.exe" goto dependencies
py -3 -c "import sys; assert sys.version_info >= (3,10)" >nul 2>&1
if not errorlevel 1 goto use_py
python -c "import sys; assert sys.version_info >= (3,10)" >nul 2>&1
if not errorlevel 1 goto use_python
echo Python 3.10 or newer was not found.
echo Install Python for Windows with the Python launcher, then run Install_CN.bat again.
goto failed
:use_py
py -3 -m venv .venv
if errorlevel 1 goto failed
goto dependencies
:use_python
python -m venv .venv
if errorlevel 1 goto failed
:dependencies
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -c "import pdfplumber; import sqlite3; print('PDF reader and database ready')"
if errorlevel 1 goto failed
echo.
echo Setup complete. Double-click Start_Calculator.bat to open the calculator.
echo To continue existing work, first export a full backup from your OLD calculator,
echo then restore that backup into this NEW copy. See START_HERE.txt.
echo Optional own-window mode: Setup_Desktop.bat once, then Start_Desktop.bat.
pause
exit /b 0
:missing
echo Extract the WHOLE ZIP first. Do not run setup from inside the ZIP.
:failed
echo Setup stopped. Review the error above. Your other calculator folders are unchanged.
pause
exit /b 1
