import os

from kivy.factory import Factory
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout


log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ElsBar(BoxLayout):
    feed_button = ObjectProperty(None)
    mode = StringProperty("FEED")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_current_position(self):
        Factory.Keypad().show_with_callback(self.servo.set_current_position, self.servo.scaledPosition)

    def set_feed_mode(self, mode):
        log.info(f"Setting feed mode to {mode}")
        self.mode = mode
