import glob
import os

from kivy.clock import Clock
from kivy.logger import Logger, FileHandler
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class LogsPanel(BoxLayout):
    log_files = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.refresh_logs())

    @staticmethod
    def get_log_dir() -> str:
        for h in Logger.root.handlers:
            if isinstance(h, FileHandler):
                return os.path.dirname(h.filename)
        # Fallback: use Kivy's default log directory
        from kivy.config import Config
        kivy_home = os.environ.get("KIVY_HOME", os.path.expanduser("~/.kivy"))
        return Config.get("kivy", "log_dir") or os.path.join(kivy_home, "logs")

    def refresh_logs(self):
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
            btn.bind(on_release=lambda b, p=path: self._open_log(p))
            file_list.add_widget(btn)

    def _open_log(self, path: str):
        from rcp.app import MainApp
        app = MainApp.get_running_app()
        app.log_viewer.load_file(path)
        app.manager.goto("log_viewer")