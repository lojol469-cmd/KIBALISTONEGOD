#!/usr/bin/env python3
"""
🏗️ Script de Build pour Launcher All Servers Portable
Crée un exécutable oneDir avec PyInstaller
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Affiche l'en-tête du build"""
    header = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                🏗️  BUILD LAUNCHER PORTABLE 🏗️                ║
    ║                                                              ║
    ║              📦 Création d'un exécutable oneDir              ║
    ║              🚀 Tous serveurs intégrés                       ║
    ║              🔧 Lancement en un clic                          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(header)

def check_pyinstaller():
    """Vérifie que PyInstaller est installé"""
    try:
        import PyInstaller
        print("✅ PyInstaller détecté")
        return True
    except ImportError:
        print("❌ PyInstaller non installé")
        print("   Installation automatique...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installé")
            return True
        except Exception as e:
            print(f"❌ Impossible d'installer PyInstaller: {e}")
            return False

def build_executable():
    """Construit l'exécutable avec PyInstaller"""
    print("\n🔨 Construction de l'exécutable...")

    # Chemin vers le spec file
    spec_path = Path("launcher_all_servers.spec")

    if not spec_path.exists():
        print(f"❌ Fichier spec non trouvé: {spec_path}")
        return False

    try:
        # Lancer PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(spec_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Exécutable créé avec succès!")
            print(f"   📁 Dossier: dist/launcher_all_servers/")
            return True
        else:
            print("❌ Erreur lors de la construction:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_launcher_script():
    """Crée un script de lancement pour Windows"""
    launcher_content = '''@echo off
echo ========================================
echo   🚀 Lancement Multi-Serveurs Portable
echo ========================================
cd /d "%~dp0"
launcher_all_servers.exe
pause
'''

    launcher_path = Path("dist/launcher_all_servers/start_launcher.bat")
    try:
        launcher_path.parent.mkdir(parents=True, exist_ok=True)
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        print("✅ Script de lancement créé: start_launcher.bat")
    except Exception as e:
        print(f"⚠️ Impossible de créer le script de lancement: {e}")

def main():
    """Fonction principale"""
    print_header()

    if not check_pyinstaller():
        return

    if not build_executable():
        return

    create_launcher_script()

    print("\n" + "="*60)
    print("🎉 Build terminé!")
    print("\n📦 Pour utiliser l'application portable:")
    print("   1. Allez dans le dossier: dist/launcher_all_servers/")
    print("   2. Double-cliquez sur: start_launcher.bat")
    print("   3. Ou lancez directement: launcher_all_servers.exe")
    print("\n💡 Le dossier peut être copié sur n'importe quel PC Windows")
    print("   (Node.js et MariaDB doivent être installés sur le système cible)")
    print("="*60)

if __name__ == "__main__":
    main()