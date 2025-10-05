# main.py
import subprocess
import sys
import time
import os

def run_both():
    print("🚀 Starting Harvest Horizon...")
    print("🎮 Launching Pygame client...")
    pygame_proc = subprocess.Popen([sys.executable, "pygame_game.py"])
    
    time.sleep(2)
    
    print("📊 Launching Streamlit dashboard...")
    streamlit_proc = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8501"])
    
    try:
        pygame_proc.wait()
    except KeyboardInterrupt:
        pygame_proc.terminate()
        streamlit_proc.terminate()
        print("\n🛑 Stopped both apps.")

if __name__ == "__main__":
    run_both()