@echo off
setlocal
cd /d "%~dp0"
echo Building a separate DESKTOP-window executable. Existing data is not moved.
py -3 -m venv .desktop-build-venv
if errorlevel 1 goto failed
".desktop-build-venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller==6.22.3 pywebview==6.2.1
if errorlevel 1 goto failed
".desktop-build-venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onedir --windowed --name AllCropCNDesktop --icon "static\app.ico" --collect-all webview --collect-all pdfplumber --collect-all pypdfium2 --add-data "static;static" --add-data "fixtures/ashapura.pdf;fixtures" desktop_app.py
if errorlevel 1 goto failed
echo Ready: dist\AllCropCNDesktop\AllCropCNDesktop.exe
echo Keep the WHOLE folder. WebView2 Runtime is required. Restore a fresh backup into this separate copy.
pause
exit /b 0
:failed
echo Build stopped. Existing app and data were not changed.
pause
exit /b 1
