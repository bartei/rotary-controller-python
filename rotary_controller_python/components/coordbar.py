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
from rotary_controller_python.utils.devices import SCALES_COUNT

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class CoordBar(BoxLayout, SavingDispatcher):
    device = ObjectProperty()
    inputIndex = NumericProperty(0)
    axisName = StringProperty("?")
    ratioNum = NumericProperty(5)
    ratioDen = NumericProperty(1)
    syncRatioNum = NumericProperty(360)
    syncRatioDen = NumericProperty(100)
    syncEnable = BooleanProperty(False)
    position = NumericProperty(0)
    newPosition = NumericProperty(0)
    speed = NumericProperty(0.0)
    mode = NumericProperty(0)
    syncButtonColor = ListProperty([0.3, 0.3, 0.3, 1])

    _skip_save = ["position", "newPosition", "syncEnable", "speed", ]

    def __init__(self, **kv):
        self.app = App.get_running_app()
        super().__init__(**kv)

        self.speed_history = collections.deque(maxlen=5)
        self.previous_axis_time: float = 0
        self.previous_axis_pos: Decimal = Decimal(0)
        self.upload()
        Clock.schedule_interval(self.speed_task, 1.0/25.0)

    def upload(self):
        if self.device is None:
            return

        if not self.device.dm.connected:
            log.error(f"Unable to upload scale {self.inputIndex} connection is down!")
            return
        props = self.get_our_properties()
        prop_names = [item.name for item in props]
        device_props = [item.name for item in self.device['scales'][self.inputIndex].variables]
        matches = [item for item in prop_names if item in device_props]
        for item in matches:
            log.info(f"Writing scale settings for scale {self.inputIndex}: {item}={self.__getattribute__(item)}")
            self.device['scales'][self.inputIndex][item] = self.__getattribute__(item)

    def toggle_sync(self):
        current_app = App.get_running_app()
        if not current_app.connected:
            return
        self.syncEnable = not self.device['scales'][self.inputIndex]['syncEnable']
        self.device['scales'][self.inputIndex]['syncEnable'] = self.syncEnable

    def on_syncRatioNum(self, instance, value):
        self.device['scales'][instance.inputIndex]['syncRatioNum'] = int(value)

    def on_syncRatioDen(self, instance, value):
        self.device['scales'][instance.inputIndex]['syncRatioDen'] = int(value)

    # def on_ratioNum(self, instance, value):
    #     self.device['scales'][instance.inputIndex]['ratioNum'] = int(value)

    # def on_ratioDen(self, instance, value):
    #     self.device['scales'][instance.inputIndex]['ratioDen'] = int(value)

    # def on_mode(self, instance, value):
    #     self.device['scales'][instance.inputIndex]['mode'] = int(value)

    def on_newPosition(self, instance, value):
        self.device['scales'][self.inputIndex]['position'] = int(float(value) * self.app.formats.factor * 1000)

    def update_position(self):
        current_app = App.get_running_app()
        if not self.syncEnable and not self.mode == 1:
            Factory.Keypad().show(self, 'newPosition', self.position / current_app.formats.factor)

    def zero_position(self):
        self.newPosition = 0
        prop = self.property('newPosition')
        prop.dispatch(self)

    def speed_task(self, *args, **kv):
        current_time = time.time()

        app = App.get_running_app()
        if app is None:
            return

        if app.fast_data_values is not None:
            speed_or_zero = app.fast_data_values.get('scaleSpeed', [0] * SCALES_COUNT)[self.inputIndex]
        else:
            speed_or_zero = 0
        self.speed_history.append(speed_or_zero)
        average = (sum(self.speed_history) / len(self.speed_history))

        if app.formats.current_format == "IN":
            # Speed in feet per minute
            self.speed = float(average * 60 / 25.4 / 12)
        else:
            # Speed in mt/minute
            self.speed = float(average * 60 / 1000 / 1000)

        self.previous_axis_time = current_time
        self.previous_axis_pos = Decimal(self.position)
