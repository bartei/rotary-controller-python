import math
import os

from kivy import Logger
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.popup import Popup

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ScenePopup(Popup):
    zoom = NumericProperty(1.0)
    current_scene = NumericProperty(0)
    mouse_position = ListProperty([10, 20, 0])
    scan = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.window_mouse_pos)
        Window.bind(on_motion=self.on_motion)

    def on_motion(self, window, etype, event):
        # will receive all motion events.
        if self.collide_point(window.mouse_pos[0], window.mouse_pos[1]):
            if event.device == 'mouse' and event.button in ('scrollup', 'scrolldown'):
                if event.button == 'scrollup':
                    self.zoom = self.zoom / 1.1
                if event.button == 'scrolldown':
                    self.zoom = self.zoom * 1.1

    def on_scan(self, instance, value):
        self.ids.current_scene.max = len(self.scan) - 1
        self.ids.scene_canvas.scan = value

    def on_current_scene(self, instance, value):
        pass
        # if self.scan:
        #     self.ids.lbl_time.text = "{:0.2f}".format(self.scan[int(value)][0][IDX_TIME] / 1000000.0)

    def window_mouse_pos(self, instance, value):
        global_pos = self.ids.scene_canvas.to_widget(value[0], value[1])
        deltaX = global_pos[0] - 5000
        deltaY = global_pos[1] - 5000
        degrees = math.degrees(math.atan2(deltaY, deltaX))
        self.mouse_position = [deltaX / self.zoom, deltaY / self.zoom, degrees]

    def cancel(self):
        self.dismiss()
