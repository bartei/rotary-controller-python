from rcp.components.home.dro_coordbar import DroCoordBar
from rcp.components.home.mode_layout import ModeLayout
from kivy.uix.widget import Widget


class DroModeLayout(ModeLayout):
    """DRO mode: simplified DroCoordBars, no bottom bar."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.build_axis_bars()
        self.spacer = Widget()
        self.add_widget(self.spacer)

        self.app.formats.bind(max_row_height=lambda *_: self._update_row_heights())
        self.app.formats.bind(show_speeds=lambda *_: self.rebuild_axes())
        self.bind(height=self._update_row_heights)
        self._update_row_heights()

    def _update_row_heights(self, *args):
        num_rows = len(self.axis_bars)
        if num_rows == 0:
            return

        row_height = min(self.height / num_rows, self.app.formats.max_row_height)

        for bar in self.axis_bars:
            bar.size_hint_y = None
            bar.height = row_height

        # spacer absorbs remaining space (size_hint_y defaults to 1)

    def build_axis_bars(self):
        for axis_disp in self.app.axes:
            cb = DroCoordBar(axis=axis_disp)
            self.axis_bars.append(cb)
            self.add_widget(cb)

    def rebuild_axes(self):
        self.remove_widget(self.spacer)
        super().rebuild_axes()
        self.add_widget(self.spacer)
        self._update_row_heights()
