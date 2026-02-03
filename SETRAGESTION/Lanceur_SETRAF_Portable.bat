@echo off
chcp 65001 >nul

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║                🚀 APPLICATION SETRAF 2026 🚀                 ║
echo ║                      VERSION PORTABLE                        ║
echo ║                                                              ║
echo ║              Système de Gestion des Risques                  ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM ===== DÉTECTION DE PYTHON =====
echo 🔍 Détection de Python...

REM 1. Chercher Python portable dans protected_excel
set "PYTHON_PORTABLE=%~dp0protected_excel\python311\python.exe"
if exist "%PYTHON_PORTABLE%" (
    echo ✅ Python portable trouvé: protected_excel\python311\python.exe
    set "PYTHON_CMD=%PYTHON_PORTABLE%"
    goto :python_found
)

REM 2. Chercher Python portable à la racine
set "PYTHON_PORTABLE=%~dp0python311\python.exe"
if exist "%PYTHON_PORTABLE%" (
    echo ✅ Python portable trouvé: python311\python.exe
    set "PYTHON_CMD=%PYTHON_PORTABLE%"
    goto :python_found
)

REM 3. Chercher Python portable dans le dossier parent
set "PYTHON_PORTABLE=%~dp0..\python311\python.exe"
if exist "%PYTHON_PORTABLE%" (
    echo ✅ Python portable trouvé: ..\python311\python.exe
    set "PYTHON_CMD=%PYTHON_PORTABLE%"
    goto :python_found
)

REM 4. Utiliser Python système
python --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ Python système trouvé
    set "PYTHON_CMD=python"
    goto :python_found
)

REM Aucun Python trouvé
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ❌ PYTHON NON DISPONIBLE ❌                     ║
echo ║                                                              ║
echo ║  Aucune installation Python n'a été trouvée.                ║
echo ║                                                              ║
echo ║  Solutions:                                                  ║
echo ║  1. Copiez le dossier python311 à la racine                 ║
echo ║  2. Installez Python depuis python.org                      ║
echo ║  3. Ajoutez Python au PATH système                          ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
exit /b 1

:python_found
:python_found
echo.

REM Changer vers le dossier protected_excel
cd /d "%~dp0protected_excel"

REM ===== PAS DE VENV AVEC PYTHON PORTABLE =====
REM Si on utilise Python portable, on n'a pas besoin de venv
REM Les dépendances sont déjà installées dans Python portable

echo.
echo 🔐 Vérification de la licence en cours...
echo.

"%PYTHON_CMD%" license_check.py
if errorlevel 1 (
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║                                                              ║
    echo ║             ⚠️  LICENCE NON VALIDEE ⚠️                       ║
    echo ║                                                              ║
    echo ║  Démarrage du serveur de demande de licence...              ║
    echo ║                                                              ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo 🚀 Lancement du serveur pour obtenir une licence...
    echo.
    echo 📝 Instructions :
    echo    1. Le serveur de licence va démarrer
    echo    2. Ouvrez votre navigateur : http://localhost:4000
    echo    3. Remplissez le formulaire pour obtenir votre licence
    echo    4. Vérifiez votre email pour le code OTP
    echo    5. Redémarrez l'application après activation
    echo.
    "%PYTHON_CMD%" launcher_license_server_only.py
    pause
    exit /b 0
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║                   ✅ LICENCE VALIDEE ✅                      ║
echo ║                                                              ║
echo ║                Démarrage de l'application...                 ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝

echo.
echo 🚀 Démarrage de l'application Streamlit et serveurs...
"%PYTHON_CMD%" launcher_all_servers.py

goto :end

:env_error
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ❌ ERREUR PYTHON ❌                             ║
echo ║                                                              ║
echo ║  Impossible d'utiliser Python.                              ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
exit /b 1

:end
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ✅ APPLICATION DEMARREE ✅                     ║
echo ║                                                              ║
echo ║  Vous pouvez maintenant utiliser SETRAF dans votre          ║
echo ║  navigateur web.                                            ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
