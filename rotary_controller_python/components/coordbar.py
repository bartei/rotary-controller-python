import os

from kivy.factory import Factory
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from rotary_controller_python.dispatchers.scale import ScaleDispatcher
from rotary_controller_python.dispatchers.servo import ServoDispatcher

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class CoordBar(BoxLayout):
    servo: ServoDispatcher = ObjectProperty(None)
    scale: ScaleDispatcher = ObjectProperty(None)

    def update_position(self):
        if not self.scale.spindleMode:
            Factory.Keypad().show_with_callback(self.scale.set_current_position, self.scale.scaledPosition)
