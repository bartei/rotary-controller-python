import os

from kivy import Logger
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, NumericProperty

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class CoordsOverlay(BoxLayout):
    mouse_position = ListProperty([0, 0])
    zoom = NumericProperty(0.0)
    tool_x = NumericProperty(0.0)
    tool_y = NumericProperty(0.0)
