from fractions import Fraction

from kivy.logger import Logger
from kivy.properties import (
    NumericProperty,
    StringProperty, ListProperty, ObjectProperty,
)

from rcp.dispatchers import SavingDispatcher

log = Logger.getChild(__name__)


class FormatsDispatcher(SavingDispatcher):
    _force_save = ['display_color']
    metric_position = StringProperty("{:+0.3f}")
    metric_speed = StringProperty("{:+0.3f}")

    imperial_position = StringProperty("{:+0.4f}")
    imperial_speed = StringProperty("{:+0.4f}")

    angle_format = StringProperty("{:+0.1f}")
    angle_speed_format = StringProperty("{:+0.1f} RPM")

    current_format = StringProperty("MM")
    speed_format = StringProperty()
    position_format = StringProperty()
    factor = ObjectProperty(Fraction(1, 1))

    display_color = ListProperty([1, 1, 1, 1])
    accept_color = ListProperty([0.2, 1, 0.2, 1])
    cancel_color = ListProperty([1, 0.2, 0.2, 1])

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
