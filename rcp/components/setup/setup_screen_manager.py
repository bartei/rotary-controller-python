import os

from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition

from rcp.components.setup.scale_panel import ScalePanel
from rcp.components.setup.servo_panel import ServoPanel
from rcp.components.setup.formats_panel import FormatsPanel
from rcp.components.setup.network_panel import NetworkPanel



log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class SetupScreenManager(ScreenManager):
    setup_popup = ObjectProperty()

    def __init__(self, **kv):
        super().__init__(**kv)
        app = App.get_running_app()
        self.transition = NoTransition()

        # Add tabs for the input scales
        for i in range(4):
            screen = Screen(name=f"scale_{i}")
            screen.add_widget(ScalePanel(scale=app.scales[i]))
            self.add_widget(screen)

        # Add Tab for the servo motor configuration
        screen = Screen(name="servo")
        screen.add_widget(ServoPanel(servo=app.servo))
        self.add_widget(screen)

        # TODO: Disable network for now, need to finish working on this
        screen = Screen(name="network")
        screen.add_widget(NetworkPanel())
        self.add_widget(screen)

        screen = Screen(name="formats")
        screen.add_widget(FormatsPanel(formats=app.formats))
        self.add_widget(screen)

        # Add Tab to allow reviewing the application logs
        # screen = Screen(name="logs")
        # screen.add_widget(LogsPanel())
        # self.add_widget(screen)
