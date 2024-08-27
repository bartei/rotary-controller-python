import collections
import math
import time
from fractions import Fraction

from kivy.logger import Logger
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.app import App

from rotary_controller_python.dispatchers import SavingDispatcher
from rotary_controller_python.utils.ctype_calc import uint32_subtract_to_int32

log = Logger.getChild(__name__)


class ServoDispatcher(SavingDispatcher):
    name = StringProperty("R")
    maxSpeed = NumericProperty(1000)
    acceleration = NumericProperty(1000)
    speed = NumericProperty(0)
    jogSpeed = NumericProperty(0)
    ratioNum = NumericProperty(400)
    ratioDen = NumericProperty(360)
    offset = NumericProperty(0.0)
    divisions = NumericProperty(12)
    index = NumericProperty(0)
    servoEnable = NumericProperty(0)
    stepsPerTurn = NumericProperty(4096)
    unitsPerTurn = NumericProperty(360.0)
    oldOffset = NumericProperty(0.0)

    # indexOffset = NumericProperty(0.0)
    # oldIndexOffset = NumericProperty(0.0)

    position = NumericProperty(0)
    scaledPosition = NumericProperty(0)

    disableControls = BooleanProperty(False)
    _skip_save = [
        "update_tick",
        "connected",
        "device",
        "position",
        "scaledPosition",
        "servoEnable",
        "oldOffset",
        "offset",
        "index",
        # "indexOffset",
        # "oldIndexOffset",
        "disableControls",
        "speed",
        "direction",
    ]

    def __init__(self, **kv):
        self.app = App.get_running_app()
        super().__init__(**kv)
        # App event bindings
        self.app.bind(connected=self.connected)
        self.app.bind(connected=self.update_positions)
        self.app.bind(update_tick=self.update_tick)

        # Widget event bindings
        self.bind(divisions=self.update_positions)
        self.bind(ratioNum=self.update_positions)
        self.bind(ratioDen=self.update_positions)
        self.bind(ratioNum=self.update_scaledPosition)
        self.bind(ratioDen=self.update_scaledPosition)
        self.bind(position=self.update_scaledPosition)

        # Private variables that don't need dispatchers etc
        self.encoderPrevious = 0
        self.encoderCurrent = 0
        self.previous_axis_time = time.time()
        self.speed_history = collections.deque(maxlen=10)
        self.previousIndex = 0
        self.step_positions = dict()
        self.positions = dict()

    def connected(self, instance, value):
        try:
            if self.app.connected:
                self.encoderPrevious = self.app.fast_data_values['servoCurrent']
                self.encoderCurrent = self.app.fast_data_values['servoCurrent']
                self.servoEnable = self.app.fast_data_values['servoEnable']
                self.app.device['servo']['maxSpeed'] = self.maxSpeed
                self.app.device['servo']['acceleration'] = self.acceleration

                if self.servoEnable == 0:
                    self.disableControls = True
                else:
                    self.disableControls = False
        except Exception as e:
            log.error(e.__str__())

    def update_positions(self, *args, **kv):
        ratio = Fraction(self.ratioNum, self.ratioDen)
        if self.divisions < 1:
            self.divisions = 1
        self.positions = dict()
        self.step_positions = dict()
        for i in range(self.divisions):
            self.positions[i] = i * (self.unitsPerTurn / self.divisions)
            self.step_positions[i] = round(self.positions[i] / ratio)

        self.previousIndex = 0
        self.index = self.index = 0

    def update_tick(self, instance, value):
        if not self.app.connected:
            return

        self.encoderPrevious = self.encoderCurrent
        self.encoderCurrent = self.app.fast_data_values['servoCurrent']
        self.servoEnable = self.app.fast_data_values['servoEnable']

        steps_per_second = self.app.fast_data_values['servoSpeed']
        self.speed_history.append(steps_per_second)
        self.speed = (sum(self.speed_history) / len(self.speed_history))

        delta = uint32_subtract_to_int32(self.encoderCurrent, self.encoderPrevious)
        self.position += delta
        if self.app.fast_data_values['stepsToGo'] == 0 and self.servoEnable != 0:
            self.disableControls = False

    def update_scaledPosition(self, *args, **kv):
        ratio = Fraction(self.ratioNum, self.ratioDen)
        if self.unitsPerTurn != 0:
            self.scaledPosition = float(self.position * ratio) % self.unitsPerTurn
        else:
            self.scaledPosition = float(self.position * ratio)

    def on_index(self, instance, value):
        ratio = Fraction(self.ratioNum, self.ratioDen)
        self.index = self.index % self.divisions

        index_delta = (self.index - self.previousIndex)
        half_divisions = self.divisions // 2
        steps_per_turn = (self.unitsPerTurn / ratio)
        delta = self.step_positions[self.index] - self.step_positions[self.previousIndex]

        if index_delta > half_divisions:
            delta = -(steps_per_turn - delta)
        if index_delta < -half_divisions:
            delta = (delta + steps_per_turn)
        if delta != 0:
            self.app.device['servo']['direction'] = delta
            self.disableControls = True
            self.previousIndex = self.index

    def on_offset(self, instance, value):
        ratio = Fraction(self.ratioNum, self.ratioDen)
        delta = value - self.oldOffset
        delta_steps = int(delta / ratio)
        if delta_steps != 0:
            self.app.device['servo']['direction'] = delta_steps
            self.disableControls = True
            self.oldOffset = value

    def on_maxSpeed(self, instance, value):
        self.app.device['servo']['maxSpeed'] = self.maxSpeed

    def on_jogSpeed(self, instance, value):
        self.app.device['servo']['jogSpeed'] = self.jogSpeed

    def on_acceleration(self, instance, value):
        self.app.device['servo']['acceleration'] = self.acceleration

    def on_servoEnable(self, instance, value):
        self.app.device['fastData']['servoEnable'] = self.servoEnable
        if self.servoEnable != 0:
            self.disableControls = False
        else:
            self.disableControls = True

    def toggle_enable(self):
        if not self.app.connected:
            return

        if self.servoEnable != 0:
            self.servoEnable = 0
        else:
            self.servoEnable = 1

    def set_current_position(self, value):
        ratio = Fraction(self.ratioNum, self.ratioDen)
        self.position = int(value / ratio)
