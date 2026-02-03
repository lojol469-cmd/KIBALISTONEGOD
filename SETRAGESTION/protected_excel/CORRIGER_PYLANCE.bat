@echo off
echo.
echo ========================================
echo   RESOLUTION ERREURS PYLANCE
echo ========================================
echo.
echo Les packages Python sont installes correctement.
echo Les erreurs Pylance sont des faux positifs de cache.
echo.
echo Solutions (dans l'ordre):
echo.
echo 1. RECHARGEZ VS CODE
echo    Ctrl+Shift+P puis tapez: Developer: Reload Window
echo.
echo 2. SELECTIONNEZ L'INTERPRETEUR
echo    Ctrl+Shift+P puis tapez: Python: Select Interpreter
echo    Choisissez: .\python311\python.exe
echo.
echo 3. REDEMARREZ PYLANCE
echo    Ctrl+Shift+P puis tapez: Pylance: Restart Server
echo.
echo ========================================
echo   VERIFICATION
echo ========================================
echo.
echo Test d'import Python...
python311\python.exe -c "import streamlit, pandas, plotly; print('OK: Tous les packages fonctionnent!')"
echo.
echo ========================================
echo.
pause
