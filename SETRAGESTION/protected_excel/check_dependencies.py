# pyright: reportMissingImports=false, reportMissingModuleSource=false
# type: ignore
# Vérification des dépendances Python
# Ce script vérifie que toutes les dépendances requises sont installées

import sys
print(f"Python version: {sys.version}")
print(f"Chemin Python: {sys.executable}")
print("\n" + "="*60)
print("Vérification des dépendances principales")
print("="*60 + "\n")

modules = {
    'streamlit': 'Framework pour l\'interface web',
    'pandas': 'Manipulation et analyse de données',
    'plotly.express': 'Graphiques interactifs',
    'plotly.graph_objects': 'Graphiques personnalisés',
    'reportlab': 'Génération de PDF',
    'PIL': 'Traitement d\'images (Pillow)',
    'cloudinary': 'Stockage cloud d\'images',
    'matplotlib.pyplot': 'Visualisation de données',
    'openpyxl': 'Manipulation de fichiers Excel',
    'requests': 'Requêtes HTTP',
    'dotenv': 'Variables d\'environnement',
    'sqlite3': 'Base de données SQLite (intégré)',
    'json': 'Manipulation JSON (intégré)',
    'datetime': 'Gestion des dates (intégré)',
    'pathlib': 'Gestion des chemins (intégré)'
}

errors = []
success = []

for module_name, description in modules.items():
    try:
        if '.' in module_name:
            parts = module_name.split('.')
            __import__(parts[0])
            exec(f"import {module_name}")
        else:
            __import__(module_name)
        success.append(f"✅ {module_name:30} - {description}")
    except ImportError as e:
        errors.append(f"❌ {module_name:30} - ERREUR: {str(e)}")

# Affichage des résultats
for msg in success:
    print(msg)

if errors:
    print("\n" + "="*60)
    print("ERREURS DÉTECTÉES")
    print("="*60 + "\n")
    for msg in errors:
        print(msg)
    print("\nPour installer les dépendances manquantes, exécutez:")
    print("python -m pip install -r requirements.txt")
else:
    print("\n" + "="*60)
    print("🎉 TOUTES LES DÉPENDANCES SONT INSTALLÉES CORRECTEMENT!")
    print("="*60)

# Affichage des versions des packages importants
print("\n" + "="*60)
print("Versions des packages principaux")
print("="*60 + "\n")

try:
    import streamlit
    print(f"streamlit: {streamlit.__version__}")
except:
    pass

try:
    import pandas
    print(f"pandas: {pandas.__version__}")
except:
    pass

try:
    import plotly
    print(f"plotly: {plotly.__version__}")
except:
    pass

try:
    import PIL
    print(f"Pillow: {PIL.__version__}")
except:
    pass

try:
    import cloudinary
    print(f"cloudinary: {cloudinary.__version__}")
except:
    pass

try:
    import matplotlib
    print(f"matplotlib: {matplotlib.__version__}")
except:
    pass

print("\n✅ Vérification terminée!")
