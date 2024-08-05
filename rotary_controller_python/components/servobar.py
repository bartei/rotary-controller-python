import os
from fractions import Fraction

from kivy.factory import Factory
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

from rotary_controller_python.dispatchers import SavingDispatcher
from rotary_controller_python.utils.ctype_calc import uint32_subtract_to_int32
from rotary_controller_python.utils.devices import Global

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
    ratioNum = NumericProperty(400)
    ratioDen = NumericProperty(360)
    offset = NumericProperty(0.0)
    divisions = NumericProperty(12)
    index = NumericProperty(0)
    servoEnable = NumericProperty(0)
    device = ObjectProperty()
    stepsPerTurn = NumericProperty(4096)
    unitsPerTurn = NumericProperty(360.0)
    oldOffset = NumericProperty(0.0)

    indexOffset = NumericProperty(0.0)
    oldIndexOffset = NumericProperty(0.0)

    position = NumericProperty(0)
    scaledPosition = NumericProperty(0)

    disableControls = BooleanProperty(False)
    _skip_save = [
        "position",
        "scaledPosition",
        "servoEnable",
        "oldOffset",
        "offset",
        "index",
        "indexOffset",
        "oldIndexOffset",
    ]

    def __init__(self, **kv):
        self.app = App.get_running_app()
        super().__init__(**kv)
        self.app.bind(update_tick=self.update_tick)
        self.app.bind(connected=self.init_connection)

        # Private variables that don't need dispatchers etc
        self.encoderPrevious = 0
        self.encoderCurrent = 0

    def init_connection(self, *args, **kv):
        """
        This method is called when the connection is established
        """
        if self.device.dm.connected:
            self.encoderPrevious = self.app.fast_data_values['servoCurrent']
            self.encoderCurrent = self.app.fast_data_values['servoCurrent']
            self.servoEnable = self.app.fast_data_values['servoEnable']
            if self.servoEnable == 0:
                self.disableControls = True
            else:
                self.disableControls = False

    def update_tick(self, *arg, **kv):
        self.encoderPrevious = self.encoderCurrent
        self.encoderCurrent = self.app.fast_data_values['servoCurrent']
        self.position += uint32_subtract_to_int32(self.encoderCurrent, self.encoderPrevious)
        if self.app.fast_data_values['stepsToGo'] == 0 and self.servoEnable != 0:
            self.disableControls = False

    def update_scaledPosition(self, *args, **kv):
        ratio = Fraction(self.ratioNum, self.ratioDen)
        if self.unitsPerTurn != 0:
            self.scaledPosition = float(self.position * ratio) % self.unitsPerTurn
        else:
            self.scaledPosition = float(self.position * ratio)

    def on_position(self, instance, value):
        self.update_scaledPosition()

    def on_index(self, instance, value):
        ratio = Fraction(self.ratioNum, self.ratioDen)
        if self.divisions != 0:
            self.index = self.index % self.divisions
            self.indexOffset = self.unitsPerTurn / self.divisions * self.index

        delta = self.indexOffset - self.oldIndexOffset
        self.oldIndexOffset = self.indexOffset
        delta_steps = delta / ratio

        if delta_steps != 0:
            self.device['servo']['direction'] = delta_steps
            self.disableControls = True
        return True

    def on_offset(self, instance, value):
        ratio = Fraction(self.ratioNum, self.ratioDen)
        delta = value - self.oldOffset
        delta_steps = int(delta / ratio)
        if delta_steps != 0:
            self.device['servo']['direction'] = delta_steps
            self.disableControls = True
            self.oldOffset = value

    def on_maxSpeed(self, instance, value):
        self.device['servo']['maxSpeed'] = self.maxSpeed

    def on_acceleration(self, instance, value):
        self.device['servo']['acceleration'] = self.acceleration

    def on_ratioNum(self, instance, value):
        self.update_scaledPosition()

    def on_ratioDen(self, instance, value):
        self.update_scaledPosition()

    def on_servoEnable(self, instance, value):
        self.device['fastData']['servoEnable'] = self.servoEnable
        if self.servoEnable == 1:
            self.disableControls = False
        else:
            self.disableControls = True

    def toggle_enable(self):
        current_app = App.get_running_app()
        if not current_app.connected:
            return

        if self.servoEnable != 0:
            self.servoEnable = 0
        else:
            self.servoEnable = 1

    def set_current_position(self, value):
        ratio = Fraction(self.ratioNum, self.ratioDen)
        self.position = int(value / ratio)

    def update_current_position(self):
        Factory.Keypad().show_with_callback(self.set_current_position, self.scaledPosition)
