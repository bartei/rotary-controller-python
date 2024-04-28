import os

from kivy import Logger
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import Color, Point, Ellipse, Line, Rectangle
from kivy.uix.stencilview import StencilView

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class Scene(FloatLayout, StencilView):
    zoom = NumericProperty(1.0)
    points = ListProperty([])

    def __init__(self, **kwargs):
        super(Scene, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)
        self.bind(zoom=self.update_canvas)
        self.bind(points=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0, 1, 0, 1)
            #Rectangle(pos=[-10 + self.width/2, -10 + self.height/2], size=[20, 20])
            Line(rectangle=(-10 + self.width/2, -10 + self.height/2, 20, 20), width=1)

            for p in self.points:
                dot_radius = 20
                cross_extra = 10
                trx_x = p[0] * self.zoom + self.width / 2 - dot_radius
                trx_y = p[1] * self.zoom + self.height / 2 - dot_radius

                Color(0.2, 0.2, 0.2, 0.6)
                Ellipse(
                    pos=(trx_x, trx_y),
                    size=(dot_radius * 2, dot_radius * 2),
                    angle_start=0,
                    angle_end=360
                )

                Color(1, 1, 1, 1)
                Line(
                    points=(
                        trx_x - cross_extra,
                        trx_y+dot_radius,
                        trx_x+dot_radius * 2 + cross_extra,
                        trx_y+dot_radius
                    )
                )
                Line(
                    points=(
                        trx_x+dot_radius,
                        trx_y - cross_extra,
                        trx_x+dot_radius,
                        trx_y+dot_radius*2 + cross_extra
                    )
                )
