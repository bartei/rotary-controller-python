from kivy.logger import Logger
from kivy.properties import NumericProperty

from rcp.dispatchers.saving_dispatcher import SavingDispatcher

log = Logger.getChild(__name__)


class ElsDispatcher(SavingDispatcher):
    """Persists ELS axis role assignments: spindle, saddle (Z), and cross slide (X)."""

    _save_class_name = "Els"
    _skip_save = ["x", "y", "width", "height", "size_hint_x", "size_hint_y",
                  "pos", "size", "minimum_height", "minimum_width", "padding", "spacing"]

    spindle_axis_index = NumericProperty(-1)
    z_axis_index = NumericProperty(-1)
    x_axis_index = NumericProperty(-1)

    def __init__(self, **kwargs):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kwargs)
        self.bind(spindle_axis_index=self._apply_spindle_mode)
        # Apply on startup in case a saved value exists
        self._apply_spindle_mode()

    def _apply_spindle_mode(self, *args):
        """Set spindleMode=True on the selected spindle axis, False on all others."""
        idx = int(self.spindle_axis_index)
        for i, axis in enumerate(self.app.axes):
            axis.spindleMode = (i == idx)

    def get_spindle_axis(self):
        idx = int(self.spindle_axis_index)
        if 0 <= idx < len(self.app.axes):
            return self.app.axes[idx]
        return None

    def get_z_axis(self):
        idx = int(self.z_axis_index)
        if 0 <= idx < len(self.app.axes):
            return self.app.axes[idx]
        return None

    def get_x_axis(self):
        idx = int(self.x_axis_index)
        if 0 <= idx < len(self.app.axes):
            return self.app.axes[idx]
        return None
