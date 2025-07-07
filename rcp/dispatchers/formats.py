from fractions import Fraction

from kivy.logger import Logger
from kivy.properties import (
    NumericProperty,
    StringProperty, ListProperty, ObjectProperty, ColorProperty,
)

from rcp.dispatchers import SavingDispatcher

log = Logger.getChild(__name__)


class FormatsDispatcher(SavingDispatcher):
    _force_save = [
        'display_color',
        'accept_color',
        'cancel_color',
        'color_on',
        'color_off'
    ]

    metric_position = StringProperty("{:+0.3f}")
    metric_speed = StringProperty("{:+0.3f}")

    imperial_position = StringProperty("{:+0.4f}")
    imperial_speed = StringProperty("{:+0.4f}")

    angle_format = StringProperty("{:+0.1f}")
    angle_speed_format = StringProperty("{:+0.1f} RPM")

    font_size = NumericProperty(24)

    current_format = StringProperty("MM")
    speed_format = StringProperty()
    position_format = StringProperty()
    factor = ObjectProperty(Fraction(1, 1))

    display_color = ColorProperty("#ffcc35ff")
    accept_color = ColorProperty("#32ff32ff")
    cancel_color = ColorProperty("#ff3232ff")
    color_on = ColorProperty("#ffcc32a0")
    color_off = ColorProperty("#ffcc3220")

    volume = NumericProperty(0.2)

    def __init__(self, **kv):
        super().__init__(**kv)
        self.bind(current_format=self.update_format)
        self.update_format()

    def update_format(self, *args, **kv):
        if self.current_format == "MM":
            self.speed_format = f"{self.metric_speed} M/min"
            self.position_format = self.metric_position
            self.factor = Fraction(1, 1)
        else:
            self.speed_format = f"{self.imperial_speed} Ft/min"
            self.position_format = self.imperial_position
            self.factor = Fraction(10, 254)

    def toggle(self, *_):
        if self.current_format == "MM":
            self.current_format = "IN"
        else:
            self.current_format = "MM"
