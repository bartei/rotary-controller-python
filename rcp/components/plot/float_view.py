from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, NumericProperty, ObjectProperty

from rcp.components.home.coordbar import CoordBar
from rcp.dispatchers.circle_pattern import CirclePatternDispatcher
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class FloatView(FloatLayout):
    scene_canvas = ObjectProperty(None)
    mouse_position = ListProperty([0, 0])
    circle_pattern = ObjectProperty(CirclePatternDispatcher(id_override="0"))
    zoom = NumericProperty(1.0)
    tool_x = NumericProperty(0)
    tool_y = NumericProperty(0)
    tool_z = NumericProperty(0)

    def __init__(self, **kwargs):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kwargs)
        # Window.bind(mouse_pos=self.window_mouse_pos)
        Window.bind(on_motion=self.on_motion)
        self.circle_pattern.recalculate()
        self.app.bind(update_tick=self.update_tick)

    def update_tick(self, *arg, **kv):
        coord_bars: list[CoordBar] = self.app.scales
        self.tool_x = coord_bars[0].scaledPosition
        self.tool_y = coord_bars[1].scaledPosition
        self.tool_z = coord_bars[2].scaledPosition

    def on_motion(self, window, etype, event):
        # will receive all motion events.
        if self.collide_point(window.mouse_pos[0], window.mouse_pos[1]):
            if event.device == 'mouse' and event.button in ('scrollup', 'scrolldown'):
                if event.button == 'scrollup':
                    self.zoom = self.zoom / 1.1
                if event.button == 'scrolldown':
                    self.zoom = self.zoom * 1.1
