from kivy.properties import NumericProperty, StringProperty
from kivy.logger import Logger
from kivy.uix.button import Button

log = Logger.getChild(__name__)


class ToolbarButton(Button):
    font_name = StringProperty("fonts/Manrope-Bold.ttf")
    font_size = NumericProperty(32)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.bind(width=self.update_height) # Bind width to update_height
        self.update_height(self, self.width)

    def update_height(self, instance, value):
        self.height = self.width