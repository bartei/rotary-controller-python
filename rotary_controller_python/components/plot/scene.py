import os

from kivy import Logger
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty
from kivy.graphics import Color, Point, Ellipse, Line
from kivy.uix.stencilview import StencilView

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class Scene(FloatLayout, StencilView):
    zoom = NumericProperty(1.0)
    current_scene = NumericProperty(0)
    scan = []

    def __init__(self, **kwargs):
        super(Scene, self).__init__(**kwargs)
        self.points = []
        self.old_points = []
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)
        self.bind(zoom=self.update_canvas)
        self.bind(current_scene=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        self.old_points = self.points
        self.points = []
        cs = self.current_scene
        with self.canvas:
            Color(0.2, 1, 0.2, 1)
            # Ellipse(
            #     pos=(self.width / 2 - 10, self.height / 2 - 10),
            #     size=(20, 20),
            #     angle_start=0,
            #     angle_end=360
            # )
            Line(circle=(0 + self.width / 2, 0 + self.height / 2, 20), width=1.5)
            # Point(points=self.old_points, pointsize=2)
            # if self.scan:
            #     for s in self.scan[int(cs)]:
            #         self.points.append(s[IDX_X] * self.zoom + self.width / 2)
            #         self.points.append(s[IDX_Y] * self.zoom + self.height / 2)

            Color(1.0, 0.5, 0.5, 1)
            if self.points:
                Point(points=self.points, pointsize=2)
