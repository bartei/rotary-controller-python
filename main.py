import logging
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ConfigParserProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout

from components.appsettings import config
from utils import communication

log = logging.getLogger(__file__)


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
    current_units = StringProperty("mm")
    current_origin = StringProperty("Origin 0")
    x_axis = NumericProperty(10)
    y_axis = NumericProperty(20)
    z_axis = NumericProperty(20)

    in_motion = BooleanProperty(False)
    motion_enable = BooleanProperty(False)  # Normal = False, down = True

    desired_position = NumericProperty(0.0)
    current_position = NumericProperty(0.0)

    divisions = NumericProperty(16)
    division_index = NumericProperty(0)
    division_offset = NumericProperty(0.0)

    jog_speed = NumericProperty(0.1)
    jog_accel = NumericProperty(0.01)
    jog_forward = BooleanProperty(False)
    jog_backward = BooleanProperty(False)

    # device = communication.DeviceManager()
    home = None

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

    def set_jog_speed(self, value):
        self.jog_speed = value

    def set_jog_accel(self, value):
        self.jog_accel = value

    def update_desired_position(self, *args, **kwargs):
        if not self.divisions > 0:
            self.divisions = 1

        self.desired_position = 360 / self.divisions * self.division_index + self.division_offset
        self.division_index = self.division_index % self.divisions
        return True

    def update(self, *args, **kwargs):
        if (abs(self.current_position - self.desired_position) > 0.1) and self.motion_enable:
            self.in_motion = True
        else:
            self.in_motion = False

        print(self.jog_backward, self.jog_forward)

    def on_desired_position(self, instance, value):
        pass
        # self.device.set_final_position(value)

    def on_motion_enable(self, instance, value):
        log.info("Motion enable status: {}".format(self.motion_enable))
        pass

    def build(self):
        self.home = Home()
        self.bind(divisions=self.update_desired_position)
        self.bind(division_index=self.update_desired_position)
        self.bind(division_offset=self.update_desired_position)
        Clock.schedule_interval(self.update, 1.0 / 10)
        return self.home


if __name__ == '__main__':
    MainApp().run()
