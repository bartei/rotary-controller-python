import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import BooleanProperty, StringProperty, ColorProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

log = Logger.getChild(__name__)

kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class LedButton(ButtonBehavior, BoxLayout):
    label = StringProperty()
    checkbox_value = BooleanProperty()
    current_color = ColorProperty((0, 0, 0, 1))

    def on_checkbox_value(self, instance, value):
        if value:
            self.current_color = self.color_on
        else:
            self.current_color = self.color_off
