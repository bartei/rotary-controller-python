from kivy.clock import Clock
from kivy.factory import Factory
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import NumericProperty

from rcp.dispatchers.axis import AxisDispatcher
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
        self._dtg_labels: list[tuple[int, AxisDispatcher, Label]] = []
        self._sel_labels: list[tuple[int, AxisDispatcher, Label]] = []
        self._tool_labels: list[tuple[int, AxisDispatcher, Label]] = []
        super().__init__(**kwargs)

        self._axes: list[tuple[int, AxisDispatcher]] = [
            (i, a) for i, a in enumerate(self.app.axes)
            if not a.spindleMode
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
        self._dtg_labels: list[tuple[int, AxisDispatcher, Label]] = []
        self._sel_labels: list[tuple[int, AxisDispatcher, Label]] = []
        self._tool_labels: list[tuple[int, AxisDispatcher, Label]] = []

        for i, a in self._axes:
            dtg = Factory.CoordsValue()
            self.ids.dtg_box.add_widget(dtg)
            self._dtg_labels.append((i, a, dtg))

            sel = Factory.CoordsValue()
            self.ids.sel_box.add_widget(sel)
            self._sel_labels.append((i, a, sel))

            tool = Factory.CoordsValue()
            self.ids.tool_box.add_widget(tool)
            self._tool_labels.append((i, a, tool))

    def update_tick(self, *arg, **kv):
        self._update_values()

    def _update_values(self, *args):
        h_idx = int(self.plane_h_index)
        v_idx = int(self.plane_v_index)

        for i, axis, lbl in self._tool_labels:
            pos = axis.scaledPosition
            lbl.text = f"{axis.axis_name}: {pos:0.3f}"

        for i, axis, lbl in self._sel_labels:
            if i == h_idx:
                lbl.text = f"{axis.axis_name}: {self.selected_x:0.3f}"
            elif i == v_idx:
                lbl.text = f"{axis.axis_name}: {self.selected_y:0.3f}"
            else:
                lbl.text = f"{axis.axis_name}: --"

        for i, axis, lbl in self._dtg_labels:
            tool_pos = axis.scaledPosition
            if i == h_idx:
                lbl.text = f"{axis.axis_name}: {self.selected_x - tool_pos:0.3f}"
            elif i == v_idx:
                lbl.text = f"{axis.axis_name}: {self.selected_y - tool_pos:0.3f}"
            else:
                lbl.text = f"{axis.axis_name}: --"
