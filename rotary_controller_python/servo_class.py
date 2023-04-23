from loguru import logger as log

from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty, BooleanProperty

from rotary_controller_python.utils import communication
from rotary_controller_python.components.appsettings import config


class ServoClass(EventDispatcher):
    section_name = "rotary"
    name = StringProperty("N")
    min_speed = NumericProperty(150.0)
    max_speed = NumericProperty(3600.0)
    acceleration = NumericProperty(5.0)
    ratio_num = NumericProperty(360)
    ratio_den = NumericProperty(36000)

    current_position = NumericProperty(0.0)
    desired_position = NumericProperty(0.0)

    # Offset to add to the sync and index calculated values
    offset = NumericProperty(0.0)
    divisions = NumericProperty(16)
    index = NumericProperty(0)
    enable = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_default_config_section()
        config.add_callback(callback=self.read_all_config_values)

    def create_default_config_section(self):
        if not config.has_section(self.section_name):
            config.add_section(self.section_name)

        config.setdefaults(section=self.section_name, keyvalues=dict(
            name="N",
            min_speed=1,
            max_speed=3600,
            acceleration=0.1,
            ratio_num=360,
            ratio_den=36000,
            offset=0.0,
            divisions=10,
            index=0,
        ))
        config.write()

    def read_all_config_values(self, *args, **kwargs):
        self.name = config.get(section=self.section_name, option="name")
        self.min_speed = config.getint(section=self.section_name, option="min_speed")
        self.max_speed = config.getint(section=self.section_name, option="max_speed")
        self.acceleration = config.getint(section=self.section_name, option="acceleration")
        self.ratio_num = config.getint(section=self.section_name, option="ratio_num")
        self.ratio_den = config.get(section=self.section_name, option="ratio_den")
        self.offset = config.get(section=self.section_name, option="offset")
        self.divisions = config.get(section=self.section_name, option="divisions")
        self.index = config.get(section=self.section_name, option="index")

    def on_ratio_num(self, instance, value):
        config.set(section=self.section_name, option="ratio_num", value=value)
        config.write()

    def on_ratio_den(self, instance, value):
        config.set(section=self.section_name, option="ratio_den", value=value)
        config.write()

    def on_offset(self, instance, value):
        config.set(section=self.section_name, option="offset", value=value)
        config.write()

    def on_divisions(self, instance, value):
        config.set(section=self.section_name, option="divisions", value=value)
        config.write()

    def on_desired_position(self, instance, value):
        from kivy.app import App
        app = App.get_running_app()
        if app.device is None:
            return
        try:
            log.warning(f"Update desired position to: {value}")
            app.device.min_speed = self.min_speed
            app.device.max_speed = self.max_speed
            app.device.acceleration = self.acceleration
            app.device.ratio_num = self.ratio_num
            app.device.ratio_den = self.ratio_den
            # app.device.mode = communication.MODE_HALT

            # Send the destination converted to steps
            current_position = app.device.current_position * self.ratio_num / self.ratio_den
            final_position = value
            delta = final_position - current_position
            if abs(delta) > 180.0:
                delta = 360 - delta

            index_delta_steps = int(delta / self.ratio_num * self.ratio_den)
            app.device.index_delta_steps = index_delta_steps
            app.device.mode = communication.MODE_SYNCHRO_INIT
        except Exception as e:
            log.exception(e.__str__())
        return True

    def on_index(self, instance, value):
        config.set(section=self.section_name, option="index", value=value)
        config.write()

        if self.divisions != 0:
            self.desired_position = 360.0 / self.divisions * self.index + self.offset
        else:
            log.error("Divisions must be != 0")
        return True
