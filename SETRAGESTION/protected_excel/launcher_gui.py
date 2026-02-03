#!/usr/bin/env python3
"""
🌟 Interface Graphique pour le Lanceur Multi-Serveurs
GUI Tkinter pour lancer, surveiller et arrêter les serveurs
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import sys
import threading
import queue
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageTk

class ServerLauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Lanceur Multi-Serveurs - Application Excel")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Variables
        self.process = None
        self.running = False
        self.log_queue = queue.Queue()
        self.status_label = None

        self.generate_logo()

        # Définir l'icône de la fenêtre
        # self.root.iconphoto(False, self.logo_image)  # Commenté pour debug

        # Interface
        self.create_widgets()
        self.setup_layout()

        # Démarrer le thread de lecture des logs
        self.root.after(100, self.check_log_queue)

    def generate_logo(self):
        """Génère le logo GST"""
        width, height = 200, 100
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # Fond dégradé
        for y in range(height):
            r = int(76 + (33 - 76) * y / height)
            g = int(175 + (150 - 175) * y / height)
            b = int(80 + (243 - 80) * y / height)
            draw.line([0, y, width, y], fill=(r, g, b))

        # Texte GST
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()

        # Centrer le texte
        bbox = draw.textbbox((0, 0), "GST", font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 10
        draw.text((x, y), "GST", fill="white", font=font)

        # Texte secondaire
        try:
            small_font = ImageFont.truetype("arial.ttf", 16)
        except:
            small_font = ImageFont.load_default()

        bbox2 = draw.textbbox((0, 0), "Logiciel Excel", font=small_font)
        text_width2 = bbox2[2] - bbox2[0]
        x2 = (width - text_width2) // 2
        y2 = y + 40
        draw.text((x2, y2), "Logiciel Excel", fill="white", font=small_font)

        self.logo_image = ImageTk.PhotoImage(image)

    def create_widgets(self):
        """Créer les widgets de l'interface"""
        # Titre
        self.title_label = tk.Label(
            self.root,
            text="🚀 Lanceur Multi-Serveurs\nApplication Excel d'Analyse Avancée",
            font=("Arial", 16, "bold"),
            justify="center"
        )

        # Logo
        self.logo_label = tk.Label(self.root, image=self.logo_image)

        # Zone de logs
        self.log_text = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=20
        )
        self.log_text.insert(tk.END, "Bienvenue dans le lanceur de serveurs!\n\n")
        self.log_text.config(state=tk.DISABLED)

        # Boutons
        self.start_button = tk.Button(
            self.root,
            text="▶️ DÉMARRER LES SERVEURS",
            command=self.start_servers,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            height=2
        )

        self.stop_button = tk.Button(
            self.root,
            text="⏹️ ARRÊTER LES SERVEURS",
            command=self.stop_servers,
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            height=2,
            state=tk.DISABLED
        )

        # Boutons d'information
        self.manual_button = tk.Button(
            self.root,
            text="📖 Mode d'Emploi",
            command=self.show_manual,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white"
        )

        self.usage_button = tk.Button(
            self.root,
            text="❓ Utilisation",
            command=self.show_usage,
            font=("Arial", 10),
            bg="#FF9800",
            fg="white"
        )

        self.about_button = tk.Button(
            self.root,
            text="ℹ️ À Propos",
            command=self.show_about,
            font=("Arial", 10),
            bg="#9C27B0",
            fg="white"
        )

        # Statut
        self.status_label = tk.Label(
            self.root,
            text="Statut: Prêt",
            font=("Arial", 10),
            fg="#666"
        )

    def setup_layout(self):
        """Organiser la disposition des widgets"""
        self.logo_label.pack(pady=10)
        # self.title_label.pack(pady=5)  # Retiré pour garder seulement le logo

        # Frame pour les boutons principaux
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button.pack(side=tk.LEFT, padx=10)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Frame pour les boutons d'information
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)

        self.manual_button.pack(side=tk.LEFT, padx=5)
        self.usage_button.pack(side=tk.LEFT, padx=5)
        self.about_button.pack(side=tk.LEFT, padx=5)

        self.status_label.pack(pady=5)  # type: ignore

        # Zone de logs
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log_message(self, message):
        """Ajouter un message aux logs"""
        self.log_queue.put(message)

    def check_log_queue(self):
        """Vérifier la file d'attente des logs et mettre à jour l'interface"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass

        self.root.after(100, self.check_log_queue)

    def start_servers(self):
        """Démarrer les serveurs"""
        if self.running:
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Statut: Démarrage en cours...", fg="#ff9800")  # type: ignore

        self.log_message("🚀 Démarrage des serveurs...")

        # Lancer dans un thread séparé
        thread = threading.Thread(target=self.run_launcher)
        thread.daemon = True
        thread.start()

    def run_launcher(self):
        """Exécuter le lanceur de serveurs"""
        try:
            # Obtenir le chemin du script launcher_all_servers.py
            base_dir = Path(__file__).parent
            launcher_path = base_dir / "launcher_all_servers.py"

            if not launcher_path.exists():
                self.log_message(f"❌ Fichier launcher_all_servers.py non trouvé: {launcher_path}")
                self.reset_ui()
                return

            # Lancer le processus
            self.process = subprocess.Popen(
                [sys.executable, str(launcher_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Lire la sortie en temps réel
            stdout = self.process.stdout
            if stdout:
                while self.running and self.process.poll() is None:
                    output = stdout.readline()
                    if output:
                        self.log_message(output.strip())

            # Attendre la fin du processus
            if self.process:
                self.process.wait()

            if self.running:  # Si pas arrêté manuellement
                self.log_message("✅ Serveurs démarrés avec succès!")
                self.status_label.config(text="Statut: Serveurs actifs", fg="#4CAF50")  # type: ignore

        except Exception as e:
            self.log_message(f"❌ Erreur: {str(e)}")
            self.reset_ui()

    def stop_servers(self):
        """Arrêter les serveurs"""
        if not self.running:
            return

        self.log_message("⏹️ Arrêt des serveurs...")
        self.running = False

        if self.process:
            try:
                # Tuer le processus et ses enfants
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.log_message("⚠️ Processus forcé à s'arrêter")

        self.reset_ui()

    def reset_ui(self):
        """Remettre l'interface à l'état initial"""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Statut: Arrêté", fg="#666")  # type: ignore

    def on_closing(self):
        """Gestionnaire de fermeture de la fenêtre"""
        if self.running:
            if messagebox.askyesno("Confirmation", "Les serveurs sont en cours d'exécution. Voulez-vous vraiment quitter ?"):
                self.stop_servers()
            else:
                return
        self.root.destroy()

    def show_manual(self):
        """Affiche le mode d'emploi"""
        manual_window = tk.Toplevel(self.root)
        manual_window.title("📖 Mode d'Emploi")
        manual_window.geometry("700x600")

        text = scrolledtext.ScrolledText(manual_window, wrap=tk.WORD, font=("Arial", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        manual_content = """
MODE D'EMPLOI - Application Excel d'Analyse Avancée

1. INSTALLATION
   - Décompressez le dossier portable
   - Double-cliquez sur start.bat ou utilisez cette interface

2. DÉMARRAGE
   - Cliquez sur "DÉMARRER LES SERVEURS"
   - L'application s'ouvre automatiquement dans votre navigateur

3. UTILISATION
   - Importez vos fichiers Excel
   - Analysez les données avec l'IA
   - Générez des rapports PDF
   - Sauvegardez vos analyses

4. FONCTIONNALITÉS PRINCIPALES
   - Analyse de fichiers Excel
   - Détection automatique de dangers
   - Génération de rapports
   - Interface web moderne
   - Base de données intégrée

5. SUPPORT
   - Vérifiez les logs en cas de problème
   - Assurez-vous que le port 8501 n'est pas occupé
   - MariaDB doit être accessible sur localhost:3306

6. ARRÊT
   - Cliquez sur "ARRÊTER LES SERVEURS"
   - Tous les serveurs seront fermés proprement

Pour plus d'informations, consultez le README.md
        """

        text.insert(tk.END, manual_content)
        text.config(state=tk.DISABLED)

    def show_usage(self):
        """Affiche les instructions d'utilisation"""
        usage_window = tk.Toplevel(self.root)
        usage_window.title("❓ Utilisation du Logiciel")
        usage_window.geometry("700x500")

        text = scrolledtext.ScrolledText(usage_window, wrap=tk.WORD, font=("Arial", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        usage_content = """
UTILISATION DE L'APPLICATION EXCEL D'ANALYSE

ÉTAPES D'UTILISATION :

1. DÉMARRAGE
   - Lancez l'application via cette interface
   - Attendez que tous les serveurs soient démarrés
   - L'interface web s'ouvre automatiquement

2. IMPORT DE DONNÉES
   - Cliquez sur "Importer Fichier Excel"
   - Sélectionnez votre fichier .xlsx ou .xls
   - L'application analyse automatiquement la structure

3. ANALYSE DES DONNÉES
   - L'IA détecte les colonnes importantes
   - Analyse les risques et dangers potentiels
   - Génère des visualisations interactives

4. GÉNÉRATION DE RAPPORTS
   - Cliquez sur "Générer Rapport"
   - Personnalisez le contenu
   - Téléchargez le PDF généré

5. SAUVEGARDE
   - Les analyses sont automatiquement sauvegardées
   - Base de données MariaDB pour la persistance

CONSEILS :
- Utilisez des fichiers Excel bien structurés
- Vérifiez la qualité des données avant import
- Les analyses peuvent prendre quelques minutes
- Fermez proprement l'application après usage

DÉPANNAGE :
- Si l'app ne démarre pas : vérifiez les ports 8501 et 3306
- Logs disponibles dans l'interface pour diagnostiquer
        """

        text.insert(tk.END, usage_content)
        text.config(state=tk.DISABLED)

    def show_about(self):
        """Affiche les informations sur l'application"""
        about_text = """
Application Excel d'Analyse Avancée
Version 1.0

Technologies utilisées :
• Python 3.11
• Streamlit (Interface Web)
• MariaDB (Base de données)
• Node.js (Backend API)
• IA intégrée pour l'analyse

Développé pour l'analyse automatisée de fichiers Excel
avec détection de risques et génération de rapports.

© 2026 - Tous droits réservés
        """
        messagebox.showinfo("ℹ️ À Propos", about_text)

def main():
    try:
        root = tk.Tk()
        app = ServerLauncherGUI(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        print(f"Erreur fatale dans l'interface: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()