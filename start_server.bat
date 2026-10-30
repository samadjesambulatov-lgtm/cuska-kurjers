@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe goto missing
.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
pause
exit /b
:missing
echo Vispirms palaid setup.bat.
pause
