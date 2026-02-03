#!/usr/bin/env python3
"""
🌟 Lanceur Multi-Serveurs pour Application Excel
Lance simultanément les serveurs principaux :
- MariaDB Database Server
- Serveur Node.js Backend (Express)
- Application Excel d'Analyse (Streamlit)
"""

import subprocess
import sys
import os
import time
import socket
from pathlib import Path

# ===== VÉRIFICATION DE LICENCE =====
try:
    import license_check
    if not license_check.check_license():
        license_check.show_license_error()
    print("✅ Vérification de licence réussie")
except ImportError:
    print("⚠️  Module de licence non trouvé. Continuation...")
except Exception as e:
    print(f"⚠️  Erreur licence: {e}. Continuation...")

# ===== VÉRIFICATION D'INTÉGRITÉ =====
try:
    from integrity_checker import IntegrityChecker
    integrity_checker = IntegrityChecker()
    if not integrity_checker.check_integrity():
        print("❌ Violation d'intégrité détectée. Arrêt.")
        sys.exit(1)
    print("✅ Intégrité vérifiée")
except ImportError:
    print("⚠️  Vérificateur d'intégrité non trouvé. Continuation...")
except Exception as e:
    print(f"⚠️  Erreur intégrité: {e}. Continuation...")

def print_logo():
    """Affiche le logo ASCII de l'application"""
    logo = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                🚀 LANCEUR MULTI-SERVEURS 🚀                  ║
    ║                                                              ║
    ║              📊  Application Excel d'Analyse Avancée         ║
    ║              🔧  Serveur Backend Node.js                     ║
    ║              🗄️   Base de Données SQLite (Optimisée)          ║
    ║                                                              ║
    ║              Technologies Intégrées:                         ║
    ║              • SQLite - Base de données rapide               ║
    ║              • Node.js/Express - API Backend                 ║
    ║              • Streamlit - Interface Web                     ║
    ║              • Cloudinary - Stockage Fichiers                ║
    ║              • Nodemailer - Envoi d'emails                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(logo)

def get_local_ip():
    """Détecte l'adresse IP locale de l'appareil"""
    try:
        # Créer une connexion UDP (pas besoin qu'elle aboutisse)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        # Fallback si détection échoue
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return "127.0.0.1"

def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        return False
    print(f"✅ Python {sys.version.split()[0]} détecté")
    return True

def get_base_dir():
    """Obtient le répertoire de base (pour l'exécutable bundled ou portable)"""
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        return Path(sys.executable).parent
    else:
        # Running in normal Python environment
        return Path(__file__).parent

def get_node_executable():
    """Trouve l'exécutable Node.js portable ou système"""
    base_dir = get_base_dir()
    
    # Chemins possibles pour Node.js portable
    possible_node_paths = [
        base_dir / "node-v24.13.0-win-x64" / "node.exe",
        base_dir / "node_modules" / ".bin" / "node.exe",
        base_dir.parent / "node-v24.13.0-win-x64" / "node.exe",
    ]
    
    # Chercher Node.js portable
    for node_path in possible_node_paths:
        if node_path.exists():
            print(f"✅ Node.js portable trouvé: {node_path}")
            return str(node_path)
    
    # Fallback: utiliser node du système
    print("⚠️ Node.js portable non trouvé, utilisation du système")
    return "node"

def get_mariadb_dir():
    """Obtient le répertoire contenant MariaDB (peut être différent du répertoire de base)"""
    current_dir = Path(__file__).parent

    # Chercher start_mariadb.bat dans différents emplacements possibles
    possible_paths = [
        current_dir / "start_mariadb.bat",                    # Même répertoire
        current_dir.parent / "start_mariadb.bat",            # Répertoire parent
        current_dir / "mariadb_portable" / "start_mariadb.bat", # Sous-dossier mariadb_portable
        current_dir.parent / "mariadb_portable" / "start_mariadb.bat" # Parent/mariadb_portable
    ]

    for path in possible_paths:
        if path.exists():
            return path.parent

    # Fallback: retourner le répertoire courant
    return current_dir

def launch_mariadb():
    """Lance le serveur MariaDB"""
    mariadb_dir = get_mariadb_dir()
    bat_path = mariadb_dir / "start_mariadb.bat"
    if not bat_path.exists():
        print(f"❌ Fichier MariaDB non trouvé: {bat_path}")
        return False

    print("\n🔄 Démarrage de MariaDB...")
    try:
        process = subprocess.Popen([str(bat_path)], cwd=mariadb_dir)
        time.sleep(3)  # Attendre un peu
        if process.poll() is None:
            print("✅ MariaDB lancé avec succès")
            return True
        else:
            print("❌ MariaDB s'est arrêté immédiatement")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du lancement de MariaDB: {e}")
        return False

def launch_node_server():
    """Lance le serveur Node.js"""
    base_dir = get_base_dir()

    # Chercher server.js dans plusieurs emplacements
    possible_server_paths = [
        base_dir / "server.js",
        base_dir / "server" / "server.js",
        base_dir.parent / "server.js"
    ]

    server_path = None
    for path in possible_server_paths:
        if path.exists():
            server_path = path
            break

    if not server_path:
        print(f"❌ Serveur Node.js non trouvé dans les emplacements recherchés")
        return False

    print("\n🔄 Démarrage du Serveur Node.js...")
    node_exe = get_node_executable()
    if node_exe:
        print(f"✅ Node.js portable trouvé: {node_exe}")
    else:
        print("⚠️ Node.js portable non trouvé, utilisation de Node.js système")
        node_exe = "node"

    try:
        process = subprocess.Popen([str(node_exe), str(server_path)], cwd=server_path.parent,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        
        # Attendre que le fichier server_info.json soit créé
        server_info_path = base_dir / "server_info.json"
        max_wait = 10  # Attendre maximum 10 secondes
        waited = 0
        
        while waited < max_wait:
            time.sleep(0.5)
            waited += 0.5
            
            if server_info_path.exists():
                # Lire les informations du serveur
                try:
                    import json
                    with open(server_info_path, 'r') as f:
                        server_info = json.load(f)
                    port = server_info.get('port', 3000)
                    local_ip = server_info.get('localIP', '127.0.0.1')
                    print(f"✅ Serveur Node.js lancé avec succès sur le port {port}")
                    print(f"   • URL locale: http://localhost:{port}")
                    print(f"   • URL réseau: http://{local_ip}:{port}")
                    return True
                except Exception as e:
                    print(f"⚠️ Fichier server_info.json créé mais illisible: {e}")
            
            if process.poll() is not None:
                print("❌ Serveur Node.js s'est arrêté immédiatement (port occupé ?)")
                return False
        
        # Si on arrive ici, le serveur a démarré mais le fichier n'a pas été créé
        if process.poll() is None:
            print("✅ Serveur Node.js lancé (fichier server_info.json non créé)")
            return True
        else:
            print("❌ Serveur Node.js s'est arrêté immédiatement")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du lancement du Serveur Node.js: {e}")
        return False

    print("\n🔄 Démarrage du Serveur Node.js...")
    try:
        node_exe = get_node_executable()
        process = subprocess.Popen([node_exe, str(server_path)], cwd=server_path.parent, 
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        time.sleep(3)  # Attendre que le serveur démarre
        if process.poll() is None:
            print("✅ Serveur Node.js lancé avec succès")
            return True
        else:
            print("❌ Serveur Node.js s'est arrêté immédiatement (port occupé ?)")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du lancement du Serveur Node.js: {e}")
        print(f"   💡 Vérifiez que Node.js est disponible")
        return False

def launch_license_server():
    """Lance le serveur de licence"""
    import socket
    base_dir = get_base_dir()
    license_server_path = base_dir / "license_server.js"

    if not license_server_path.exists():
        print("⚠️ Serveur de licence non trouvé, fonctionnalité limitée")
        return False

    # Vérifier si le serveur est déjà en cours d'exécution
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 4000))
        sock.close()
        if result == 0:
            print("✅ Serveur de Licence déjà en cours d'exécution (port 4000)")
            return True
    except:
        pass

    print("\n🔄 Démarrage du Serveur de Licence...")
    try:
        node_exe = get_node_executable()
        process = subprocess.Popen([node_exe, str(license_server_path)], cwd=base_dir,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        time.sleep(2)  # Attendre que le serveur démarre
        if process.poll() is None:
            print("✅ Serveur de Licence lancé avec succès (port 4000)")
            return True
        else:
            print("❌ Serveur de Licence s'est arrêté immédiatement")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du lancement du Serveur de Licence: {e}")
        return False

def launch_excel_app():
    """Lance l'application Excel (Streamlit)"""
    base_dir = get_base_dir()

    # Chercher app.py dans plusieurs emplacements
    possible_app_paths = [
        base_dir / "app.py",
        base_dir.parent / "app.py"
    ]

    app_path = None
    for path in possible_app_paths:
        if path.exists():
            app_path = path
            break

    if not app_path:
        print(f"❌ Application Excel non trouvée dans les emplacements recherchés")
        return False

    print("\n🔄 Démarrage de l'Application Excel...")

    try:
        # Configurer Streamlit pour écouter sur toutes les interfaces (0.0.0.0)
        # Cela permet l'accès depuis d'autres machines sur le réseau
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", "8501", 
            "--server.address", "0.0.0.0",  # Écouter sur toutes les interfaces
            "--server.headless", "true"  # Mode sans navigateur auto
        ], cwd=app_path.parent)
        time.sleep(3)  # Attendre que Streamlit démarre
        if process.poll() is None:
            print("✅ Application Excel lancée avec succès")
            return True
        else:
            print("❌ Application Excel s'est arrêtée immédiatement")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du lancement de l'Application Excel: {e}")
        return False

def main():
    """Fonction principale"""
    print_logo()

    if not check_python_version():
        return

    base_dir = get_base_dir()
    print(f"📁 Répertoire de base: {base_dir}")

    print("\n🚀 Lancement des serveurs en cours...\n")

    # Lancer le serveur de licence
    license_ok = launch_license_server()

    # Plus de MariaDB - utilisation de SQLite uniquement
    mariadb_ok = True  # Simuler succès car on n'utilise plus MariaDB
    print("✅ Base de données SQLite (pas de serveur MariaDB requis)")

    # Lancer le serveur Node.js
    node_ok = launch_node_server()

    # Attendre un peu pour le serveur Node
    if node_ok:
        time.sleep(3)

    # Lancer l'application Streamlit
    excel_ok = launch_excel_app()

    print("\n" + "="*60)
    print("📋 STATUT DES SERVEURS:")
    print(f"   Serveur de Licence: {'✅ OK' if license_ok else '❌ ÉCHEC'}")
    print(f"   Base de données: {'✅ OK (SQLite)' if mariadb_ok else '❌ ÉCHEC'}")
    print(f"   Serveur Node.js: {'✅ OK' if node_ok else '❌ ÉCHEC'}")
    print(f"   App Excel: {'✅ OK' if excel_ok else '❌ ÉCHEC'}")

    # Détecter l'adresse IP locale
    local_ip = get_local_ip()
    
    if all([license_ok, mariadb_ok, node_ok, excel_ok]):
        print("\n🎉 Tous les serveurs ont été lancés avec succès!")
        print("\n🌐 ADRESSES D'ACCÈS:")
        print("\n📱 Depuis CET ordinateur:")
        print(f"   • Application Excel: http://localhost:8501")
        print(f"   • API Backend: http://localhost:3000")
        print(f"   • Serveur de Licence: http://localhost:4000")
        print("\n🌍 Depuis UN AUTRE ordinateur sur le réseau:")
        print(f"   • Application Excel: http://{local_ip}:8501")
        print(f"   • API Backend: http://{local_ip}:3000")
        print(f"   • Serveur de Licence: http://{local_ip}:4000")
        print(f"\n📍 Adresse IP de cette machine: {local_ip}")
        print("\n💡 Gardez ce terminal ouvert pour maintenir les serveurs actifs.")
        print("\n🔥 IMPORTANT: Partagez l'adresse IP ci-dessus avec les autres utilisateurs!")
    else:
        print("\n⚠️ Certains serveurs n'ont pas pu être lancés. Vérifiez les erreurs ci-dessus.")

    # Lancer l'icône de la barre des tâches
    try:
        subprocess.Popen([sys.executable, 'tray_icon.py'], cwd=base_dir)
        print("🔔 Icône de la barre des tâches activée")
    except Exception as e:
        print(f"⚠️ Impossible de lancer l'icône: {e}")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()