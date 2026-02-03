import os
import sys
import json
import hashlib
import base64
from pathlib import Path
from datetime import datetime

# Code PIN du développeur (hashé pour sécurité)
# Code par défaut: 12345
DEV_PIN_HASH = "8cb2237d0679ca88db6464eac60da96345513964"  # SHA1 de "12345"

# Fichiers et dossiers sensibles à protéger
SENSITIVE_ITEMS = [
    "license_check.py",
    "license_manager.py",
    "license_config.py",
    "license_server.js",
    "server.js",
    ".env",
    "integrity_checker.py",
    "config_licence.py",
    "create_build_spec.py",
    "build_portable.py",
    "build_launcher_portable.py"
]

LOCK_FILE = "protection.lock"
HIDDEN_DIR = ".protected_files"

def hash_pin(pin):
    """Hash le code PIN"""
    return hashlib.sha1(pin.encode()).hexdigest()

def create_lock():
    """Crée le fichier de verrouillage"""
    lock_data = {
        "locked": True,
        "locked_at": datetime.now().isoformat(),
        "locked_by": "developer"
    }
    
    with open(LOCK_FILE, 'w') as f:
        json.dump(lock_data, f, indent=2)
    
    print(f"✅ Fichier de verrouillage créé: {LOCK_FILE}")

def hide_sensitive_files():
    """Cache les fichiers sensibles"""
    base_dir = Path(__file__).parent
    hidden_dir = base_dir / HIDDEN_DIR
    
    # Créer le dossier caché s'il n'existe pas
    hidden_dir.mkdir(exist_ok=True)
    
    # Rendre le dossier caché sur Windows
    try:
        import ctypes
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ctypes.windll.kernel32.SetFileAttributesW(str(hidden_dir), FILE_ATTRIBUTE_HIDDEN)
    except:
        pass
    
    protected_count = 0
    
    for item in SENSITIVE_ITEMS:
        source = base_dir / item
        
        if source.exists():
            # Encoder le nom du fichier
            encoded_name = base64.b64encode(item.encode()).decode()
            dest = hidden_dir / encoded_name
            
            # Lire le contenu
            try:
                if source.is_file():
                    with open(source, 'rb') as f:
                        content = f.read()
                    
                    # Encoder le contenu (simple obfuscation)
                    encoded_content = base64.b64encode(content)
                    
                    # Sauvegarder dans le dossier caché
                    with open(dest, 'wb') as f:
                        f.write(encoded_content)
                    
                    # Créer un fichier placeholder
                    with open(source, 'w', encoding='utf-8') as f:
                        f.write("# FICHIER PROTÉGÉ - Accès réservé au développeur\n")
                        f.write("# Pour déverrouiller, exécutez DEVERROUILLER_FICHIERS.bat avec le code PIN\n")
                    
                    protected_count += 1
                    print(f"🔒 Protégé: {item}")
            except Exception as e:
                print(f"⚠️  Erreur avec {item}: {e}")
    
    print(f"\n✅ {protected_count} fichiers protégés avec succès!")

def main():
    """Fonction principale"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║            🔒 VERROUILLAGE DES FICHIERS SENSIBLES 🔒         ║")
    print("║                                                              ║")
    print("║              Protection niveau développeur                   ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Vérifier si déjà verrouillé
    if os.path.exists(LOCK_FILE):
        print("⚠️  Les fichiers sont déjà verrouillés!")
        response = input("Voulez-vous re-verrouiller? (o/n): ")
        if response.lower() != 'o':
            print("❌ Opération annulée")
            return
    
    # Demander confirmation
    print("⚠️  ATTENTION: Cette opération va protéger les fichiers sensibles.")
    print("   Vous aurez besoin du code PIN développeur pour les déverrouiller.")
    print()
    
    confirm = input("Confirmer le verrouillage? (o/n): ")
    
    if confirm.lower() != 'o':
        print("❌ Opération annulée")
        return
    
    print("\n🔄 Verrouillage en cours...\n")
    
    # Cacher les fichiers sensibles
    hide_sensitive_files()
    
    # Créer le fichier de verrouillage
    create_lock()
    
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║              ✅ VERROUILLAGE TERMINÉ ✅                      ║")
    print("║                                                              ║")
    print("║  Les fichiers sensibles sont maintenant protégés.           ║")
    print("║                                                              ║")
    print("║  Pour déverrouiller:                                         ║")
    print("║  1. Exécutez DEVERROUILLER_FICHIERS.bat                     ║")
    print("║  2. Entrez le code PIN développeur (5 chiffres)             ║")
    print("║                                                              ║")
    print("║  ⚠️  IMPORTANT: Conservez le code PIN en lieu sûr!          ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")

if __name__ == "__main__":
    try:
        main()
        input("\nAppuyez sur Entrée pour quitter...")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        input("\nAppuyez sur Entrée pour quitter...")
        sys.exit(1)
