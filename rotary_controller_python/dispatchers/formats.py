from kivy.app import App
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    StringProperty,
)
from loguru import logger as log

from rotary_controller_python.dispatchers import SavingDispatcher
from rotary_controller_python.utils.communication import DeviceManager


class FormatsDispatcher(SavingDispatcher):
    metric_position = StringProperty("{:+0.3f}")
    metric_speed = StringProperty("{:+0.3f}")

    imperial_position = StringProperty("{:+0.4f}")
    imperial_speed = StringProperty("{:+0.4f}")

    angle_format = StringProperty("{:+0.1f}")
    current_format = StringProperty("MM")
    speed_format = StringProperty()
    position_format = StringProperty()
    factor = NumericProperty(1)

    def __init__(self, **kv):
        super().__init__(**kv)
        self.update_format()

    def update_format(self):
        if self.current_format == "MM":
            self.speed_format = self.metric_speed
            self.position_format = self.metric_position
            self.factor = 1.0
        else:
            self.speed_format = self.metric_speed
            self.position_format = self.metric_position
            self.factor = 25.4

    def toggle(self):
        if self.current_format == "MM":
            self.current_format = "IN"
        else:
            self.current_format = "MM"

    def on_current_format(self, instance, value):
        self.update_format()
