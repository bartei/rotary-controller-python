import time

from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

load_kv(__file__)

LONG_PRESS_THRESHOLD = 1.0


class DroCoordBar(BoxLayout):
    """Simplified CoordBar for DRO/ELS modes: no sync ratio Num/Den columns, no sync toggle."""
    axis = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._zero_press_time = 0

    def update_position(self):
        if self.axis is not None:
            self.axis.update_position()

    def on_zero_press(self):
        self._zero_press_time = time.monotonic()

    def on_zero_release(self):
        if self.axis is None:
            return
        if time.monotonic() - self._zero_press_time >= LONG_PRESS_THRESHOLD:
            self.axis.undo_zero()
        else:
            self.axis.zero_position()
