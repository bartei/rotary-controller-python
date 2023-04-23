from decimal import Decimal
from loguru import logger as log

from kivy.app import App
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty
from rotary_controller_python.utils import communication

from rotary_controller_python.components.appsettings import config


class InputClass(EventDispatcher):
    input_index = NumericProperty(0, options={'force': True, 'allownone': True, 'min': None, 'max': None, 'step': 1})
    section_name = StringProperty("input0")
    axis_name = StringProperty("NN")
    ratio_num = NumericProperty(1, options={'force': True, 'allownone': True, 'min': None, 'max': None, 'step': 1})
    ratio_den = NumericProperty(1, options={'force': True, 'allownone': True, 'min': None, 'max': None, 'step': 1})
    sync_num = NumericProperty(1, options={'force': True, 'allownone': True, 'min': None, 'max': None, 'step': 1})
    sync_den = NumericProperty(1, options={'force': True, 'allownone': True, 'min': None, 'max': None, 'step': 1})
    sync_enable = StringProperty("normal")
    position = NumericProperty(123.123)

    def __init__(self, input_index: int, **kwargs):
        super().__init__(**kwargs)
        self.input_index = input_index
        self.section_name = f"input{self.input_index}"

        self.create_default_config_section()
        self.read_all_config_values()
        config.add_callback(callback=self.read_all_config_values)

    def create_default_config_section(self):
        if not config.has_section(self.section_name):
            config.add_section(self.section_name)

        config.setdefaults(section=self.section_name, keyvalues=dict(
            axis_name="N",
            ratio_num=1,
            ratio_den=1,
            sync_num=1,
            sync_den=1,
            sync_enable="normal"
        ))
        config.write()

    def read_all_config_values(self, *args, **kwargs):
        self.axis_name = config.get(section=self.section_name, option="axis_name")
        self.ratio_num = config.getint(section=self.section_name, option="ratio_num")
        self.ratio_den = config.getint(section=self.section_name, option="ratio_den")
        self.sync_num = config.getint(section=self.section_name, option="sync_num")
        self.sync_den = config.getint(section=self.section_name, option="sync_den")
        self.sync_enable = config.get(section=self.section_name, option="sync_enable")

    def on_axis_name(self, instance, value):
        config.set(section=self.section_name, option="axis_name", value=value)
        config.write()

    def on_ratio_num(self, instance, value):
        config.set(section=self.section_name, option="ratio_num", value=int(value))
        config.write()

    def on_ratio_den(self, instance, value):
        config.set(section=self.section_name, option="ratio_den", value=int(value))
        config.write()

    def on_sync_enable(self, instance, value):
        config.set(section=self.section_name, option="sync_enable", value=value)
        config.write()
        app = App.get_running_app()
        if app is None:
            return

        if value == "down":
            for data_instance in app.data:
                if data_instance.input_index != instance.input_index:
                    data_instance.sync_enable = "normal"
                else:
                    pass

            if app.device is None:
                return

            app.device.syn_scale_index = instance.input_index
            app.device.syn_ratio_num = instance.sync_num
            app.device.syn_ratio_den = instance.sync_den
            app.device.mode = communication.MODE_SYNCHRO_INIT
            log.info(f"Setting syn scale index to: {instance.input_index}")
        else:
            if app.device is None:
                return
            app.device.mode = communication.MODE_HALT

    def on_sync_num(self, instance, value):
        app = App.get_running_app()
        config.set(section=self.section_name, option="sync_num", value=int(value))
        config.write()
        if instance.sync_enable == "down":
            app.device.syn_ratio_num = value
            app.device.mode = communication.MODE_SYNCHRO_INIT

    def on_sync_den(self, instance, value):
        app = App.get_running_app()
        config.set(section=self.section_name, option="sync_den", value=int(value))
        config.write()
        if instance.sync_enable == "down":
            app.device.syn_ratio_den = value
            app.device.mode = communication.MODE_SYNCHRO_INIT

    @property
    def update_raw_scale(self):
        return 0

    @update_raw_scale.setter
    def update_raw_scale(self, value):
        if self.ratio_den != 0:
            self.position = float(value) * float(self.ratio_num) / float(self.ratio_den)
        else:
            self.position = 0

    @property
    def set_position(self):
        return 0

    @set_position.setter
    def set_position(self, value):
        try:
            app = App.get_running_app()
            if app.device is None:
                return

            log.warning(f"Set New position to: {value} for {self.input_index}")
            decimal_value = Decimal(self.ratio_den) / Decimal(self.ratio_num) * Decimal(value)
            int_value = int(decimal_value)
            log.warning(f"Raw value set to to: {int_value}")
            app.device.encoder_preset_index = self.input_index
            app.device.encoder_preset_value = int_value
            app.device.mode = communication.MODE_SET_ENCODER
        except Exception as e:
            log.exception(e.__str__())
            self.position = 9999.99
