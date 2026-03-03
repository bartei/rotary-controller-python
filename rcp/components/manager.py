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
        self.app.color_picker = ColorPickerScreen(name="color_picker")
        self.add_widget(self.app.color_picker)

        # Add screen for font picker
        from rcp.components.screens.font_picker_screen import FontPickerScreen
        self.app.font_picker = FontPickerScreen(name="font_picker")
        self.add_widget(self.app.font_picker)

        # Add inputs listing screen and individual scale screens
        from rcp.components.screens.inputs_setup_screen import InputsSetupScreen
        self.add_widget(InputsSetupScreen(name="inputs_setup"))

        from rcp.components.screens.scale_screen import ScaleScreen
        for i in range(len(self.app.scales)):
            self.add_widget(ScaleScreen(name=f"scale_{i}", scale=self.app.scales[i]))

        # Add axes configuration screens
        from rcp.components.screens.axes_setup_screen import AxesSetupScreen
        self.add_widget(AxesSetupScreen(name="axes_setup"))

        from rcp.components.screens.axis_screen import AxisScreen
        for ax in self.app.axes:
            self.add_widget(AxisScreen(name=f"axis_{ax.id_override}", axis=ax))

        # Add screen for servo setup
        from rcp.components.screens.servo_screen import ServoScreen
        self.add_widget(ServoScreen(name="servo", servo=self.app.servo))

        from rcp.components.screens.update_screen import UpdateScreen
        self.add_widget(UpdateScreen(name="update"))

        from rcp.components.screens.system_screen import SystemScreen
        self.add_widget(SystemScreen(name="system"))

        from rcp.components.screens.logs_screen import LogsScreen
        self.add_widget(LogsScreen(name="logs"))

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
