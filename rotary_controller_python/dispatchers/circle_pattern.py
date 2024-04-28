import math

from kivy.logger import Logger
from kivy.properties import (
    NumericProperty,
    ListProperty,
)

from rotary_controller_python.dispatchers import SavingDispatcher

log = Logger.getChild(__name__)


class CirclePatternDispatcher(SavingDispatcher):
    origin_x = NumericProperty(0)
    origin_y = NumericProperty(0)
    holes_count = NumericProperty(6)
    diameter = NumericProperty(120.0)
    start_angle = NumericProperty(0)
    end_angle = NumericProperty(360)
    points = ListProperty([])

    def __init__(self, **kv):
        super().__init__(**kv)
        self.bind(
            origin_x=self.recalculate,
            origin_y=self.recalculate,
            holes_count=self.recalculate,
            diameter=self.recalculate,
            start_angle=self.recalculate,
            end_angle=self.recalculate,
        )

    def recalculate(self, *kv):
        points_list = []
        for i in range(self.holes_count + 1):
            angle_offset = (self.end_angle - self.start_angle) / self.holes_count * i * math.pi / 180
            angle_offset += self.start_angle * math.pi / 180

            # angle_for_i = 2 * math.pi / self.holes_count * i + self.start_angle
            relative_x = math.cos(angle_offset) * self.diameter / 2
            relative_y = math.sin(angle_offset) * self.diameter / 2
            points_list.append(
                (self.origin_x + relative_x, self.origin_y + relative_y)
            )

        self.points = points_list
