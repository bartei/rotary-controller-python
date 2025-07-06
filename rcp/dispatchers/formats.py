from fractions import Fraction

from kivy.logger import Logger
from kivy.properties import (
    NumericProperty,
    StringProperty,
    ListProperty,
    ObjectProperty,
    ColorProperty,
    BooleanProperty
)

from rcp.dispatchers import SavingDispatcher

log = Logger.getChild(__name__)


class FormatsDispatcher(SavingDispatcher):
    _force_save = [
        'display_color',
        'accept_color',
        'cancel_color',
        'color_on',
        'color_off',
        'metric_speed_mode',
        'imperial_speed_mode'
    ]

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
    
    # New properties to track the speed display mode
    # True = M/min, False = mm/min for metric
    # True = ft/min, False = in/min for imperial
    metric_speed_mode = BooleanProperty(True)
    imperial_speed_mode = BooleanProperty(True)
    
    # Speed conversion factor: 1.0 for standard units, higher for smaller units
    speed_conversion_factor = NumericProperty(1.0)

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
            if self.metric_speed_mode:
                self.speed_format = f"{self.metric_speed} M/min"
                self.speed_conversion_factor = 1.0
            else:
                self.speed_format = f"{self.metric_speed} mm/min"
                self.speed_conversion_factor = 1000.0
            self.position_format = self.metric_position
            self.factor = Fraction(1, 1)
        else:
            if self.imperial_speed_mode:
                self.speed_format = f"{self.imperial_speed} Ft/min"
                self.speed_conversion_factor = 1.0
            else:
                self.speed_format = f"{self.imperial_speed} in/min"
                self.speed_conversion_factor = 12.0
            self.position_format = self.imperial_position
            self.factor = Fraction(10, 254)
            
    def toggle_speed_mode(self):
        """Toggle between different speed display modes"""
        if self.current_format == "MM":
            self.metric_speed_mode = not self.metric_speed_mode
        else:
            self.imperial_speed_mode = not self.imperial_speed_mode
        self.update_format()

    def toggle(self, *_):
        if self.current_format == "MM":
            self.current_format = "IN"
        else:
            self.current_format = "MM"
