#!/usr/bin/env python3
"""
🛢️ Simulateur Ultra-Réaliste de Risques Pétroliers
Lanceur principal pour l'application Streamlit

Usage:
    python launch_petroleum_app.py

Ou directement:
    streamlit run petroleum_risk_app.py
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Vérifie que les dépendances principales sont installées"""
    required_packages = [
        'streamlit', 'cantera', 'open3d', 'plotly', 'numpy', 'pandas'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)

    if missing:
        print(f"❌ Dépendances manquantes: {', '.join(missing)}")
        print("Installez-les avec: pip install -r requirements.txt")
        return False

    return True

def launch_app():
    """Lance l'application Streamlit"""
    app_path = Path(__file__).parent / "petroleum_risk_app.py"

    if not app_path.exists():
        print(f"❌ Fichier application non trouvé: {app_path}")
        return False

    print("🚀 Lancement du Simulateur de Risques Pétroliers...")
    print("=" * 60)
    print("🛢️ Technologies intégrées:")
    print("   • Cantera: Modélisation combustion chimique")
    print("   • OpenFOAM: Simulation CFD ultra-réaliste")
    print("   • Open3D + Plotly: Visualisation 3D interactive")
    print("   • IA RAG: Analyse intelligente de documents")
    print("   • Text-to-Simulation: Requêtes naturelles")
    print("=" * 60)

    try:
        # Lancement Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        print("\n👋 Application arrêtée par l'utilisateur")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        return False
    except FileNotFoundError:
        print("❌ Streamlit n'est pas installé ou accessible")
        return False

    return True

def main():
    """Fonction principale"""
    print("🛢️ Simulateur Ultra-Réaliste de Risques Pétroliers v2.0")
    print("Dépassement PHAST/SAFETI via IA et interactivité temps réel")
    print()

    # Vérification des dépendances
    if not check_dependencies():
        sys.exit(1)

    # Lancement de l'application
    if not launch_app():
        sys.exit(1)

    print("✅ Application lancée avec succès!")

if __name__ == "__main__":
    main()