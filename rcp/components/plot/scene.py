import os

from kivy import Logger
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import Color, Line, Ellipse
from kivy.uix.stencilview import StencilView

from rcp.components.coordbar import CoordBar

# from rcp.components.plot.point_widget import PointWidget

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class Scene(FloatLayout, StencilView):
    zoom = NumericProperty(1.0)
    points = ListProperty([])
    scaled_points = ListProperty([])
    selected_point = NumericProperty(0)
    dot_size = NumericProperty(20)
    tool_x = NumericProperty(0.0)
    tool_y = NumericProperty(0.0)

    def __init__(self, **kwargs):
        self.app = App.get_running_app()
        super(Scene, self).__init__(**kwargs)
        # self.bind(pos=self.update_canvas)
        self.bind(size=self.update_points)
        self.bind(zoom=self.update_points)
        self.bind(points=self.update_points)
        self.bind(tool_x=self.update_points)
        self.bind(tool_y=self.update_points)

    def update_points(self, *args):
        self.scaled_points = [
            [
                item[0] * self.zoom,
                item[1] * self.zoom,
            ] for item in self.points
        ]

        self.canvas.clear()
        with self.canvas:
            Color(0, 1, 0, 1)
            Line(rectangle=(-10 + self.width/2, -10 + self.height/2, 20, 20), width=1)

            Color(0.5, 1, 0.5, 1)
            Line(points=[self.width/2, 0, self.width/2, self.height], width=1)
            Line(points=[0, self.height/2, self.width,  self.height/2], width=1)

            for i, p in enumerate(self.scaled_points):
                if i == self.selected_point:
                    Color(0.8, 1, 0.8, 1)
                else:
                    Color(0.8, 1, 0.8, 0.2)

                Ellipse(
                    pos=(
                        p[0] + self.width / 2 - self.dot_size/2,
                        p[1] + self.height / 2 - self.dot_size/2
                    ),
                    size=(self.dot_size, self.dot_size),
                    angle_start=0,
                    angle_end=360
                )

            Color(0.5, 1, 0.5, 1)
            Ellipse(
                pos=(
                    self.tool_x * self.zoom + self.width / 2 - self.dot_size / 2,
                    self.tool_y * self.zoom + self.height / 2 - self.dot_size / 2
                ),
                size=(self.dot_size, self.dot_size),
                angle_start=0,
                angle_end=360
            )

    def on_touch_up(self, touch):
        touch_x = touch.x - self.width/2
        touch_y = touch.y - self.height/2

        for i, p in enumerate(self.scaled_points):
            if p[0] - self.dot_size < touch_x < p[0] + self.dot_size and p[1] - self.dot_size < touch_y < p[1] + self.dot_size:
                self.selected_point = i
                break

        self.update_points()
