#!/usr/bin/env python3
"""
🏗️ Script de Build pour Application Excel Portable
Crée une version portable complète avec tous les serveurs et dépendances
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

def print_header():
    """Affiche l'en-tête du build"""
    header = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                🏗️  BUILD APPLICATION PORTABLE 🏗️              ║
    ║                                                              ║
    ║              📦 Création d'une version autonome              ║
    ║              🔧 Tous serveurs et dépendances inclus          ║
    ║              🚀 Lancement en un clic                          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(header)

def create_build_directory():
    """Crée le dossier de build"""
    build_dir = Path("build_portable")
    if build_dir.exists():
        print(f"🗑️ Suppression de l'ancien build: {build_dir}")
        try:
            shutil.rmtree(build_dir)
        except Exception as e:
            print(f"⚠️ Impossible de supprimer l'ancien build ({e}), création d'un nouveau nom")
            import time
            build_dir = Path(f"build_portable_{int(time.time())}")

    build_dir.mkdir()
    print(f"📁 Dossier de build créé: {build_dir}")
    return build_dir

def copy_excel_app(build_dir):
    """Copie l'application Excel"""
    print("\n📋 Copie de l'application Excel...")

    excel_dir = build_dir / "excel"
    excel_dir.mkdir()

    # Fichiers à copier
    files_to_copy = [
        "app.py", "server.js", "serverbackup.js", "launcher_all_servers.py",
        "package.json", "package-lock.json", "requirements.txt",
        "background_b64.txt", "video_b64.txt", "LOGO VECTORISE PNG.png",
        "app_exe.spec", "diagnostic_streamlit.bat", "fix_background.py",
        "launch.bat", "launch.py", "launch.spec", "pyrightconfig.json",
        "README.md", "Dockerfile", ".env"
    ]

    for file in files_to_copy:
        src = Path(".") / file
        if src.exists():
            shutil.copy2(src, excel_dir / file)
            print(f"  ✅ {file}")

    # Copier les dossiers
    dirs_to_copy = ["static", "uploads", "logs_audit", "deploy_server"]
    for dir_name in dirs_to_copy:
        src_dir = Path(".") / dir_name
        if src_dir.exists():
            shutil.copytree(src_dir, excel_dir / dir_name, dirs_exist_ok=True)
            print(f"  ✅ {dir_name}/")

    return excel_dir

def copy_mariadb(build_dir):
    """Copie MariaDB portable"""
    print("\n🗄️ Copie de MariaDB portable...")

    mariadb_src = Path("../mariadb_portable")
    mariadb_dst = build_dir / "mariadb_portable"

    if mariadb_src.exists():
        shutil.copytree(mariadb_src, mariadb_dst, dirs_exist_ok=True)
        print("  ✅ MariaDB portable copié")

        # Copier le script de lancement
        start_script = Path("../start_mariadb.bat")
        if start_script.exists():
            shutil.copy2(start_script, build_dir / "start_mariadb.bat")
            print("  ✅ Script de lancement MariaDB copié")
    else:
        print("  ⚠️ MariaDB portable non trouvé, création d'un placeholder")
        mariadb_dst.mkdir()
        (mariadb_dst / "README_MARIADB.txt").write_text("MariaDB portable à installer ici")

def create_python_venv(build_dir):
    """Crée un environnement virtuel Python avec toutes les dépendances"""
    print("\n🐍 Création de l'environnement virtuel Python...")

    venv_dir = build_dir / "venv"
    excel_dir = build_dir / "excel"

    # Créer l'environnement virtuel
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    print("  ✅ Environnement virtuel créé")

    # Installer les dépendances
    pip_exe = venv_dir / "Scripts" / "pip.exe"
    requirements_file = excel_dir / "requirements.txt"

    if requirements_file.exists():
        print("  📦 Installation des dépendances Python...")
        subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
        print("  ✅ Dépendances Python installées")

    # Installer Streamlit spécifiquement
    subprocess.run([str(pip_exe), "install", "streamlit"], check=True)
    print("  ✅ Streamlit installé")

    return venv_dir

def install_node_dependencies(build_dir):
    """Installe les dépendances Node.js"""
    print("\n📦 Installation des dépendances Node.js...")

    excel_dir = build_dir / "excel"

    # Vérifier si package.json existe
    package_json = excel_dir / "package.json"
    if package_json.exists():
        # Installer npm si nécessaire
        try:
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
        except:
            print("  ⚠️ npm non trouvé, installation des dépendances Node.js ignorée")
            return

        # Installer les dépendances
        os.chdir(excel_dir)
        subprocess.run(["npm", "install"], check=True)
        os.chdir("..")
        print("  ✅ Dépendances Node.js installées")
    else:
        print("  ⚠️ package.json non trouvé")

def create_portable_launcher(build_dir):
    """Crée le lanceur portable"""
    print("\n🚀 Création du lanceur portable...")

    launcher_content = '''#!/usr/bin/env python3
"""
🌟 Lanceur Portable - Application Excel Complète
Version autonome avec tous les serveurs intégrés
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def print_logo():
    """Affiche le logo de l'application"""
    logo = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              🚀 APPLICATION EXCEL PORTABLE 🚀                ║
    ║                                                              ║
    ║              📊 Analyse Avancée - Version Autonome           ║
    ║              🔧 Tous serveurs intégrés                       ║
    ║              🗄️  Base de données incluse                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(logo)

def get_base_dir():
    """Obtient le répertoire de base de l'application"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent

def launch_mariadb(base_dir):
    """Lance MariaDB portable"""
    mariadb_bin = base_dir / "mariadb_portable" / "mariadb-11.4.2-winx64" / "bin" / "mariadbd.exe"
    data_dir = base_dir / "mariadb_portable" / "mariadb-11.4.2-winx64" / "data"
    
    if mariadb_bin.exists():
        print("\\n🔄 Démarrage de MariaDB...")
        try:
            process = subprocess.Popen([
                str(mariadb_bin),
                "--datadir=" + str(data_dir),
                "--port=3307"
            ], cwd=mariadb_bin.parent)
            time.sleep(5)
            if process.poll() is None:
                print("✅ MariaDB lancé")
                return True
        except Exception as e:
            print(f"❌ Erreur MariaDB: {e}")
    else:
        print("⚠️ MariaDB non trouvé - mode sans base de données")
    return False

def launch_node_server(base_dir):
    """Lance le serveur Node.js"""
    server_js = base_dir / "excel" / "server.js"
    if server_js.exists():
        print("\\n🔄 Démarrage du serveur Node.js...")
        try:
            process = subprocess.Popen(["node", str(server_js)], cwd=base_dir / "excel")
            time.sleep(3)
            if process.poll() is None:
                print("✅ Serveur Node.js lancé")
                return True
        except Exception as e:
            print(f"❌ Erreur serveur Node.js: {e}")
    return False

def launch_excel_app(base_dir):
    """Lance l'application Excel"""
    app_py = base_dir / "excel" / "app.py"
    venv_python = base_dir / "venv" / "Scripts" / "python.exe"

    if app_py.exists() and venv_python.exists():
        print("\\n🔄 Démarrage de l'application Excel...")
        try:
            process = subprocess.Popen([
                str(venv_python), "-m", "streamlit", "run", str(app_py),
                "--server.port", "8502", "--server.address", "localhost"
            ], cwd=base_dir / "excel")
            time.sleep(3)
            if process.poll() is None:
                print("✅ Application Excel lancée")
                return True
        except Exception as e:
            print(f"❌ Erreur application Excel: {e}")
    return False

def main():
    """Fonction principale"""
    print_logo()

    base_dir = get_base_dir()
    print(f"📁 Répertoire de base: {base_dir}")

    print("\\n🚀 Lancement des serveurs...\\n")

    # Lancer MariaDB
    mariadb_ok = launch_mariadb(base_dir)

    # Attendre MariaDB
    if mariadb_ok:
        time.sleep(10)

    # Lancer Node.js
    node_ok = launch_node_server(base_dir)

    # Attendre Node.js
    if node_ok:
        time.sleep(3)

    # Lancer l'application Excel
    excel_ok = launch_excel_app(base_dir)

    print("\\n" + "="*60)
    print("📋 STATUT DES SERVEURS:")
    print(f"   MariaDB: {'✅ OK' if mariadb_ok else '❌ ÉCHEC'}")
    print(f"   Serveur Node.js: {'✅ OK' if node_ok else '❌ ÉCHEC'}")
    print(f"   App Excel: {'✅ OK' if excel_ok else '❌ ÉCHEC'}")

    if excel_ok:
        print("\\n🎉 Application lancée avec succès!")
        print("🌐 Accès:")
        print("   • Application Excel: http://localhost:8501")
        if node_ok:
            print("   • API Backend: http://localhost:3000")
        print("\\n💡 Gardez ce terminal ouvert pour maintenir les serveurs actifs.")
        print("\\n🔄 Appuyez sur Ctrl+C pour arrêter tous les serveurs.")
    else:
        print("\\n⚠️ L'application n'a pas pu démarrer correctement.")

    print("\\n" + "="*60)

    # Garder le terminal ouvert
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\n\\n🛑 Arrêt des serveurs...")
        sys.exit(0)

if __name__ == "__main__":
    main()
'''

    launcher_path = build_dir / "LAUNCH_PORTABLE.py"
    launcher_path.write_text(launcher_content, encoding='utf-8')
    print("  ✅ Lanceur portable créé")

    # Créer un fichier batch pour Windows
    batch_content = '''@echo off
chcp 65001 >nul
echo.
echo 🚀 Démarrage de l'Application Excel Portable...
echo.
venv\\Scripts\\python.exe LAUNCH_PORTABLE.py
pause
'''

    batch_path = build_dir / "LAUNCH_PORTABLE.bat"
    batch_path.write_text(batch_content, encoding='utf-8')
    print("  ✅ Script batch Windows créé")

def create_readme(build_dir):
    """Crée le fichier README pour le build"""
    print("\n📖 Création du README...")

    readme_content = '''# 🚀 Application Excel Portable

Version autonome complète avec tous les serveurs intégrés.

## 📋 Description

Cette version portable contient :
- ✅ Application Excel d'analyse avancée (Streamlit)
- ✅ Serveur backend Node.js/Express
- ✅ Base de données MariaDB
- ✅ Toutes les dépendances Python et Node.js
- ✅ Environnement virtuel Python isolé

## 🚀 Lancement

### Windows
Double-cliquez sur `LAUNCH_PORTABLE.bat`

### Manuel
```bash
python LAUNCH_PORTABLE.py
```

## 🌐 Accès aux applications

- **Application Excel** : http://localhost:8501
- **API Backend** : http://localhost:3000 (si disponible)

## 📁 Structure

```
build_portable/
├── LAUNCH_PORTABLE.py      # Lanceur Python
├── LAUNCH_PORTABLE.bat     # Lanceur Windows
├── excel/                  # Application Excel
│   ├── app.py
│   ├── server.js
│   └── ...
├── venv/                   # Environnement virtuel Python
├── mariadb_portable/       # Base de données MariaDB
└── start_mariadb.bat       # Script MariaDB
```

## ⚠️ Prérequis

- Windows 10/11
- Aucun logiciel supplémentaire requis
- Tout est inclus dans ce dossier

## 🛑 Arrêt

Pour arrêter tous les serveurs :
- Fermez le terminal (Ctrl+C)
- Ou fermez simplement la fenêtre

## 📞 Support

En cas de problème, vérifiez :
1. Que tous les fichiers sont présents
2. Que les ports 8501 et 3000 sont libres
3. Que l'antivirus n'a pas bloqué l'application

---
*Build créé automatiquement - Version portable*
'''

    readme_path = build_dir / "README_PORTABLE.md"
    readme_path.write_text(readme_content, encoding='utf-8')
    print("  ✅ README créé")

def main():
    """Fonction principale du build"""
    print_header()

    try:
        # Créer le dossier de build
        build_dir = create_build_directory()

        # Copier l'application Excel
        excel_dir = copy_excel_app(build_dir)

        # Copier MariaDB
        copy_mariadb(build_dir)

        # Créer l'environnement virtuel Python
        create_python_venv(build_dir)

        # Installer les dépendances Node.js
        install_node_dependencies(build_dir)

        # Créer le lanceur portable
        create_portable_launcher(build_dir)

        # Créer le README
        create_readme(build_dir)

        print("\n" + "="*60)
        print("🎉 BUILD TERMINÉ AVEC SUCCÈS!")
        print("="*60)
        print(f"📁 Dossier créé: {build_dir.absolute()}")
        print("\n🚀 Pour lancer l'application:")
        print("   • Double-cliquez sur LAUNCH_PORTABLE.bat")
        print("   • Ou exécutez: python LAUNCH_PORTABLE.py")
        print("\n📋 Contenu du build:")
        print("   • Application Excel complète")
        print("   • Serveur Node.js avec dépendances")
        print("   • Base de données MariaDB portable")
        print("   • Environnement Python virtuel")
        print("   • Lanceur en un clic")
        print("="*60)

    except Exception as e:
        print(f"\n❌ ERREUR LORS DU BUILD: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())