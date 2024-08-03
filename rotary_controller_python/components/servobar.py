import os

from kivy.factory import Factory
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

from rotary_controller_python.dispatchers import SavingDispatcher
from rotary_controller_python.utils.devices import Global

log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ServoBar(BoxLayout, SavingDispatcher):
    name = StringProperty("R")
    minSpeed = NumericProperty(1)
    maxSpeed = NumericProperty(1000)
    acceleration = NumericProperty(1000)
    ratioNum = NumericProperty(400)
    ratioDen = NumericProperty(360)
    offset = NumericProperty(0.0)
    divisions = NumericProperty(12)
    index = NumericProperty(0)
    servoEnable = NumericProperty(0)
    device = ObjectProperty()
    newCurrentPosition = NumericProperty(0)
    newDesiredPosition = NumericProperty(0)

    # enable = BooleanProperty(False)
    currentPosition = NumericProperty(0.0)
    desiredPosition = NumericProperty(0.0)
    _skip_save = ["currentPosition", "desiredPosition", "servoEnable"]

    def __init__(self, **kv):
        super().__init__(**kv)
        self.upload()

    def upload(self):
        if self.device is None:
            return

        props = self.get_our_properties()
        prop_names = [item.name for item in props]

        device_props = [item.name for item in self.device['servo'].variables]

        matches = [item for item in prop_names if item in device_props]
        for item in matches:
            self.device['servo'][item] = self.__getattribute__(item)

    def on_index(self, instance, value):
        # if self.divisions != 0 and self.device is not None:
        #     self.device['index']['index'] = self.index
        #     self.device['index']['divisions'] = self.divisions
        # else:
        #     log.error("Divisions must be != 0")
        return True

    # def on_offset(self, instance, value):
    #     self.device['servo']['absoluteOffset'] = self.offset
    #     self.offset = self.device['servo']['absoluteOffset']

    # def on_divisions(self, instance, value):
    #     self.device['index']['divisions'] = self.divisions

    # def on_minSpeed(self, instance, value):
    #     self.device['servo']['minSpeed'] = self.minSpeed

    def on_maxSpeed(self, instance, value):
        self.device['servo']['maxSpeed'] = self.maxSpeed

    def on_acceleration(self, instance, value):
        self.device['servo']['acceleration'] = self.acceleration

    # def on_ratioNum(self, instance, value):
    #     self.device['servo']['ratioNum'] = self.ratioNum

    # def on_ratioDen(self, instance, value):
    #     self.device['servo']['ratioDen'] = self.ratioDen

    def on_servoEnable(self, instance, value):
        self.device['fastData']['servoEnable'] = self.servoEnable

    def toggle_enable(self):
        current_app = App.get_running_app()
        if not current_app.connected:
            return

        if self.servoEnable != 0:
            self.servoEnable = 0
        else:
            self.servoEnable = 1

    def on_newCurrentPosition(self, instance, value):
        is_enabled = self.device['fastData']['servoEnable']
        self.device['fastData']['servoEnable'] = 0
        self.device['servo']['currentSteps'] = value
        self.device['servo']['desiredSteps'] = value
        self.device['fastData']['servoEnable'] = is_enabled

    def on_newDesiredPosition(self, instance, value):
        self.device['servo']['direction'] = value

    def update_current_position(self):
        current_app = App.get_running_app()
        Factory.Keypad().show(self, 'newCurrentPosition', self.currentPosition)

    def update_desired_position(self):
        current_app = App.get_running_app()
        Factory.Keypad().show(self, 'newDesiredPosition', self.desiredPosition)
