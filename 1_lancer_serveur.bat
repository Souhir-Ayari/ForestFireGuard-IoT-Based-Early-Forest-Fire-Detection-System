@echo off
REM Lance le serveur FastAPI. La premiere fois, installe aussi tout ce qu'il faut.
cd /d "%~dp0server"

if exist .venv\Scripts\uvicorn.exe goto start
echo === Premiere fois : installation du serveur, patiente quelques minutes ===
python -m venv .venv
if errorlevel 1 goto error
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error

:start
if not exist .env copy .env.example .env
if not exist ml\model.joblib .venv\Scripts\python.exe ml\train_model.py
echo.
echo === Serveur lance : http://localhost:8000/docs  -  NE PAS FERMER CETTE FENETRE ===
echo.
.venv\Scripts\uvicorn.exe app.main:app --reload
pause
exit /b

:error
echo.
echo ERREUR : verifie que Python est installe et coche "Add python.exe to PATH".
pause
