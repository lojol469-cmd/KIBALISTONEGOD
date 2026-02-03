@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║                  📚 DOCUMENTATION SETRAF 📚                  ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo Quelle documentation voulez-vous consulter ?
echo.
echo 1. INDEX.md                    - Vue d'ensemble des solutions
echo 2. README_SOLUTION.md          - Guide complet du problème
echo 3. GUIDE_PORTABILITE.md        - Guide de portabilité détaillé
echo 4. protected_excel\README_LICENCE.md - Documentation technique
echo.
echo 5. Ouvrir tous les fichiers
echo.

set /p "CHOICE=Votre choix (1-5): "

if "%CHOICE%"=="1" (
    start INDEX.md
    echo ✅ Ouverture de INDEX.md
)

if "%CHOICE%"=="2" (
    start README_SOLUTION.md
    echo ✅ Ouverture de README_SOLUTION.md
)

if "%CHOICE%"=="3" (
    start GUIDE_PORTABILITE.md
    echo ✅ Ouverture de GUIDE_PORTABILITE.md
)

if "%CHOICE%"=="4" (
    start protected_excel\README_LICENCE.md
    echo ✅ Ouverture de README_LICENCE.md
)

if "%CHOICE%"=="5" (
    start INDEX.md
    timeout /t 1 /nobreak >nul
    start README_SOLUTION.md
    timeout /t 1 /nobreak >nul
    start GUIDE_PORTABILITE.md
    timeout /t 1 /nobreak >nul
    start protected_excel\README_LICENCE.md
    echo ✅ Ouverture de tous les fichiers
)

echo.
pause
