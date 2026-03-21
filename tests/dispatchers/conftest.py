from fractions import Fraction

from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, NumericProperty, StringProperty, ObjectProperty


class MockBoard(EventDispatcher):
    connected = BooleanProperty(False)
    update_tick = NumericProperty(0)
    device = ObjectProperty(None, allownone=True)

    def __init__(self, **kv):
        super().__init__(**kv)
        self.fast_data_values = {}


class MockFormats(EventDispatcher):
    current_format = StringProperty("MM")
    factor = ObjectProperty(Fraction(1, 1))
    position_format = StringProperty("{:+0.3f}")
    angle_format = StringProperty("{:+0.1f}")
    angle_speed_format = StringProperty("{:+0.1f}")
    speed_format = StringProperty("{:+0.3f} M/min")
    display_color = StringProperty("#ffffffff")


class MockOffsetProvider(EventDispatcher):
    currentOffset = NumericProperty(0)
    abs_mode = BooleanProperty(False)
