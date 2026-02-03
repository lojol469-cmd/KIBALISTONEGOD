"""
Script de test pour vérifier la configuration des notifications email
Exécutez ce script pour tester votre configuration SMTP
"""

import os
import sys
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

# Configuration Email
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_SMTP_SERVER = os.environ.get('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.environ.get('EMAIL_SMTP_PORT', '587'))

def test_email_config():
    """Test de la configuration email"""
    print("=" * 60)
    print("🧪 TEST DE CONFIGURATION EMAIL - SETRAGESTION")
    print("=" * 60)
    print()
    
    # Vérification des paramètres
    print("📋 Vérification de la configuration:")
    print(f"   EMAIL_SENDER: {EMAIL_SENDER if EMAIL_SENDER else '❌ NON CONFIGURÉ'}")
    print(f"   EMAIL_PASSWORD: {'✅ Configuré (' + str(len(EMAIL_PASSWORD)) + ' caractères)' if EMAIL_PASSWORD else '❌ NON CONFIGURÉ'}")
    print(f"   EMAIL_SMTP_SERVER: {EMAIL_SMTP_SERVER}")
    print(f"   EMAIL_SMTP_PORT: {EMAIL_SMTP_PORT}")
    print()
    
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("❌ Configuration incomplète!")
        print()
        print("📝 Instructions:")
        print("   1. Créez un fichier .env depuis .env.example")
        print("   2. Configurez EMAIL_SENDER et EMAIL_PASSWORD")
        print("   3. Pour Gmail: générez un mot de passe d'application")
        print("      → https://myaccount.google.com/apppasswords")
        print()
        return False
    
    # Test de connexion SMTP
    print("🔌 Test de connexion au serveur SMTP...")
    try:
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, timeout=10)
        print("   ✅ Connexion établie")
        
        print("🔐 Test de STARTTLS...")
        server.starttls()
        print("   ✅ TLS activé")
        
        print("🔑 Test d'authentification...")
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        print("   ✅ Authentification réussie")
        
        server.quit()
        print()
        print("✅ CONFIGURATION EMAIL VALIDE!")
        print()
        
        # Proposer d'envoyer un email de test
        response = input("📧 Voulez-vous envoyer un email de test? (o/N): ").lower()
        if response == 'o':
            send_test_email()
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("   ❌ Erreur d'authentification")
        print(f"   Détails: {str(e)}")
        print()
        print("💡 Solutions:")
        print("   • Vérifiez EMAIL_SENDER (adresse complète)")
        print("   • Vérifiez EMAIL_PASSWORD (mot de passe d'application)")
        print("   • Gmail: activez l'authentification à 2 facteurs")
        print("   • Générez un nouveau mot de passe d'application")
        return False
        
    except smtplib.SMTPConnectError as e:
        print("   ❌ Impossible de se connecter au serveur")
        print(f"   Détails: {str(e)}")
        print()
        print("💡 Solutions:")
        print("   • Vérifiez EMAIL_SMTP_SERVER")
        print("   • Vérifiez EMAIL_SMTP_PORT")
        print("   • Vérifiez votre connexion internet")
        return False
        
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
        return False

def send_test_email():
    """Envoie un email de test"""
    print()
    print("📧 Envoi d'un email de test...")
    
    destinataire = input("📮 Adresse email de destination (laisser vide pour EMAIL_SENDER): ").strip()
    if not destinataire:
        destinataire = EMAIL_SENDER
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_SENDER
        msg['To'] = destinataire
        msg['Subject'] = "[SETRAGESTION] Test de configuration email"
        
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .header {{ background-color: #1E3A8A; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f4f4f4; }}
                    .footer {{ padding: 10px; text-align: center; font-size: 12px; color: #666; }}
                    .badge {{ display: inline-block; padding: 5px 10px; border-radius: 5px; font-weight: bold; }}
                    .badge-success {{ background-color: #10B981; color: white; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚀 SETRAGESTION</h1>
                    <p>Système de Gestion des Risques</p>
                </div>
                <div class="content">
                    <h2>✅ Test de configuration réussi!</h2>
                    <p>Votre configuration email fonctionne correctement.</p>
                    <p><strong>Configuration:</strong></p>
                    <ul>
                        <li>Serveur SMTP: {EMAIL_SMTP_SERVER}</li>
                        <li>Port: {EMAIL_SMTP_PORT}</li>
                        <li>Expéditeur: {EMAIL_SENDER}</li>
                    </ul>
                    <p class="badge badge-success">Configuration validée</p>
                    <p>Les notifications seront envoyées automatiquement pour:</p>
                    <ul>
                        <li>🎓 Habilitations (ajout, modification)</li>
                        <li>💾 Enregistrements de données</li>
                        <li>⚠️ Alertes importantes</li>
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
        
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"   ✅ Email de test envoyé à: {destinataire}")
        print("   📬 Vérifiez votre boîte de réception (et le dossier SPAM)")
        
    except Exception as e:
        print(f"   ❌ Erreur lors de l'envoi: {str(e)}")

if __name__ == "__main__":
    print()
    test_email_config()
    print()
    print("=" * 60)
    input("Appuyez sur Entrée pour quitter...")
