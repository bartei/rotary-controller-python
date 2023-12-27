from decimal import Decimal

from kivy.uix.popup import Popup
from loguru import logger as log

from kivy.app import App
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty, ConfigParserProperty, BooleanProperty, ListProperty, \
    DictProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from rotary_controller_python.components.appsettings import config, AppSettings
from rotary_controller_python.utils import communication

from rotary_controller_python.components.appsettings import config
from rotary_controller_python.input_class import InputClass
from rotary_controller_python.network.models import Wireless, NetworkInterface
from rotary_controller_python.utils.communication import DeviceManager


class ServoClass(EventDispatcher):
    name = ConfigParserProperty(defaultvalue="R", section="rotary", key="name", config=config, val_type=str)
    min_speed = ConfigParserProperty(defaultvalue="150.0", section="rotary", key="min_speed", config=config,
                                     val_type=float)
    max_speed = ConfigParserProperty(defaultvalue="3600.0", section="rotary", key="max_speed", config=config,
                                     val_type=float)
    acceleration = ConfigParserProperty(defaultvalue="5.0", section="rotary", key="acceleration", config=config,
                                        val_type=float)
    ratio_num = ConfigParserProperty(defaultvalue="360", section="rotary", key="ratio_num", config=config, val_type=int)
    ratio_den = ConfigParserProperty(defaultvalue="1600", section="rotary", key="ratio_den", config=config,
                                     val_type=int)

    current_position = NumericProperty(0.0)
    desired_position = NumericProperty(0.0)

    # Offset to add to the sync and index calculated values
    offset = ConfigParserProperty(defaultvalue="0.0", section="rotary", key="offset", config=config, val_type=float)
    divisions = ConfigParserProperty(defaultvalue="0", section="rotary", key="divisions", config=config, val_type=int)
    index = ConfigParserProperty(defaultvalue="0", section="rotary", key="index", config=config, val_type=int)
    enable = BooleanProperty(False)

    def on_index(self, instance, value):
        app = App.get_running_app()
        app.device: DeviceManager
        if self.divisions != 0:
            app.device.index.index = self.index
            app.device.index.divisions = self.divisions
        else:
            log.error("Divisions must be != 0")
        return True

    def on_offset(self, instance, value):
        app = App.get_running_app()
        app.device: DeviceManager
        app.device.servo.absolute_offset = self.offset


class Home(BoxLayout):
    pass


class MainApp(App):
    network_settings = ObjectProperty(defaultvalue=NetworkInterface(
        name="wlan0",
        dhcp=False,
        address="10.0.0.1/24",
        gateway="10.0.0.254",
        wireless=Wireless(
            ssid="test",
            password="test"
        )
    ))

    display_color = ConfigParserProperty(defaultvalue="#ffffffff", section="formatting", key="display_color",
                                         config=config)
    metric_pos_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="metric", config=config)
    metric_speed_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="metric_speed",
                                               config=config)
    imperial_pos_format = ConfigParserProperty(defaultvalue="{:+0.4f}", section="formatting", key="imperial",
                                               config=config)
    imperial_speed_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="imperial_speed",
                                                 config=config)
    angle_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="angle", config=config)
    pos_format = StringProperty("{}")
    speed_format = StringProperty("{}")

    min_speed = ConfigParserProperty(defaultvalue="150.0", section="rotary", key="min_speed", config=config,
                                     val_type=float)
    max_speed = ConfigParserProperty(defaultvalue="3600.0", section="rotary", key="max_speed", config=config,
                                     val_type=float)
    acceleration = ConfigParserProperty(defaultvalue="5.0", section="rotary", key="acceleration", config=config,
                                        val_type=float)
    ratio_num = ConfigParserProperty(defaultvalue="360", section="rotary", key="ratio_num", config=config, val_type=int)
    ratio_den = ConfigParserProperty(defaultvalue="1600", section="rotary", key="ratio_den", config=config,
                                     val_type=int)

    data = ListProperty([
        InputClass(0),
        InputClass(1),
        InputClass(2),
        InputClass(3),
    ])
    servo = ServoClass()

    desired_position = NumericProperty(0.0)
    # current_position = NumericProperty(0.0)

    divisions = NumericProperty(16)
    division_index = NumericProperty(0)
    division_offset = NumericProperty(0.0)
    index_mode = BooleanProperty(False)

    jog_speed = NumericProperty(0.1)
    jog_accel = NumericProperty(0.01)
    jog_forward = BooleanProperty(False)
    jog_backward = BooleanProperty(False)
    jog_mode = BooleanProperty(True)

    syn_ratio_num = NumericProperty(defaultvalue=1024)
    syn_ratio_den = NumericProperty(defaultvalue=36000)

    mode = NumericProperty(0)
    blink = BooleanProperty(False)
    connected = BooleanProperty(False)

    current_units = ConfigParserProperty(defaultvalue="mm", section="global", key="current_units", config=config,
                                         val_type=str)
    abs_inc = ConfigParserProperty(defaultvalue="ABS", section="global", key="abs_inc", config=config, val_type=str)
    unit_factor = NumericProperty(1.0)
    current_origin = StringProperty("Origin 0")
    tool = NumericProperty(0)

    serial_port = ConfigParserProperty(defaultvalue="/dev/serial0", section="device", key="serial_port", config=config)
    device = None
    home = None

    task_update = None

    def on_network_settings(self):
        print(self.network_settings.dict())

    def open_custom_settings(self):
        settings = AppSettings()
        popup = Popup(title='Custom Settings', content=settings, size_hint=(0.9, 0.9))
        popup.open()

    def on_current_units(self, instance, value):
        if value == "in":
            self.pos_format = self.imperial_pos_format
            self.speed_format = self.imperial_speed_format
            self.unit_factor = 25.4
        else:
            self.pos_format = self.metric_pos_format
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
                    serial_device=self.serial_port,
                    baudrate=115200,
                    address=17
                )
                if not self.device.connected:
                    raise Exception("No Connection")

                self.device.servo.acceleration = self.acceleration
                self.device.servo.max_speed = self.max_speed
                self.device.servo.min_speed = self.min_speed
                self.device.servo.ratio_num = self.ratio_num
                self.device.servo.ratio_den = self.ratio_den

                self.connected = True
                log.warning(f"Device connection: {self.device.connected}")
                self.task_update.timeout = 1.0 / 25
            except Exception as e:
                self.connected = False
                log.error(e.__str__())
                self.device = None
                self.task_update.timeout = 2.0

    def on_ratio_num(self, instance, value):
        self.device.servo.ratio_num = value

    def on_ratio_den(self, instance, value):
        self.device.servo.ratio_den = value

    def on_acceleration(self, instance, value):
        self.device.servo.acceleration = float(value)

    def on_min_speed(self, instance, value):
        self.device.servo.min_speed = float(value)

    def on_max_speed(self, instance, value):
        self.device.servo.max_speed = float(value)

    def blinker(self, *args):
        self.blink = not self.blink

    def build(self):
        self.home = Home()
        if self.current_units == "mm":
            self.pos_format = self.metric_pos_format
            self.speed_format = self.metric_speed_format
            self.unit_factor = 1.0
        else:
            self.pos_format = self.imperial_pos_format
            self.speed_format = self.imperial_speed_format
            self.unit_factor = 25.4

        self.task_update = Clock.schedule_interval(self.update, 1.0 / 25)
        Clock.schedule_interval(self.blinker, 1.0 / 4)
        return self.home


if __name__ == '__main__':
    MainApp().run()
