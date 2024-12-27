import os
import time
import collections

from decimal import Decimal
from fractions import Fraction

from kivy.logger import Logger
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

from rcp.dispatchers import SavingDispatcher
from rcp.utils.ctype_calc import uint32_subtract_to_int32
from rcp.utils.devices import SCALES_COUNT

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class CoordBar(BoxLayout, SavingDispatcher):
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
    spindleMode = BooleanProperty(False)
    stepsPerRev = NumericProperty(4096)
    stepsPerMM = NumericProperty(1000)
    offsets = ListProperty([0 for item in range(100)])
    syncButtonColor = ListProperty([0.3, 0.3, 0.3, 1])
    scaledPosition = NumericProperty(0)
    formattedPosition = StringProperty("--")
    formattedSpeed = StringProperty("--")

    _skip_save = [
        "position",
        "syncEnable",
        "speed",
        "scaledPosition",
        "encoderPrevious",
        "encoderCurrent",
        "currentOffset",
        "formattedSpeed",
        "formattedPosition",
        "x", "y",
        "minimum_width",
        "minimum_height",
        "width", "height",
    ]
    _force_save = ["offsets"]

    def __init__(self, **kv):
        from rcp.main import MainApp
        self.app: MainApp = App.get_running_app()
        super().__init__(**kv)

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
        try:
            if not self.app.connected:
                return

            self.encoderPrevious = self.encoderCurrent
            self.encoderCurrent = self.app.fast_data_values['scaleCurrent'][self.inputIndex]
            self.position += uint32_subtract_to_int32(self.encoderCurrent, self.encoderPrevious)
        except Exception as e:
            log.error(f"Unable to update scale: {e.__str__()}")

    def toggle_sync(self):
        if not self.app.connected:
            return
        self.syncEnable = not self.device['scales'][self.inputIndex]['syncEnable']
        self.device['scales'][self.inputIndex]['syncEnable'] = self.syncEnable

    def set_sync_ratio(self, *args, **kv):
        if not self.app.connected:
            return

        # check and make sure the denominator is not 0
        if self.syncRatioDen == 0:
            self.syncRatioDen = 1

        if self.spindleMode:
            scale_ratio = Fraction(self.ratioNum, self.ratioDen)
        else:
            scale_ratio = Fraction(self.ratioNum, self.ratioDen) * self.app.formats.factor

        servo_ratio = Fraction(self.app.servo.ratioNum, self.app.servo.ratioDen)
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

        if self.spindleMode:
            self.formattedPosition = self.app.formats.angle_speed_format.format(self.speed)
            self.formattedSpeed = self.app.formats.angle_speed_format.format(self.speed)
        else:
            self.formattedPosition = self.app.formats.position_format.format(self.scaledPosition)
            self.formattedSpeed = self.app.formats.speed_format.format(self.speed)

    def on_newPosition(self, instance, value):
        self.set_current_position(value)

    def set_current_position(self, value):
        # 0 is the reference position for the DRO when offset 0 is selected we reset the absolute position of the scale
        if self.app.currentOffset == 0:
            self.position = float(value / self.app.formats.factor / Fraction(self.ratioNum, self.ratioDen))
            self.offsets[self.app.currentOffset] = 0
        else:
            raw_position = self.position * Fraction(self.ratioNum, self.ratioDen)
            raw_offset = value / self.app.formats.factor
            self.offsets[self.app.currentOffset] = float(raw_offset - raw_position)
            self.save_settings()
            self.update_scaledPosition()

    def update_position(self):
        if not self.spindleMode:
            Factory.Keypad().show_with_callback(self.set_current_position, self.scaledPosition)

    def zero_position(self):
        self.set_current_position(0)

    def speed_task(self, *args, **kv):
        if self.app is None or self.app.fast_data_values is None:
            return

        if self.stepsPerMM == 0 and not self.spindleMode:
            return

        if self.stepsPerRev == 0 and self.spindleMode:
            return

        current_time = time.time()
        steps_per_second = self.app.fast_data_values.get('scaleSpeed', [0] * SCALES_COUNT)[self.inputIndex]
        self.speed_history.append(steps_per_second)
        avg_steps_per_second = (sum(self.speed_history) / len(self.speed_history))

        # Calculate Revs/Min for spindleMode
        if self.spindleMode:
            self.speed = (avg_steps_per_second / self.stepsPerRev) * 60

        # Calculate feeds
        if not self.spindleMode:
            if self.app.formats.current_format == "MM":
                self.speed = float(avg_steps_per_second * 60 * (1 / self.stepsPerMM) * (1 / 1000))
            if self.app.formats.current_format == "IN":
                self.speed = float(avg_steps_per_second * 60 * (1 / self.stepsPerMM) * (1 / 1000) * (120 / 254))

        self.previous_axis_time = current_time
        self.previous_axis_pos = self.position
