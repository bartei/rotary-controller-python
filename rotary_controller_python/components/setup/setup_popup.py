import os

from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanelItem

from rotary_controller_python.components.setup.logs_panel import LogsPanel
from rotary_controller_python.components.setup.scale_panel import ScalePanel
from rotary_controller_python.components.setup.servo_panel import ServoPanel

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class SetupPopup(Popup):
    tabbed_panel = ObjectProperty()

    def __init__(self, **kv):
        super().__init__(**kv)
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

    def on_dismiss(self):
        app = App.get_running_app()
        app.manual_full_update()
        log.info("Close setup page")
