import os
import sys
import json
import hashlib
import base64
from pathlib import Path
import getpass

# Code PIN du développeur (hashé pour sécurité)
# Code par défaut: 12345
DEV_PIN_HASH = "8cb2237d0679ca88db6464eac60da96345513964"  # SHA1 de "12345"

LOCK_FILE = "protection.lock"
HIDDEN_DIR = ".protected_files"

def hash_pin(pin):
    """Hash le code PIN"""
    return hashlib.sha1(pin.encode()).hexdigest()

def verify_pin():
    """Vérifie le code PIN du développeur"""
    print("🔐 Authentification requise")
    print()
    
    attempts = 3
    
    for attempt in range(attempts):
        pin = getpass.getpass(f"Entrez le code PIN développeur (5 chiffres) [{attempt + 1}/{attempts}]: ")
        
        if len(pin) != 5 or not pin.isdigit():
            print("❌ Le code PIN doit contenir exactement 5 chiffres")
            continue
        
        if hash_pin(pin) == DEV_PIN_HASH:
            return True
        else:
            remaining = attempts - attempt - 1
            if remaining > 0:
                print(f"❌ Code PIN incorrect. {remaining} tentative(s) restante(s)")
            else:
                print("❌ Code PIN incorrect. Accès refusé!")
    
    return False

def restore_files():
    """Restaure les fichiers sensibles"""
    base_dir = Path(__file__).parent
    hidden_dir = base_dir / HIDDEN_DIR
    
    if not hidden_dir.exists():
        print("⚠️  Aucun fichier protégé trouvé")
        return 0
    
    restored_count = 0
    
    for encoded_file in hidden_dir.iterdir():
        if encoded_file.is_file():
            try:
                # Décoder le nom du fichier
                original_name = base64.b64decode(encoded_file.name.encode()).decode()
                dest = base_dir / original_name
                
                # Lire le contenu encodé
                with open(encoded_file, 'rb') as f:
                    encoded_content = f.read()
                
                # Décoder le contenu
                original_content = base64.b64decode(encoded_content)
                
                # Restaurer le fichier original
                with open(dest, 'wb') as f:
                    f.write(original_content)
                
                # Supprimer le fichier encodé
                encoded_file.unlink()
                
                restored_count += 1
                print(f"🔓 Restauré: {original_name}")
                
            except Exception as e:
                print(f"⚠️  Erreur avec {encoded_file.name}: {e}")
    
    # Supprimer le dossier caché s'il est vide
    try:
        hidden_dir.rmdir()
    except:
        pass
    
    return restored_count

def remove_lock():
    """Supprime le fichier de verrouillage"""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
        print(f"✅ Fichier de verrouillage supprimé: {LOCK_FILE}")

def main():
    """Fonction principale"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║          🔓 DÉVERROUILLAGE DES FICHIERS SENSIBLES 🔓        ║")
    print("║                                                              ║")
    print("║              Accès réservé au développeur                    ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Vérifier si verrouillé
    if not os.path.exists(LOCK_FILE):
        print("ℹ️  Les fichiers ne sont pas verrouillés")
        return
    
    # Vérifier le code PIN
    if not verify_pin():
        print("\n❌ Authentification échouée. Accès refusé!")
        return
    
    print("\n✅ Authentification réussie!")
    print("\n🔄 Déverrouillage en cours...\n")
    
    # Restaurer les fichiers
    restored = restore_files()
    
    # Supprimer le verrouillage
    remove_lock()
    
    print(f"\n✅ {restored} fichier(s) restauré(s) avec succès!")
    
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║            ✅ DÉVERROUILLAGE TERMINÉ ✅                      ║")
    print("║                                                              ║")
    print("║  Les fichiers sensibles sont maintenant accessibles.        ║")
    print("║                                                              ║")
    print("║  ⚠️  N'oubliez pas de re-verrouiller après utilisation!     ║")
    print("║     Exécutez: VERROUILLER_FICHIERS.bat                      ║")
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
