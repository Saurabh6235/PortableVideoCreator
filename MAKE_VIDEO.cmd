@echo off
rem Makes the Hinglish + English shorts from the newest topic .txt in the inbox folder (see GUIDE.md)
cd /d "%~dp0"
set CI=1
set PYTHONIOENCODING=utf-8
set HEYGEN_NO_ANALYTICS=1
py -3.12 pipeline\auto.py make %*
echo.
pause
