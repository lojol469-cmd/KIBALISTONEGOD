@echo off
chcp 65001 >nul
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║           🧪 TEST RAPIDE NOTIFICATION EMAIL 🧪               ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

if exist "python311\python.exe" (
    python311\python.exe test_email_rapide.py
) else (
    python test_email_rapide.py
)
