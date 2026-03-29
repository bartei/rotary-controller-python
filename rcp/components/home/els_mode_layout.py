from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from rcp.components.home.dro_coordbar import DroCoordBar
from rcp.components.home.elsbar import ElsBar
from rcp.components.home.mode_layout import ModeLayout
from rcp.utils.kv_loader import load_kv

load_kv(__file__)

# Font Awesome 6 icons for rotation direction
ICON_CW = "\uf01e"   # rotate-right
ICON_CCW = "\uf0e2"  # rotate-left
ICON_STOP = "\uf04d"  # stop

LONG_PRESS_THRESHOLD = 1.0

class ElsSpindleInfo(BoxLayout):
    """Displays spindle speed with direction icon and absolute position with zero button."""
    spindle_rpm = StringProperty("--")
    spindle_position = StringProperty("--")
    direction_icon = StringProperty(ICON_STOP)

    def __init__(self, **kwargs):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        self._long_press_event = None
        super().__init__(**kwargs)
        self.app.board.bind(update_tick=self._update_spindle)

    def _update_spindle(self, *args):
        axis = self.app.els.get_spindle_axis()
        if axis is None:
            if self.spindle_rpm != "--":
                self.spindle_rpm = "--"
            if self.spindle_position != "--":
                self.spindle_position = "--"
            if self.direction_icon != ICON_STOP:
                self.direction_icon = ICON_STOP
            return

        rpm = axis.formattedPosition
        if rpm != self.spindle_rpm:
            self.spindle_rpm = rpm

        pos = self.app.formats.position_format.format(axis.scaledPosition) + "\u00b0"
        if pos != self.spindle_position:
            self.spindle_position = pos

        if axis.speed > 0.5:
            icon = ICON_CW
        elif axis.speed < -0.5:
            icon = ICON_CCW
        else:
            icon = ICON_STOP
        if icon != self.direction_icon:
            self.direction_icon = icon

    def on_zero_press(self):
        self._long_press_event = Clock.schedule_once(self._do_undo_zero, LONG_PRESS_THRESHOLD)

    def on_zero_release(self):
        if self._long_press_event is not None:
            self._long_press_event.cancel()
            self._long_press_event = None
            axis = self.app.els.get_spindle_axis()
            if axis is not None:
                axis.zero_position()

    def _do_undo_zero(self, dt):
        self._long_press_event = None
        axis = self.app.els.get_spindle_axis()
        if axis is not None:
            axis.undo_zero()


class ElsModeLayout(ModeLayout):
    """ELS mode: spindle info bar + DroCoordBars for Z/X axes + ElsBar."""

    def __init__(self, els_bar: ElsBar, **kwargs):
        super().__init__(**kwargs)
        self.els_bar = els_bar
        self.spindle_info = ElsSpindleInfo()
        self.spacer = Widget()

        self.build_axis_bars()
        self.add_widget(self.spindle_info)
        self.add_widget(self.spacer)
        self.add_widget(self.els_bar)

        # Rebuild when ELS axis assignments change
        self.app.els.bind(
            spindle_axis_index=lambda *a: self.rebuild_axes(),
            z_axis_index=lambda *a: self.rebuild_axes(),
            x_axis_index=lambda *a: self.rebuild_axes(),
        )

        self.app.formats.bind(max_row_height=lambda *_: self._update_row_heights())
        self.app.formats.bind(show_speeds=lambda *_: self.rebuild_axes())
        self.bind(height=self._update_row_heights)
        self._update_row_heights()

    def _update_row_heights(self, *args):
        num_rows = len(self.axis_bars) + 1  # axis bars + spindle info
        if num_rows == 0:
            return

        available = self.height - self.els_bar.height
        row_height = min(available / num_rows, self.app.formats.max_row_height)

        self.spindle_info.size_hint_y = None
        self.spindle_info.height = row_height
        for bar in self.axis_bars:
            bar.size_hint_y = None
            bar.height = row_height

        # spacer absorbs remaining space (size_hint_y defaults to 1)

    def build_axis_bars(self):
        for axis in [self.app.els.get_z_axis(), self.app.els.get_x_axis()]:
            if axis is None:
                continue
            cb = DroCoordBar(axis=axis)
            self.axis_bars.append(cb)
            self.add_widget(cb)

    def rebuild_axes(self):
        self.remove_widget(self.spindle_info)
        self.remove_widget(self.spacer)
        self.remove_widget(self.els_bar)
        super().rebuild_axes()
        self.add_widget(self.spindle_info)
        self.add_widget(self.spacer)
        self.add_widget(self.els_bar)
        self._update_row_heights()
