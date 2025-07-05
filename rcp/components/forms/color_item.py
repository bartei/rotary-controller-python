import os
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty, ColorProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file {kv_file}")
    Builder.load_file(kv_file)


class ColorPickerPopup(Popup):
    color = ColorProperty("#ffffff")
    callback = ObjectProperty()

    def __init__(self, color, callback, **kw):
        super().__init__(**kw)
        self.color = color
        self.callback = callback
        log.info(f"Received color {self.color}")

    def apply(self):
        self.callback(self.color)
        self.dismiss()


class ColorItem(BoxLayout):
    name = StringProperty()
    color = ColorProperty()
    help_file = StringProperty()

    def set_color(self, color: list[float]):
        log.debug(f"Color selected is {color}")
        self.color = color

    def open_picker(self):
        picker = ColorPickerPopup(color=self.color, callback=self.set_color)
        picker.open()