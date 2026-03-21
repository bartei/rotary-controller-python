import glob
import os
from collections import deque

from kivy.logger import Logger, FileHandler
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

PI_LOG_DIR = "/var/log"
MAX_LINES = 500


class LogsPanel(BoxLayout):
    log_file_path = StringProperty("")
    log_content = StringProperty("")
    log_files = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_logs()

    @staticmethod
    def get_log_dir() -> str:
        for h in Logger.root.handlers:
            if isinstance(h, FileHandler):
                return os.path.dirname(h.filename)
        return PI_LOG_DIR

    def refresh_logs(self):
        self.log_file_path = ""
        self.log_content = ""
        log_dir = self.get_log_dir()
        pattern = os.path.join(log_dir, "kivy_*.txt")
        files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
        self.log_files = files
        self._rebuild_file_list()

    def _rebuild_file_list(self):
        file_list = self.ids.get("file_list")
        if not file_list:
            return
        file_list.clear_widgets()

        from rcp.app import MainApp
        app = MainApp.get_running_app()
        font_size = app.formats.font_size if app else 24

        if not self.log_files:
            file_list.add_widget(Button(
                text="No log files found",
                size_hint_y=None, height=60,
                font_size=font_size, disabled=True,
            ))
            return

        for path in self.log_files:
            filename = os.path.basename(path)
            btn = Button(
                text=filename,
                size_hint_y=None, height=60,
                font_size=font_size,
            )
            btn.bind(on_release=lambda b, p=path: self.view_log(p))
            file_list.add_widget(btn)

    def view_log(self, path: str):
        self.log_file_path = path
        try:
            with open(path, "r") as f:
                lines = deque(f, maxlen=MAX_LINES)
            self.log_content = "".join(lines)
        except OSError as e:
            self.log_content = f"Error reading log file: {e}"

    def go_back_to_list(self):
        self.log_file_path = ""
        self.log_content = ""