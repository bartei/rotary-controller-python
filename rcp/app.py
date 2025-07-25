import os
from typing import List


from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, CardTransition, FadeTransition
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty, ConfigParserProperty, BooleanProperty, NumericProperty, ListProperty, \
    StringProperty

from rcp.components.appsettings import config
from rcp.components.home.home_page import HomePage
from rcp.components.home.coordbar import CoordBar
from rcp.components.home.servobar import ServoBar
from rcp.components.setup.servo_screen import ServoScreen
from rcp.components.setup.setup_screen import SetupScreen
from rcp.components.setup.network_screen import NetworkScreen
from rcp.components.setup.formats_screen import FormatsScreen

from rcp.dispatchers.formats import FormatsDispatcher
from rcp.main import log
from rcp.utils import communication, devices

import sentry_sdk


class MainApp(App):
    display_color = ConfigParserProperty(
        defaultvalue="#ffffffff",
        section="formatting",
        key="display_color",
        config=config,
    )

    blink = BooleanProperty(False)
    connected = BooleanProperty(False)
    formats = ObjectProperty()
    abs_inc = ConfigParserProperty(
        defaultvalue="ABS", section="global", key="abs_inc", config=config, val_type=str
    )
    currentOffset = NumericProperty(0)
    tool = NumericProperty(0)
    serial_port = ConfigParserProperty(
        defaultvalue="/dev/serial0", section="device", key="serial_port", config=config, val_type=str
    )
    serial_baudrate = ConfigParserProperty(
        defaultvalue="115200", section="device", key="baudrate", config=config, val_type=int
    )
    serial_address = ConfigParserProperty(
        defaultvalue=17, section="device", key="address", config=config, val_type=int
    )
    device = ObjectProperty()
    home = ObjectProperty()
    update_tick = NumericProperty(0)

    servo: ServoBar = ObjectProperty()
    scales: List[CoordBar] = ListProperty()
    current_mode = ConfigParserProperty(
        defaultvalue=1, section="device", key="current_mode", config=config, val_type=int
    )
    scales_count = ConfigParserProperty(
        defaultvalue=4, section="device", key="scales_count", config=config, val_type=int
    )
    color_picker = ObjectProperty()
    scale_screens = ListProperty()

    previous = ListProperty()
    manager = ObjectProperty()

    version = StringProperty()

    task_update = None

    def __init__(self, **kv):
        self.fast_data_values = dict()
        try:
            self.connection_manager = communication.ConnectionManager(
                serial_device=self.serial_port,
                baudrate=self.serial_baudrate,
                address=self.serial_address
            )
            self.device = devices.Global(connection_manager=self.connection_manager, base_address=0)

        except Exception as e:
            log.error(f"Communication cannot be started, will try again: {e.__str__()}")

        super().__init__(**kv)

        # sound_file = f"{os.path.dirname(__file__)}/sounds/beep.mp3"
        # self.sound = SoundLoader.load(sound_file)

    def beep(self, *args, **kv):
        pass
        # self.sound.volume = self.formats.volume
        # self.sound.play()

    @staticmethod
    def load_help(help_file_name):
        """
        Loads the specified help file text from the help files folder.
        """
        help_file_path = os.path.join(
            os.path.dirname(__file__),
            "help",
            help_file_name
        )
        if not os.path.exists(help_file_path):
            return "Help file not found"

        with open(help_file_path, "r") as f:
            return f.read()

    def set_mode(self, mode_id: int):
        self.current_mode = mode_id

    def get_spindle_scale(self):
        """
        Returns the current spindle scale if there is one configured, otherwise None
        """
        filtered_scales = [item for item in self.scales if item.spindleMode is True]
        if len(filtered_scales) != 1:
            return None
        return filtered_scales[0]

    def update(self, *args):
        try:
            self.fast_data_values = self.device['fastData'].refresh()

        except Exception as e:
            log.error(f"No connection: {e.__str__()}")
            self.task_update.timeout = 2.0
            self.connection_manager.connected = False

        # Handle state change connected -> disconnected
        if not self.connection_manager.connected:
            self.connected = self.connection_manager.connected
            self.task_update.timeout = 2.0
            self.update_tick = (self.update_tick + 1) % 100

        # Handle state change disconnected -> connected
        if not self.connected and self.connection_manager.connected:
            self.task_update.timeout = 1.0 / 30
            self.connected = self.connection_manager.connected

        if self.connection_manager.connected:
            self.update_tick = (self.update_tick + 1) % 100

        self.connected = self.connection_manager.connected

    def blinker(self, *args):
        self.blink = not self.blink

    def set_previous(self, instance, value):
        self.previous.append(value)
        log.info(f"Previous history: {self.previous}")

    def back(self):
        # self.manager.transition.mode = "pop"
        self.manager.current = self.previous.pop()
        log.debug(f"Back array {self.previous}")

    def goto(self, screen: str):
        # self.manager.transition.mode = "push"
        self.previous.append(self.manager.current)
        log.debug(f"Goto array {self.previous}")
        self.manager.current = screen

    def build(self):
        self.formats = FormatsDispatcher(id_override="0")

        if not self.formats.disable_error_reporting:
            log.info("Error reporting is enabled, configuring Sentry")
            sentry_sdk.init(
                dsn="https://8fd20c0607e9c930a16d51a4b1eacc94@o4509625403506688.ingest.us.sentry.io/4509625405014016",
                send_default_pii=False,
                traces_sample_rate=0.2,
            )

        self.servo = ServoBar(
            id_override="0",
        )
        for i in range(4):
            self.scales.append(CoordBar(inputIndex=i, device=self.device, id_override=f"{i}"))

        self.task_update = Clock.schedule_interval(self.update, 1.0 / 30)
        Clock.schedule_interval(self.blinker, 1.0 / 4)
        self.beep()

        import importlib.metadata
        self.version = "v" + importlib.metadata.version("rcp")

        self.manager = ScreenManager(transition=FadeTransition())
        self.manager.transition.duration = .05
        self.manager.add_widget(HomePage(name="home"))
        self.manager.add_widget(SetupScreen(name="setup_screen"))
        self.manager.add_widget(NetworkScreen(name="network"))
        self.manager.add_widget(FormatsScreen(name="formats"))

        # Add screen for color picker
        from rcp.components.setup.color_picker_screen import ColorPickerScreen
        self.color_picker = ColorPickerScreen(name="color_picker")
        self.manager.add_widget(self.color_picker)

        # Add screens for scales setup
        from rcp.components.setup.scale_screen import ScaleScreen
        for i in range(len(self.scales)):
            self.manager.add_widget(ScaleScreen(name=f"scale_{i}", scale=self.scales[i]))

        # Add screen for servo setup
        self.manager.add_widget(ServoScreen(name="servo", servo=self.servo))

        # Add screen for servo setup
        from rcp.components.setup.update_screen import UpdateScreen
        self.manager.add_widget(UpdateScreen(name="update"))

        # Add screen for plot view
        from rcp.components.plot.plot_screen import PlotScreen
        self.manager.add_widget(PlotScreen(name="plot"))
        self.manager.current = "home"

        return self.manager
