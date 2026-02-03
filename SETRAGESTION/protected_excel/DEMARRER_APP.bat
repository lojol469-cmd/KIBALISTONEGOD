@echo off
REM Script de lancement de l'application SETRAGESTION
REM Ce script démarre l'application Streamlit avec l'environnement Python local

echo.
echo ========================================
echo   SETRAGESTION - Application de Gestion
echo ========================================
echo.
echo Verification de l'environnement Python...

if not exist "python311\python.exe" (
    echo [ERREUR] Python 3.11 non trouve dans le dossier python311
    echo Veuillez installer Python 3.11 dans le dossier python311
    pause
    exit /b 1
)

echo [OK] Python 3.11 trouve
echo.
echo Verification des dependances...

python311\python.exe -c "import streamlit, pandas, plotly" 2>nul
if errorlevel 1 (
    echo [ATTENTION] Certaines dependances sont manquantes
    echo Installation des dependances...
    python311\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERREUR] Echec de l'installation des dependances
        pause
        exit /b 1
    )
)

echo [OK] Toutes les dependances sont installees
echo.
echo ========================================
echo   Demarrage de l'application...
echo ========================================
echo.
echo L'application va s'ouvrir dans votre navigateur
echo Pour arreter l'application, appuyez sur Ctrl+C dans cette fenetre
echo.

REM Démarrer Streamlit avec l'environnement Python local
python311\python.exe -m streamlit run app.py

pause
