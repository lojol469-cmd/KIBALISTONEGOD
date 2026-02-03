import subprocess
import sys
import os
import time
import socket
from pathlib import Path

# Changer vers le répertoire du script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def get_local_ip():
    """Détecte l'adresse IP locale de l'appareil"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return "127.0.0.1"

def get_node_executable():
    """Trouve l'exécutable Node.js portable ou système"""
    base_dir = Path(script_dir)
    
    # Chemins possibles pour Node.js portable
    possible_node_paths = [
        base_dir / "node-v24.13.0-win-x64" / "node.exe",
        base_dir / "node_modules" / ".bin" / "node.exe",
        base_dir.parent / "node-v24.13.0-win-x64" / "node.exe",
    ]
    
    # Chercher Node.js portable
    for node_path in possible_node_paths:
        if node_path.exists():
            print(f"✅ Node.js portable trouvé: {node_path}")
            return str(node_path)
    
    # Fallback: utiliser node du système
    print("⚠️ Node.js portable non trouvé, utilisation du système")
    return "node"

# Lancer le serveur Node.js en arrière-plan
print("Démarrage du serveur Node.js...")
node_exe = get_node_executable()
server_process = subprocess.Popen([node_exe, "server.js"], 
                                  creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

# Attendre un peu que le serveur démarre
time.sleep(2)

# Détecter l'IP locale
local_ip = get_local_ip()

# Lancer Streamlit avec écoute sur toutes les interfaces
print("Démarrage de l'application Streamlit...")
print(f"\n🌐 Accès depuis cet ordinateur: http://localhost:8501")
print(f"🌍 Accès depuis d'autres ordinateurs: http://{local_ip}:8501")
print(f"📍 Adresse IP de cette machine: {local_ip}\n")

subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", 
                "--server.address", "0.0.0.0", 
                "--server.port", "8501"])