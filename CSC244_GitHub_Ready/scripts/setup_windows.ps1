# Run from the repository root: powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..'))
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) { $cmd = 'py'; $prefix = @('-3') }
else { $cmd = 'python'; $prefix = @() }
Write-Host 'Checking Python...'
& $cmd @prefix --version
if ($LASTEXITCODE -ne 0) { throw 'Python 3.9+ is required.' }
Write-Host 'Running all tests...'
& $cmd @prefix scripts/run_tests.py
if ($LASTEXITCODE -ne 0) { throw 'Tests failed. Fix them before demo.' }
Write-Host 'Starting dashboard at http://127.0.0.1:8501 (Ctrl+C to stop)'
& $cmd @prefix app.py
