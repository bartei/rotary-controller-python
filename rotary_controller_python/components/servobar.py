import os

from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

from rotary_controller_python.dispatchers import SavingDispatcher
from rotary_controller_python.utils.devices import Global

log = Logger.getChild(__name__)

current_app = App.get_running_app()
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ServoBar(BoxLayout, SavingDispatcher):
    name = StringProperty("R")
    min_speed = NumericProperty(1)
    max_speed = NumericProperty(1000)
    acceleration = NumericProperty(1000)
    ratio_num = NumericProperty(400)
    ratio_den = NumericProperty(360)
    offset = NumericProperty(0.0)
    divisions = NumericProperty(12)
    index = NumericProperty(0)
    enable = BooleanProperty(False)
    current_position = NumericProperty(0.0)
    desired_position = NumericProperty(0.0)

    def __init__(self, device: Global, **kv):
        self.device = device
        super().__init__(**kv)
        self.upload()

    def upload(self):
        props = self.get_our_properties()
        prop_names = [item.name for item in props]

        device_props = [item.name for item in self.device['servo'].variables]

        matches = [item for item in prop_names if item in device_props]
        for item in matches:
            self.device['servo'][item] = self.__getattribute__(item)

    def on_index(self, instance, value):
        if self.divisions != 0 and self.device is not None:
            self.device['index']['index'] = self.index
            self.device['index']['divisions'] = self.divisions
        else:
            log.error("Divisions must be != 0")
        return True

    def on_offset(self, instance, value):
        self.device['servo']['absolute_offset'] = self.offset
        self.offset = self.device['servo']['absolute_offset']

    def on_divisions(self, instance, value):
        self.device['index']['divisions'] = self.divisions

    def on_min_speed(self, instance, value):
        self.device['servo']['min_speed'] = self.min_speed

    def on_max_speed(self, instance, value):
        self.device['servo']['max_speed'] = self.max_speed

    def on_acceleration(self, instance, value):
        self.device['servo']['acceleration'] = self.acceleration

    def on_ratio_num(self, instance, value):
        self.device['servo']['ratio_num'] = self.ratio_num

    def on_ratio_den(self, instance, value):
        self.device['servo']['ratio_den'] = self.ratio_den
