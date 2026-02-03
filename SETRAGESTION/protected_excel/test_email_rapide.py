"""Test rapide d'envoi d'email - SETRAGESTION"""
import os
import sys
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Charger .env
load_dotenv()

EMAIL_SENDER = os.environ.get('EMAIL_USER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS', '')
SUPER_ADMIN = 'nyundumathryme@gmail.com'

print("=" * 60)
print("🧪 TEST RAPIDE ENVOI EMAIL")
print("=" * 60)
print()
print(f"📧 EMAIL_SENDER: {EMAIL_SENDER}")
print(f"🔑 EMAIL_PASSWORD: {'✅ Configuré (' + str(len(EMAIL_PASSWORD)) + ' car.)' if EMAIL_PASSWORD else '❌ VIDE'}")
print(f"👑 SUPER_ADMIN: {SUPER_ADMIN}")
print()

if not EMAIL_SENDER or not EMAIL_PASSWORD:
    print("❌ CONFIGURATION MANQUANTE!")
    print("Vérifiez votre fichier .env")
    input("\nAppuyez sur Entrée pour quitter...")
    sys.exit(1)

print("📤 Envoi d'un email de test...")
print()

try:
    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_SENDER
    msg['To'] = SUPER_ADMIN
    msg['Subject'] = "[SETRAGESTION] TEST - Email de notification"
    
    html_body = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .header {{ background-color: #1E3A8A; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f4f4f4; }}
                .footer {{ padding: 10px; text-align: center; font-size: 12px; color: #666; }}
                .badge-success {{ background-color: #10B981; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 SETRAGESTION</h1>
                <p>Système de Gestion des Risques</p>
            </div>
            <div class="content">
                <h2>✅ Test de notification réussi!</h2>
                <p><span class="badge-success">SYSTÈME ACTIF</span></p>
                <p>Ce test confirme que les notifications par email fonctionnent correctement.</p>
                <p><strong>Configuration:</strong></p>
                <ul>
                    <li>📧 Expéditeur: {EMAIL_SENDER}</li>
                    <li>👑 Super Admin: {SUPER_ADMIN}</li>
                    <li>🔐 Mot de passe: {'*' * len(EMAIL_PASSWORD)}</li>
                </ul>
                <p><strong>Types de notifications activées:</strong></p>
                <ul>
                    <li>✅ Enregistrement de données (véhicules, achats, anomalies, habilitations)</li>
                    <li>✅ Ajout/modification d'habilitations</li>
                    <li>✅ Notifications automatiques à l'utilisateur et au super admin</li>
                </ul>
            </div>
            <div class="footer">
                <p>Cet email a été envoyé automatiquement par SETRAGESTION</p>
                <p>Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html'))
    
    print("🔌 Connexion au serveur SMTP...")
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
    
    print("🔐 Activation TLS...")
    server.starttls()
    
    print("🔑 Authentification...")
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    
    print("📨 Envoi de l'email...")
    server.send_message(msg)
    server.quit()
    
    print()
    print("=" * 60)
    print("✅ EMAIL ENVOYÉ AVEC SUCCÈS!")
    print("=" * 60)
    print()
    print(f"📬 Vérifiez la boîte email: {SUPER_ADMIN}")
    print("   (Vérifiez aussi le dossier SPAM/Indésirables)")
    print()
    print("✨ Les notifications fonctionnent correctement!")
    
except smtplib.SMTPAuthenticationError as e:
    print()
    print("❌ ERREUR D'AUTHENTIFICATION")
    print(f"Détails: {str(e)}")
    print()
    print("💡 Solutions:")
    print("   1. Vérifiez EMAIL_USER dans .env")
    print("   2. Vérifiez EMAIL_PASS (mot de passe d'application Gmail)")
    print("   3. Générez un nouveau: https://myaccount.google.com/apppasswords")
    
except smtplib.SMTPException as e:
    print()
    print(f"❌ ERREUR SMTP: {str(e)}")
    
except Exception as e:
    print()
    print(f"❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()

print()
input("Appuyez sur Entrée pour quitter...")
