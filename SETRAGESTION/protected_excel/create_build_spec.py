#!/usr/bin/env python3
"""
Génère le fichier .spec pour PyInstaller
Crée un exécutable portable de SETRAF
"""

import sys
from pathlib import Path

def create_spec_file():
    """Crée le fichier .spec pour PyInstaller"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Tous les fichiers Python à inclure
a = Analysis(
    ['launcher_all_servers.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app.py', '.'),
        ('license_check.py', '.'),
        ('license_config.py', '.'),
        ('integrity_checker.py', '.'),
        ('server.js', '.'),
        ('package.json', '.'),
        ('requirements.txt', '.'),
        ('static', 'static'),
        ('.env', '.'),
        ('LOGO VECTORISE PNG.png', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'PIL',
        'openpyxl',
        'mysql.connector',
        'cloudinary',
        'python-dotenv',
        'license_check',
        'license_config',
        'integrity_checker',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SETRAF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # True pour voir les messages de debug
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='LOGO VECTORISE PNG.png' if Path('LOGO VECTORISE PNG.png').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SETRAF_Portable',
)
'''

    # Écrire le fichier
    spec_file = Path('setraf_portable.spec')
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ Fichier spec créé : {spec_file}")
    return spec_file

if __name__ == "__main__":
    try:
        create_spec_file()
        print("\n🎉 Fichier .spec prêt pour PyInstaller")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)
