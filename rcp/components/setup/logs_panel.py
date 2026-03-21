import glob
import os
from collections import deque

from kivy.clock import Clock
from kivy.logger import Logger, FileHandler
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

MAX_LINES = 500


class LogsPanel(BoxLayout):
    log_file_path = StringProperty("")
    log_files = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._viewing_content = False
        self._file_list_view = None
        self._content_view = None
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
        self._show_file_list()

    def _show_file_list(self):
        self._remove_current_view()

        from rcp.app import MainApp
        app = MainApp.get_running_app()
        font_size = app.formats.font_size if app else 24

        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        file_list = BoxLayout(
            orientation="vertical", size_hint_y=None,
            spacing=4, padding=10,
        )
        file_list.bind(minimum_height=file_list.setter("height"))

        if not self.log_files:
            file_list.add_widget(Button(
                text="No log files found",
                size_hint_y=None, height=60,
                font_size=font_size, disabled=True,
            ))
        else:
            for path in self.log_files:
                filename = os.path.basename(path)
                btn = Button(
                    text=filename,
                    size_hint_y=None, height=60,
                    font_size=font_size,
                )
                btn.bind(on_release=lambda b, p=path: self.view_log(p))
                file_list.add_widget(btn)

        scroll.add_widget(file_list)
        self._file_list_view = scroll
        self.add_widget(scroll)

        self.ids.header_label.text = "Select a log file"
        self.ids.action_button.text = "Refresh"
        self._viewing_content = False

    def view_log(self, path: str):
        self._remove_current_view()

        self.log_file_path = path
        try:
            with open(path, "r") as f:
                lines = deque(f, maxlen=MAX_LINES)
            content = "".join(lines)
        except OSError as e:
            content = f"Error reading log file: {e}"

        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        label = Label(
            text=content,
            size_hint_y=None,
            text_size=(None, None),
            padding=(10, 10),
            font_size=14,
            halign="left",
            valign="top",
        )
        label.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
        label.bind(texture_size=label.setter("size"))
        scroll.add_widget(label)

        self._content_view = scroll
        self.add_widget(scroll)

        self.ids.header_label.text = os.path.basename(path)
        self.ids.action_button.text = "Back"
        self._viewing_content = True

    def _remove_current_view(self):
        if self._file_list_view and self._file_list_view.parent:
            self.remove_widget(self._file_list_view)
            self._file_list_view = None
        if self._content_view and self._content_view.parent:
            self.remove_widget(self._content_view)
            self._content_view = None

    def on_action_button(self):
        if self._viewing_content:
            self._show_file_list()
        else:
            self.refresh_logs()