import os
from fractions import Fraction

from kivy.factory import Factory
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

from rcp.dispatchers import SavingDispatcher
from rcp.dispatchers.servo import ServoDispatcher
from rcp.utils.ctype_calc import uint32_subtract_to_int32
from rcp.utils.devices import Global

log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ServoBar(BoxLayout):
    servo: ServoDispatcher = ObjectProperty()

    def update_current_position(self):
        Factory.Keypad().show_with_callback(self.servo.set_current_position, self.servo.scaledPosition)
