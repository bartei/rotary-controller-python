from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.properties import ListProperty
from kivy.logger import Logger
log = Logger.getChild(__name__)


class Manager(ScreenManager):
    previous = ListProperty()
    transition = FadeTransition()

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kv)
        self.transition.duration = .05

        from rcp.components.screens.home_screen import HomePage
        self.add_widget(HomePage(name="home"))

        from rcp.components.screens.setup_screen import SetupScreen
        self.add_widget(SetupScreen(name="setup_screen"))

        from rcp.components.screens.network_screen import NetworkScreen
        self.add_widget(NetworkScreen(name="network"))

        from rcp.components.screens.formats_screen import FormatsScreen
        self.add_widget(FormatsScreen(name="formats"))

        # Add screen for color picker
        from rcp.components.screens.color_picker_screen import ColorPickerScreen
        self.color_picker = ColorPickerScreen(name="color_picker")
        self.add_widget(self.color_picker)

        # Add screens for scales setup
        from rcp.components.screens.scale_screen import ScaleScreen
        for i in range(len(self.app.scales)):
            self.add_widget(ScaleScreen(name=f"scale_{i}", scale=self.app.scales[i]))

        # Add screen for servo setup
        from rcp.components.screens.servo_screen import ServoScreen
        self.add_widget(ServoScreen(name="servo", servo=self.app.servo))

        from rcp.components.screens.update_screen import UpdateScreen
        self.add_widget(UpdateScreen(name="update"))

        # Add screen for plot view
        from rcp.components.plot.plot_screen import PlotScreen
        self.add_widget(PlotScreen(name="plot"))
        self.current = "home"

    def set_previous(self, instance, value):
        self.previous.append(value)
        log.info(f"Previous history: {self.previous}")

    def back(self):
        # self.manager.transition.mode = "pop"
        self.current = self.previous.pop()
        log.debug(f"Back array {self.previous}")

    def goto(self, screen: str):
        # self.manager.transition.mode = "push"
        self.previous.append(self.current)
        log.debug(f"Goto array {self.previous}")
        self.current = screen
