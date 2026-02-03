@echo off
chcp 65001 >nul
cd /d "%~dp0protected_excel"

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║        🔧 CONFIGURATION BACKEND RÉSEAU 🔧                    ║
echo ║                                                              ║
echo ║                   SETRAGESTION 2026                          ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Détecter Python portable
set "PYTHON_PORTABLE=%~dp0protected_excel\python311\python.exe"
if exist "%PYTHON_PORTABLE%" (
    "%PYTHON_PORTABLE%" configure_backend.py
    goto :end
)

REM Sinon utiliser Python système
python configure_backend.py

:end
pause
