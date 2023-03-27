from decimal import Decimal
import logging

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (
    StringProperty,
    NumericProperty,
    ConfigParserProperty,
    BooleanProperty,
    ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout

from rotary_controller_python.device_event_dispatcher import DeviceEventDispatcher
from rotary_controller_python.utils import communication
from rotary_controller_python.config import config
log = logging.getLogger(__file__)


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

    # min_speed = ConfigParserProperty(defaultvalue="150.0", section="rotary", key="min_speed", config=config, val_type=float)
    # max_speed = ConfigParserProperty(defaultvalue="3600.0", section="rotary", key="max_speed", config=config, val_type=float)
    # acceleration = ConfigParserProperty(defaultvalue="5.0", section="rotary", key="acceleration", config=config, val_type=float)
    # ratio_num = ConfigParserProperty(defaultvalue="360", section="rotary", key="ratio_num", config=config, val_type=int)
    # ratio_den = ConfigParserProperty(defaultvalue="1600", section="rotary", key="ratio_den", config=config, val_type=int)

    divisions = NumericProperty(16)
    division_index = NumericProperty(0)
    division_offset = NumericProperty(0.0)
    index_mode = BooleanProperty(False)

    jog_speed = NumericProperty(0.1)
    jog_accel = NumericProperty(0.01)
    jog_forward = BooleanProperty(False)
    jog_backward = BooleanProperty(False)
    jog_mode = BooleanProperty(True)

    # syn_ratio_num = NumericProperty(defaultvalue=1024)
    # syn_ratio_den = NumericProperty(defaultvalue=36000)

    status = NumericProperty(0)
    blink = BooleanProperty(False)
    connected = BooleanProperty(False)

    current_units = ConfigParserProperty(defaultvalue="mm", section="global", key="current_units", config=config, val_type=str)
    abs_inc = ConfigParserProperty(defaultvalue="ABS", section="global", key="abs_inc", config=config, val_type=str)
    unit_factor = NumericProperty(1.0)
    tool = ConfigParserProperty(defaultvalue=0, section="global", key="tool", config=config, val_type=int)
    origin = ConfigParserProperty(defaultvalue=0, section="global", key="origin", config=config, val_type=int)

    # device = ObjectProperty(communication.configure_device())
    device = DeviceEventDispatcher()
    home = Home()

    def on_current_units(self, instance, value):
        if value == "in":
            self.pos_format = self.imperial_pos_format
            self.speed_format = self.imperial_speed_format
            self.unit_factor = 25.4
        else:
            self.pos_format = self.metric_pos_format
            self.speed_format = self.metric_speed_format
            self.unit_factor = 1

    def request_syn_mode(self):
        if self.connected:
            self.device.syn_ratio_num = self.syn_ratio_num
            self.device.syn_ratio_den = self.syn_ratio_den
            self.device.status = communication.MODE_SYNCHRO_INIT

    def request_index_mode(self):
        if self.connected:
            self.device.status = communication.MODE_INDEX_INIT

    def on_syn_ratio_num(self, instance, value):
        self.device.syn_ratio_num = value

    def on_syn_ratio_den(self, instance, value):
        self.device.syn_ratio_den = value

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

        # Clock.schedule_interval(self.update, 1.0 / 25)
        Clock.schedule_interval(self.blinker, 1.0 / 4)
        return self.home


if __name__ == '__main__':
    MainApp().run()
