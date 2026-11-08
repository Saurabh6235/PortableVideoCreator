@echo off
rem Checks that every tool the pipeline needs is installed and signed in (changes nothing)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup\install.ps1" -CheckOnly
echo.
pause
