@echo off
rem Writes only the script (videos\<slug>\script.json) from the newest topic .txt in the inbox, so you can read/edit it first
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
py -3.12 pipeline\auto.py write %*
echo.
pause
