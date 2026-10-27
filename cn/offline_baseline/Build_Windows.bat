@echo off
setlocal
cd /d "%~dp0"
echo Building a SEPARATE standalone preview. Existing calculator data is not touched.
echo First build requires internet. The built app runs offline without Python.
py -3 -m venv .build-venv
if errorlevel 1 goto failed
".build-venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller==6.22.3
if errorlevel 1 goto failed
".build-venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onedir --console --name AllCropCN --collect-all pdfplumber --collect-all pypdfium2 --add-data "static;static" --add-data "fixtures/ashapura.pdf;fixtures" app.py
if errorlevel 1 goto failed
echo.
echo Build ready: dist\AllCropCN\AllCropCN.exe
echo Keep the WHOLE AllCropCN folder together. Test with a backup in this separate folder.
echo Your existing launcher and databases have not been moved.
pause
exit /b 0
:failed
echo Build stopped. Your existing calculator has not been changed.
pause
exit /b 1
