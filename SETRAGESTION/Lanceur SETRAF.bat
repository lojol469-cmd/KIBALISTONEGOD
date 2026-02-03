@echo off
chcp 65001 >nul
cd /d "%~dp0protected_excel"

cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║                🚀 APPLICATION SETRAF 2026 🚀                 ║
echo ║                                                              ║
echo ║              Système de Gestion des Risques                  ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🔐 Vérification de la licence en cours...
echo.

python license_check.py
if errorlevel 1 goto :license_error

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║                   ✅ LICENCE VALIDEE ✅                      ║
echo ║                                                              ║
echo ║                Démarrage de l'application...                 ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔧 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 goto :env_error

echo 🚀 Démarrage de l'application Streamlit et serveurs...
python launcher_all_servers.py

goto :end

:license_error
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║                 ❌ LICENCE NON VALIDEE ❌                    ║
echo ║                                                              ║
echo ║  L'application ne peut pas démarrer sans licence valide.    ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
exit /b 1

:env_error
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║                 ❌ ERREUR ENVIRONNEMENT ❌                   ║
echo ║                                                              ║
echo ║  Impossible d'activer l'environnement virtuel.              ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause
exit /b 1

:end
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║              ✅ APPLICATION DEMARREE ✅                     ║
echo ║                                                              ║
echo ║  Vous pouvez maintenant utiliser SETRAF dans votre          ║
echo ║  navigateur web.                                            ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
pause