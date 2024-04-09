import os
import time
import collections

from decimal import Decimal
from kivy.logger import Logger
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

from rotary_controller_python.dispatchers import SavingDispatcher
from rotary_controller_python.utils.addresses import SCALES_COUNT
# from rotary_controller_python.utils.communication import ConnectionManager
# from rotary_controller_python.utils.devices import Global

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class CoordBar(BoxLayout, SavingDispatcher):
    device = ObjectProperty()
    input_index = NumericProperty(0)
    axis_name = StringProperty("?")
    ratio_num = NumericProperty(5)
    ratio_den = NumericProperty(1)
    sync_ratio_num = NumericProperty(360)
    sync_ratio_den = NumericProperty(100)
    sync_enable = BooleanProperty(False)
    position = NumericProperty(0)
    new_position = NumericProperty(0)
    speed = NumericProperty(0.0)
    mode = NumericProperty(0)
    sync_button_color = ListProperty([0.3, 0.3, 0.3, 1])

    _skip_save = ["position", "new_position", "formatted_axis_speed", "sync_enable"]

    def __init__(self, input_index, **kv):
        self.app = App.get_running_app()
        super().__init__(**kv)
        self.input_index = input_index

        self.speed_history = collections.deque(maxlen=5)
        self.previous_axis_time: float = 0
        self.previous_axis_pos: Decimal = Decimal(0)
        self.upload()
        Clock.schedule_interval(self.speed_task, 1.0/25.0)

    def upload(self):
        props = self.get_our_properties()
        prop_names = [item.name for item in props]
        device_props = [item.name for item in self.device['scales'][self.input_index].variables]
        matches = [item for item in prop_names if item in device_props]
        for item in matches:
            log.info(f"Writing scale settings for scale {self.input_index}: {item}={self.__getattribute__(item)}")
            self.device['scales'][self.input_index][item] = self.__getattribute__(item)

    def toggle_sync(self):
        running_app = App.get_running_app()
        self.sync_enable = not self.device['scales'][self.input_index]['sync_enable']
        self.device['scales'][self.input_index]['sync_enable'] = self.sync_enable
        running_app.manual_full_update()

    def on_sync_ratio_num(self, instance, value):
        self.device['scales'][instance.input_index]['sync_ratio_num'] = int(value)

    def on_sync_ratio_den(self, instance, value):
        self.device['scales'][instance.input_index]['sync_ratio_den'] = int(value)

    def on_ratio_num(self, instance, value):
        self.device['scales'][instance.input_index]['ratio_num'] = int(value)

    def on_ratio_den(self, instance, value):
        self.device['scales'][instance.input_index]['ratio_den'] = int(value)

    def on_mode(self, instance, value):
        self.device['scales'][instance.input_index]['mode'] = int(value)

    def on_new_position(self, instance, value):
        self.device['scales'][self.input_index]['position'] = int(float(value) * self.app.formats.factor * 1000)

    def update_position(self):
        if not self.sync_enable and not self.mode == 1:
            self.new_position = self.position
            Factory.Keypad().show(self, 'new_position', self.position)
            # Factory.Keypad(self.new_position).show()

    def zero_position(self):
        self.new_position = 0
        prop = self.property('new_position')
        prop.dispatch(self)

    def speed_task(self, *args, **kv):
        current_time = time.time()

        app = App.get_running_app()
        if app is None:
            return

        if app.fast_data_values is not None:
            speed_or_zero = app.fast_data_values.get('scaleSpeed', [0] * SCALES_COUNT)[self.input_index]
        else:
            speed_or_zero = 0
        self.speed_history.append(speed_or_zero)
        average = (sum(self.speed_history) / len(self.speed_history))

        if app.formats.current_format == "IN":
            # Speed in feet per minute
            self.speed = float(average * 60 / 25.4 / 12)
        else:
            # Speed in mt/minute
            self.speed = float(average * 60 / 1000)

        self.previous_axis_time = current_time
        self.previous_axis_pos = Decimal(self.position)
