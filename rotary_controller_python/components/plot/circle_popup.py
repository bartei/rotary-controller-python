import os

from kivy import Logger
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from rotary_controller_python.dispatchers.circle_pattern import CirclePatternDispatcher

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class CirclePopup(Popup):
    ref = ObjectProperty(None)

    def show(self):
        self.open()

    def on_data(self, instance, value):
        if self.ref is not None:
            self.ref.circle_pattern.origin_x = self.data.origin_x

    def cancel(self):
        self.dismiss()
