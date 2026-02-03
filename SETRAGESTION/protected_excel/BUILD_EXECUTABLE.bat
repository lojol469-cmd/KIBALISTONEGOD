@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║            🏗️  BUILD APPLICATION PORTABLE 🏗️                ║
echo ║                                                              ║
echo ║              Création d'un exécutable autonome               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Détecter Python
set "PYTHON_CMD="
if exist "python311\python.exe" (
    set "PYTHON_CMD=python311\python.exe"
    echo ✅ Python local détecté
) else (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
        echo ✅ Python système détecté
    ) else (
        echo ❌ Python non disponible
        pause
        exit /b 1
    )
)

echo.
echo 📋 Options de build :
echo.
echo 1. Build COMPLET (PyInstaller - Recommandé)
echo    • Exécutable unique
echo    • Pas besoin de Python
echo    • ~200-300 MB
echo.
echo 2. Build LÉGER (Avec Python inclus - Actuel)
echo    • Utilise Python portable
echo    • Plus rapide à démarrer
echo    • ~150 MB
echo.
echo 3. ANNULER
echo.

set /p "CHOICE=Votre choix (1-3): "

if "%CHOICE%"=="1" goto :build_pyinstaller
if "%CHOICE%"=="2" goto :build_light
if "%CHOICE%"=="3" goto :end

echo ❌ Choix invalide
pause
exit /b 1

:build_pyinstaller
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              🏗️  BUILD AVEC PYINSTALLER 🏗️                  ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔍 Vérification de PyInstaller...
"%PYTHON_CMD%" -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installation de PyInstaller...
    "%PYTHON_CMD%" -m pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Erreur d'installation
        pause
        exit /b 1
    )
)
echo ✅ PyInstaller prêt

echo.
echo 🔨 Création du fichier .spec...
"%PYTHON_CMD%" create_build_spec.py

echo.
echo 🏗️  Construction de l'exécutable...
echo    ⏱️  Cela peut prendre 5-10 minutes...
"%PYTHON_CMD%" -m PyInstaller --clean setraf_portable.spec

if errorlevel 1 (
    echo ❌ Erreur de build
    pause
    exit /b 1
)

echo.
echo ✅ BUILD TERMINÉ !
echo.
echo 📦 L'exécutable se trouve dans: dist\SETRAF_Portable\
echo.
echo 🚀 Pour lancer : dist\SETRAF_Portable\SETRAF.exe
echo.
pause
goto :end

:build_light
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              📦  BUILD LÉGER (DÉJÀ FAIT!) 📦                 ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo ✅ Votre application est déjà en mode portable léger !
echo.
echo 📂 Structure actuelle :
echo    SETRAGESTION\
echo    ├── protected_excel\
echo    │   ├── python311\           ← Python inclus ✅
echo    │   ├── venv\
echo    │   └── ...
echo    └── Lanceur_SETRAF_Portable.bat ← Prêt à l'emploi ✅
echo.
echo 💡 Pour une portabilité complète, utilisez Option 1 (PyInstaller)
echo.
pause
goto :end

:end
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║                   ✅ TERMINÉ ✅                             ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
