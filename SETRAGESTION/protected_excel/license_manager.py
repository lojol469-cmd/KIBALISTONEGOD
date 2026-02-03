#!/usr/bin/env python3
"""
Gestionnaire de Licence - Protection Anti-Crack
Vérifie la validité de la licence avant lancement de l'application
"""

import os
import sys
import hashlib
import uuid
import platform
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
from pathlib import Path

class LicenseManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.license_file = self.base_dir / "license.key"
        self.config_file = self.base_dir / "license_config.json"

    def get_machine_id(self):
        """Génère un ID unique de la machine basé sur plusieurs facteurs"""
        try:
            # Combinaison de plusieurs identifiants
            machine_id = ""

            # UUID de la machine
            machine_id += str(uuid.getnode())

            # Nom de l'ordinateur
            machine_id += platform.node()

            # Version du système
            machine_id += platform.version()

            # Hash pour créer un ID unique
            return hashlib.sha256(machine_id.encode()).hexdigest()[:16].upper()

        except:
            # Fallback
            return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:16].upper()

    def generate_license_key(self, machine_id):
        """Génère une clé de licence basée sur l'ID machine"""
        # Clé maître (à changer pour la production)
        master_key = "SETRAF2026LICENCE"
        combined = master_key + machine_id
        return hashlib.sha256(combined.encode()).hexdigest()[:20].upper()

    def check_license(self):
        """Vérifie si la licence est valide"""
        machine_id = self.get_machine_id()

        if not self.license_file.exists():
            return self.request_license(machine_id)

        try:
            with open(self.license_file, 'r') as f:
                stored_license = f.read().strip()

            expected_license = self.generate_license_key(machine_id)

            if stored_license == expected_license:
                return True
            else:
                messagebox.showerror("Licence Invalide",
                                   "La clé de licence ne correspond pas à cette machine.\n"
                                   "Contactez SETRAF pour obtenir une licence valide.")
                return False

        except Exception as e:
            messagebox.showerror("Erreur de Licence",
                               f"Erreur lors de la vérification de la licence: {str(e)}")
            return False

    def request_license(self, machine_id):
        """Demande la saisie d'une clé de licence"""
        root = tk.Tk()
        root.withdraw()  # Masquer la fenêtre principale

        # Afficher l'accord de licence d'abord
        license_text = """
        LICENCE D'UTILISATION - SETRAF

        Ce logiciel est protégé par copyright.
        Toute utilisation non autorisée est interdite.

        En continuant, vous acceptez les termes de la licence.

        ID Machine: {machine_id}

        Contactez SETRAF pour obtenir votre clé de licence.
        """

        accept = messagebox.askyesno("Accord de Licence",
                                   license_text.format(machine_id=machine_id))

        if not accept:
            messagebox.showerror("Licence Rejetée",
                               "Vous devez accepter la licence pour utiliser ce logiciel.")
            return False

        # Demander la clé de licence
        license_key = simpledialog.askstring("Clé de Licence",
                                           "Entrez votre clé de licence SETRAF:",
                                           parent=root)

        if not license_key:
            messagebox.showerror("Licence Requise",
                               "Une clé de licence est requise pour utiliser ce logiciel.")
            return False

        # Vérifier la clé
        expected = self.generate_license_key(machine_id)
        if license_key.upper() == expected:
            # Sauvegarder la clé
            try:
                with open(self.license_file, 'w') as f:
                    f.write(license_key.upper())
                messagebox.showinfo("Licence Activée",
                                  "Licence activée avec succès !")
                return True
            except Exception as e:
                messagebox.showerror("Erreur",
                                   f"Impossible de sauvegarder la licence: {str(e)}")
                return False
        else:
            messagebox.showerror("Clé Invalide",
                               "La clé de licence saisie est invalide.")
            return False

    def is_debugger_present(self):
        """Détecte si un débogueur est présent (anti-debug)"""
        try:
            import ctypes
            # Vérification Windows
            if platform.system() == "Windows":
                kernel32 = ctypes.windll.kernel32
                return kernel32.IsDebuggerPresent() != 0
            return False
        except:
            return False

    def is_virtual_machine(self):
        """Détecte si l'application tourne dans une VM"""
        try:
            # Vérifications simples
            vm_indicators = [
                "virtual", "vmware", "vbox", "qemu", "xen"
            ]
            system_info = platform.platform().lower()
            for indicator in vm_indicators:
                if indicator in system_info:
                    return True
            return False
        except:
            return False

    def run_security_checks(self):
        """Exécute toutes les vérifications de sécurité"""
        # Vérifier licence
        if not self.check_license():
            sys.exit(1)

        # Anti-debug
        if self.is_debugger_present():
            messagebox.showerror("Sécurité",
                               "Détection d'un débogueur. L'application va se fermer.")
            sys.exit(1)

        # Anti-VM (optionnel, peut être désactivé)
        # if self.is_virtual_machine():
        #     messagebox.showerror("Sécurité",
        #                        "Exécution dans un environnement virtuel détectée.")
        #     sys.exit(1)

        return True

def main():
    """Fonction principale pour test"""
    manager = LicenseManager()

    print(f"ID Machine: {manager.get_machine_id()}")
    print(f"Clé attendue: {manager.generate_license_key(manager.get_machine_id())}")

    if manager.run_security_checks():
        print("✅ Toutes les vérifications de sécurité passées")
    else:
        print("❌ Échec des vérifications de sécurité")

if __name__ == "__main__":
    main()