@echo off
chcp 65001 >nul

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           🧪 TEST CONFIGURATION EMAIL - SETRAGESTION 🧪      ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Détecter Python portable
set "PYTHON_CMD=python311\python.exe"
if not exist "%PYTHON_CMD%" (
    set "PYTHON_CMD=python"
)

echo 🔍 Lancement du test de configuration email...
echo.

"%PYTHON_CMD%" test_email_config.py

echo.
pause
