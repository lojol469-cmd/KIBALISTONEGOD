@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║        📦 PRÉPARATION DU PACKAGE PORTABLE SETRAF 📦         ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo 🔍 Vérification de l'environnement...
echo.

REM Vérifier que Python est disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas disponible
    pause
    exit /b 1
)

REM Vérifier que python311 existe LOCALEMENT ou au niveau parent
if exist "python311\python.exe" (
    echo ✅ Python311 trouvé localement: protected_excel\python311\
) else if exist "..\python311\python.exe" (
    echo ⚠️  Dossier python311 trouvé au niveau parent
    echo    Considérez de le copier dans protected_excel\ pour une meilleure portabilité
) else if exist "..\..\python311\python.exe" (
    echo ⚠️  Dossier python311 trouvé deux niveaux au-dessus
    echo    Considérez de le copier dans protected_excel\ pour une meilleure portabilité
) else (
    echo ⚠️  Dossier python311 non trouvé
    echo    Chemin attendu: protected_excel\python311\
    echo.
    set /p "CONTINUE=Continuer quand même ? (o/n): "
    if /i not "%CONTINUE%"=="o" exit /b 0
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              🔧 ÉTAPE 1: CONFIGURATION LICENCE               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo Configuration de la licence en mode PORTABLE...
python -c "import os; open('license_config.py', 'w', encoding='utf-8').write('''#!/usr/bin/env python3\n\"\"\"Configuration de la licence SETRAF\"\"\"\n\nLICENSE_MODE = \"portable\"\n\nADMIN_EMAIL = \"nyundumathryme@gmail.com\"\nSMTP_SERVER = \"smtp.gmail.com\"\nSMTP_PORT = 587\n\nPORTABLE_OPTIONS = {\n    \"max_machines\": None,\n    \"check_email_only\": True,\n    \"allow_transfer\": True,\n    \"validity_days\": None\n}\n\nDEV_MODE = False\n''')"

if errorlevel 1 (
    echo ❌ Erreur lors de la configuration
    pause
    exit /b 1
)

echo ✅ Licence configurée en mode PORTABLE

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║            🔍 ÉTAPE 2: VÉRIFICATION DES FICHIERS             ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

set ERROR_COUNT=0

REM Vérifier les fichiers essentiels
if not exist "license.key" (
    echo ❌ license.key manquant
    set /a ERROR_COUNT+=1
) else (
    echo ✅ license.key
)

if not exist "license.dat" (
    echo ❌ license.dat manquant
    set /a ERROR_COUNT+=1
) else (
    echo ✅ license.dat
)

if not exist "app.py" (
    echo ❌ app.py manquant
    set /a ERROR_COUNT+=1
) else (
    echo ✅ app.py
)

if not exist "launcher_all_servers.py" (
    echo ❌ launcher_all_servers.py manquant
    set /a ERROR_COUNT+=1
) else (
    echo ✅ launcher_all_servers.py
)

if not exist "requirements.txt" (
    echo ❌ requirements.txt manquant
    set /a ERROR_COUNT+=1
) else (
    echo ✅ requirements.txt
)

if %ERROR_COUNT% gtr 0 (
    echo.
    echo ⚠️  %ERROR_COUNT% fichier(s) manquant(s)
    echo    Le package pourrait ne pas fonctionner correctement
    echo.
    set /p "CONTINUE=Continuer quand même ? (o/n): "
    if /i not "%CONTINUE%"=="o" exit /b 0
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              📋 ÉTAPE 3: INSTRUCTIONS FINALES                ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo ✅ Préparation terminée!
echo.
echo 📦 FICHIERS À COPIER SUR VOTRE SSD:
echo.
echo    1. Le dossier complet: SETRAGESTION\
echo       (celui qui contient ce script)
echo       ✅ Python311 est déjà INCLUS dans protected_excel\
echo.
if not exist "python311\python.exe" (
    echo    2. Le dossier Python portable (OPTIONNEL):
    if exist "..\python311\python.exe" (
        echo       %cd%\..\python311\
        echo       💡 Pour une meilleure portabilité, copiez-le aussi
    ) else if exist "..\..\python311\python.exe" (
        echo       Trouvé à: %cd%\..\..\python311\
        echo       💡 Pour une meilleure portabilité, copiez-le
    ) else (
        echo       ⚠️  Non trouvé - cherchez-le manuellement
    )
)
echo.

echo 💡 STRUCTURE SUR LE SSD:
echo.
echo    [Votre SSD]\
echo    ├── python311\
echo    │   ├── python.exe
echo    │   └── ...
echo    │
echo    └── SETRAGESTION\
echo        ├── Lanceur_SETRAF_Portable.bat
echo        └── protected_excel\
echo            ├── license.key
echo            ├── license.dat
echo            ├── license_config.py  ← MODE PORTABLE ✓
echo            └── ...
echo.

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║                   📝 SUR LE NOUVEL ORDINATEUR                ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo Une fois sur le nouvel ordinateur, suivez ces étapes:
echo.
echo 1. Ouvrez un terminal dans: [SSD]\SETRAGESTION\protected_excel
echo.
echo 2. Supprimez l'ancien environnement:
echo    ^> rmdir /s /q venv
echo.
echo 3. Recréez l'environnement:
echo    ^> RECREER_ENVIRONNEMENT.bat
echo.
echo 4. Lancez l'application:
echo    ^> cd ..
echo    ^> Lanceur_SETRAF_Portable.bat
echo.

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║                    ✅ PRÊT À COPIER! ✅                     ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

pause
