@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         🔐 TEST SERVEUR DE DEMANDE DE LICENCE 🔐            ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

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
echo 🚀 Lancement du serveur de licence...
echo.

"%PYTHON_CMD%" launcher_license_server_only.py

pause
