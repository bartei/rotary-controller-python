from kivy.uix.button import Button
from kivy.properties import NumericProperty, StringProperty


class KeypadButton(Button):
    text_halign = "center"
    font_style = "bold"
    font_name = StringProperty("fonts/Manrope-Bold.ttf")
    halign = "center"
    background_color = [1, 1, 1, 1]
    return_value = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_height(self, instance, value):
        self.font_size = value / 3
