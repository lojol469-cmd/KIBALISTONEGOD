@echo off
chcp 65001 >nul 2>&1
title Téléchargement Node.js Portable

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║          📥 TÉLÉCHARGEMENT NODE.JS PORTABLE 📥             ║
echo ║                                                              ║
echo ║     Télécharge et configure Node.js portable v24.13.0       ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

set "NODE_VERSION=v24.13.0"
set "NODE_URL=https://nodejs.org/dist/%NODE_VERSION%/node-%NODE_VERSION%-win-x64.zip"
set "NODE_ZIP=node_portable.zip"
set "NODE_FOLDER=nodejs"

echo 📍 Dossier de travail: %CD%
echo.

REM Vérifier si Node.js portable existe déjà
if exist "%NODE_FOLDER%\node.exe" (
    echo ✅ Node.js portable déjà installé dans %NODE_FOLDER%\
    echo.
    "%NODE_FOLDER%\node.exe" --version
    echo.
    echo Rien à faire!
    pause
    exit /b 0
)

echo 📥 Téléchargement de Node.js %NODE_VERSION%...
echo URL: %NODE_URL%
echo.

REM Télécharger avec PowerShell
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%NODE_URL%' -OutFile '%NODE_ZIP%' -UseBasicParsing }"

if not exist "%NODE_ZIP%" (
    echo ❌ Échec du téléchargement
    pause
    exit /b 1
)

echo ✅ Téléchargement réussi
echo.
echo 📦 Extraction de l'archive...

REM Extraire avec PowerShell
powershell -Command "& { Expand-Archive -Path '%NODE_ZIP%' -DestinationPath '.' -Force }"

if errorlevel 1 (
    echo ❌ Échec de l'extraction
    del "%NODE_ZIP%"
    pause
    exit /b 1
)

echo ✅ Extraction réussie
echo.
echo 🔄 Renommage du dossier...

REM Renommer le dossier extrait
if exist "node-%NODE_VERSION%-win-x64" (
    if exist "%NODE_FOLDER%" rd /s /q "%NODE_FOLDER%"
    move "node-%NODE_VERSION%-win-x64" "%NODE_FOLDER%" >nul
)

REM Nettoyer
del "%NODE_ZIP%"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║            ✅ NODE.JS PORTABLE INSTALLÉ ✅                   ║
echo ║                                                              ║
echo ║  📁 Emplacement: %NODE_FOLDER%\                             
echo ║                                                              ║
echo ║  ✓ node.exe                                                  ║
echo ║  ✓ npm.cmd                                                   ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🧪 Test de l'installation:
"%NODE_FOLDER%\node.exe" --version
"%NODE_FOLDER%\npm.cmd" --version

echo.
echo ✅ Tout est prêt! Vous pouvez maintenant lancer l'application.
echo.
pause
