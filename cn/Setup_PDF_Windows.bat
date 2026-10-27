@echo off
cd /d "%~dp0"
python -m pip install -r offline_baseline\requirements.txt
if errorlevel 1 (
  echo PDF setup failed. Review the message above.
) else (
  python -c "import pdfplumber; print('PDF reader ready:', pdfplumber.__version__)"
)
pause
