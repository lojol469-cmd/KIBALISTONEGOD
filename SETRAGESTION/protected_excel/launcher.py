import sys
import os
import subprocess

if __name__ == "__main__":
    # Get the directory of this script
    app_dir = os.path.dirname(__file__)
    app_py = os.path.join(app_dir, 'app.py')

    # Run streamlit run app.py in background
    subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', app_py])