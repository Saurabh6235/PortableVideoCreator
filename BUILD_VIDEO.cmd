@echo off
rem Builds the video from an existing script: BUILD_VIDEO.cmd <slug>   (slug = folder name inside videos\)
cd /d "%~dp0"
set CI=1
set PYTHONIOENCODING=utf-8
set HEYGEN_NO_ANALYTICS=1
set SLUG=%1
if "%SLUG%"=="" set /p SLUG=Video folder name inside videos\ (slug): 
py -3.12 pipeline\auto.py build %SLUG%
echo.
pause
