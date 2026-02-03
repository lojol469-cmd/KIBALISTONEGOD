@echo off
chcp 65001 >nul
cd /d "%~dp0protected_excel"

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           🌐 TEST DE CONFIGURATION RÉSEAU 🌐                 ║
echo ║                                                              ║
echo ║                   SETRAGESTION 2026                          ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Détecter Python portable
set "PYTHON_PORTABLE=%~dp0protected_excel\python311\python.exe"
if exist "%PYTHON_PORTABLE%" (
    "%PYTHON_PORTABLE%" test_network.py
    goto :end
)

REM Sinon utiliser Python système
python test_network.py

:end
