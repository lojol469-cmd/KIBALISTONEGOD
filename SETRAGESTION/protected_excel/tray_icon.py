#!/usr/bin/env python3
"""
Icône de la barre des tâches pour l'application Excel
Affiche une icône dans la barre des tâches avec menu pour accéder à l'app
"""

import pystray  # type: ignore
from PIL import Image, ImageDraw, ImageFont
import webbrowser
import psutil  # type: ignore
import os
import sys
from pathlib import Path

def generate_tray_icon():
    """Génère l'icône pour la barre des tâches"""
    width, height = 64, 64
    image = Image.new('RGB', (width, height), (76, 175, 80))  # Vert
    draw = ImageDraw.Draw(image)

    # Texte GST
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    # Centrer GST
    bbox = draw.textbbox((0, 0), "GST", font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), "GST", fill="white", font=font)

    return image

def open_app(icon, item):
    """Ouvre l'application dans le navigateur"""
    webbrowser.open("http://localhost:8501")

def show_about(icon, item):
    """Affiche les informations sur l'app"""
    icon.notify("Application Excel d'Analyse Avancée\nVersion 1.0\n\nCliquez pour ouvrir", "GST Logiciel")

def exit_app(icon, item):
    """Quitte l'application"""
    # Tuer les processus liés
    killed = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if any(keyword in cmdline for keyword in ['streamlit', 'mysqld', 'node']):
                proc.kill()
                killed.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if killed:
        icon.notify(f"Processus arrêtés: {', '.join(killed)}", "Arrêt de l'application")
    else:
        icon.notify("Aucun processus trouvé", "Arrêt de l'application")

    icon.stop()

def main():
    """Fonction principale"""
    # Générer l'icône
    icon_image = generate_tray_icon()

    # Créer le menu
    menu = pystray.Menu(
        pystray.MenuItem("Ouvrir l'application", open_app),
        pystray.MenuItem("À propos", show_about),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quitter", exit_app)
    )

    # Créer l'icône de la barre des tâches
    icon = pystray.Icon(
        "GST Excel App",
        icon_image,
        "Application Excel GST",
        menu
    )

    # Démarrer l'icône
    icon.run()

if __name__ == "__main__":
    main()