@echo off
chcp 65001 >nul
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║     📧 GUIDE RAPIDE - NOTIFICATIONS EMAIL SETRAGESTION       ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🎯 Système de notifications push intégré
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  📋 CONFIGURATION RAPIDE (2 minutes)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo  Étape 1: Créer le fichier .env
echo     ^> copy .env.example .env
echo.
echo  Étape 2: Gmail - Générer un mot de passe d'application
echo     1. Allez sur: https://myaccount.google.com/apppasswords
echo     2. Créez "SETRAGESTION"
echo     3. Copiez le mot de passe (16 caractères)
echo.
echo  Étape 3: Modifier le fichier .env avec Notepad
echo     EMAIL_SENDER=votre.email@gmail.com
echo     EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
echo.
echo  Étape 4: Tester la configuration
echo     ^> TEST_EMAIL.bat
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  📧 NOTIFICATIONS AUTOMATIQUES
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo  ✅ Habilitations
echo     • Nouvelle habilitation ajoutée
echo     • Habilitation modifiée
echo     • Détails complets + jours restants
echo.
echo  ✅ Enregistrements
echo     • Sauvegarde de données
echo     • Résumé par catégorie
echo     • Total des enregistrements
echo.
echo  ✅ Destinataires
echo     • Utilisateur concerné
echo     • Super Admin (nyundumathryme@gmail.com)
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  📚 DOCUMENTATION
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo  📄 CONFIGURATION_NOTIFICATIONS.md  - Guide complet
echo  📄 NOTIFICATIONS_RESUME.md         - Résumé des changements
echo  🧪 test_email_config.py            - Script de test
echo  🚀 TEST_EMAIL.bat                  - Test rapide
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo  💡 Mode dégradé: Si non configuré, l'application fonctionne
echo     normalement sans envoyer d'emails (logs seulement)
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
