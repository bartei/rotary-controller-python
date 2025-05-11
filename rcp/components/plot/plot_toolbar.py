import os

from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class PlotToolbar(BoxLayout):
    popup_instance = ObjectProperty(None)
    float_view = ObjectProperty()

    def next_point(self, instance=None, value=None):
        self.float_view.scene_canvas.selected_point = (self.float_view.scene_canvas.selected_point + 1) % len(self.float_view.scene_canvas.points)

    def prev_point(self, instance=None, value=None):
        self.float_view.scene_canvas.selected_point = (self.float_view.scene_canvas.selected_point - 1) % len(self.float_view.scene_canvas.points)
