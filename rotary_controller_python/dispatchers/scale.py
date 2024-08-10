import time
import collections

from decimal import Decimal
from fractions import Fraction

from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.app import App

from rotary_controller_python.dispatchers import SavingDispatcher
from rotary_controller_python.dispatchers.formats import FormatsDispatcher
from rotary_controller_python.dispatchers.servo import ServoDispatcher
from rotary_controller_python.utils.ctype_calc import uint32_subtract_to_int32
from rotary_controller_python.utils.devices import SCALES_COUNT

log = Logger.getChild(__name__)


class ScaleDispatcher(SavingDispatcher):
    formats: FormatsDispatcher = ObjectProperty(None)
    servo: ServoDispatcher = ObjectProperty(None)

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
    offsets = ListProperty([0 for item in range(100)])
    syncButtonColor = ListProperty([0.3, 0.3, 0.3, 1])
    scaledPosition = NumericProperty(0)
    formattedPosition = StringProperty("--")
    formattedSpeed = StringProperty("--")

    _skip_save = [
        "update_tick",
        "formats",
        "position",
        "syncEnable",
        "speed",
        "scaledPosition",
        "encoderPrevious",
        "encoderCurrent",
        "currentOffset",
        "formattedSpeed",
        "formattedPosition",
    ]
    _force_save = ["offsets"]

    def __init__(self, **kv):
        from rotary_controller_python.main import MainApp
        self.app: MainApp = App.get_running_app()
        super().__init__(**kv)

        self.speed_history = collections.deque(maxlen=5)
        self.previous_axis_time: float = 0
        self.previous_axis_pos: Decimal = Decimal(0)
        self.app.bind(currentOffset=self.update_scaledPosition)
        self.app.bind(connected=self.connected)
        self.app.bind(update_tick=self.update_tick)

        self.formats.bind(factor=self.update_scaledPosition)
        self.formats.bind(factor=self.set_sync_ratio)
        self.update_scaledPosition()
        Clock.schedule_interval(self.speed_task, 1.0 / 25.0)

        # Private variables that don't need dispatchers etc
        self.encoderPrevious = 0
        self.encoderCurrent = 0

    def connected(self, instance, value):
        """
        This method is called when the connection is established
        """
        self.syncEnable = self.app.device['scales'][self.inputIndex]['syncEnable'] == 1
        self.set_sync_ratio()

    def update_tick(self, instance, value):
        if not self.app.connected:
            return
        self.encoderPrevious = self.encoderCurrent
        self.encoderCurrent = self.app.fast_data_values['scaleCurrent'][self.inputIndex]
        self.position += uint32_subtract_to_int32(self.encoderCurrent, self.encoderPrevious)

    def toggle_sync(self):
        if not self.app.connected:
            return
        log.info(f"Sync for: {self.axisName}, set to: {self.syncEnable}")

        if self.syncEnable is True:
            self.app.device['scales'][self.inputIndex]['syncEnable'] = 0
            self.syncEnable = False
        else:
            self.app.device['scales'][self.inputIndex]['syncEnable'] = 1
            self.syncEnable = True

    def set_sync_ratio(self, *args, **kv):
        scale_ratio = Fraction(self.ratioNum, self.ratioDen) * self.formats.factor
        servo_ratio = Fraction(self.servo.ratioNum, self.servo.ratioDen)
        sync_ratio = Fraction(self.syncRatioNum, self.syncRatioDen)

        final_ratio = scale_ratio * sync_ratio / servo_ratio
        self.app.device['scales'][self.inputIndex]['syncRatioNum'] = final_ratio.numerator
        self.app.device['scales'][self.inputIndex]['syncRatioDen'] = final_ratio.denominator

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
        ) * self.formats.factor

        if self.spindleMode:
            self.formattedPosition = self.formats.angle_speed_format.format(self.speed)
            self.formattedSpeed = self.formats.angle_speed_format.format(self.speed)
        else:
            self.formattedPosition = self.formats.position_format.format(self.scaledPosition)
            self.formattedSpeed = self.formats.speed_format.format(self.speed)

    def on_newPosition(self, instance, value):
        raw_position = self.position * Fraction(self.ratioNum, self.ratioDen)
        raw_offset = value / self.formats.factor
        self.offsets[self.app.currentOffset] = float(raw_offset - raw_position)
        self.save_settings()
        self.update_scaledPosition()

    def set_current_position(self, value):
        raw_position = self.position * Fraction(self.ratioNum, self.ratioDen)
        raw_offset = value / self.formats.factor
        self.offsets[self.app.currentOffset] = float(raw_offset - raw_position)
        # self.save_settings()
        self.update_scaledPosition()

    def zero_position(self):
        self.set_current_position(0)

    def speed_task(self, *args, **kv):
        if self.app is None or self.app.fast_data_values is None:
            return

        current_time = time.time()
        steps_per_second = self.app.fast_data_values.get('scaleSpeed', [0] * SCALES_COUNT)[self.inputIndex]
        self.speed_history.append(steps_per_second)
        avg_steps_per_second = (sum(self.speed_history) / len(self.speed_history))

        # Calculate Revs/Min for spindleMode
        if self.spindleMode:
            self.speed = float(
                avg_steps_per_second
                * Fraction(self.ratioNum, self.ratioDen)
                * Fraction(1, 60)
            )

        # Calculate feeds
        if not self.spindleMode:
            if self.formats.current_format == "MM":
                self.speed = float(
                    avg_steps_per_second
                    * Fraction(self.ratioNum, self.ratioDen)
                    * Fraction(60, 1000)
                )
            if self.formats.current_format == "IN":
                self.speed = float(
                    avg_steps_per_second
                    * Fraction(self.ratioNum, self.ratioDen)
                    * Fraction(60, 1000)
                    * Fraction(120, 254)
                )

        self.previous_axis_time = current_time
        self.previous_axis_pos = self.position
