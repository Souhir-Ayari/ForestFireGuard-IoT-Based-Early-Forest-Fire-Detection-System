@echo off
REM Verifie la connexion a Firebase : ecrit, relit puis supprime une mesure de test.
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0server"

if exist .venv\Scripts\python.exe goto start
echo Lance d'abord 1_lancer_serveur.bat
pause
exit /b

:start
.venv\Scripts\python.exe scripts\test_firebase.py
pause
