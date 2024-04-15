import os
import subprocess
import time
import threading

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class CustomEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.lock = threading.Lock()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            print(f"Detected changes in {event.src_path}. Restarting app...")
            self.start_or_restart_process()

    def start_or_restart_process(self):
        with self.lock:
            if self.process:
                self.process.terminate()
                self.process.wait()  # Wait for the process to terminate
            # Start the subprocess in a separate thread to avoid blocking
            threading.Thread(target=self.run_subprocess).start()

    def run_subprocess(self):
        # Command to start your application
        self.process = subprocess.Popen(["python", "server.py"])


if __name__ == "__main__":
    path = "./"
    event_handler = CustomEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    # Start the application at the script start
    event_handler.start_or_restart_process()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        if event_handler.process:
            event_handler.process.terminate()
            event_handler.process.wait()
