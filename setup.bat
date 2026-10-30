@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Gatavs. Palaid start_server.bat un pēc tam start_game.bat.
pause
exit /b 0
:failed
echo Uzstādīšana neizdevās. Instalē Python 3.11 vai jaunāku un atzīmē Add Python to PATH.
pause
exit /b 1
