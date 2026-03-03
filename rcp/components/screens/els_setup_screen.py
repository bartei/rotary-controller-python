from kivy.logger import Logger
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

NONE_LABEL = "None"


class ElsSetupScreen(Screen):
    els = ObjectProperty()

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kv)

    def on_pre_enter(self, *args):
        axis_names = [ax.axis_name for ax in self.app.axes]
        options = [NONE_LABEL] + axis_names

        self.ids.spindle_dropdown.options = options
        self.ids.z_dropdown.options = options
        self.ids.x_dropdown.options = options

        self.ids.spindle_dropdown.value = self._index_to_name(self.els.spindle_axis_index)
        self.ids.z_dropdown.value = self._index_to_name(self.els.z_axis_index)
        self.ids.x_dropdown.value = self._index_to_name(self.els.x_axis_index)

    def on_spindle_selected(self, instance, value):
        self.els.spindle_axis_index = self._name_to_index(value)

    def on_z_selected(self, instance, value):
        self.els.z_axis_index = self._name_to_index(value)

    def on_x_selected(self, instance, value):
        self.els.x_axis_index = self._name_to_index(value)

    def _name_to_index(self, name: str) -> int:
        if name == NONE_LABEL:
            return -1
        for i, ax in enumerate(self.app.axes):
            if ax.axis_name == name:
                return i
        return -1

    def _index_to_name(self, index) -> str:
        idx = int(index)
        if 0 <= idx < len(self.app.axes):
            return self.app.axes[idx].axis_name
        return NONE_LABEL
