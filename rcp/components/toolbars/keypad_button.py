from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty


class KeypadButton(Button):

    return_value = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text_halign = "center"
        self.font_style = "bold"
        self.halign = "center"
        self.background_color = [1, 1, 1, 1]
        self.font_name = "fonts/Manrope-Bold.ttf"

    def on_height(self, instance, value):
        self.font_size = value / 3
