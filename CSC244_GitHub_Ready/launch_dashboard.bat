@echo off
cd /d "%~dp0"
echo CSC 244 - Multi-Agent Financial Risk Review
where py >nul 2>&1
if %errorlevel% EQU 0 (
  start "CSC 244 Local Dashboard Server" cmd /k "py -3 app.py"
) else (
  start "CSC 244 Local Dashboard Server" cmd /k "python app.py"
)
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8501"
echo Your browser should open the dashboard.
echo Leave the server terminal running while photographing it.
pause
