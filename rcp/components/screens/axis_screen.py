from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.screenmanager import Screen

from rcp.dispatchers.axis_transform import AxisTransform, TransformType
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

TRANSFORM_TYPE_LABELS = {
    TransformType.IDENTITY: "Identity",
    TransformType.SUM: "Sum",
}

LABEL_TO_TRANSFORM_TYPE = {v: k for k, v in TRANSFORM_TYPE_LABELS.items()}


class AxisScreen(Screen):
    axis = ObjectProperty()

    # Editable fields mirroring current transform config
    transform_type_label = StringProperty("Identity")
    input_0 = StringProperty("Input 0")
    input_1 = StringProperty("Input 1")
    input_0_options = ListProperty()
    input_1_options = ListProperty()

    def __init__(self, **kv):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kv)
        self.bind(input_0=self._update_input_options)
        self.bind(transform_type_label=self._update_input_options)

    def _all_scale_labels(self):
        return [f"Input {i}" for i in range(len(self.app.scales))]

    def _label_to_index(self, label):
        try:
            return int(label.split()[-1])
        except (ValueError, IndexError, AttributeError):
            return 0

    def _update_input_options(self, *args):
        all_labels = self._all_scale_labels()
        self.input_0_options = all_labels
        if self.transform_type_label == "Sum":
            self.input_1_options = [l for l in all_labels if l != self.input_0]
            if self.input_1 not in self.input_1_options and self.input_1_options:
                self.input_1 = self.input_1_options[0]
        else:
            self.input_1_options = all_labels

    def on_pre_enter(self, *args):
        """Sync UI fields from the current axis transform when entering."""
        if self.axis is None:
            return
        t = self.axis.transform
        self.transform_type_label = TRANSFORM_TYPE_LABELS.get(t.transform_type, "Identity")
        if t.contributions:
            self.input_0 = f"Input {t.contributions[0]}"
        if len(t.contributions) > 1:
            self.input_1 = f"Input {t.contributions[1]}"
        self._update_input_options()

    def apply_transform(self):
        """Build an AxisTransform from the current UI field values and apply it."""
        tt = LABEL_TO_TRANSFORM_TYPE.get(self.transform_type_label, TransformType.IDENTITY)
        idx0 = self._label_to_index(self.input_0)
        idx1 = self._label_to_index(self.input_1)

        if tt == TransformType.SUM:
            transform = AxisTransform.sum(idx0, idx1)
        else:
            transform = AxisTransform.identity(idx0)

        self.axis.transform = transform
        log.info(f"Applied transform: {tt.value} to axis '{self.axis.axis_name}'")

    def remove_axis(self):
        """Remove this axis from the board, clean up this screen, and go back."""
        if len(self.app.axes) <= 1:
            log.warning("Cannot remove the last axis")
            return
        self.app.board.remove_axis(self.axis)
        self.app.axes = list(self.app.board.axes)
        self.app.manager.back()
        self.app.manager.remove_widget(self)
