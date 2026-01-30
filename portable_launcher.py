import streamlit.web.cli as stcli
import sys
import os

# Set the working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Simulate command line args for streamlit run
sys.argv = ["streamlit", "run", "excel/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

# Run streamlit
stcli.main()