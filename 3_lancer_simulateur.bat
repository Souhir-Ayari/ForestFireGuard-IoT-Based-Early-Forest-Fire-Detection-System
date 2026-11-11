@echo off
REM Envoie des mesures de test au serveur : normal, puis vigilance, puis feu.
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0server"

if exist .venv\Scripts\python.exe goto start
echo Lance d'abord 1_lancer_serveur.bat
pause
exit /b

:start
.venv\Scripts\python.exe scripts\simulate_sensor.py --scenario demo
pause
