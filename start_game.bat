@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe goto missing
.venv\Scripts\python.exe -m client.main
if errorlevel 1 pause
exit /b
:missing
echo Vispirms palaid setup.bat.
pause
