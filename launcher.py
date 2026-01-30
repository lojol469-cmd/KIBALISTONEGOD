import subprocess
import threading

def run_server():
    # Run npm start in excel directory
    subprocess.run(['npm', 'start'], cwd='excel', shell=True)

def run_streamlit():
    # Run Streamlit from root directory
    subprocess.run(['streamlit', 'run', 'excel/app.py', '--server.port', '8501', '--server.address', '0.0.0.0'])

if __name__ == "__main__":
    # Run both in parallel
    server_thread = threading.Thread(target=run_server)
    streamlit_thread = threading.Thread(target=run_streamlit)

    server_thread.start()
    streamlit_thread.start()

    server_thread.join()
    streamlit_thread.join()