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
from pathlib import Path

def print_logo():
    """Affiche le logo ASCII de l'application"""
    logo = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                🚀 LANCEUR MULTI-SERVEURS 🚀                  ║
    ║                                                              ║
    ║              📊  Application Excel d'Analyse Avancée         ║
    ║              🔧  Serveur Backend Node.js                     ║
    ║              🗄️   Base de Données MariaDB                     ║
    ║                                                              ║
    ║              Technologies Intégrées:                         ║
    ║              • MariaDB - Base de données                     ║
    ║              • Node.js/Express - API Backend                 ║
    ║              • Streamlit - Interface Web                     ║
    ║              • Cloudinary - Stockage Fichiers                ║
    ║              • Nodemailer - Envoi d'emails                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(logo)

def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        return False
    print(f"✅ Python {sys.version.split()[0]} détecté")
    return True

def launch_mariadb():
    """Lance le serveur MariaDB"""
    bat_path = Path(__file__).parent.parent / "start_mariadb.bat"
    if not bat_path.exists():
        print(f"❌ Fichier MariaDB non trouvé: {bat_path}")
        return False

    print("\n🔄 Démarrage de MariaDB...")
    try:
        process = subprocess.Popen([str(bat_path)], cwd=bat_path.parent)
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
    server_path = Path(__file__).parent / "server.js"
    if not server_path.exists():
        print(f"❌ Serveur Node.js non trouvé: {server_path}")
        return False

    print("\n🔄 Démarrage du Serveur Node.js...")
    try:
        process = subprocess.Popen(["node", str(server_path)], cwd=server_path.parent)
        time.sleep(3)  # Attendre que le serveur démarre
        if process.poll() is None:
            print("✅ Serveur Node.js lancé avec succès")
            return True
        else:
            print("❌ Serveur Node.js s'est arrêté immédiatement (port occupé ?)")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du lancement du Serveur Node.js: {e}")
        return False

def launch_excel_app():
    """Lance l'application Excel"""
    app_path = Path(__file__).parent / "app.py"
    if not app_path.exists():
        print(f"❌ Application Excel non trouvée: {app_path}")
        return False

    print("\n🔄 Démarrage de l'Application Excel...")
    try:
        process = subprocess.Popen(["streamlit", "run", str(app_path)], cwd=app_path.parent)
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

    print("\n🚀 Lancement des serveurs en cours...\n")

    # Lancer MariaDB en premier
    mariadb_ok = launch_mariadb()

    # Attendre un peu pour MariaDB
    if mariadb_ok:
        print("⏳ Attente du démarrage de MariaDB...")
        time.sleep(10)

    # Lancer le serveur Node.js
    node_ok = launch_node_server()

    # Attendre un peu pour le serveur Node
    if node_ok:
        time.sleep(3)

    # Lancer l'application Streamlit
    excel_ok = launch_excel_app()

    print("\n" + "="*60)
    print("📋 STATUT DES SERVEURS:")
    print(f"   MariaDB: {'✅ OK' if mariadb_ok else '❌ ÉCHEC'}")
    print(f"   Serveur Node.js: {'✅ OK' if node_ok else '❌ ÉCHEC'}")
    print(f"   App Excel: {'✅ OK' if excel_ok else '❌ ÉCHEC'}")

    if all([mariadb_ok, node_ok, excel_ok]):
        print("\n🎉 Tous les serveurs ont été lancés avec succès!")
        print("🌐 Applications disponibles sur:")
        print("   • Application Excel: http://localhost:8501")
        print("   • API Backend: http://localhost:3000")
        print("\n💡 Gardez ce terminal ouvert pour maintenir les serveurs actifs.")
    else:
        print("\n⚠️ Certains serveurs n'ont pas pu être lancés. Vérifiez les erreurs ci-dessus.")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()