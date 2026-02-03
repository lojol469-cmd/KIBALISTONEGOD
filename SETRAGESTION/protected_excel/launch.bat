@echo off
echo Arrêt des processus Node.js existants...
taskkill /f /im node.exe >nul 2>&1
timeout /t 1 /nobreak > nul

echo Démarrage du serveur de licence...
cd /d "%~dp0"
start "" node license_server.js
timeout /t 10 /nobreak > nul
echo Démarrage du logiciel de gestion...
start "" "dist\launch.exe"
echo Logiciel et serveur de licence démarrés. Vous pouvez fermer cette fenêtre.