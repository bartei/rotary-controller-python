import math

from kivy.logger import Logger
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.uix.stencilview import StencilView

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

# CNC Dark color theme
BG_COLOR = (0.102, 0.102, 0.180, 1)          # #1a1a2e
GRID_COLOR = (0.165, 0.165, 0.243, 1)        # #2a2a3e
AXIS_COLOR = (0.306, 0.804, 0.769, 1)        # #4ecdc4
ORIGIN_COLOR = (0.306, 0.804, 0.769, 1)      # #4ecdc4
SELECTED_COLOR = (1.0, 0.8, 0.208, 1)        # #ffcc35
UNSELECTED_COLOR = (0.306, 0.804, 0.769, 0.4)  # #4ecdc4 @ 40%
TOOL_COLOR = (1.0, 0.42, 0.42, 1)            # #ff6b6b

GRID_SPACING = 50  # world-space mm


class Scene(FloatLayout, StencilView):
    zoom = NumericProperty(1.0)
    points = ListProperty([])
    scaled_points = ListProperty([])
    selected_point = NumericProperty(0)
    dot_size = NumericProperty(20)
    tool_x = NumericProperty(0.0)
    tool_y = NumericProperty(0.0)

    def __init__(self, **kwargs):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super(Scene, self).__init__(**kwargs)
        self.bind(size=self.update_points)
        self.bind(zoom=self.update_points)
        self.bind(points=self.update_points)
        self.bind(tool_x=self.update_points)
        self.bind(tool_y=self.update_points)
        self.bind(selected_point=self.update_points)

    def update_points(self, *args):
        self.scaled_points = [
            [
                item[0] * self.zoom,
                item[1] * self.zoom,
            ] for item in self.points
        ]

        cx = self.width / 2
        cy = self.height / 2

        self.canvas.clear()
        with self.canvas:
            # 1. Background fill
            Color(*BG_COLOR)
            Rectangle(pos=(0, 0), size=(self.width, self.height))

            # 2. Grid lines at GRID_SPACING world-space intervals
            Color(*GRID_COLOR)
            spacing = GRID_SPACING * self.zoom
            if spacing > 2:  # skip grid when zoomed out too far
                # Vertical grid lines
                n_left = math.ceil(-cx / spacing)
                n_right = math.floor((self.width - cx) / spacing)
                for n in range(n_left, n_right + 1):
                    if n == 0:
                        continue  # axis drawn separately
                    x = n * spacing + cx
                    Line(points=[x, 0, x, self.height], width=1)

                # Horizontal grid lines
                n_bottom = math.ceil(-cy / spacing)
                n_top = math.floor((self.height - cy) / spacing)
                for n in range(n_bottom, n_top + 1):
                    if n == 0:
                        continue
                    y = n * spacing + cy
                    Line(points=[0, y, self.width, y], width=1)

            # 3. Axes — teal, full widget span
            Color(*AXIS_COLOR)
            Line(points=[cx, 0, cx, self.height], width=1)
            Line(points=[0, cy, self.width, cy], width=1)

            # 4. Origin marker — teal cross (±15px)
            Color(*ORIGIN_COLOR)
            arm = 15
            Line(points=[cx - arm, cy, cx + arm, cy], width=1.5)
            Line(points=[cx, cy - arm, cx, cy + arm], width=1.5)

            # 5. Pattern points — crosshair + dot markers
            for i, p in enumerate(self.scaled_points):
                px = p[0] + cx
                py = p[1] + cy
                if i == self.selected_point:
                    Color(*SELECTED_COLOR)
                    arm = 12
                    w = 1.5
                else:
                    Color(*UNSELECTED_COLOR)
                    arm = 8
                    w = 1
                # Center dot
                Ellipse(pos=(px - 3, py - 3), size=(6, 6))
                # Horizontal arm
                Line(points=[px - arm, py, px + arm, py], width=w)
                # Vertical arm
                Line(points=[px, py - arm, px, py + arm], width=w)

            # 6. Tool position — coral red diamond
            Color(*TOOL_COLOR)
            tx = self.tool_x * self.zoom + cx
            ty = self.tool_y * self.zoom + cy
            r = self.dot_size * 0.7  # diamond half-size
            Line(
                points=[
                    tx, ty + r,       # top
                    tx + r, ty,       # right
                    tx, ty - r,       # bottom
                    tx - r, ty,       # left
                ],
                close=True,
                width=1.5,
            )

    def on_touch_up(self, touch):
        touch_x = touch.x - self.width / 2
        touch_y = touch.y - self.height / 2

        for i, p in enumerate(self.scaled_points):
            if p[0] - self.dot_size < touch_x < p[0] + self.dot_size and p[1] - self.dot_size < touch_y < p[1] + self.dot_size:
                self.selected_point = i
                break
