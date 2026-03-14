from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
import math

from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty

from rcp.dispatchers.circle_pattern import CirclePatternDispatcher
from rcp.dispatchers.line_pattern import LinePatternDispatcher
from rcp.dispatchers.rect_pattern import RectPatternDispatcher
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class FloatView(FloatLayout):
    scene_canvas = ObjectProperty(None)
    mouse_position = ListProperty([0, 0])
    circle_pattern = ObjectProperty(CirclePatternDispatcher(id_override="0"))
    rect_pattern = ObjectProperty(RectPatternDispatcher(id_override="0"))
    line_pattern = ObjectProperty(LinePatternDispatcher(id_override="0"))
    active_pattern = StringProperty("circle")
    active_points = ListProperty([])
    zoom = NumericProperty(1.0)
    tool_x = NumericProperty(0)
    tool_y = NumericProperty(0)
    tool_z = NumericProperty(0)
    plane_label = StringProperty("?-?")
    plane_h_index = NumericProperty(0)
    plane_v_index = NumericProperty(1)
    plane_h_label = StringProperty("X")
    plane_v_label = StringProperty("Y")
    at_position = BooleanProperty(False)

    def __init__(self, **kwargs):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        self.plane_pairs: list[tuple[int, int]] = []
        self._plane_index = 0
        super().__init__(**kwargs)
        Window.bind(on_motion=self.on_motion)
        self.circle_pattern.recalculate()
        self.rect_pattern.recalculate()
        self.line_pattern.recalculate()
        self.bind(active_pattern=self.update_active_points)
        self.circle_pattern.bind(points=self.update_active_points)
        self.rect_pattern.bind(points=self.update_active_points)
        self.line_pattern.bind(points=self.update_active_points)
        self.update_active_points()
        self.build_plane_pairs()
        self.app.board.bind(update_tick=self.update_tick)

    def update_tick(self, *arg, **kv):
        if self.app.manager.current != "plot":
            return
        axes = self.app.axes
        h = int(self.plane_h_index)
        v = int(self.plane_v_index)
        self.tool_x = axes[h].scaledPosition if h < len(axes) else 0.0
        self.tool_y = axes[v].scaledPosition if v < len(axes) else 0.0
        self.tool_z = axes[2].scaledPosition if len(axes) > 2 else 0.0

        if self.active_points and self.scene_canvas:
            idx = self.scene_canvas.selected_point
            if 0 <= idx < len(self.active_points):
                pt = self.active_points[idx]
                dist = math.hypot(self.tool_x - pt[0], self.tool_y - pt[1])
                self.at_position = dist <= self.app.formats.position_tolerance
            else:
                self.at_position = False
        else:
            self.at_position = False

    def build_plane_pairs(self):
        from itertools import combinations
        non_spindle = [
            i for i, a in enumerate(self.app.axes)
            if not a.spindleMode
        ]
        self.plane_pairs = list(combinations(non_spindle, 2))
        if not self.plane_pairs:
            self.plane_pairs = [(0, 1)]
        self._plane_index = 0
        self._apply_plane()

    def cycle_plane(self, *args):
        log.info(f"cycle_plane called, pairs={self.plane_pairs}, index={self._plane_index}")
        if not self.plane_pairs:
            return
        self._plane_index = (self._plane_index + 1) % len(self.plane_pairs)
        self._apply_plane()
        log.info(f"plane now: {self.plane_label} (index={self._plane_index})")

    def _apply_plane(self):
        if not self.plane_pairs:
            return
        self._plane_index = min(self._plane_index, len(self.plane_pairs) - 1)
        h, v = self.plane_pairs[self._plane_index]
        axes = self.app.axes
        # Clamp to valid range in case axes were removed
        h = min(h, len(axes) - 1) if axes else 0
        v = min(v, len(axes) - 1) if axes else 0
        self.plane_h_index = h
        self.plane_v_index = v
        self.plane_h_label = axes[h].axis_name if h < len(axes) else "?"
        self.plane_v_label = axes[v].axis_name if v < len(axes) else "?"
        self.plane_label = f"{self.plane_h_label}-{self.plane_v_label}"

    def update_active_points(self, *args):
        if self.scene_canvas is not None:
            self.scene_canvas.selected_point = 0
        if self.active_pattern == "circle":
            self.active_points = self.circle_pattern.points
        elif self.active_pattern == "line":
            self.active_points = self.line_pattern.points
        else:
            self.active_points = self.rect_pattern.points

    def on_motion(self, window, etype, event):
        # will receive all motion events.
        if self.collide_point(window.mouse_pos[0], window.mouse_pos[1]):
            if event.device == 'mouse' and event.button in ('scrollup', 'scrolldown'):
                if event.button == 'scrollup':
                    self.zoom = self.zoom / 1.1
                if event.button == 'scrolldown':
                    self.zoom = self.zoom * 1.1
