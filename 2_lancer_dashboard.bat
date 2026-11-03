@echo off
REM Lance le dashboard React. La premiere fois, installe les dependances.
cd /d "%~dp0dashboard"

if exist node_modules goto start
echo === Premiere fois : installation du dashboard, patiente quelques minutes ===
call npm install
if errorlevel 1 goto error

:start
echo.
echo === Dashboard lance : http://localhost:5173  -  NE PAS FERMER CETTE FENETRE ===
echo.
call npm run dev -- --open
pause
exit /b

:error
echo.
echo ERREUR : verifie que Node.js est installe (https://nodejs.org, version LTS).
pause
