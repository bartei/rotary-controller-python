from rcp.components.home.dro_coordbar import DroCoordBar
from rcp.components.home.mode_layout import ModeLayout


class DroModeLayout(ModeLayout):
    """DRO mode: simplified DroCoordBars filling all space, no bottom bar."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_axis_bars()

    def build_axis_bars(self):
        for axis_disp in self.app.axes:
            cb = DroCoordBar(axis=axis_disp)
            self.axis_bars.append(cb)
            self.add_widget(cb)
