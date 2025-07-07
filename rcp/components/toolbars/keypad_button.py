import os

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.properties import NumericProperty

log = Logger.getChild(__name__)


kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class KeypadButton(Button):
    return_value = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = "fonts/Manrope-Bold.ttf"
