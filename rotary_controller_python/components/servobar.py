import logging
import os
from _decimal import Decimal

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ConfigParserProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from rotary_controller_python.config import config
from rotary_controller_python.device_event_dispatcher import DeviceEventDispatcher
from rotary_controller_python.utils.communication import DeviceManager

# current_app = App.get_running_app()
log = logging.getLogger(__file__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ServoBar(BoxLayout):
    name = ConfigParserProperty(defaultvalue="R", section="rotary", key="name", config=config, val_type=str)
    min_speed = ConfigParserProperty(defaultvalue="150.0", section="rotary", key="min_speed", config=config, val_type=float)
    max_speed = ConfigParserProperty(defaultvalue="3600.0", section="rotary", key="max_speed", config=config, val_type=float)
    acceleration = ConfigParserProperty(defaultvalue="5.0", section="rotary", key="acceleration", config=config, val_type=float)
    ratio_num = ConfigParserProperty(defaultvalue="360", section="rotary", key="ratio_num", config=config, val_type=int)
    ratio_den = ConfigParserProperty(defaultvalue="1600", section="rotary", key="ratio_den", config=config, val_type=int)

    # current_position = NumericProperty(0.0)
    # desired_position = NumericProperty(0.0)

    # Offset to add to the sync and index calculated values
    offset = ConfigParserProperty(defaultvalue="0.0", section="rotary", key="offset", config=config, val_type=float)
    divisions = ConfigParserProperty(defaultvalue="0", section="rotary", key="divisions", config=config, val_type=int)
    index = ConfigParserProperty(defaultvalue="0", section="rotary", key="index", config=config, val_type=int)
    enable = BooleanProperty(False)
    device: DeviceEventDispatcher = ObjectProperty(DeviceEventDispatcher())

    def on_enable(self, instance, value):
        if self.device is not None:
            log.warning(f"The status of the synchro is set to: {self.enable}")
            self.device.global_enable = value

    def on_index(self, instance, value):
        log.warning(f"The index changed to: {value}")
        if self.divisions > 0:
            self.device.final_position = 360 / self.divisions * self.index + self.offset

    def on_offset(self, instance, value):
        log.warning(f"The offset changed to: {value}")
        if self.divisions > 0:
            self.device.final_position = 360 / self.divisions * self.index + self.offset

    def on_divisions(self, instance, value):
        self.index = self.index % self.divisions
        log.warning(f"The offset changed to: {value}")
        if self.divisions > 0:
            self.device.final_position = 360 / self.divisions * self.index + self.offset

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

    def __init__(self, *args, **kv):
        super(ServoBar, self).__init__(**kv)
        self.on_index(self, self.index)
        self.device.ratio_num = self.ratio_num
        self.device.ratio_den = self.ratio_den
        self.device.acceleration = self.acceleration
        self.device.min_speed = self.min_speed
        self.device.max_speed = self.max_speed
