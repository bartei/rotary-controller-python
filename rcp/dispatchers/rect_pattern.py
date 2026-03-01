import math

from kivy.logger import Logger
from kivy.properties import (
    NumericProperty,
    ListProperty,
)

from rcp.dispatchers.saving_dispatcher import SavingDispatcher

log = Logger.getChild(__name__)


class RectPatternDispatcher(SavingDispatcher):
    origin_x = NumericProperty(0)
    origin_y = NumericProperty(0)
    columns = NumericProperty(3)
    rows = NumericProperty(3)
    spacing_x = NumericProperty(25.0)
    spacing_y = NumericProperty(25.0)
    angle = NumericProperty(0)
    points = ListProperty([])

    _skip_save = ["points"]

    def __init__(self, **kv):
        super().__init__(**kv)
        self.bind(
            origin_x=self.recalculate,
            origin_y=self.recalculate,
            columns=self.recalculate,
            rows=self.recalculate,
            spacing_x=self.recalculate,
            spacing_y=self.recalculate,
            angle=self.recalculate,
        )

    def recalculate(self, *kv):
        points_list = []
        a = math.radians(self.angle)
        cos_a = math.cos(a)
        sin_a = math.sin(a)

        for row in range(int(self.rows)):
            for col in range(int(self.columns)):
                x_off = (col - (self.columns - 1) / 2) * self.spacing_x
                y_off = (row - (self.rows - 1) / 2) * self.spacing_y

                rotated_x = x_off * cos_a - y_off * sin_a
                rotated_y = x_off * sin_a + y_off * cos_a

                points_list.append(
                    (self.origin_x + rotated_x, self.origin_y + rotated_y)
                )

        self.points = points_list
