@echo off
cd /d %~dp0

echo Arrêt des processus Node.js existants...
taskkill /f /im node.exe >nul 2>&1
timeout /t 1 /nobreak > nul

echo Démarrage du serveur de licence...
start "" node license_server.js
timeout /t 10 /nobreak > nul

echo 🔐 Vérification de la licence...
python license_check.py
if errorlevel 1 goto :license_error

echo Activating environment...
call venv\Scripts\activate.bat

echo Starting all servers...
python launcher_all_servers.py

goto :end

:license_error
echo ❌ Licence invalide. Arrêt du programme.
pause
exit /b 1

:end
pause