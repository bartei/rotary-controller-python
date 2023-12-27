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

    angle = StringProperty("{:+0.1f}")
