@echo off
chcp 65001 >nul 2>&1
title Installation des Dépendances Portables

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║        📦 INSTALLATION DÉPENDANCES PORTABLES 📦             ║
echo ║                                                              ║
echo ║           Pour rendre l'application 100% portable           ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Vérifier Python portable
if exist "python311\python.exe" (
    set "PYTHON_CMD=python311\python.exe"
    echo ✅ Python portable trouvé: python311\python.exe
) else (
    echo ❌ Python portable introuvable dans python311\
    pause
    exit /b 1
)

echo.
echo 📦 Installation des dépendances Python...
echo.

"%PYTHON_CMD%" -m pip install --upgrade pip --quiet
"%PYTHON_CMD%" -m pip install python-dotenv --quiet
"%PYTHON_CMD%" -m pip install requests --quiet
"%PYTHON_CMD%" -m pip install streamlit --quiet
"%PYTHON_CMD%" -m pip install pandas --quiet
"%PYTHON_CMD%" -m pip install plotly --quiet
"%PYTHON_CMD%" -m pip install cloudinary --quiet

if errorlevel 1 (
    echo ❌ Erreur lors de l'installation
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ✅ INSTALLATION TERMINÉE ✅                     ║
echo ║                                                              ║
echo ║  Toutes les dépendances Python sont maintenant installées   ║
echo ║  dans le Python portable (python311\)                        ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
