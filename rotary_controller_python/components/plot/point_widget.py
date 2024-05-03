import os

from kivy import Logger
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from kivy.graphics import Color, Point, Ellipse, Line, Rectangle
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class PointWidget(Widget):
    size_hint = (None, None)
    size = (10, 10)
    active = BooleanProperty(False)
    dot_size = NumericProperty(10)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas.clear()
        with self.canvas:
            Color(0.2, 0.2, 0.2, 0.6)
            Ellipse(
                pos=(self.center_x - self.dot_size/2, self.center_y-self.dot_size/2),
                size=(self.dot_size, self.dot_size),
                angle_start=0,
                angle_end=360
            )

            # Color(1, 1, 1, 1)
            # Line(
            #     points=(
            #         trx_x - cross_extra,
            #         trx_y + dot_radius,
            #         trx_x + dot_radius * 2 + cross_extra,
            #         trx_y + dot_radius
            #     )
            # )
            # Line(
            #     points=(
            #         trx_x + dot_radius,
            #         trx_y - cross_extra,
            #         trx_x + dot_radius,
            #         trx_y + dot_radius * 2 + cross_extra
            #     )
            # )

