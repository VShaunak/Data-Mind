@echo off
title Data Mind - Autonomous AI Data Analyst
cd /d "%~dp0"

echo ========================================================
echo   Data Mind: Think Data. Discover Intelligence.
echo ========================================================
echo.
echo Launching Data Mind desktop application...
echo.

if exist "backend\.venv\Scripts\python.exe" (
    start "" "backend\.venv\Scripts\python.exe" "desktop\launch_desktop.py"
) else (
    start "" python "desktop\launch_desktop.py"
)

exit

