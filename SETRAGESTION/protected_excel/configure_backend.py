"""
🔧 Configuration Automatique Backend - SETRAGESTION
Configure l'adresse IP du backend dans le fichier .env
"""

import socket
import os
from pathlib import Path

def get_local_ip():
    """Détecte l'adresse IP locale"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return "127.0.0.1"

def update_env_file():
    """Met à jour le fichier .env avec l'IP locale"""
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("❌ Fichier .env non trouvé!")
        print("   Créez d'abord un fichier .env à partir de .env.example")
        return False
    
    # Lire le fichier .env
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Détecter l'IP locale
    local_ip = get_local_ip()
    
    # Chercher et mettre à jour BACKEND_HOST
    found = False
    new_lines = []
    
    for line in lines:
        if line.startswith('BACKEND_HOST='):
            new_lines.append(f'BACKEND_HOST={local_ip}\n')
            found = True
            print(f"✅ BACKEND_HOST mis à jour: {local_ip}")
        else:
            new_lines.append(line)
    
    # Si BACKEND_HOST n'existe pas, l'ajouter
    if not found:
        new_lines.append(f'\n# Configuration Backend Réseau\n')
        new_lines.append(f'BACKEND_HOST={local_ip}\n')
        print(f"✅ BACKEND_HOST ajouté: {local_ip}")
    
    # Écrire le fichier mis à jour
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return True

def main():
    print("\n" + "="*70)
    print("🔧 CONFIGURATION AUTOMATIQUE BACKEND")
    print("="*70 + "\n")
    
    local_ip = get_local_ip()
    hostname = socket.gethostname()
    
    print(f"📍 Nom de l'ordinateur: {hostname}")
    print(f"📍 Adresse IP locale: {local_ip}")
    print()
    
    print("Cette configuration permettra aux autres ordinateurs")
    print("d'accéder au serveur backend pour l'inscription/connexion.")
    print()
    
    choice = input("Voulez-vous configurer automatiquement l'IP dans .env ? (o/n): ")
    
    if choice.lower() in ['o', 'oui', 'y', 'yes']:
        if update_env_file():
            print("\n✅ Configuration réussie!")
            print(f"\nLes clients peuvent maintenant se connecter à:")
            print(f"   Backend: http://{local_ip}:3000")
            print(f"   Application: http://{local_ip}:8501")
            print("\n⚠️  Redémarrez l'application pour appliquer les changements")
        else:
            print("\n❌ Échec de la configuration")
    else:
        print("\n❌ Configuration annulée")
        print(f"\nPour configurer manuellement, ajoutez dans .env:")
        print(f"BACKEND_HOST={local_ip}")
    
    print("\n" + "="*70)
    input("\nAppuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        input("\nAppuyez sur Entrée pour fermer...")
