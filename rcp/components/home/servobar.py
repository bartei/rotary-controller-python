import collections
import time
import os

from fractions import Fraction

from kivy.logger import Logger
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from rcp.dispatchers import SavingDispatcher
from rcp.components.keypad import Keypad
from rcp.utils.ctype_calc import uint32_subtract_to_int32

log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ServoBar(BoxLayout, SavingDispatcher):
    name = StringProperty("R")
    maxSpeed = NumericProperty(1000)
    acceleration = NumericProperty(1000)
    speed = NumericProperty(0)
    jogSpeed = NumericProperty(0)
    ratioNum = NumericProperty(400)
    ratioDen = NumericProperty(360)
    offset = NumericProperty(0.0)
    divisions = NumericProperty(12)
    preferredDirection = NumericProperty(1)
    index = NumericProperty(0)

    servoEnable = NumericProperty(0)
    unitsPerTurn = NumericProperty(360.0)
    oldOffset = NumericProperty(0.0)

    elsMode = BooleanProperty(False)
    leadScrewPitch = NumericProperty(0.25)
    leadScrewPitchIn = BooleanProperty(True)
    leadScrewPitchSteps = BooleanProperty(800)

    position = NumericProperty(0)
    scaledPosition = NumericProperty(0)
    formattedPosition = StringProperty("--")

    disableControls = BooleanProperty(False)
    _skip_save = [
        "update_tick",
        "connected",
        "device",
        "position",
        "scaledPosition",
        "formattedPosition",
        "servoEnable",
        "oldOffset",
        "offset",
        "index",
        "preferredDirection",
        "disableControls",
        "speed",
        "direction",
        "x",
        "width"
    ]

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kv)
        self.configure_lead_screw_ratio(self, None)

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
        self.bind(elsMode=self.update_scaledPosition)
        self.app.formats.bind(current_format=self.update_scaledPosition)
        self.update_scaledPosition(self, None)

        self.bind(leadScrewPitch=self.configure_lead_screw_ratio)
        self.bind(leadScrewPitchIn=self.configure_lead_screw_ratio)
        self.bind(leadScrewPitchSteps=self.configure_lead_screw_ratio)

        # Private variables that don't need dispatchers etc
        self.encoderPrevious = 0
        self.encoderCurrent = 0
        self.previous_axis_time = time.time()
        self.speed_history = collections.deque(maxlen=4)
        self.previousIndex = 0
        self.step_positions = dict()
        self.positions = dict()
        self.disableControls = True
        self.servoEnable = 0

    def configure_lead_screw_ratio(self, instance, value):
        # Configure the ratio when operating in ELS mode
        if self.elsMode is True:
            leadScrewPitch = Fraction(self.leadScrewPitch)

            if self.leadScrewPitchIn is True:
                leadScrewPitch = leadScrewPitch * Fraction(254, 10)

            leadScrewRatio = leadScrewPitch * Fraction(1, self.leadScrewPitchSteps)
            self.ratioNum = leadScrewRatio.numerator
            self.ratioDen = leadScrewRatio.denominator

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
        try:
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
            if (
                    self.app.fast_data_values['stepsToGo'] == 0 and
                    self.servoEnable != 0 and
                    self.disableControls
                    and self.app.connected
            ):
                log.info("Disable Controls False")
                self.disableControls = False
        except Exception as e:
            log.error(f"Unable to read servo: {e.__str__()}")

    def update_scaledPosition(self, instance, value):
        ratio = Fraction(self.ratioNum, self.ratioDen)

        if self.elsMode is False and self.unitsPerTurn > 0:
            self.scaledPosition = float(self.position * ratio) % self.unitsPerTurn
            self.formattedPosition = self.app.formats.angle_format.format(self.scaledPosition)
        else:
            self.scaledPosition = float(self.position * ratio) * self.app.formats.factor
            self.formattedPosition = self.app.formats.position_format.format(self.scaledPosition)

    def go_next(self):
        self.preferredDirection = 1
        self.index = (self.index + 1) % self.divisions

    def go_previous(self):
        self.preferredDirection = -1
        self.index = (self.index - 1) % self.divisions


    def on_index(self, instance, value):
        ratio = Fraction(self.ratioNum, self.ratioDen)
        self.index = self.index % self.divisions

        index_delta = (self.index - self.previousIndex)
        half_divisions = self.divisions // 2
        steps_per_turn = (self.unitsPerTurn / ratio)
        delta = self.step_positions[self.index] - self.step_positions[self.previousIndex]

        if self.preferredDirection > 0:
            if index_delta > half_divisions:
                delta = -(steps_per_turn - delta)
            if index_delta <= -half_divisions:
                delta = (delta + steps_per_turn)

        if self.preferredDirection < 0:
            if index_delta >= half_divisions:
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
            log.info("Disable Controls False")
            self.disableControls = False
        else:
            log.info("Disable Controls True")
            self.disableControls = True

    def toggle_enable(self):
        if not self.app.connected:
            self.servoEnable = 0
            return

        if self.servoEnable != 0:
            self.servoEnable = 0
        else:
            self.servoEnable = 1

    def set_current_position(self, value):
        ratio = Fraction(self.ratioNum, self.ratioDen)
        self.position = int(value / ratio)

    def update_current_position(self):
        keypad = Keypad()
        keypad.show_with_callback(self.set_current_position, self.scaledPosition)
