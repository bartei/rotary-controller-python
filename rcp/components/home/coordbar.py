from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

load_kv(__file__)


class CoordBar(BoxLayout):
    """Pure UI widget displaying axis state. All logic lives in AxisDispatcher."""
    axis = ObjectProperty()

    def update_position(self):
        if self.axis is not None:
            self.axis.update_position()

    def toggle_sync(self):
        if self.axis is not None:
            from rcp.app import MainApp
            app = MainApp.get_running_app()
            self.axis.toggle_sync(all_axes=list(app.axes))

    def zero_position(self):
        if self.axis is not None:
            self.axis.zero_position()
