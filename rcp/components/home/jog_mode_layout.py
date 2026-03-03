from rcp.components.home.coordbar import CoordBar
from rcp.components.home.jogbar import JogBar
from rcp.components.home.mode_layout import ModeLayout


class JogModeLayout(ModeLayout):
    """Jog mode: full CoordBars (with sync ratio Num/Den) + JogBar."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jog_bar = JogBar()
        self.build_axis_bars()
        self.add_widget(self.jog_bar)

    def build_axis_bars(self):
        for axis_disp in self.app.axes:
            cb = CoordBar(axis=axis_disp)
            self.axis_bars.append(cb)
            self.add_widget(cb)

    def rebuild_axes(self):
        self.remove_widget(self.jog_bar)
        super().rebuild_axes()
        self.add_widget(self.jog_bar)
