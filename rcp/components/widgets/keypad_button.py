from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.properties import NumericProperty

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class KeypadButton(Button):
    return_value = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = "fonts/Manrope-Bold.ttf"
