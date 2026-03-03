from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

load_kv(__file__)


class DroCoordBar(BoxLayout):
    """Simplified CoordBar for DRO/ELS modes: no sync ratio Num/Den columns, no sync toggle."""
    axis = ObjectProperty()

    def update_position(self):
        if self.axis is not None:
            self.axis.update_position()

    def zero_position(self):
        if self.axis is not None:
            self.axis.zero_position()
