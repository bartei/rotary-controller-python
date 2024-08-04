import os
import time
import collections

from decimal import Decimal
from fractions import Fraction

from kivy.logger import Logger
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty, BooleanProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

from rotary_controller_python.components.servobar import ServoBar
from rotary_controller_python.dispatchers import SavingDispatcher
from rotary_controller_python.utils.ctype_calc import uint32_subtract_to_int32
from rotary_controller_python.utils.devices import SCALES_COUNT

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class CoordBar(BoxLayout, SavingDispatcher):
    servo = ObjectProperty(None)
    device = ObjectProperty()
    inputIndex = NumericProperty(0)
    axisName = StringProperty("?")
    ratioNum = NumericProperty(1)
    ratioDen = NumericProperty(1)
    syncRatioNum = NumericProperty(360)
    syncRatioDen = NumericProperty(100)
    syncEnable = BooleanProperty(False)
    position = NumericProperty(0)

    speed = NumericProperty(0)
    mode = NumericProperty(0)
    offsets = ListProperty([0 for item in range(100)])
    syncButtonColor = ListProperty([0.3, 0.3, 0.3, 1])
    scaledPosition = NumericProperty(0)

    _skip_save = [
        "position", "syncEnable", "speed", "scaledPosition", "encoderPrevious", "encoderCurrent", "currentOffset"
    ]
    _force_save = ["offsets"]

    def __init__(self, servo: ServoBar, **kv):
        self.app = App.get_running_app()
        super().__init__(**kv)

        self.servo: ServoBar = servo
        self.speed_history = collections.deque(maxlen=5)
        self.previous_axis_time: float = 0
        self.previous_axis_pos: Decimal = Decimal(0)
        self.app.bind(currentOffset=self.update_scaledPosition)
        self.app.formats.bind(factor=self.update_scaledPosition)
        self.app.formats.bind(factor=self.set_sync_ratio)
        self.app.bind(connected=self.init_connection)
        self.app.bind(update_tick=self.update_tick)
        Clock.schedule_interval(self.speed_task, 1.0/25.0)

        # Private variables that don't need dispatchers etc
        self.encoderPrevious = 0
        self.encoderCurrent = 0

    def init_connection(self, *args, **kv):
        """
        This method is called when the connection is established
        """
        self.syncEnable = self.device['scales'][self.inputIndex]['syncEnable']
        self.set_sync_ratio()

    def update_tick(self, *args, **kv):
        self.encoderPrevious = self.encoderCurrent
        self.encoderCurrent = self.app.fast_data_values['scaleCurrent'][self.inputIndex]
        self.position += uint32_subtract_to_int32(self.encoderCurrent, self.encoderPrevious)

    def toggle_sync(self):
        if not self.app.connected:
            return
        self.syncEnable = not self.device['scales'][self.inputIndex]['syncEnable']
        self.device['scales'][self.inputIndex]['syncEnable'] = self.syncEnable

    def set_sync_ratio(self, *args, **kv):
        scale_ratio = Fraction(self.ratioNum, self.ratioDen) * self.app.formats.factor
        servo_ratio = Fraction(self.servo.ratioNum, self.servo.ratioDen)
        sync_ratio = Fraction(self.syncRatioNum, self.syncRatioDen)

        final_ratio = scale_ratio * sync_ratio / servo_ratio
        self.device['scales'][self.inputIndex]['syncRatioNum'] = final_ratio.numerator
        self.device['scales'][self.inputIndex]['syncRatioDen'] = final_ratio.denominator

    def on_syncRatioNum(self, instance, value):
        if self.app.home is None:
            return
        self.set_sync_ratio()

    def on_syncRatioDen(self, instance, value):
        if self.app.home is None:
            return
        self.set_sync_ratio()

    def on_position(self, instance, value):
        self.update_scaledPosition()

    def on_ratioNum(self, instance, value):
        self.update_scaledPosition()

    def on_ratioDen(self, instance, value):
        self.update_scaledPosition()

    def update_scaledPosition(self, *args, **kv):
        self.scaledPosition = float(
            self.position * Fraction(self.ratioNum, self.ratioDen) + self.offsets[self.app.currentOffset]
        ) * self.app.formats.factor

    def on_newPosition(self, instance, value):
        raw_position = self.position * Fraction(self.ratioNum, self.ratioDen)
        raw_offset = value / self.app.formats.factor
        self.offsets[self.app.currentOffset] = float(raw_offset - raw_position)
        self.save_settings()
        self.update_scaledPosition()

    def set_current_position(self, value):
        raw_position = self.position * Fraction(self.ratioNum, self.ratioDen)
        raw_offset = value / self.app.formats.factor
        self.offsets[self.app.currentOffset] = float(raw_offset - raw_position)
        self.save_settings()
        self.update_scaledPosition()

    def update_position(self):
        if not self.mode == 1:
            Factory.Keypad().show_with_callback(self.set_current_position, self.scaledPosition)

    def zero_position(self):
        self.set_current_position(0)

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
