import time
import collections

from decimal import Decimal
from fractions import Fraction

from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty, BooleanProperty

from rcp.dispatchers.saving_dispatcher import SavingDispatcher
from rcp.utils.ctype_calc import uint32_subtract_to_int32
from rcp.utils.devices import SCALES_COUNT

log = Logger.getChild(__name__)


class ScaleDispatcher(SavingDispatcher):
    _save_class_name = "CoordBar"

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
    stepsPerMM = NumericProperty(1000)
    offsets = ListProperty([0 for item in range(100)])
    syncButtonColor = ListProperty([0.3, 0.3, 0.3, 1])
    basePosition = NumericProperty(0)
    scaledPosition = NumericProperty(0)
    formattedPosition = StringProperty("--")
    formattedSpeed = StringProperty("--")

    _skip_save = [
        "position",
        "syncEnable",
        "speed",
        "basePosition",
        "scaledPosition",
        "encoderPrevious",
        "encoderCurrent",
        "currentOffset",
        "formattedSpeed",
        "formattedPosition",
    ]
    _force_save = ["offsets"]

    def __init__(self, board, formats, servo, offset_provider, **kv):
        self.board = board
        self.formats = formats
        self.servo = servo
        self.offset_provider = offset_provider
        self._updating_scaled = False
        super().__init__(**kv)

        self.speed_history = collections.deque(maxlen=25)
        self.previous_position = 0
        self.previous_axis_time: float = 0
        self.previous_axis_pos: Decimal = Decimal(0)
        self.offset_provider.bind(currentOffset=self.update_scaledPosition)
        self.formats.bind(factor=self.update_scaledPosition)
        self.formats.bind(factor=self.set_sync_ratio)
        self.board.bind(connected=self.init_connection)
        self.board.bind(update_tick=self.on_update_tick)
        self.bind(position=self.update_scaledPosition)
        self.bind(ratioNum=self.update_scaledPosition)
        self.bind(ratioDen=self.update_scaledPosition)
        self.bind(syncRatioDen=self.set_sync_ratio)
        self.bind(syncRatioNum=self.set_sync_ratio)
        self.update_scaledPosition(self, None)
        Clock.schedule_interval(self.speed_task, 1.0 / 25.0)

        # Private variables that don't need dispatchers etc
        self.encoderPrevious = 0
        self.encoderCurrent = 0

    def init_connection(self, *args, **kv):
        self.syncEnable = self.board.device['scales'][self.inputIndex]['syncEnable']
        self.set_sync_ratio()

    def on_update_tick(self, *args, **kv):
        try:
            if not self.board.connected:
                return

            self.encoderPrevious = self.encoderCurrent
            self.encoderCurrent = self.board.fast_data_values['scaleCurrent'][self.inputIndex]
            self.position += uint32_subtract_to_int32(self.encoderCurrent, self.encoderPrevious)
        except Exception as e:
            log.error(f"Unable to update scale: {str(e)}")

    def toggle_sync(self):
        if not self.board.connected:
            return
        self.syncEnable = not self.board.device['scales'][self.inputIndex]['syncEnable']
        self.board.device['scales'][self.inputIndex]['syncEnable'] = self.syncEnable

    def set_sync_ratio(self, *args, **kv):
        if not self.board.connected:
            return

        if self.syncRatioDen == 0:
            self.syncRatioDen = 1

        if self.spindleMode:
            scale_ratio = Fraction(self.ratioNum, self.ratioDen)
        else:
            scale_ratio = Fraction(self.ratioNum, self.ratioDen) * self.formats.factor

        if self.servo.elsMode:
            servo_ratio = Fraction(self.servo.ratioNum, self.servo.ratioDen) * self.formats.factor
        else:
            servo_ratio = Fraction(self.servo.ratioNum, self.servo.ratioDen)

        sync_ratio = Fraction(self.syncRatioNum, self.syncRatioDen)

        final_ratio = scale_ratio * sync_ratio / servo_ratio
        self.board.device['scales'][self.inputIndex]['syncRatioNum'] = final_ratio.numerator
        self.board.device['scales'][self.inputIndex]['syncRatioDen'] = final_ratio.denominator

    def update_scaledPosition(self, instance=None, value=None):
        if self._updating_scaled:
            return
        self._updating_scaled = True
        try:
            current_offset = self.offset_provider.currentOffset
            ratio = Fraction(self.ratioNum, self.ratioDen)
            if self.spindleMode:
                base = float(self.position * ratio)
                scaled = float(self.position * ratio + self.offsets[current_offset])

                # Wrap into [0, ratioNum) using modular arithmetic so we
                # adjust self.position at most once (no recursive re-entry).
                if self.ratioNum > 0:
                    wrapped = scaled % self.ratioNum
                    if wrapped != scaled:
                        n = round((scaled - wrapped) / self.ratioNum)
                        self.position -= n * self.ratioDen
                        scaled = wrapped
                        base = float(self.position * ratio)

                self.basePosition = base
                self.scaledPosition = scaled
            else:
                base = float(self.position * ratio) * self.formats.factor
                self.basePosition = base
                self.scaledPosition = float(
                    self.position * ratio + self.offsets[current_offset]
                ) * self.formats.factor
        finally:
            self._updating_scaled = False

    def set_current_position(self, value):
        current_offset = self.offset_provider.currentOffset
        self.previous_position = self.scaledPosition
        if current_offset == 0:
            self.position = float(value / self.formats.factor / Fraction(self.ratioNum, self.ratioDen))
            self.offsets[current_offset] = 0
        else:
            raw_position = self.position * Fraction(self.ratioNum, self.ratioDen)
            raw_offset = value / self.formats.factor
            self.offsets[current_offset] = float(raw_offset - raw_position)
            self.save_settings()
            self.update_scaledPosition()

    def update_position(self):
        if not self.spindleMode:
            from rcp.components.popups.keypad import Keypad
            Keypad().show_with_callback(self.set_current_position, self.scaledPosition)

    def zero_position(self):
        self.set_current_position(0)

    def undo_zero(self):
        self.set_current_position(self.previous_position)

    def speed_task(self, *args, **kv):
        if self.board.fast_data_values is None:
            return

        if self.stepsPerMM == 0 and not self.spindleMode:
            return

        current_time = time.time()
        steps_per_second = self.board.fast_data_values.get('scaleSpeed', [0] * SCALES_COUNT)[self.inputIndex]
        self.speed_history.append(steps_per_second)
        avg_steps_per_second = (sum(self.speed_history) / len(self.speed_history))

        if self.spindleMode:
            self.speed = (avg_steps_per_second / self.ratioDen) * 60

        if not self.spindleMode:
            if self.formats.current_format == "MM":
                self.speed = float(avg_steps_per_second * 60 * (1 / self.stepsPerMM) * (1 / 1000))
            if self.formats.current_format == "IN":
                self.speed = float(avg_steps_per_second * 60 * (1 / self.stepsPerMM) * (1 / 1000) * (120 / 254))

        self.previous_axis_time = current_time
        self.previous_axis_pos = self.position
