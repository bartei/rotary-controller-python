import os
from typing import List

from keke import ktrace
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.logger import Logger, KivyFormatter
from kivy.properties import (
    NumericProperty,
    ConfigParserProperty,
    BooleanProperty,
    ObjectProperty, ListProperty,
)

from rcp.components.appsettings import config
from rcp.components.home.coordbar import CoordBar
from rcp.components.home.home_page import HomePage
from rcp.components.home.servobar import ServoBar
from rcp.dispatchers.formats import FormatsDispatcher
from rcp.network.models import Wireless, NetworkInterface
from rcp.utils import communication, devices
from kivy.core.window import Window

log = Logger.getChild(__name__)

# Window.show_cursor = False

for h in log.root.handlers:
    h.formatter = KivyFormatter('%(asctime)s - %(name)s:%(lineno)s-%(funcName)s - %(levelname)s - %(message)s')


class MainApp(App):
    network_settings = ObjectProperty(
        defaultvalue=NetworkInterface(
            name="wlan0",
            dhcp=False,
            address="10.0.0.1/24",
            gateway="10.0.0.254",
            wireless=Wireless(ssid="test", password="test"),
        )
    )
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

        sound_file = f"{os.path.dirname(__file__)}/sounds/beep.mp3"
        self.sound = SoundLoader.load(sound_file)

    def beep(self, *args, **kv):
        self.sound.volume = self.formats.volume
        self.sound.play()

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

    def on_network_settings(self):
        print(self.network_settings.dict())

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
            self.task_update.timeout = 1.0 / 20
            self.connected = self.connection_manager.connected

        if self.connection_manager.connected:
            self.update_tick = (self.update_tick + 1) % 100

        self.connected = self.connection_manager.connected

    def blinker(self, *args):
        self.blink = not self.blink

    def build(self):
        self.formats = FormatsDispatcher(id_override="0")
        self.servo = ServoBar(
            id_override="0",
        )
        for i in range(4):
            self.scales.append(CoordBar(inputIndex=i, device=self.device, id_override=f"{i}"))

        self.home = HomePage()
        self.task_update = Clock.schedule_interval(self.update, 1.0 / 30)
        Clock.schedule_interval(self.blinker, 1.0 / 4)

        self.beep()
        return self.home

    def on_stop(self):
        self.home.exit_stack.close()


if __name__ == "__main__":
    # Monkeypatch to add more trace events
    EventLoop.idle = ktrace()(EventLoop.idle)
    MainApp().run()
