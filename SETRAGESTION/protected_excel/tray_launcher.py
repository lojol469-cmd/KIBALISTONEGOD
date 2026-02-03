import pystray
from PIL import Image
import subprocess
import os
import sys

def launch_app(icon, item):
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_exe = os.path.join(script_dir, 'app.exe')
    subprocess.Popen([app_exe])

def quit_app(icon, item):
    icon.stop()

# Create a simple icon (you can replace with a real icon file)
icon_image = Image.new('RGB', (64, 64), color='blue')

menu = pystray.Menu(
    pystray.MenuItem('Lancer l\'app', launch_app),
    pystray.MenuItem('Quitter', quit_app)
)

icon = pystray.Icon("Mon App", icon_image, "Mon Application", menu)
icon.run()