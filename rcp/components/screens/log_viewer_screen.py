import os
from collections import deque

from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

MAX_LINES = 500


class LogViewerScreen(Screen):
    log_file_path = StringProperty("")
    log_content = StringProperty("")
    log_file_name = StringProperty("Log Viewer")

    def load_file(self, path: str):
        self.log_file_path = path
        self.log_file_name = os.path.basename(path)
        try:
            with open(path, "r") as f:
                lines = deque(f, maxlen=MAX_LINES)
            self.log_content = "".join(lines)
        except OSError as e:
            self.log_content = f"Error reading log file: {e}"