#!/usr/bin/env python3
"""
Utilitaire de Configuration de Licence SETRAF
Permet de changer le mode de licence facilement
"""

import os
import sys

def print_logo():
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║           🔧 CONFIGURATION DE LICENCE SETRAF 🔧              ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

def print_current_mode():
    """Affiche le mode actuel"""
    try:
        from license_config import LICENSE_MODE, DEV_MODE, PORTABLE_OPTIONS
        print("📋 Configuration actuelle:")
        print(f"   Mode de licence: {LICENSE_MODE}")
        print(f"   Mode développement: {'Activé' if DEV_MODE else 'Désactivé'}")
        if LICENSE_MODE == "portable":
            print(f"   Vérification email uniquement: {PORTABLE_OPTIONS.get('check_email_only', False)}")
        print()
    except Exception as e:
        print(f"⚠️  Impossible de lire la configuration: {e}\n")

def change_mode():
    """Change le mode de licence"""
    print("Modes disponibles:")
    print("  1. STRICT   - Licence liée à la machine (sécurité maximale)")
    print("  2. PORTABLE - Licence utilisable sur plusieurs machines")
    print("  3. DEV      - Mode développement (pas de vérification)")
    print()
    
    choice = input("Choisissez un mode (1-3): ").strip()
    
    if choice == "1":
        mode = "strict"
        dev_mode = False
        check_email_only = False
    elif choice == "2":
        mode = "portable"
        dev_mode = False
        check_email_only = True
        print("\n💡 En mode PORTABLE, la licence vérifiera uniquement l'email utilisateur")
    elif choice == "3":
        mode = "strict"
        dev_mode = True
        check_email_only = False
        print("\n⚠️  Mode DÉVELOPPEMENT - Toutes les vérifications sont désactivées!")
    else:
        print("❌ Choix invalide")
        return False
    
    # Écrire le nouveau fichier de configuration
    config_content = f'''#!/usr/bin/env python3
"""
Configuration de la licence SETRAF
Permet de contrôler le mode de vérification de la licence
"""

# ===== MODES DE LICENCE =====
# "strict"   : La licence est liée à l'empreinte machine (défaut)
# "portable" : La licence peut être utilisée sur plusieurs machines
# "dev"      : Mode développement - pas de vérification
LICENSE_MODE = "{mode}"

# ===== CONFIGURATION EMAIL =====
ADMIN_EMAIL = "nyundumathryme@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ===== OPTIONS DE LICENCE PORTABLE =====
# Si LICENSE_MODE = "portable", permet de définir:
PORTABLE_OPTIONS = {{
    # Nombre maximum de machines autorisées (None = illimité)
    "max_machines": None,
    
    # Vérifier uniquement l'email de l'utilisateur
    "check_email_only": {str(check_email_only)},
    
    # Autoriser le transfert de licence
    "allow_transfer": True,
    
    # Durée de validité de la licence (en jours, None = illimité)
    "validity_days": None
}}

# ===== MODE DÉVELOPPEMENT =====
DEV_MODE = {str(dev_mode)}  # Mettre à True pour désactiver toutes les vérifications
'''
    
    try:
        with open("license_config.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        
        print("\n✅ Configuration mise à jour avec succès!")
        print(f"   Nouveau mode: {mode.upper()}")
        if dev_mode:
            print("   Mode développement: ACTIVÉ")
        print("\n⚠️  Redémarrez l'application pour appliquer les changements")
        return True
    
    except Exception as e:
        print(f"\n❌ Erreur lors de l'écriture de la configuration: {e}")
        return False

def view_license_info():
    """Affiche les informations de licence actuelle"""
    try:
        import json
        if not os.path.exists("license.dat"):
            print("❌ Aucune licence trouvée\n")
            return
        
        with open("license.dat", "r") as f:
            license_data = json.load(f)
        
        print("📄 Informations de licence:")
        print(f"   Utilisateur: {license_data.get('user_name', 'N/A')}")
        print(f"   Email: {license_data.get('user_email', 'N/A')}")
        print(f"   Créée le: {license_data.get('created', 'N/A')}")
        print(f"   Validée: {'Oui' if license_data.get('validated', False) else 'Non'}")
        print(f"   Empreinte machine: {license_data.get('fingerprint', 'N/A')[:16]}...")
        print()
    
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de la licence: {e}\n")

def main():
    print_logo()
    print_current_mode()
    
    while True:
        print("\nOptions:")
        print("  1. Changer le mode de licence")
        print("  2. Voir les informations de licence")
        print("  3. Quitter")
        print()
        
        choice = input("Votre choix: ").strip()
        
        if choice == "1":
            if change_mode():
                break
        elif choice == "2":
            view_license_info()
        elif choice == "3":
            print("\n👋 Au revoir!\n")
            break
        else:
            print("❌ Choix invalide")

if __name__ == "__main__":
    # Changer vers le répertoire du script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
    input("\nAppuyez sur Entrée pour quitter...")
