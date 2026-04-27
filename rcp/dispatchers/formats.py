from fractions import Fraction

from kivy.logger import Logger
from kivy.properties import (
    NumericProperty,
    StringProperty, ListProperty, ObjectProperty, ColorProperty, BooleanProperty,
)

from rcp.dispatchers.saving_dispatcher import SavingDispatcher

log = Logger.getChild(__name__)


class FormatsDispatcher(SavingDispatcher):
    _force_save = [
        'display_color',
        'accept_color',
        'cancel_color',
        'color_on',
        'color_off'
    ]
    
    MM_FRACTION = Fraction(1, 1)
    INCHES_FRACTION = Fraction(10, 254)

    metric_position = StringProperty("{:+0.3f}")
    metric_speed = StringProperty("{:+0.3f}")

    imperial_position = StringProperty("{:+0.4f}")
    imperial_speed = StringProperty("{:+0.4f}")

    angle_format = StringProperty("{:+0.1f}")
    angle_speed_format = StringProperty("{:+0.1f}")

    font_size = NumericProperty(24)
    font_name = StringProperty("fonts/iosevka-regular.ttf")

    current_format = StringProperty("MM")
    speed_format = StringProperty()
    position_format = StringProperty()
    factor = ObjectProperty(MM_FRACTION)

    display_color = ColorProperty("#ffcc35ff")
    accept_color = ColorProperty("#32ff32ff")
    cancel_color = ColorProperty("#ff3232ff")
    color_on = ColorProperty("#ffcc32a0")
    color_off = ColorProperty("#ffcc3220")

    metric_speed_unit = StringProperty("m/min")
    imperial_speed_unit = StringProperty("ft/min")

    volume = NumericProperty(0.2)

    disable_error_reporting = BooleanProperty(False)

    position_tolerance = NumericProperty(0.05)

    hide_mouse_cursor = BooleanProperty(False)

    show_speeds = BooleanProperty(True)
    show_wizard = BooleanProperty(True)

    max_row_height = NumericProperty(150)

    def __init__(self, **kv):
        super().__init__(**kv)
        self.angle_speed_format = self.angle_speed_format.replace("RPM", "").replace(" ", "")
        self.bind(current_format=self.update_format)
        self.bind(metric_speed_unit=self.update_format)
        self.bind(imperial_speed_unit=self.update_format)
        self.update_format()

    def update_format(self, *args, **kv):
        if self.current_format == "MM":
            self.speed_format = f"{self.metric_speed} {self.metric_speed_unit}"
            self.position_format = self.metric_position
            self.factor = self.MM_FRACTION
        else:
            self.speed_format = f"{self.imperial_speed} {self.imperial_speed_unit}"
            self.position_format = self.imperial_position
            self.factor = self.INCHES_FRACTION

    def toggle(self, *_):
        if self.current_format == "MM":
            self.current_format = "IN"
        else:
            self.current_format = "MM"
