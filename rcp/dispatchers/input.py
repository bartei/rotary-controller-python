"""
InputDispatcher — raw encoder input layer.

Each InputDispatcher tracks a single hardware encoder, accumulates position
deltas, and exposes a scaled_value (position * ratio) for consumption by
AxisDispatchers.  It owns ratioNum/ratioDen/stepsPerMM but has no knowledge
of offsets, formatting, or sync ratios — those live in AxisDispatcher.
"""

import time
import collections

from fractions import Fraction

from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty

from rcp.dispatchers.saving_dispatcher import SavingDispatcher
from rcp.utils.ctype_calc import uint32_subtract_to_int32
from rcp.utils.devices import SCALES_COUNT

log = Logger.getChild(__name__)


class InputDispatcher(SavingDispatcher):
    _save_class_name = "CoordBar"  # backward compat with existing YAML filenames

    # ── Persisted properties ─────────────────────────────────────────
    inputIndex = NumericProperty(0)
    ratioNum = NumericProperty(1)
    ratioDen = NumericProperty(1)
    stepsPerMM = NumericProperty(1000)
    spindleMode = BooleanProperty(False)
    encoder_ppr = NumericProperty(1000)
    gear_ratio_num = NumericProperty(1)
    gear_ratio_den = NumericProperty(1)

    # ── Transient computed properties ────────────────────────────────
    _spindle_wrap_steps = NumericProperty(0)
    position = NumericProperty(0)
    scaled_value = NumericProperty(0)
    steps_per_second = NumericProperty(0)

    _skip_save = [
        "position",
        "scaled_value",
        "steps_per_second",
        "_spindle_wrap_steps",
    ]

    def __init__(self, board, **kv):
        self.board = board
        super().__init__(**kv)

        self.speed_history = collections.deque(maxlen=25)

        # Encoder tracking state
        self.encoderPrevious = 0
        self.encoderCurrent = 0

        # Bindings
        self.board.bind(update_tick=self._on_update_tick)
        self.bind(position=self._update_scaled_value)
        self.bind(ratioNum=self._update_scaled_value)
        self.bind(ratioDen=self._update_scaled_value)
        self.bind(spindleMode=self._update_scaled_value)
        self.bind(_spindle_wrap_steps=self._update_scaled_value)
        self.bind(spindleMode=self._update_wrap_steps)
        self.bind(encoder_ppr=self._update_wrap_steps)
        self.bind(gear_ratio_num=self._update_wrap_steps)

        self._update_wrap_steps()
        self._update_scaled_value()
        Clock.schedule_interval(self._speed_task, 1.0 / 25.0)

    def _update_wrap_steps(self, *args, **kv):
        if self.spindleMode:
            self._spindle_wrap_steps = self.encoder_ppr * self.gear_ratio_num
        else:
            self._spindle_wrap_steps = 0

    def _on_update_tick(self, *args, **kv):
        try:
            if not self.board.connected:
                return

            self.encoderPrevious = self.encoderCurrent
            self.encoderCurrent = self.board.fast_data_values['scaleCurrent'][self.inputIndex]
            self.position += uint32_subtract_to_int32(self.encoderCurrent, self.encoderPrevious)
        except Exception as e:
            log.error(f"Unable to update input: {str(e)}")

    def _update_scaled_value(self, *args, **kv):
        if self.spindleMode:
            # Identity pass-through: scaled_value = position (in raw steps).
            # Wrap position to prevent unbounded growth from hardware encoder.
            spr = self._spindle_wrap_steps
            if spr > 0:
                wrapped = self.position % spr
                if wrapped != self.position:
                    self.position = wrapped
                    return  # re-triggered by position binding
            self.scaled_value = float(self.position)
            return

        ratio = Fraction(self.ratioNum, self.ratioDen)
        self.scaled_value = float(self.position * ratio)

    def _speed_task(self, *args, **kv):
        if self.board.fast_data_values is None:
            return

        steps_per_second = self.board.fast_data_values.get(
            'scaleSpeed', [0] * SCALES_COUNT
        )[self.inputIndex]
        self.speed_history.append(steps_per_second)
        self.steps_per_second = sum(self.speed_history) / len(self.speed_history)
