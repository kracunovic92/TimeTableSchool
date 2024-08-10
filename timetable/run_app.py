import threading
import webbrowser
import time
import subprocess
import signal
import sys
from waitress import serve
from timetable.app import app
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_server():
    try:
        logger.info("Starting server...")
        serve(app, host = '127.0.0.1', port=8080)
    except Exception as e:
        logger.error("Server stopped due to an error", exc_info=True)

def open_browser():
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:8080')

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
