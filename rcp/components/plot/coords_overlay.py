from kivy.clock import Clock
from kivy.factory import Factory
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import NumericProperty

from rcp.dispatchers.scale import ScaleDispatcher
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)


class CoordsOverlay(BoxLayout):
    zoom = NumericProperty(0.0)
    selected_x = NumericProperty(0.0)
    selected_y = NumericProperty(0.0)
    plane_h_index = NumericProperty(0)
    plane_v_index = NumericProperty(1)

    def __init__(self, **kwargs):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        self._dtg_labels: list[tuple[int, str, Label]] = []
        self._sel_labels: list[tuple[int, str, Label]] = []
        self._tool_labels: list[tuple[int, str, Label]] = []
        super().__init__(**kwargs)

        self._axes: list[tuple[int, ScaleDispatcher]] = [
            (i, s) for i, s in enumerate(self.app.scales)
            if not s.spindleMode
        ]

        Clock.schedule_once(self._post_init)

    def _post_init(self, dt):
        self._populate_sections()
        self.app.board.bind(update_tick=self.update_tick)
        self.bind(selected_x=self._update_values)
        self.bind(selected_y=self._update_values)
        self.bind(plane_h_index=self._update_values)
        self.bind(plane_v_index=self._update_values)

    def _populate_sections(self):
        self._dtg_labels: list[tuple[int, str, Label]] = []
        self._sel_labels: list[tuple[int, str, Label]] = []
        self._tool_labels: list[tuple[int, str, Label]] = []

        for i, s in self._axes:
            dtg = Factory.CoordsValue()
            self.ids.dtg_box.add_widget(dtg)
            self._dtg_labels.append((i, s.axisName, dtg))

            sel = Factory.CoordsValue()
            self.ids.sel_box.add_widget(sel)
            self._sel_labels.append((i, s.axisName, sel))

            tool = Factory.CoordsValue()
            self.ids.tool_box.add_widget(tool)
            self._tool_labels.append((i, s.axisName, tool))

    def update_tick(self, *arg, **kv):
        self._update_values()

    def _update_values(self, *args):
        coord_bars: list[ScaleDispatcher] = self.app.scales
        h_idx = int(self.plane_h_index)
        v_idx = int(self.plane_v_index)

        for i, name, lbl in self._tool_labels:
            pos = coord_bars[i].scaledPosition
            lbl.text = f"{name}: {pos:0.3f}"

        for i, name, lbl in self._sel_labels:
            if i == h_idx:
                lbl.text = f"{name}: {self.selected_x:0.3f}"
            elif i == v_idx:
                lbl.text = f"{name}: {self.selected_y:0.3f}"
            else:
                lbl.text = f"{name}: --"

        for i, name, lbl in self._dtg_labels:
            tool_pos = coord_bars[i].scaledPosition
            if i == h_idx:
                lbl.text = f"{name}: {self.selected_x - tool_pos:0.3f}"
            elif i == v_idx:
                lbl.text = f"{name}: {self.selected_y - tool_pos:0.3f}"
            else:
                lbl.text = f"{name}: --"
