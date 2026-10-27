@echo off
setlocal
set "CN_FIX_FILE=%~f0"
powershell.exe -NoProfile -STA -Command "& ([scriptblock]::Create((Get-Content -LiteralPath $env:CN_FIX_FILE -Raw).Split([string[]]@('###'+'SCRIPT###'),[System.StringSplitOptions]::None)[1]))"
pause
exit /b
###SCRIPT###
$ErrorActionPreference = 'Stop'
function Run-PythonCheck([string]$exe, [string]$code) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $exe
    $psi.Arguments = '-c "' + $code.Replace('"','\"') + '"'
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()
    $stdout = $process.StandardOutput.ReadToEndAsync()
    $stderr = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()
    $text = $stdout.Result + $stderr.Result
    Write-Host $text
    if ($script:log) { $text | Add-Content -LiteralPath $script:log }
    return $process.ExitCode
}
try {
    Add-Type -AssemblyName System.Windows.Forms
    Write-Host 'Select app.py from your extracted calculator folder.' -ForegroundColor Cyan
    $picker = New-Object System.Windows.Forms.OpenFileDialog
    $picker.Title = 'Select app.py in the All Crop CN Calculator folder'
    $picker.Filter = 'Calculator app (app.py)|app.py'
    if ($picker.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { exit 0 }
    $appFolder = Split-Path -Parent $picker.FileName
    if (!(Test-Path (Join-Path $appFolder 'engine.py'))) { throw 'Select app.py from the calculator folder.' }
    Set-Location -LiteralPath $appFolder
    $python = Join-Path $appFolder '.venv\Scripts\python.exe'
    if (!(Test-Path -LiteralPath $python)) { throw 'The installed Python environment was not found in this folder. Select app.py from the same folder used for the repair.' }
    $script:log = Join-Path $appFolder 'CN_Start_Diagnostic.txt'
    ('Python: ' + $python) | Set-Content -LiteralPath $script:log
    Write-Host 'Checking the installed PDF reader...' -ForegroundColor Cyan
    $code = Run-PythonCheck $python "import sys; print('Python:', sys.executable); import pdfplumber; print('PDF reader ready:', pdfplumber.__version__)"
    if ($code -ne 0) {
        Write-Host 'The actual PDF-reader error is printed above. Send that text or CN_Start_Diagnostic.txt.' -ForegroundColor Yellow
        exit 1
    }
    # A different local port avoids connecting to an older calculator process.
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback,0)
    $listener.Start()
    $port = $listener.LocalEndpoint.Port
    $listener.Stop()
    $env:CN_PORT = [string]$port
    Write-Host ('Starting the calculator at http://127.0.0.1:' + $port) -ForegroundColor Green
    Write-Host 'Use the NEW browser tab that opens. Keep this window open.' -ForegroundColor Cyan
    # Run through cmd to preserve native errors as normal terminal output.
    $start = New-Object System.Diagnostics.ProcessStartInfo
    $start.FileName = $python
    $start.Arguments = '"' + (Join-Path $appFolder 'app.py') + '"'
    $start.WorkingDirectory = $appFolder
    $start.UseShellExecute = $false
    $child = [System.Diagnostics.Process]::Start($start)
    $child.WaitForExit()
    if ($child.ExitCode -ne 0) { throw ('Calculator stopped with code ' + $child.ExitCode + '. Send the error printed above.') }
} catch {
    Write-Host ($_ | Out-String) -ForegroundColor Red
    if ($script:log) { ($_ | Out-String) | Add-Content -LiteralPath $script:log }
    Write-Host 'Send the error text above or the CN_Start_Diagnostic.txt file.'
    exit 1
}
