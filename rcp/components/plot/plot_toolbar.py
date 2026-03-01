from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class PlotToolbar(BoxLayout):
    popup_instance = ObjectProperty(None)
    float_view = ObjectProperty()

    def next_point(self, instance=None, value=None):
        self.float_view.scene_canvas.selected_point = (self.float_view.scene_canvas.selected_point + 1) % len(self.float_view.scene_canvas.points)

    def prev_point(self, instance=None, value=None):
        self.float_view.scene_canvas.selected_point = (self.float_view.scene_canvas.selected_point - 1) % len(self.float_view.scene_canvas.points)
