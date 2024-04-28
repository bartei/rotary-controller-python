import math
import os

from kivy import Logger
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.uix.popup import Popup

from rotary_controller_python.dispatchers.circle_pattern import CirclePatternDispatcher

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ScenePopup(Popup):
    zoom = NumericProperty(1.0)
    mouse_position = ListProperty([10, 20, 0])
    scene_canvas = ObjectProperty(None)
    circle_pattern = ObjectProperty(CirclePatternDispatcher())
    rect_pattern = ObjectProperty(CirclePatternDispatcher())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.window_mouse_pos)
        Window.bind(on_motion=self.on_motion)

        self.circle_pattern.recalculate()

    def connect_rect(self):
        self.rect_pattern.recalculate()
        self.scene_canvas.points = self.rect_pattern.points
        self.scene_canvas.bind(points=self.rect_pattern.setter('points'))
        pass

    def on_motion(self, window, etype, event):
        # will receive all motion events.
        if self.collide_point(window.mouse_pos[0], window.mouse_pos[1]):
            if event.device == 'mouse' and event.button in ('scrollup', 'scrolldown'):
                if event.button == 'scrollup':
                    self.zoom = self.zoom / 1.1
                if event.button == 'scrolldown':
                    self.zoom = self.zoom * 1.1

    def window_mouse_pos(self, instance, value):
        global_pos = self.ids.scene_canvas.to_widget(value[0], value[1])
        delta_x = global_pos[0] - 5000
        delta_y = global_pos[1] - 5000
        degrees = math.degrees(math.atan2(delta_y, delta_x))
        self.mouse_position = [delta_x / self.zoom, delta_y / self.zoom, degrees]

    def cancel(self):
        self.dismiss()
