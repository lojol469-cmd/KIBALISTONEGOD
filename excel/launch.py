import subprocess
import sys
import os
import time

# Changer vers le répertoire du script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Lancer le serveur Node.js en arrière-plan
print("Démarrage du serveur Node.js...")
server_process = subprocess.Popen([sys.executable, "-c", "import subprocess; subprocess.run(['node', 'server.js'])"], shell=True)

# Attendre un peu que le serveur démarre
time.sleep(2)

# Lancer Streamlit
print("Démarrage de l'application Streamlit...")
subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])