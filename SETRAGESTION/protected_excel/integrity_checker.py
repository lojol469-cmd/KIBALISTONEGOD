#!/usr/bin/env python3
"""
Vérificateur d'Intégrité - Protection contre la modification du code
"""

import hashlib
import os
import sys
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

class IntegrityChecker:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.integrity_file = self.base_dir / "integrity.json"

    def calculate_file_hash(self, file_path):
        """Calcule le hash SHA256 d'un fichier"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return None

    def generate_integrity_file(self):
        """Génère le fichier d'intégrité avec les hashes actuels"""
        important_files = [
            "app.py",
            "launcher_all_servers.py",
            "license_manager.py",
            "tray_icon.py",
            "server.js",
            "start.bat"
        ]

        integrity_data = {}
        for file in important_files:
            file_path = self.base_dir / file
            if file_path.exists():
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    integrity_data[file] = file_hash

        try:
            with open(self.integrity_file, 'w') as f:
                json.dump(integrity_data, f, indent=2)
            return True
        except:
            return False

    def check_integrity(self):
        """Vérifie l'intégrité des fichiers"""
        if not self.integrity_file.exists():
            # Premier lancement, générer le fichier
            return self.generate_integrity_file()

        try:
            with open(self.integrity_file, 'r') as f:
                stored_hashes = json.load(f)
        except:
            return False

        modified_files = []
        for file, stored_hash in stored_hashes.items():
            file_path = self.base_dir / file
            if file_path.exists():
                current_hash = self.calculate_file_hash(file_path)
                if current_hash != stored_hash:
                    modified_files.append(file)
            else:
                modified_files.append(f"{file} (supprimé)")

        if modified_files:
            error_msg = "Fichiers modifiés détectés :\n" + "\n".join(modified_files)
            error_msg += "\n\nL'application a été altérée. Contactez SETRAF."
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Violation d'Intégrité", error_msg)
            except:
                print("❌ VIOLATION D'INTÉGRITÉ:")
                print(error_msg)
            return False

        return True

def main():
    """Test de l'intégrité"""
    checker = IntegrityChecker()
    if checker.check_integrity():
        print("✅ Intégrité vérifiée")
    else:
        print("❌ Intégrité compromise")
        sys.exit(1)

if __name__ == "__main__":
    main()