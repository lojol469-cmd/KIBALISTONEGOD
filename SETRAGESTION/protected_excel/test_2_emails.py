"""Test d'envoi email AVEC l'utilisateur spécifique"""
import os
import sys
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

load_dotenv()

EMAIL_SENDER = os.environ.get('EMAIL_USER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS', '')

# Utilisateurs
USER_EMAIL = "lojol469@gmail.com"
SUPER_ADMIN = "nyundumathryme@gmail.com"

print("=" * 70)
print("🧪 TEST ENVOI EMAIL - 2 DESTINATAIRES")
print("=" * 70)
print()
print(f"📤 Expéditeur: {EMAIL_SENDER}")
print(f"👤 Utilisateur: {USER_EMAIL}")
print(f"👑 Super Admin: {SUPER_ADMIN}")
print()

def send_test_email(to_email, is_admin=False):
    """Envoie un email de test"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = "[SETRAGESTION] TEST - Notification d'enregistrement"
        
        user_prefix = f"<p><strong>Notification pour l'utilisateur:</strong> {USER_EMAIL}</p>" if is_admin else ""
        
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .header {{ background-color: #1E3A8A; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f4f4f4; }}
                    .footer {{ padding: 10px; text-align: center; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚀 SETRAGESTION</h1>
                    <p>Système de Gestion des Risques</p>
                </div>
                <div class="content">
                    {user_prefix}
                    <h2>✅ Enregistrement réussi!</h2>
                    <p>Vos données ont été sauvegardées avec succès:</p>
                    <ul>
                        <li>🚗 Véhicules: 2 enregistrement(s)</li>
                        <li>🛒 Achats: 1 enregistrement(s)</li>
                        <li>⚠️ Anomalies: 0 enregistrement(s)</li>
                        <li>🎓 Habilitations: 1 enregistrement(s)</li>
                    </ul>
                    <p><strong>Total:</strong> 4 enregistrement(s)</p>
                    <p><strong>Date de sauvegarde:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="footer">
                    <p>Cet email a été envoyé automatiquement par SETRAGESTION</p>
                    <p>Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        print(f"📨 Envoi à {to_email}...")
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"   ✅ Envoyé avec succès!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Envoyer à l'utilisateur
print("1️⃣  Envoi à l'utilisateur...")
user_sent = send_test_email(USER_EMAIL, is_admin=False)
print()

# Envoyer au super admin
print("2️⃣  Envoi au super admin...")
admin_sent = send_test_email(SUPER_ADMIN, is_admin=True)
print()

print("=" * 70)
if user_sent and admin_sent:
    print("✅ LES 2 EMAILS ONT ÉTÉ ENVOYÉS!")
    print()
    print("📬 Vérifiez les boîtes email:")
    print(f"   • {USER_EMAIL}")
    print(f"   • {SUPER_ADMIN}")
    print()
    print("⚠️  Vérifiez aussi le dossier SPAM/Indésirables")
elif user_sent or admin_sent:
    print("⚠️  UN SEUL EMAIL ENVOYÉ")
else:
    print("❌ ÉCHEC COMPLET")
print("=" * 70)

input("\nAppuyez sur Entrée pour quitter...")
