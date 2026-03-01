from kivy.logger import Logger
from kivy.properties import ColorProperty, ObjectProperty
from kivy.uix.screenmanager import Screen

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class ColorPickerScreen(Screen):
    color = ColorProperty("#ffffff")
    callback = ObjectProperty()

    # def __init__(self, color, callback, **kw):
    #     super().__init__(**kw)
    #     self.color = color
    #     self.callback = callback
    #     log.info(f"Received color {self.color}")


