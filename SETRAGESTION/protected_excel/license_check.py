#!/usr/bin/env python3
"""
License Manager for SETRAF Application
Simple OTP-based license activation via email
Supports portable mode for multi-machine usage
"""

import hashlib
import platform
import os
import uuid
from datetime import datetime
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Import configuration
try:
    from license_config import LICENSE_MODE, PORTABLE_OPTIONS, DEV_MODE, ADMIN_EMAIL, SMTP_SERVER, SMTP_PORT
except ImportError:
    # Valeurs par défaut si le fichier de config n'existe pas
    LICENSE_MODE = "strict"
    DEV_MODE = False
    ADMIN_EMAIL = "nyundumathryme@gmail.com"
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    PORTABLE_OPTIONS = {"check_email_only": False}

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

def get_machine_fingerprint():
    """Get a unique fingerprint of the machine"""
    try:
        system = platform.system()
        node = platform.node()
        machine = platform.machine()
        processor = platform.processor()
        cpu_count = os.cpu_count()
        mac = hex(uuid.getnode())

        fingerprint_data = f"{system}{node}{machine}{processor}{cpu_count}{mac}"
        fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
        return fingerprint
    except:
        return "unknown"

def generate_otp():
    """Generate a 8-digit OTP"""
    return ''.join(random.choices(string.digits, k=8))

def send_email(to_email, subject, body):
    """Send email using Gmail SMTP"""
    try:
        if not EMAIL_USER or not EMAIL_PASS:
            print("❌ Erreur: EMAIL_USER ou EMAIL_PASS non configurés dans .env")
            return False

        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Erreur d'envoi d'email: {e}")
        return False

def check_existing_license():
    """Check if a valid license exists"""
    try:
        # MODE DÉVELOPPEMENT - bypass toutes les vérifications
        if DEV_MODE:
            print("✅ Mode développement - licence auto-validée")
            return True

        license_file = os.path.join(os.path.dirname(__file__), "license.key")
        license_dat_file = os.path.join(os.path.dirname(__file__), "license.dat")

        if not os.path.exists(license_file) or not os.path.exists(license_dat_file):
            return False

        # Read license data
        with open(license_dat_file, 'r') as f:
            license_data = json.load(f)

        # Check if validated
        if not license_data.get('validated', False):
            return False

        # MODE PORTABLE - vérification allégée
        if LICENSE_MODE == "portable":
            if PORTABLE_OPTIONS.get('check_email_only', False):
                # Vérifier uniquement l'email
                print(f"✅ Licence portable valide pour: {license_data.get('user_email', 'Utilisateur')}")
                return True
            else:
                # Vérification standard même en portable
                pass

        # MODE STRICT - vérification de l'empreinte machine
        if LICENSE_MODE == "strict":
            current_fingerprint = get_machine_fingerprint()
            if license_data.get('fingerprint') != current_fingerprint:
                print("❌ Empreinte machine différente - licence invalide pour cet ordinateur")
                print(f"   Cette licence est liée à une autre machine.")
                print(f"   Mode actuel: {LICENSE_MODE}")
                return False

        print("✅ Licence valide trouvée")
        return True

    except Exception as e:
        print(f"❌ Erreur de vérification de licence: {e}")
        return False

# Alias for backward compatibility with launcher
def check_license():
    """Alias for check_existing_license() - for launcher compatibility"""
    return check_existing_license()

def show_license_error():
    """Show license error and allow license request - for launcher compatibility"""
    return main()

def request_license():
    """Request license activation via OTP email"""
    print("\n" + "="*60)
    print("📝 FORMULAIRE DE DEMANDE DE LICENCE SETRAF")
    print("="*60)

    # Get user info
    user_name = input("Entrez votre nom complet: ").strip()
    user_email = input("Entrez votre email: ").strip()
    id_card = input("Entrez le numéro de votre carte d'identité: ").strip()

    if not user_name or not user_email or not id_card:
        print("❌ Tous les champs sont requis")
        return False

    # Get machine fingerprint
    fingerprint = get_machine_fingerprint()

    # Generate OTP
    otp = generate_otp()

    # Send email to admin
    admin_subject = f"🔐 DEMANDE LICENCE SETRAF - {user_name}"
    admin_body = f"""
    <h2>Nouvelle demande d'activation de licence SETRAF</h2>

    <h3>Informations de l'utilisateur:</h3>
    <ul>
        <li><strong>Nom:</strong> {user_name}</li>
        <li><strong>Email:</strong> {user_email}</li>
        <li><strong>Carte d'identité:</strong> {id_card}</li>
        <li><strong>Empreinte machine:</strong> {fingerprint}</li>
    </ul>

    <h3>Code OTP généré: <span style="color: red; font-size: 24px; font-weight: bold;">{otp}</span></h3>

    <p><strong>INSTRUCTION:</strong> Veuillez transmettre ce code OTP à l'utilisateur: <strong>{user_email}</strong></p>

    <p>Envoyez un email à l'utilisateur avec le code OTP pour qu'il puisse activer sa licence.</p>

    <hr>
    <p><em>Cette demande a été faite le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</em></p>
    """

    print(f"\n📧 Envoi de la demande à {ADMIN_EMAIL}...")
    if not send_email(ADMIN_EMAIL, admin_subject, admin_body):
        print("❌ Échec de l'envoi de la demande")
        return False

    print("✅ Demande envoyée avec succès!")
    print("📧 Attendez de recevoir le code OTP de SETRAF par email")
    print()

    # Wait for OTP from user
    entered_otp = input("Entrez le code OTP reçu de SETRAF: ").strip()

    if entered_otp == otp:
        # Activate license
        return activate_license(fingerprint, user_email, user_name, otp)
    else:
        print("❌ Code OTP incorrect")
        return False

def activate_license(fingerprint, user_email, user_name, license_code):
    """Activate the license with the provided code"""
    try:
        # Save license data
        license_data = {
            "fingerprint": fingerprint,
            "license_code": license_code,
            "user_email": user_email,
            "user_name": user_name,
            "created": datetime.now().isoformat(),
            "validated": True
        }

        # Save to license.dat
        with open("license.dat", "w") as f:
            json.dump(license_data, f)

        # Save license code to license.key
        license_file = os.path.join(os.path.dirname(__file__), "license.key")
        with open(license_file, "w") as f:
            f.write(license_code)

        print("✅ Licence activée avec succès!")
        print(f"   Utilisateur: {user_name}")
        print(f"   Email: {user_email}")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de l'activation: {e}")
        return False

def main():
    """Main license check function"""
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + " "*58 + "║")
    print("║                🔐 VERIFICATION DE LICENCE 🔐              ║")
    print("║" + " "*58 + "║")
    mode_text = f"Mode: {LICENSE_MODE.upper()}"
    padding = (58 - len(mode_text)) // 2
    print("║" + " "*padding + mode_text + " "*(58-padding-len(mode_text)) + "║")
    print("╚" + "═"*58 + "╝")

    # Check existing license
    if check_existing_license():
        return True

    # No valid license found
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + " "*58 + "║")
    print("║              🚫 LICENCE NON VALIDE 🚫                  ║")
    print("║" + " "*58 + "║")
    if LICENSE_MODE == "strict":
        print("║  Votre licence SETRAF n'est pas valide pour cette      ║")
        print("║  machine.                                               ║")
    else:
        print("║  Aucune licence valide n'a été trouvée.                ║")
    print("║" + " "*58 + "║")
    print("║  Remplissez le formulaire ci-dessous pour demander      ║")
    print("║  l'accès.                                               ║")
    print("║" + " "*58 + "║")
    print("╚" + "═"*58 + "╝")

    # Ask to request license
    response = input("\nVoulez-vous faire une demande de licence ? (o/n): ").strip().lower()
    if response == 'o':
        return request_license()
    else:
        print("❌ Accès refusé - licence requise")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
    else:
        print("\n🎉 Licence validée - accès autorisé!")
        input("Appuyez sur Entrée pour continuer...")