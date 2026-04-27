from kivy.logger import Logger
from kivy.properties import BooleanProperty, NumericProperty

from rcp.dispatchers.saving_dispatcher import SavingDispatcher

log = Logger.getChild(__name__)


class ElsDispatcher(SavingDispatcher):
    """Persists ELS axis role assignments and Assisted Threading machine settings."""

    _save_class_name = "Els"
    _skip_save = ["x", "y", "width", "height", "size_hint_x", "size_hint_y",
                  "pos", "size", "minimum_height", "minimum_width", "padding", "spacing"]

    # ── ELS axis roles ────────────────────────────────────────────────
    spindle_axis_index = NumericProperty(-1)
    z_axis_index = NumericProperty(-1)
    x_axis_index = NumericProperty(-1)

    # ── Assisted Threading: thread geometry ───────────────────────────
    at_cross_slide_diameter_mode = BooleanProperty(False)

    # ── Assisted Threading: speed & acceleration ──────────────────────
    at_reversing_speed = NumericProperty(500)
    at_preload_adjust_speed = NumericProperty(500)
    at_threading_max_speed = NumericProperty(2000)
    at_reversing_adjusting_acceleration = NumericProperty(1000)
    at_threading_acceleration = NumericProperty(1000)

    # ── Assisted Threading: tolerances & backlash ─────────────────────
    at_rotary_encoder_sync_tolerance = NumericProperty(5)
    at_saddle_encoder_stability_tolerance = NumericProperty(1)
    at_saddle_encoder_stability_samples = NumericProperty(3)
    at_metric_distances = BooleanProperty(True)
    at_saddle_backlash_distance = NumericProperty(10)
    at_backlash_cushion = NumericProperty(2)

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
        if idx < 0:
            return
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
