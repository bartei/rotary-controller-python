import math
import os

from kivy import Logger
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, NumericProperty, ObjectProperty

from rotary_controller_python.dispatchers.circle_pattern import CirclePatternDispatcher

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class FloatView(FloatLayout):
    scene_canvas = ObjectProperty(None)
    mouse_position = ListProperty([0, 0])
    circle_pattern = ObjectProperty(CirclePatternDispatcher())
    zoom = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Window.bind(mouse_pos=self.window_mouse_pos)
        Window.bind(on_motion=self.on_motion)
        self.circle_pattern.recalculate()

    def on_motion(self, window, etype, event):
        # will receive all motion events.
        if self.collide_point(window.mouse_pos[0], window.mouse_pos[1]):
            if event.device == 'mouse' and event.button in ('scrollup', 'scrolldown'):
                if event.button == 'scrollup':
                    self.zoom = self.zoom / 1.1
                if event.button == 'scrolldown':
                    self.zoom = self.zoom * 1.1
