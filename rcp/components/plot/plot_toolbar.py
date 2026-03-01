from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class PlotToolbar(BoxLayout):
    popup_instance = ObjectProperty(None)
    float_view = ObjectProperty()
    plane_label = StringProperty("?-?")

    def on_float_view(self, instance, value):
        if value is not None:
            value.bind(plane_label=self._sync_plane_label)
            self.plane_label = value.plane_label

    def _sync_plane_label(self, instance, value):
        self.plane_label = value

    def cycle_plane(self):
        if self.float_view is not None:
            self.float_view.cycle_plane()

    def next_point(self, instance=None, value=None):
        self.float_view.scene_canvas.selected_point = (self.float_view.scene_canvas.selected_point + 1) % len(self.float_view.scene_canvas.points)

    def prev_point(self, instance=None, value=None):
        self.float_view.scene_canvas.selected_point = (self.float_view.scene_canvas.selected_point - 1) % len(self.float_view.scene_canvas.points)
