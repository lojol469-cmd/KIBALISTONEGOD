@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║          🔓 DÉVERROUILLAGE DES FICHIERS SENSIBLES 🔓        ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Détecter Python
set "PYTHON_CMD="
if exist "python311\python.exe" (
    set "PYTHON_CMD=python311\python.exe"
) else (
    python --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
    ) else (
        echo ❌ Python non disponible
        pause
        exit /b 1
    )
)

"%PYTHON_CMD%" deverrouiller_fichiers.py
