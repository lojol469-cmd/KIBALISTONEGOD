@echo off
echo ============================================
echo  DIAGNOSTIC COMPLET STREAMLIT
echo ============================================
echo.

echo [1/6] Vérification du répertoire...
cd /d "%~dp0"
echo Répertoire actuel: %CD%
echo.

echo [2/6] Recherche de Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas dans le PATH
    echo Solutions:
    echo - Installez Python depuis https://python.org
    echo - Ajoutez Python au PATH système
    goto :error
) else (
    echo ✅ Python trouvé dans le PATH
)
echo.

echo [3/6] Version de Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Impossible d'exécuter Python
    goto :error
)
echo.

echo [4/6] Test d'import Streamlit...
python -c "import streamlit; print('✅ Streamlit version:', streamlit.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Streamlit n'est pas installé ou accessible
    echo Solutions:
    echo - pip install streamlit
    echo - Vérifiez l'environnement virtuel
    goto :error
)
echo.

echo [5/6] Vérification du fichier app.py...
if not exist "app.py" (
    echo ❌ app.py n'existe pas dans %CD%
    goto :error
) else (
    echo ✅ app.py trouvé
)
echo.

echo [6/6] Test de syntaxe Python...
python -m py_compile app.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ Erreur de syntaxe dans app.py
    echo Détails de l'erreur:
    python -m py_compile app.py
    goto :error
) else (
    echo ✅ Syntaxe de app.py correcte
)
echo.

echo ============================================
echo  TOUS LES TESTS SONT RÉUSSIS !
echo ============================================
echo.
echo Tentative de lancement de Streamlit...
echo Si cette fenêtre reste ouverte, Streamlit fonctionne.
echo Appuyez sur Ctrl+C pour arrêter.
echo.

python -m streamlit run app.py --server.port 8501 --server.address localhost

goto :end

:error
echo.
echo ============================================
echo  ERREUR DETECTEE - RESOLVEZ LE PROBLEME CI-DESSUS
echo ============================================
pause
exit /b 1

:end