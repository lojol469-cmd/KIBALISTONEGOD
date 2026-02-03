#!/usr/bin/env python3
"""
Diagnostic Automatique SETRAF
Vérifie tous les composants et donne des solutions
"""

import os
import sys
import platform
import json
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python():
    """Vérifie Python"""
    print_header("🐍 PYTHON")
    print(f"✅ Version: {sys.version.split()[0]}")
    print(f"✅ Executable: {sys.executable}")
    print(f"✅ Plateforme: {platform.system()} {platform.release()}")
    return True

def check_venv():
    """Vérifie l'environnement virtuel"""
    print_header("📦 ENVIRONNEMENT VIRTUEL")
    
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Environnement virtuel non trouvé")
        print("   Solution: Exécutez RECREER_ENVIRONNEMENT.bat")
        return False
    
    activate_script = venv_path / "Scripts" / "activate.bat"
    if not activate_script.exists():
        print("❌ Script d'activation manquant")
        print("   Solution: Recréez l'environnement avec RECREER_ENVIRONNEMENT.bat")
        return False
    
    # Vérifier pyvenv.cfg
    cfg_file = venv_path / "pyvenv.cfg"
    if cfg_file.exists():
        with open(cfg_file, 'r') as f:
            content = f.read()
            print("✅ Environnement virtuel trouvé")
            # Extraire la version
            for line in content.split('\n'):
                if 'version' in line.lower() and '=' in line:
                    print(f"   {line.strip()}")
                if 'home' in line.lower():
                    home = line.split('=')[1].strip()
                    if os.path.exists(home):
                        print(f"✅ Python de base accessible: {home}")
                    else:
                        print(f"⚠️  Python de base non trouvé: {home}")
                        print(f"   (Normal si copié depuis un autre ordinateur)")
    
    return True

def check_license():
    """Vérifie la licence"""
    print_header("🔐 LICENCE")
    
    # Vérifier les fichiers
    license_key = Path("license.key")
    license_dat = Path("license.dat")
    license_config = Path("license_config.py")
    
    if not license_key.exists():
        print("❌ Fichier license.key manquant")
        print("   Solution: Demandez une nouvelle licence")
        return False
    
    if not license_dat.exists():
        print("❌ Fichier license.dat manquant")
        print("   Solution: Demandez une nouvelle licence")
        return False
    
    print("✅ Fichiers de licence présents")
    
    # Lire les données de licence
    try:
        with open(license_dat, 'r') as f:
            data = json.load(f)
        
        print(f"   Utilisateur: {data.get('user_name', 'N/A')}")
        print(f"   Email: {data.get('user_email', 'N/A')}")
        print(f"   Validée: {'Oui' if data.get('validated') else 'Non'}")
        
    except Exception as e:
        print(f"⚠️  Erreur de lecture: {e}")
    
    # Vérifier la configuration
    if license_config.exists():
        try:
            from license_config import LICENSE_MODE, DEV_MODE
            print(f"✅ Mode de licence: {LICENSE_MODE}")
            if DEV_MODE:
                print("⚠️  Mode développement activé")
        except Exception as e:
            print(f"⚠️  Impossible de lire license_config.py: {e}")
    else:
        print("⚠️  Fichier license_config.py manquant")
        print("   La licence fonctionnera en mode STRICT par défaut")
    
    return True

def check_dependencies():
    """Vérifie les dépendances"""
    print_header("📚 DÉPENDANCES")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("⚠️  Fichier requirements.txt manquant")
        return False
    
    print("✅ Fichier requirements.txt trouvé")
    
    # Compter les dépendances
    with open(requirements_file, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
    
    print(f"   {len(lines)} dépendances listées")
    
    # Vérifier quelques packages critiques
    critical_packages = ['streamlit', 'pandas', 'numpy']
    
    try:
        import importlib
        for pkg in critical_packages:
            try:
                importlib.import_module(pkg)
                print(f"   ✅ {pkg}")
            except ImportError:
                print(f"   ❌ {pkg} non installé")
    except Exception as e:
        print(f"   ⚠️  Impossible de vérifier les packages: {e}")
    
    return True

def check_portable_python():
    """Vérifie Python portable"""
    print_header("🔧 PYTHON PORTABLE")
    
    # Chercher dans différents emplacements
    possible_paths = [
        Path("python311"),           # Local (dans protected_excel)
        Path("..") / "python311",    # Niveau parent (SETRAGESTION)
        Path("../..") / "python311",  # Deux niveaux au-dessus
    ]
    
    for path in possible_paths:
        python_exe = path / "python.exe"
        if python_exe.exists():
            print(f"✅ Python portable trouvé: {path.absolute()}")
            print(f"   👉 Recommandation: MEILLEUR emplacement = protected_excel\\python311\\")
            if path.name == "python311" and path.parent.name != "protected_excel":
                print(f"   ⚠️  Considérez de le copier dans protected_excel\\ pour la portabilité")
            return True
    
    print("⚠️  Python portable non trouvé")
    print("   Emplacements recherchés:")
    for path in possible_paths:
        print(f"   - {path.absolute()}")
    print("\n   💡 Pour une portabilité complète, placez python311\\ dans protected_excel\\")
    
    return False

def check_machine_fingerprint():
    """Affiche l'empreinte machine actuelle"""
    print_header("🖥️  EMPREINTE MACHINE")
    
    try:
        from license_check import get_machine_fingerprint
        fingerprint = get_machine_fingerprint()
        print(f"✅ Empreinte actuelle: {fingerprint[:32]}...")
        
        # Comparer avec la licence
        license_dat = Path("license.dat")
        if license_dat.exists():
            with open(license_dat, 'r') as f:
                data = json.load(f)
                stored_fp = data.get('fingerprint', '')
                
                if stored_fp == fingerprint:
                    print("✅ Correspond à la licence actuelle")
                else:
                    print("⚠️  Différente de la licence actuelle")
                    print(f"   Licence: {stored_fp[:32]}...")
                    print("\n   Solutions:")
                    print("   1. Passer en mode PORTABLE (CONFIGURER_LICENCE.bat)")
                    print("   2. Demander une nouvelle licence pour cette machine")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    return True

def check_files():
    """Vérifie les fichiers essentiels"""
    print_header("📁 FICHIERS ESSENTIELS")
    
    essential_files = [
        "app.py",
        "launcher_all_servers.py",
        "license_check.py",
        "requirements.txt"
    ]
    
    all_ok = True
    for file in essential_files:
        path = Path(file)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file} ({size:,} bytes)")
        else:
            print(f"❌ {file} manquant")
            all_ok = False
    
    return all_ok

def print_summary():
    """Affiche un résumé des solutions"""
    print_header("💡 SOLUTIONS RAPIDES")
    
    print("""
1. Pour recréer l'environnement Python :
   > RECREER_ENVIRONNEMENT.bat

2. Pour changer le mode de licence :
   > CONFIGURER_LICENCE.bat

3. Pour lancer l'application en mode portable :
   > cd ..
   > Lanceur_SETRAF_Portable.bat

4. Pour demander une nouvelle licence :
   > python license_check.py

5. Pour installer les dépendances manuellement :
   > call venv\\Scripts\\activate.bat
   > pip install -r requirements.txt
""")

def main():
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║              🔍 DIAGNOSTIC AUTOMATIQUE SETRAF 🔍             ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # Changer vers le répertoire du script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Exécuter tous les checks
    results = {
        "Python": check_python(),
        "Environnement virtuel": check_venv(),
        "Licence": check_license(),
        "Dépendances": check_dependencies(),
        "Python portable": check_portable_python(),
        "Empreinte machine": check_machine_fingerprint(),
        "Fichiers": check_files()
    }
    
    # Résumé
    print_header("📊 RÉSUMÉ")
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    # Solutions
    print_summary()
    
    # Compter les problèmes
    problems = sum(1 for v in results.values() if not v)
    
    if problems == 0:
        print("\n🎉 Tout semble en ordre! L'application devrait fonctionner.")
    else:
        print(f"\n⚠️  {problems} problème(s) détecté(s). Suivez les solutions ci-dessus.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n\nAppuyez sur Entrée pour quitter...")
