from kivy.uix.widget import Widget

from rcp.components.home.assisted_threading.bar import AssistedThreadingBar
from rcp.components.home.coordbar import CoordBar
from rcp.components.home.dro_coordbar import DroCoordBar
from rcp.components.home.mode_layout import ModeLayout


class AtModeLayout(ModeLayout):
    """AT mode: spindle axis uses CoordBar (Num/Den visible), all others use DroCoordBar + AssistedThreadingBar."""

    def __init__(self, at_bar: AssistedThreadingBar, **kwargs):
        super().__init__(**kwargs)
        self.at_bar = at_bar
        self.spacer = Widget()
        self.build_axis_bars()
        self.add_widget(self.spacer)
        self.add_widget(self.at_bar)

        # Rebuild when ELS axis assignments change (e.g. saved settings load)
        self.app.els.bind(
            spindle_axis_index=lambda *_: self.rebuild_axes(),
            z_axis_index=lambda *_: self.rebuild_axes(),
            x_axis_index=lambda *_: self.rebuild_axes(),
        )

        self.app.formats.bind(max_row_height=lambda *_: self._update_row_heights())
        self.bind(height=self._update_row_heights)
        self._update_row_heights()

    def _update_row_heights(self, *_):
        num_rows = len(self.axis_bars)
        if num_rows == 0:
            return
        available = self.height - self.at_bar.height
        row_height = min(available / num_rows, self.app.formats.max_row_height)
        for bar in self.axis_bars:
            bar.size_hint_y = None
            bar.height = row_height
        # spacer absorbs remaining space

    def build_axis_bars(self):
        seen = set()
        for axis in [
            self.app.els.get_z_axis(),
            self.app.els.get_x_axis(),
            self.app.els.get_spindle_axis(),
        ]:
            if axis is None or id(axis) in seen:
                continue
            seen.add(id(axis))
            cb = CoordBar(axis=axis) if axis.spindleMode else DroCoordBar(axis=axis)
            self.axis_bars.append(cb)
            self.add_widget(cb)

    def rebuild_axes(self):
        self.remove_widget(self.spacer)
        self.remove_widget(self.at_bar)
        super().rebuild_axes()
        self.add_widget(self.spacer)
        self.add_widget(self.at_bar)
        self._update_row_heights()
