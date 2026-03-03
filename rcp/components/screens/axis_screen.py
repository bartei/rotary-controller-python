from fractions import Fraction

from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.uix.screenmanager import Screen

from rcp.dispatchers.axis_transform import AxisTransform, TransformType
from rcp.utils.kv_loader import load_kv

log = Logger.getChild(__name__)
load_kv(__file__)

TRANSFORM_TYPE_LABELS = {
    TransformType.IDENTITY: "Identity",
    TransformType.SCALING: "Scaling",
    TransformType.WEIGHTED_SUM: "Weighted Sum",
    TransformType.ANGLE_COS: "Angle Cos",
    TransformType.ANGLE_SIN: "Angle Sin",
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
    weight_num = NumericProperty(1)
    weight_den = NumericProperty(1)
    weight_1_num = NumericProperty(1)
    weight_1_den = NumericProperty(1)
    angle_degrees = NumericProperty(45)

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
        if self.transform_type_label == "Weighted Sum":
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
            c0 = t.contributions[0]
            self.input_0 = f"Input {c0.input_index}"
            self.weight_num = c0.weight.numerator
            self.weight_den = c0.weight.denominator
        if len(t.contributions) > 1:
            c1 = t.contributions[1]
            self.input_1 = f"Input {c1.input_index}"
            self.weight_1_num = c1.weight.numerator
            self.weight_1_den = c1.weight.denominator
        self.angle_degrees = t.angle_degrees
        self._update_input_options()

    def apply_transform(self):
        """Build an AxisTransform from the current UI field values and apply it."""
        tt = LABEL_TO_TRANSFORM_TYPE.get(self.transform_type_label, TransformType.IDENTITY)
        idx0 = self._label_to_index(self.input_0)
        idx1 = self._label_to_index(self.input_1)

        if tt == TransformType.IDENTITY:
            transform = AxisTransform.identity(idx0)
        elif tt == TransformType.SCALING:
            den = int(self.weight_den) or 1
            transform = AxisTransform.scaling(idx0, Fraction(int(self.weight_num), den))
        elif tt == TransformType.WEIGHTED_SUM:
            den0 = int(self.weight_den) or 1
            den1 = int(self.weight_1_den) or 1
            transform = AxisTransform.weighted_sum([
                (idx0, Fraction(int(self.weight_num), den0)),
                (idx1, Fraction(int(self.weight_1_num), den1)),
            ])
        elif tt == TransformType.ANGLE_COS:
            transform = AxisTransform.angle_projection(idx0, float(self.angle_degrees), use_cos=True)
        elif tt == TransformType.ANGLE_SIN:
            transform = AxisTransform.angle_projection(idx0, float(self.angle_degrees), use_cos=False)
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
