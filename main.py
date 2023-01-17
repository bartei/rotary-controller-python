from decimal import Decimal
import logging

from kivy.app import App
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty, ConfigParserProperty, BooleanProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from components.appsettings import config
from utils.communication import device, configure_device
from utils import communication

log = logging.getLogger(__file__)


def input_class_factory():
    input_classes = []

    for item in range(4):
        section = f"input{item + 1}"

        class InputClass(EventDispatcher):
            scale_input = item
            axis_name = ConfigParserProperty(defaultvalue="X", section=section, key="axis_name", config=config, val_type=str)
            ratio_num = ConfigParserProperty(defaultvalue=360, section=section, key="ratio_num", config=config, val_type=int)
            ratio_den = ConfigParserProperty(defaultvalue=1, section=section, key="ratio_den", config=config, val_type=int)
            sync_num = ConfigParserProperty(defaultvalue=1, section=section, key="sync_num", config=config, val_type=int)
            sync_den = ConfigParserProperty(defaultvalue=100, section=section, key="sync_den", config=config, val_type=int)
            sync_enable = ConfigParserProperty(defaultvalue="normal", section=section, key="sync_enable", config=config, val_type=str)
            position = NumericProperty(123.123)

            @property
            def update_raw_scale(self):
                return 0

            @update_raw_scale.setter
            def update_raw_scale(self, value):
                if self.ratio_den != 0:
                    self.position = float(value) * float(self.ratio_num) / float(self.ratio_den)
                else:
                    self.position = 0

            @property
            def set_position(self):
                return 0

            @set_position.setter
            def set_position(self, value):
                from utils.communication import device
                try:
                    log.warning(f"Set New position to: {value} for {self.scale_input}")
                    decimal_value = Decimal(self.ratio_den) / Decimal(self.ratio_num) * Decimal(value)
                    int_value = int(decimal_value)
                    log.warning(f"Raw value set to to: {int_value}")
                    device.encoder_preset_index = self.scale_input
                    device.encoder_preset_value = int_value
                    device.mode = communication.MODE_SET_ENCODER
                except Exception as e:
                    log.exception(e.__str__())
                    self.position = 9999.99

        input_classes.append(InputClass)

    return input_classes


classes = input_class_factory()


class Home(BoxLayout):
    pass


class MainApp(App):
    display_color = ConfigParserProperty(defaultvalue="#ffffffff", section="formatting", key="display_color", config=config)
    metric_pos_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="metric", config=config)
    metric_speed_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="metric_speed", config=config)
    imperial_pos_format = ConfigParserProperty(defaultvalue="{:+0.4f}", section="formatting", key="imperial", config=config)
    imperial_speed_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="imperial_speed", config=config)
    angle_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="angle", config=config)
    pos_format = StringProperty("{}")
    speed_format = StringProperty("{}")

    min_speed = ConfigParserProperty(defaultvalue="150.0", section="rotary", key="min_speed", config=config, val_type=float)
    max_speed = ConfigParserProperty(defaultvalue="3600.0", section="rotary", key="max_speed", config=config, val_type=float)
    acceleration = ConfigParserProperty(defaultvalue="5.0", section="rotary", key="acceleration", config=config, val_type=float)
    ratio_num = ConfigParserProperty(defaultvalue="360", section="rotary", key="ratio_num", config=config, val_type=int)
    ratio_den = ConfigParserProperty(defaultvalue="1600", section="rotary", key="ratio_den", config=config, val_type=int)

    # X Axis properties
    data = ListProperty([
        classes[0](),
        classes[1](),
        classes[2](),
        classes[3](),
    ])

    desired_position = NumericProperty(0.0)
    current_position = NumericProperty(0.0)

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

    current_units = ConfigParserProperty(defaultvalue="mm", section="global", key="current_units", config=config, val_type=str)
    abs_inc = ConfigParserProperty(defaultvalue="ABS", section="global", key="abs_inc", config=config, val_type=str)
    unit_factor = NumericProperty(1.0)
    current_origin = StringProperty("Origin 0")
    tool = NumericProperty(0)

    device = None
    home = None

    def on_current_units(self, instance, value):
        if value == "in":
            self.pos_format = self.imperial_pos_format
            self.speed_format = self.imperial_speed_format
            self.unit_factor = 25.4
        else:
            self.pos_format = self.metric_pos_format
            self.speed_format = self.metric_speed_format
            self.unit_factor = 1

    def set_desired_position(self, value):
        self.desired_position = value

    def set_division_offset(self, value):
        self.division_offset = value

    def set_division_index(self, value):
        self.division_index = value

    def set_divisions(self, value):
        self.divisions = value

    def set_jog_speed(self, value):
        self.jog_speed = value

    def set_jog_accel(self, value):
        self.jog_accel = value

    def set_sync_numerator(self, value):
        self.syn_ratio_num = abs(int(value))

    def set_sync_denominator(self, value):
        self.syn_ratio_den = int(value)

    def update_desired_position(self, *args, **kwargs):
        if not self.divisions > 0:
            self.divisions = 1

        self.desired_position = 360 / self.divisions * self.division_index + self.division_offset
        return True

    def update(self, *args, **kwargs):
        if self.device is not None:
            scales = self.device.scales

            for count, scale in enumerate(scales):
                self.data[count].update_raw_scale = scale

            if not self.device.connected:
                self.mode = communication.MODE_DISCONNECTED
            else:
                self.mode = self.device.mode
        else:
            for axis in self.data:
                axis.update_raw_scale = 100

            self.mode = communication.MODE_DISCONNECTED

    def on_desired_position(self, instance, value):
        if self.connected:
            # Always send out the motion settings
            self.device.min_speed = self.min_speed
            self.device.max_speed = self.max_speed
            self.device.acceleration = self.acceleration
            self.device.ratio_num = self.ratio_num
            self.device.ratio_den = self.ratio_den
            self.device.mode = 0
            # Send the destination converted to steps
            self.device.final_position = int(value / self.ratio_num * self.ratio_den)

    def on_ratio_num(self, instance, value):
        self.device.ratio_num = value

    def on_ratio_den(self, instance, value):
        self.device.ratio_den = value

    def on_acceleration(self, instance, value):
        self.device.acceleration = float(value)

    def on_min_speed(self, instance, value):
        self.device.min_speed = float(value)

    def on_max_speed(self, instance, value):
        self.device.max_speed = float(value)

    def request_syn_mode(self):
        if self.connected:
            self.device.syn_ratio_num = self.syn_ratio_num
            self.device.syn_ratio_den = self.syn_ratio_den
            self.device.mode = communication.MODE_SYNCHRO_INIT

    def request_index_mode(self):
        if self.connected:
            self.device.mode = communication.MODE_INDEX_INIT

    def on_syn_ratio_num(self, instance, value):
        self.device.syn_ratio_num = value

    def on_syn_ratio_den(self, instance, value):
        self.device.syn_ratio_den = value

    def blinker(self, *args):
        self.blink = not self.blink

    def configure_device(self, *args):
        from utils.communication import device
        configure_device()

        if device is None:
            # Retry in 5 seconds if the connection failed
            Clock.schedule_once(self.configure_device, timeout=5)
            log.warning("Retrying to connect in 5 seconds")
            self.connected = False
        else:
            self.device = device
            self.device.ratio_num = self.ratio_num
            self.device.ratio_den = self.ratio_den
            self.device.acceleration = self.acceleration
            self.device.max_speed = self.max_speed
            self.device.min_speed = self.min_speed
            self.connected = self.device.connected
            log.warning(f"Device connection: {self.device.connected}")

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

        self.bind(divisions=self.update_desired_position)
        self.bind(division_index=self.update_desired_position)
        self.bind(division_offset=self.update_desired_position)

        # Configure the modbus communication
        self.configure_device()

        Clock.schedule_interval(self.update, 1.0 / 25)
        Clock.schedule_interval(self.blinker, 1.0 / 4)
        return self.home


if __name__ == '__main__':
    MainApp().run()
