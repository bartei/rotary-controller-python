import glob
import os
from collections import deque

from kivy.logger import Logger, FileHandler
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

PI_LOG_DIR = "/var/log"
MAX_LINES = 500


class LogsPanel(BoxLayout):
    log_file_path = StringProperty("")
    log_content = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_logs()

    @staticmethod
    def get_log_file_path() -> str | None:
        for h in Logger.root.handlers:
            if isinstance(h, FileHandler):
                return h.filename

        # Fallback: find most recent kivy log in /var/log
        pattern = os.path.join(PI_LOG_DIR, "kivy_*.txt")
        files = glob.glob(pattern)
        if files:
            return max(files, key=os.path.getmtime)

        return None

    def refresh_logs(self):
        path = self.get_log_file_path()
        if path is None:
            self.log_file_path = "No log file found"
            self.log_content = "No log file available. Kivy file logging may not be enabled."
            return

        self.log_file_path = path
        try:
            with open(path, "r") as f:
                lines = deque(f, maxlen=MAX_LINES)
            self.log_content = "".join(lines)
        except OSError as e:
            self.log_content = f"Error reading log file: {e}"