import os

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ConfigParserProperty
from kivy.uix.boxlayout import BoxLayout

from components.appsettings import config
from utils import communication


class Home(BoxLayout):
    pass


class MainApp(App):
    display_color = ConfigParserProperty(
        defaultvalue="#ffffffff",
        section="formatting",
        key="display_color",
        config=config
    )
    metric_pos_format = ConfigParserProperty(
        defaultvalue="{:+0.3f}",
        section="formatting",
        key="metric",
        config=config
    )
    metric_speed_format = ConfigParserProperty(
        defaultvalue="{:+0.3f}",
        section="formatting",
        key="metric_speed",
        config=config
    )
    imperial_pos_format = ConfigParserProperty(
        defaultvalue="{:+0.4f}",
        section="formatting",
        key="imperial",
        config=config
    )
    imperial_speed_format = ConfigParserProperty(
        defaultvalue="{:+0.3f}",
        section="formatting",
        key="imperial_speed",
        config=config
    )
    angle_format = ConfigParserProperty(
        defaultvalue="{:+0.3f}",
        section="formatting",
        key="angle",
        config=config
    )

    min_speed = ConfigParserProperty(
        defaultvalue="150.0",
        section="rotary",
        key="min_speed",
        config=config,
        val_type=float,
    )
    max_speed = ConfigParserProperty(
        defaultvalue="3600.0",
        section="rotary",
        key="max_speed",
        config=config,
        val_type=float,
    )
    acceleration = ConfigParserProperty(
        defaultvalue="5.0",
        section="rotary",
        key="acceleration",
        config=config,
        val_type=float,
    )
    ratio_num = ConfigParserProperty(
        defaultvalue="360",
        section="rotary",
        key="ratio_num",
        config=config,
        val_type=int,
    )
    ratio_den = ConfigParserProperty(
        defaultvalue="1600",
        section="rotary",
        key="ratio_den",
        config=config,
        val_type=int,
    )

    current_units = StringProperty("mm")
    current_origin = StringProperty("Origin 0")
    x_axis = NumericProperty(10)
    y_axis = NumericProperty(20)
    z_axis = NumericProperty(20)

    desired_position = NumericProperty(0.0)
    current_position = NumericProperty(0.0)

    divisions = NumericProperty(16)
    division_index = NumericProperty(0)
    division_offset = NumericProperty(0.0)

    device = communication.DeviceManager()

    def set_current_position(self, value):
        self.current_position = value

    def set_desired_position(self, value):
        self.desired_position = value

    def set_division_offset(self, value):
        self.division_offset = value

    def set_division_index(self, value):
        self.division_index = value

    def set_divisions(self, value):
        self.divisions = value

    def update_desired_position(self, *args, **kwargs):
        self.desired_position = 360 / self.divisions * self.division_index + self.division_offset
        # self.division_index = self.division_index % self.divisions
        return True

    def update(self, *args, **kwargs):
        self.x_axis = self.device.x_position
        self.current_position = self.device.current_position * self.ratio_num / self.ratio_den

    def on_desired_position(self, instance, value):
        self.device.final_position = int(value / self.ratio_num * self.ratio_den)

    def on_ratio_num(self, instance, value):
        self.device.ratio_num = value

    def on_ratio_den(self, instance, value):
        self.device.ratio_den = value

    def on_acceleration(self, instance, value):
        self.device.acceleration = float(value)

    def on_min_speed(self, instance, value):
        self.device.min_speed = float(value)

    def on_max_speed(self, instance, value):
        self.device.max_speed = float(value)

    def build(self):
        home = Home()
        self.bind(divisions=self.update_desired_position)
        self.bind(division_index=self.update_desired_position)
        self.bind(division_offset=self.update_desired_position)
        self.device.ratio_num = self.ratio_num
        self.device.ratio_den = self.ratio_den
        self.device.acceleration = self.acceleration
        self.device.max_speed = self.max_speed
        self.device.min_speed = self.min_speed
        Clock.schedule_interval(self.update, 1.0 / 25)
        return home


if __name__ == '__main__':
    MainApp().run()
