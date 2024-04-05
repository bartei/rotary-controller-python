import os

from kivy.uix.popup import Popup
from kivy.logger import Logger, KivyFormatter

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (
    StringProperty,
    NumericProperty,
    ConfigParserProperty,
    BooleanProperty,
    ListProperty,
    ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout
from rotary_controller_python.components.appsettings import AppSettings
from rotary_controller_python.components.coordbar import CoordBar
from rotary_controller_python.components.servobar import ServoBar
from rotary_controller_python.components.statusbar import StatusBar
from rotary_controller_python.dispatchers.formats import FormatsDispatcher
from rotary_controller_python.utils import communication

from rotary_controller_python.components.appsettings import config
from rotary_controller_python.network.models import Wireless, NetworkInterface

log = Logger.getChild(__name__)

for h in log.root.handlers:
    h.formatter = KivyFormatter('%(asctime)s - %(filename)s:%(lineno)s-%(funcName)s - %(levelname)s - %(message)s')


class Home(BoxLayout):
    device = ObjectProperty()
    status_bar = ObjectProperty()
    bars_container = ObjectProperty()
    coord_bars = ListProperty([])
    servo = ObjectProperty()

    def __init__(self, device, **kv):
        super().__init__(**kv)
        self.device = device

        self.status_bar = StatusBar()
        self.bars_container.add_widget(self.status_bar)
        coord_bars = []
        for i in range(4):
            bar = CoordBar(input_index=i, device=self.device)
            coord_bars.append(bar)
            self.bars_container.add_widget(bar)

        self.coord_bars = coord_bars
        self.servo = ServoBar(device=self.device)
        self.bars_container.add_widget(self.servo)


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
        defaultvalue="57600", section="device", key="baudrate", config=config, val_type=int
    )
    serial_address = ConfigParserProperty(
        defaultvalue=7, section="device", key="address", config=config, val_type=int
    )
    device = ObjectProperty()
    home = ObjectProperty()
    task_update = None
    task_update_slow = None
    task_counter = 0

    def __init__(self, **kv):
        try:
            self.device = communication.DeviceManager(
                serial_device=self.serial_port,
                baudrate=self.serial_baudrate,
                address=self.serial_address
            )
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

    # def update_slow(self, *args):
    #     if self.device.connected:
            # self.home.status_bar.speed = self.device.servo.estimated_speed * self.home.servo.ratio_den / self.home.servo.ratio_num
            # self.home.status_bar.interval = self.device.base.execution_interval
            # self.home.status_bar.interval = self.device.servo.allowed_error
            # for i, item in enumerate(self.home.coord_bars):
            #     item.speed = self.device.scales[i].speed

    def manual_full_update(self):
        self.home.status_bar.cycles = self.device.fast_data.cycles
        self.home.status_bar.interval = self.device.base.execution_interval
        self.home.servo.offset = self.device.servo.absolute_offset

    def update(self, *args):
        try:
            self.device.fast_data.refresh()
            if not self.device.connected:
                self.device.connected = True

        except Exception as e:
            log.error(f"No connection: {e.__str__()}")
            self.task_update.timeout = 2.0
            self.device.connected = False

        if not self.connected and self.device.connected:
            self.task_update.timeout = 1.0 / 25
            self.upload()

        if self.device.connected:
            for bar in self.home.coord_bars:
                bar.position = self.device.fast_data.scale_current[bar.input_index]
                bar.speed = self.device.fast_data.scale_speed[bar.input_index]
            self.home.servo.current_position = self.device.fast_data.servo_current
            self.home.servo.desired_position = self.device.fast_data.servo_desired
            self.home.status_bar.max_speed = self.home.servo.max_speed
            self.home.status_bar.speed = abs(self.device.fast_data.servo_speed)
            self.home.status_bar.cycles = self.device.fast_data.cycles
            self.home.status_bar.interval = self.device.fast_data.execution_interval

        self.connected = self.device.connected

    def upload(self):
        self.home.servo.upload()
        for scale in self.home.coord_bars:
            scale.upload()

    def blinker(self, *args):
        self.home.status_bar.fps = Clock.get_fps()
        self.blink = not self.blink

    def build(self):
        self.home = Home(device=self.device)
        self.task_update = Clock.schedule_interval(self.update, 1.0 / 30)
        # self.task_update_slow = Clock.schedule_interval(self.update_slow, 1.0 / 10)
        Clock.schedule_interval(self.blinker, 1.0 / 4)
        return self.home


if __name__ == "__main__":
    MainApp().run()
