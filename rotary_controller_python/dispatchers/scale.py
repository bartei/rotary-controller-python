from kivy.properties import NumericProperty, StringProperty
from loguru import logger as log
from rotary_controller_python.dispatchers import SavingDispatcher


class InputClass(SavingDispatcher):
    input_index = NumericProperty(0)
    axis_name = StringProperty("NN")
    ratio_num = NumericProperty(1)
    ratio_den = NumericProperty(200)
    sync_num = NumericProperty(100)
    sync_den = NumericProperty(360)
    sync_enable = StringProperty("normal")
    position = NumericProperty(111.000)

    _skip_save = ["position"]

    def __init__(self, input_index, device, **kv):
        self.device = device
        super().__init__(*kv)

    def on_sync_enable(self, instance, value):
        if value == "down":
            self.device.scales[instance.input_index].sync_motion = True
        else:
            self.device.scales[instance.input_index].sync_motion = False

    def on_sync_num(self, instance, value):
        self.device.scales[instance.input_index].sync_ratio_num = int(value)

    def on_sync_den(self, instance, value):
        self.device.scales[instance.input_index].sync_ratio_den = int(value)

    @property
    def set_position(self):
        return 0

    @set_position.setter
    def set_position(self, value):
        try:
            self.device.scales[self.input_index].position = int(value) * 1000
            log.warning(f"Set New position to: {value} for {self.input_index}")
        except Exception as e:
            log.exception(e.__str__())
            self.position = 9999.99
