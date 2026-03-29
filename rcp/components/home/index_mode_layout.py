from rcp.components.home.coordbar import CoordBar
from rcp.components.home.mode_layout import ModeLayout
from rcp.components.home.servobar import ServoBar
from kivy.uix.widget import Widget


class IndexModeLayout(ModeLayout):
    """Index mode: full CoordBars (with sync ratio Num/Den) + ServoBar."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.servo_bar = ServoBar()
        self.spacer = Widget()

        self.build_axis_bars()
        self.add_widget(self.spacer)
        self.add_widget(self.servo_bar)

        self.app.formats.bind(max_row_height=lambda *_: self._update_row_heights())
        self.app.formats.bind(show_speeds=lambda *_: self.rebuild_axes())
        self.bind(height=self._update_row_heights)
        self._update_row_heights()

    def build_axis_bars(self):
        for axis_disp in self.app.axes:
            cb = CoordBar(axis=axis_disp)
            self.axis_bars.append(cb)
            self.add_widget(cb)

    def rebuild_axes(self):
        self.remove_widget(self.spacer)
        self.remove_widget(self.servo_bar)
        super().rebuild_axes()
        self.add_widget(self.spacer)
        self.add_widget(self.servo_bar)
        self._update_row_heights()

    def _update_row_heights(self, *args):
        num_rows = len(self.axis_bars)
        if num_rows == 0:
            return

        available = self.height - self.servo_bar.height
        row_height = min(available / num_rows, self.app.formats.max_row_height)

        for bar in self.axis_bars:
            bar.size_hint_y = None
            bar.height = row_height

        # spacer absorbs remaining space (size_hint_y defaults to 1)
