@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              🔍 DIAGNOSTIC AUTOMATIQUE SETRAF 🔍             ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Détection de Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo.
    echo Recherche d'un Python portable...
    
    if exist "..\python311\python.exe" (
        echo ✅ Python portable trouvé!
        ..\python311\python.exe diagnostic.py
    ) else if exist "..\..\python311\python.exe" (
        echo ✅ Python portable trouvé!
        ..\..\python311\python.exe diagnostic.py
    ) else (
        echo ❌ Aucun Python trouvé
        echo.
        echo Solutions:
        echo   1. Installer Python depuis python.org
        echo   2. Copier le dossier python311 à côté de SETRAGESTION
        pause
        exit /b 1
    )
) else (
    python diagnostic.py
)

pause
