#!/usr/bin/env python3
"""
🔐 Lanceur du Serveur de Licence UNIQUEMENT
Lance seulement le serveur Node.js de gestion des licences
pour permettre aux nouveaux utilisateurs d'obtenir une licence
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def print_logo():
    """Affiche le logo du serveur de licence"""
    logo = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              🔐 SERVEUR DE DEMANDE DE LICENCE 🔐             ║
    ║                                                              ║
    ║              Pour obtenir votre licence SETRAF               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(logo)

def check_node():
    """Vérifie si Node.js est installé (portable ou système)"""
    # 1. Chercher Node.js portable dans le dossier
    node_portable_paths = [
        os.path.join(os.getcwd(), 'nodejs', 'node.exe'),
        os.path.join(os.path.dirname(os.getcwd()), 'nodejs', 'node.exe'),
        os.path.join(os.getcwd(), '..', 'nodejs', 'node.exe'),
    ]
    
    for node_path in node_portable_paths:
        if os.path.exists(node_path):
            try:
                result = subprocess.run([node_path, '--version'], 
                                      capture_output=True, 
                                      text=True, 
                                      check=True)
                version = result.stdout.strip()
                print(f"✅ Node.js portable {version} détecté")
                return node_path
            except:
                continue
    
    # 2. Chercher Node.js dans le système
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        version = result.stdout.strip()
        print(f"✅ Node.js système {version} détecté")
        return 'node'
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js introuvable (ni portable, ni système)")
        print("   Solution: Téléchargez Node.js portable")
        print("   https://nodejs.org/dist/v24.13.0/node-v24.13.0-win-x64.zip")
        print("   Extrayez dans le dossier 'nodejs' à côté du script")
        return None

def install_node_dependencies(node_cmd):
    """Installe les dépendances Node.js si nécessaire"""
    if not os.path.exists("node_modules"):
        print("📦 Installation des dépendances Node.js...")
        try:
            # Déterminer npm selon le type de node
            if os.path.isabs(node_cmd) and os.path.exists(node_cmd):
                npm_cmd = os.path.join(os.path.dirname(node_cmd), 'npm.cmd')
            else:
                npm_cmd = 'npm'
            
            subprocess.run([npm_cmd, 'install'], check=True, cwd=os.getcwd())
            print("✅ Dépendances installées")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur d'installation des dépendances: {e}")
            return False
    else:
        print("✅ Dépendances Node.js déjà installées")
    return True

def start_license_server(node_cmd):
    """Lance le serveur de licence Node.js"""
    print("\n🔄 Démarrage du Serveur de Licence...")
    print("=" * 70)
    
    try:
        # Lancer le serveur de licence Node.js (license_server.js sur port 4000)
        node_process = subprocess.Popen(
            [node_cmd, 'license_server.js'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )
        
        # Attendre que le serveur démarre
        print("⏳ Attente du démarrage du serveur...")
        time.sleep(4)  # Augmenter le délai pour être sûr
        
        if node_process.poll() is None:
            print("✅ Serveur de Licence lancé avec succès (port 4000)")
            
            # Ouvrir automatiquement le navigateur
            print("\n🌐 Ouverture automatique du navigateur...")
            time.sleep(1)  # Petit délai supplémentaire
            try:
                webbrowser.open('http://localhost:4000', new=2)  # new=2 ouvre dans un nouvel onglet
                print("✅ Navigateur ouvert sur http://localhost:4000")
            except Exception as e:
                print(f"⚠️  Impossible d'ouvrir le navigateur automatiquement: {e}")
                print("   Veuillez ouvrir manuellement: http://localhost:4000")
            
            print("\n" + "=" * 70)
            print("📋 INSTRUCTIONS POUR OBTENIR VOTRE LICENCE :")
            print("=" * 70)
            print("\n1. 📝 Remplissez le formulaire dans le navigateur")
            print("2. 📧 Vérifiez votre email pour recevoir la licence")
            print("3. 🔄 Redémarrez l'application avec la nouvelle licence")
            print("\n" + "=" * 70)
            print("\n⚠️  Appuyez sur Ctrl+C pour arrêter le serveur")
            print("=" * 70)
            
            # Attendre et afficher les logs
            try:
                while True:
                    if node_process.stdout:
                        line = node_process.stdout.readline()
                        if line:
                            print(line, end='')
            except KeyboardInterrupt:
                print("\n\n🛑 Arrêt du serveur de licence...")
                node_process.terminate()
                node_process.wait()
                print("✅ Serveur arrêté")
        else:
            print("❌ Le serveur de licence n'a pas démarré correctement")
            if node_process.stderr:
                stderr = node_process.stderr.read()
                if stderr:
                    print(f"Erreur: {stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Fichier server.js non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du lancement du serveur: {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print_logo()
    
    # Vérifier Node.js
    node_cmd = check_node()
    if not node_cmd:
        print("\n⚠️  Installez Node.js portable pour continuer")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    # Installer les dépendances
    if not install_node_dependencies(node_cmd):
        print("\n❌ Impossible d'installer les dépendances")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    # Lancer le serveur de licence
    if not start_license_server(node_cmd):
        print("\n❌ Échec du lancement du serveur")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du serveur...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
