@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║    🔧 RECRÉATION DE L'ENVIRONNEMENT PYTHON PORTABLE 🔧      ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM ===== DÉTECTION DE PYTHON =====
echo 🔍 Détection de Python...
echo.

REM 1. Chercher Python portable LOCAL (dans ce dossier)
set "PYTHON_CMD="
if exist "python311\python.exe" (
    echo ✅ Python portable LOCAL trouvé: python311\python.exe
    set "PYTHON_CMD=python311\python.exe"
    goto :python_found
)

REM 2. Chercher dans le dossier parent
if exist "..\..\python311\python.exe" (
    echo ✅ Python portable trouvé: ..\..\python311\python.exe
    set "PYTHON_CMD=..\..\python311\python.exe"
    goto :python_found
)

REM 3. Utiliser Python système
python --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ Python système trouvé
    set "PYTHON_CMD=python"
    goto :python_found
)

REM Aucun Python trouvé
echo ❌ Python n'est pas disponible
echo.
echo 💡 Solutions:
echo    1. Le dossier python311 devrait être dans protected_excel\
echo    2. Ou installer Python depuis python.org
echo    3. Ou utiliser un Python portable
pause
exit /b 1

:python_found

echo 🗑️  Suppression de l'ancien environnement virtuel...
if exist "venv" (
    rmdir /s /q "venv"
    echo    ✅ Ancien venv supprimé
) else (
    echo    ℹ️  Pas d'ancien venv trouvé
)

echo.
echo 🐍 Création du nouvel environnement virtuel...
"%PYTHON_CMD%" -m venv venv
if errorlevel 1 (
    echo ❌ Erreur lors de la création du venv
    pause
    exit /b 1
)
echo    ✅ Venv créé

echo.
echo 📦 Installation des dépendances...
call venv\Scripts\activate.bat
"%PYTHON_CMD%" -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️  Certaines dépendances ont peut-être échoué
) else (
    echo    ✅ Toutes les dépendances installées
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         ✅ ENVIRONNEMENT RECRÉÉ AVEC SUCCÈS ✅             ║
echo ║                                                              ║
echo ║  Vous pouvez maintenant lancer l'application               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
