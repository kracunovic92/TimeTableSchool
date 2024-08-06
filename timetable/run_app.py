import threading
import webbrowser
import time
import subprocess
import signal
import sys

def start_server():
    subprocess.run(["gunicorn", "-c", "gunicorn_config.py"], cwd="../timetable")

def open_browser():
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:5000')

def handle_interrupt(signal, frame):
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_interrupt)

    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    open_browser()

    try:
        while server_thread.is_alive():
            server_thread.join(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Server shutdown initiated.")
