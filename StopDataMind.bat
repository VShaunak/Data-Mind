@echo off
title Stop Data Mind
cd /d "%~dp0"

echo ========================================================
echo   Stopping Data Mind application and background server...
echo ========================================================
echo.

if exist "backend\.venv\Scripts\python.exe" (
    "backend\.venv\Scripts\python.exe" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/shutdown', data=b'{}', timeout=1)" 2>nul
)

powershell -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"

echo.
echo Data Mind has been shut down successfully.
ping -n 3 127.0.0.1 >nul
