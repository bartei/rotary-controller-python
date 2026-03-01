from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, NumericProperty

from rcp.components.home.coordbar import CoordBar
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class CoordsOverlay(BoxLayout):
    zoom = NumericProperty(0.0)
    tool_x = NumericProperty(0.0)
    tool_y = NumericProperty(0.0)
    tool_z = NumericProperty(0.0)
    selected_x = NumericProperty(0.0)
    selected_y = NumericProperty(0.0)

    def __init__(self, **kwargs):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kwargs)
        self.app.bind(update_tick=self.update_tick)

    def update_tick(self, *arg, **kv):
        coord_bars: list[CoordBar] = self.app.scales
        self.tool_x = coord_bars[0].scaledPosition
        self.tool_y = coord_bars[1].scaledPosition
        self.tool_z = coord_bars[2].scaledPosition