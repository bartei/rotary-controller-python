from rcp.components.home.coordbar import CoordBar
from rcp.components.home.mode_layout import ModeLayout
from rcp.components.home.servobar import ServoBar


class IndexModeLayout(ModeLayout):
    """Index mode: full CoordBars (with sync ratio Num/Den) + ServoBar."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.servo_bar = ServoBar()
        self.build_axis_bars()
        self.add_widget(self.servo_bar)

    def build_axis_bars(self):
        for axis_disp in self.app.axes:
            cb = CoordBar(axis=axis_disp)
            self.axis_bars.append(cb)
            self.add_widget(cb)

    def rebuild_axes(self):
        self.remove_widget(self.servo_bar)
        super().rebuild_axes()
        self.add_widget(self.servo_bar)
