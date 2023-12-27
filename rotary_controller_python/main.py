from kivy.uix.popup import Popup
from loguru import logger as log

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
from rotary_controller_python.dispatchers.formats import FormatsDispatcher
from rotary_controller_python.dispatchers.servo import ServoDispatcher
from rotary_controller_python.utils import communication

from rotary_controller_python.components.appsettings import config
from rotary_controller_python.dispatchers.scale import InputClass
from rotary_controller_python.network.models import Wireless, NetworkInterface


class Home(BoxLayout):
    pass


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
    # metric_pos_format = ConfigParserProperty(
    #     defaultvalue="{:+0.3f}", section="formatting", key="metric", config=config
    # )
    metric_speed_format = ConfigParserProperty(
        defaultvalue="{:+0.3f}", section="formatting", key="metric_speed", config=config
    )
    imperial_pos_format = ConfigParserProperty(
        defaultvalue="{:+0.4f}", section="formatting", key="imperial", config=config
    )
    imperial_speed_format = ConfigParserProperty(
        defaultvalue="{:+0.3f}",
        section="formatting",
        key="imperial_speed",
        config=config,
    )
    angle_format = ConfigParserProperty(
        defaultvalue="{:+0.3f}", section="formatting", key="angle", config=config
    )
    pos_format = StringProperty("{}")
    speed_format = StringProperty("{}")

    data = ListProperty([])
    servo = ObjectProperty()

    blink = BooleanProperty(False)
    connected = BooleanProperty(False)

    formats = FormatsDispatcher()
    current_units = ConfigParserProperty(
        defaultvalue="mm",
        section="global",
        key="current_units",
        config=config,
        val_type=str,
    )
    abs_inc = ConfigParserProperty(
        defaultvalue="ABS", section="global", key="abs_inc", config=config, val_type=str
    )
    unit_factor = NumericProperty(1.0)
    current_origin = StringProperty("Origin 0")
    tool = NumericProperty(0)

    serial_port = ConfigParserProperty(
        defaultvalue="/dev/serial0", section="device", key="serial_port", config=config
    )
    device = ObjectProperty()
    home = None

    task_update = None

    def __init__(self, **kv):
        super().__init__(**kv)
        try:
            self.device = communication.DeviceManager(
                serial_device=self.serial_port, baudrate=115200, address=17
            )
        except Exception as e:
            log.error(f"Communication cannot be started, will try again: {e.__str__()}")

        self.servo = ServoDispatcher(device=self.device)
        self.data = [
            InputClass(0, self.device),
            InputClass(1, self.device),
            InputClass(2, self.device),
            InputClass(3, self.device),
        ]

    def on_network_settings(self):
        print(self.network_settings.dict())

    def open_custom_settings(self):
        settings = AppSettings()
        popup = Popup(title="Custom Settings", content=settings, size_hint=(0.9, 0.9))
        popup.open()

    def on_current_units(self, instance, value):
        if value == "in":
            self.pos_format = self.formats.imperial_position
            self.speed_format = self.formats.imperial_speed
            self.unit_factor = 25.4
        else:
            self.pos_format = self.formats.metric_position
            self.speed_format = self.metric_speed_format
            self.unit_factor = 1

    def update(self, *args):
        if self.device is not None and self.device.connected:
            for i in range(len(self.device.scales)):
                self.data[i].position = self.device.scales[i].position / 1000

            self.servo.current_position = self.device.servo.current_position
            self.servo.desired_position = self.device.servo.desired_position

        else:
            try:
                self.device = communication.DeviceManager(
                    serial_device=self.serial_port, baudrate=115200, address=17
                )
                if not self.device.connected:
                    raise Exception("No Connection")

                self.servo.upload()
                self.device.servo.acceleration = self.acceleration
                self.device.servo.max_speed = self.max_speed
                self.device.servo.min_speed = self.min_speed
                self.device.servo.ratio_num = self.ratio_num
                self.device.servo.ratio_den = self.ratio_den

                self.connected = True
                log.warning(f"Device connection: {self.device.connected}")
                self.task_update.timeout = 1.0 / 20
            except Exception as e:
                self.connected = False
                log.error(e.__str__())
                self.task_update.timeout = 2.0

    def blinker(self, *args):
        self.blink = not self.blink

    def build(self):
        self.home = Home()
        if self.current_units == "mm":
            self.pos_format = self.formats.metric_position
            self.speed_format = self.metric_speed_format
            self.unit_factor = 1.0
        else:
            self.pos_format = self.imperial_pos_format
            self.speed_format = self.imperial_speed_format
            self.unit_factor = 25.4

        self.task_update = Clock.schedule_interval(self.update, 1.0 / 20)
        Clock.schedule_interval(self.blinker, 1.0 / 4)
        return self.home


if __name__ == "__main__":
    MainApp().run()
