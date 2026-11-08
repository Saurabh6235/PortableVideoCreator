@echo off
rem One-click installer for the Merit Mantra video pipeline (see GUIDE.md)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup\install.ps1"
echo.
pause
