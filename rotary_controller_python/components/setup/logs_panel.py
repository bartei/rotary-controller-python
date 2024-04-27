import os

from kivy.lang import Builder
from kivy.logger import Logger, FileHandler
from kivy.uix.boxlayout import BoxLayout

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class LogsPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_logs()

    @staticmethod
    def get_log_file_path() -> str or None:
        for h in Logger.root.handlers:
            if isinstance(h, FileHandler):
                return h.filename
        return None

    def refresh_logs(self):
        log_filename = self.get_log_file_path()
        if log_filename is not None:
            with open(self.get_log_file_path(), "r") as logfile:
                self.ids['log_text_area'].text = logfile.read()
        else:
            self.ids['log_text_area'].text = "Enable file logging in your Kivy config!"