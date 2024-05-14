import os

from keke import ktrace
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import (
    StringProperty,
    NumericProperty,
    ConfigParserProperty,
    BooleanProperty,
    ObjectProperty,
)
from kivy.uix.popup import Popup

from rotary_controller_python.components.appsettings import AppSettings
from rotary_controller_python.components.appsettings import config
from rotary_controller_python.components.home.home_page import HomePage
from rotary_controller_python.dispatchers.formats import FormatsDispatcher
from rotary_controller_python.network.models import Wireless, NetworkInterface
from rotary_controller_python.utils import communication, devices

log = Logger.getChild(__name__)

# for h in log.root.handlers:
#     h.formatter = KivyFormatter('%(asctime)s - %(filename)s:%(lineno)s-%(funcName)s - %(levelname)s - %(message)s')


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
    formats = FormatsDispatcher()
    abs_inc = ConfigParserProperty(
        defaultvalue="ABS", section="global", key="abs_inc", config=config, val_type=str
    )
    current_origin = StringProperty("Origin 0")
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
    task_update = None
    task_update_slow = None
    task_counter = 0

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

    def open_custom_settings(self):
        settings = AppSettings()
        popup = Popup(title="Custom Settings", content=settings, size_hint=(0.9, 0.9))
        popup.open()
        log.info("Settings done")

    def manual_full_update(self):
        self.home.servo.offset = self.device['servo']['absoluteOffset']

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

        # Handle state change disconnected -> connected
        if not self.connected and self.connection_manager.connected:
            self.task_update.timeout = 1.0 / 30
            self.upload()
            self.home.status_bar.maxSpeed = self.device['servo']['maxSpeed']
            self.connected = self.connection_manager.connected

        if self.connection_manager.connected:
            for bar in self.home.coord_bars:
                bar.position = self.fast_data_values['scaleCurrent'][bar.inputIndex] / 1000
            self.home.servo.currentPosition = self.fast_data_values['servoCurrent']
            self.home.servo.desiredPosition = self.fast_data_values['servoDesired']
            self.home.servo.servoEnable = self.fast_data_values['servoEnable']
            # self.home.status_bar.cycles = self.fast_data_values['cycles']
            # self.home.status_bar.interval = self.fast_data_values['executionInterval']
            self.home.status_bar.speed = abs(self.fast_data_values['servoSpeed'])
        self.connected = self.connection_manager.connected

    def upload(self):
        self.home.servo.upload()
        for scale in self.home.coord_bars:
            scale.upload()

    def blinker(self, *args):
        self.home.status_bar.fps = Clock.get_fps()
        self.blink = not self.blink

    def build(self):
        self.home = HomePage(device=self.device)
        self.task_update = Clock.schedule_interval(self.update, 1.0 / 30)
        # self.task_update_slow = Clock.schedule_interval(self.update_slow, 1.0 / 10)
        Clock.schedule_interval(self.blinker, 1.0 / 4)
        return self.home

    def on_stop(self):
        self.home.exit_stack.close()


if __name__ == "__main__":
    # Monkeypatch to add more trace events
    EventLoop.idle = ktrace()(EventLoop.idle)
    MainApp().run()
