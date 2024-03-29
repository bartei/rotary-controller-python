import os

import kivy
from kivy.logger import Logger, FileHandler
from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.lang import Builder


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


class ServoPanel(BoxLayout):
    servo = ObjectProperty()

    def __init__(self, servo, **kv):
        self.servo = servo
        super().__init__(**kv)
        self.ids['grid_layout'].bind(minimum_height=self.ids['grid_layout'].setter('height'))


class ScalePanel(BoxLayout):
    scale = ObjectProperty()

    def __init__(self, scale, **kv):
        self.scale = scale
        super().__init__(**kv)
        self.ids['grid_layout'].bind(minimum_height=self.ids['grid_layout'].setter('height'))


class NumberItem(BoxLayout):
    name = StringProperty("")
    value = NumericProperty(0)
    help_file = StringProperty("")

    def validate(self, value):
        try:
            if "." in value:
                self.value = float(value)
            else:
                self.value = int(value)
        except Exception as e:
            log.error(e.__str__())

    def on_value(self, instance, value):
        self.validate(value)


class DualNumberItem(BoxLayout):
    name = StringProperty("")
    value = NumericProperty(0)
    ratio = NumericProperty(1)
    scaled_value = NumericProperty(0)

    def on_value(self, instance, value):
        try:
            self.scaled_value = value / self.ratio
        except Exception as e:
            log.error(e.__str__())

    def on_scaled_value(self, instance, value):
        try:
            self.value = value * self.ratio
        except Exception as e:
            log.error(e.__str__())


class StringItem(BoxLayout):
    name = StringProperty("")
    value = StringProperty("")


class Setup(Popup):
    tabbed_panel = ObjectProperty()

    def __init__(self, **kv):
        super().__init__(**kv)
        self.tabbed_panel: TabbedPanel
        app = App.get_running_app()
        panes = []

        # Add tabs for the input scales
        for i in range(4):
            pane = TabbedPanelItem(text=f"Input {i}")
            pane.add_widget(ScalePanel(scale=app.home.coord_bars[i]))
            self.tabbed_panel.add_widget(pane)
            panes.append(pane)

        # Add Tab for the servo motor configuration
        servo_pane = TabbedPanelItem(text=f"Servo")
        servo_pane.add_widget(ServoPanel(servo=app.home.servo))
        self.tabbed_panel.add_widget(servo_pane)
        panes.append(servo_pane)

        # Add Tab to allow reviewing the application logs
        log_pane = TabbedPanelItem(text=f"Logs")
        log_pane.add_widget(LogsPanel())
        self.tabbed_panel.add_widget(log_pane)

        self.tabbed_panel.default_tab = panes[0]

