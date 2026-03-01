from kivy.logger import Logger
from kivy.properties import (
    NumericProperty,
    ListProperty,
)

from rcp.dispatchers.saving_dispatcher import SavingDispatcher

log = Logger.getChild(__name__)


class LinePatternDispatcher(SavingDispatcher):
    origin_x = NumericProperty(0)
    origin_y = NumericProperty(0)
    end_x = NumericProperty(100.0)
    end_y = NumericProperty(0.0)
    holes_count = NumericProperty(5)
    points = ListProperty([])

    _skip_save = ["points"]

    def __init__(self, **kv):
        super().__init__(**kv)
        self.bind(
            origin_x=self.recalculate,
            origin_y=self.recalculate,
            end_x=self.recalculate,
            end_y=self.recalculate,
            holes_count=self.recalculate,
        )

    def recalculate(self, *kv):
        points_list = []
        count = int(self.holes_count)

        if count < 2:
            points_list.append((self.origin_x, self.origin_y))
        else:
            for i in range(count):
                t = i / (count - 1)
                x = self.origin_x + t * (self.end_x - self.origin_x)
                y = self.origin_y + t * (self.end_y - self.origin_y)
                points_list.append((x, y))

        self.points = points_list
