from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

load_kv(__file__)


class CoordBar(BoxLayout):
    """Pure UI widget displaying scale state. All logic lives in ScaleDispatcher."""
    scale = ObjectProperty()

    def update_position(self):
        if self.scale is not None:
            self.scale.update_position()

    def toggle_sync(self):
        if self.scale is not None:
            self.scale.toggle_sync()

    def zero_position(self):
        if self.scale is not None:
            self.scale.zero_position()
