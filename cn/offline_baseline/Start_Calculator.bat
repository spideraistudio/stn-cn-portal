@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo The calculator Python environment was not found. Use Start_CN_Fixed.bat.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -c "import pdfplumber; print('PDF reader ready')"
if errorlevel 1 (
 echo Please send the error shown above.
 pause
 exit /b 1
)
for /f "delims=" %%P in ('powershell.exe -NoProfile -Command "$l=[System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback,0);$l.Start();$l.LocalEndpoint.Port;$l.Stop()"') do set "CN_PORT=%%P"
".venv\Scripts\python.exe" app.py
pause
