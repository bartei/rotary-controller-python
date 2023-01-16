from decimal import Decimal
import logging

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

    # X Axis properties
    x_axis_encoder_ratio_num = ConfigParserProperty(
        defaultvalue=360,
        section="input1",
        key="ratio_num",
        config=config,
        val_type=int,
    )
    x_axis_encoder_ratio_den = ConfigParserProperty(
        defaultvalue=1024,
        section="input1",
        key="ratio_den",
        config=config,
        val_type=int,
    )

    y_axis_encoder_ratio_num = ConfigParserProperty(
        defaultvalue=360,
        section="input2",
        key="ratio_num",
        config=config,
        val_type=int,
    )
    y_axis_encoder_ratio_den = ConfigParserProperty(
        defaultvalue=1024,
        section="input2",
        key="ratio_den",
        config=config,
        val_type=int,
    )

    z_axis_encoder_ratio_num = ConfigParserProperty(
        defaultvalue=360,
        section="input3",
        key="ratio_num",
        config=config,
        val_type=int,
    )
    z_axis_encoder_ratio_den = ConfigParserProperty(
        defaultvalue=1024,
        section="input3",
        key="ratio_den",
        config=config,
        val_type=int,
    )

    a_axis_encoder_ratio_num = ConfigParserProperty(
        defaultvalue=360,
        section="input4",
        key="ratio_num",
        config=config,
        val_type=int,
    )
    a_axis_encoder_ratio_den = ConfigParserProperty(
        defaultvalue=1024,
        section="input4",
        key="ratio_den",
        config=config,
        val_type=int,
    )

    x_axis = NumericProperty(10)
    y_axis = NumericProperty(20)
    z_axis = NumericProperty(20)
    a_axis = NumericProperty(30)

    desired_position = NumericProperty(0.0)
    current_position = NumericProperty(0.0)

    divisions = NumericProperty(16)
    division_index = NumericProperty(0)
    division_offset = NumericProperty(0.0)
    index_mode = BooleanProperty(False)

    jog_speed = NumericProperty(0.1)
    jog_accel = NumericProperty(0.01)
    jog_forward = BooleanProperty(False)
    jog_backward = BooleanProperty(False)
    jog_mode = BooleanProperty(True)

    syn_ratio_num = NumericProperty(defaultvalue=1024)
    syn_ratio_den = NumericProperty(defaultvalue=36000)

    mode = NumericProperty(0)
    blink = BooleanProperty(False)
    connected = BooleanProperty(False)

    current_units = StringProperty("mm")
    current_origin = StringProperty("Origin 0")

    device = None
    home = None

    # def set_current_position(self, *args, **kwargs):
    #     print(args)
    #     print(kwargs)
    #     # if self.connected:
    #     #     new_position = int(float(value) / float(self.ratio_den) * float(self.ratio_num))
    #     #     self.device.current_position = new_position
    #     #     log.warning(f"Setting current position for device to: {new_position} , {float(self.ratio_den)}, {float(self.ratio_num)}")

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

    def set_sync_numerator(self, value):
        self.syn_ratio_num = abs(int(value))

    def set_sync_denominator(self, value):
        self.syn_ratio_den = int(value)

    def set_new_x(self, value):
        log.warning(f"Set New X to: {value}")
        decimal_value = Decimal(self.x_axis_encoder_ratio_den) / Decimal(self.x_axis_encoder_ratio_num) * Decimal(value)
        int_value = int(decimal_value)
        log.warning(f"Raw value set to to: {int_value}")
        if self.connected:
            self.device.encoder_preset_index = 0
            self.device.encoder_preset_value = int_value

            self.device.mode = communication.MODE_SET_ENCODER
        else:
            log.error("Device disconnected, cannot set encoder value")

    def set_new_y(self, value):
        log.warning(f"Set New Y to: {value}")
        decimal_value = Decimal(self.y_axis_encoder_ratio_den) / Decimal(self.y_axis_encoder_ratio_num) * Decimal(value)
        int_value = int(decimal_value)
        log.warning(f"Raw value set to to: {int_value}")
        if self.connected:
            self.device.encoder_preset_index = 1
            self.device.encoder_preset_value = int_value

            self.device.mode = communication.MODE_SET_ENCODER
        else:
            log.error("Device disconnected, cannot set encoder value")

    def set_new_z(self, value):
        log.warning(f"Set New Z to: {value}")
        decimal_value = Decimal(self.z_axis_encoder_ratio_den) / Decimal(self.z_axis_encoder_ratio_num) * Decimal(value)
        int_value = int(decimal_value)
        log.warning(f"Raw value set to to: {int_value}")
        if self.connected:
            self.device.encoder_preset_index = 2
            self.device.encoder_preset_value = int_value

            self.device.mode = communication.MODE_SET_ENCODER
        else:
            log.error("Device disconnected, cannot set encoder value")
        pass

    def update_desired_position(self, *args, **kwargs):
        if not self.divisions > 0:
            self.divisions = 1

        self.desired_position = 360 / self.divisions * self.division_index + self.division_offset
        # self.division_index = self.division_index % self.divisions
        return True

    def update(self, *args, **kwargs):
        if self.device is not None:
            scales = self.device.scales
            if self.x_axis_encoder_ratio_den != 0:
                self.x_axis = float(scales[0]) * float(self.x_axis_encoder_ratio_num) / float(self.x_axis_encoder_ratio_den)
            else:
                self.x_axis = 0

            if self.y_axis_encoder_ratio_den != 0:
                self.y_axis = float(scales[1]) * float(self.y_axis_encoder_ratio_num) / float(self.y_axis_encoder_ratio_den)
            else:
                self.y_axis = 0

            if self.z_axis_encoder_ratio_den != 0:
                self.z_axis = float(scales[2]) * float(self.z_axis_encoder_ratio_num) / float(self.z_axis_encoder_ratio_den)
            else:
                self.z_axis = 0

            if self.a_axis_encoder_ratio_den != 0:
                self.a_axis = float(scales[3]) * float(self.a_axis_encoder_ratio_num) / float(self.a_axis_encoder_ratio_den)
            else:
                self.a_axis = 0

            self.current_position = self.device.current_position * self.ratio_num / self.ratio_den

            if not self.device.connected:
                self.mode = communication.MODE_DISCONNECTED
            else:
                self.mode = self.device.mode
        else:
            self.mode = communication.MODE_DISCONNECTED

    def on_desired_position(self, instance, value):
        if self.connected:
            # Always send out the motion settings
            self.device.min_speed = self.min_speed
            self.device.max_speed = self.max_speed
            self.device.acceleration = self.acceleration
            self.device.ratio_num = self.ratio_num
            self.device.ratio_den = self.ratio_den
            self.device.mode = 0
            # Send the destination converted to steps
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

    def request_syn_mode(self):
        if self.connected:
            self.device.syn_ratio_num = self.syn_ratio_num
            self.device.syn_ratio_den = self.syn_ratio_den
            self.device.mode = communication.MODE_SYNCHRO_INIT

    def request_index_mode(self):
        if self.connected:
            self.device.mode = communication.MODE_INDEX_INIT

    def on_syn_ratio_num(self, instance, value):
        self.device.syn_ratio_num = value

    def on_syn_ratio_den(self, instance, value):
        self.device.syn_ratio_den = value

    def blinker(self, *args):
        self.blink = not self.blink

    def configure_device(self, *args):
        try:
            self.device = communication.DeviceManager()
        except Exception as e:
            # Retry in 5 seconds if the connection failed
            Clock.schedule_once(self.configure_device, timeout=5)
            log.warning("Retrying to connect in 5 seconds")
            self.device = None
            log.error(e.__str__())

        # Initialize parameters on the firmware
        if self.device is not None:
            self.device.ratio_num = self.ratio_num
            self.device.ratio_den = self.ratio_den
            self.device.acceleration = self.acceleration
            self.device.max_speed = self.max_speed
            self.device.min_speed = self.min_speed
            self.connected = self.device.connected
            log.warning(f"Device connection: {self.device.connected}")
        else:
            self.connected = False

    def build(self):
        self.home = Home()
        self.bind(divisions=self.update_desired_position)
        self.bind(division_index=self.update_desired_position)
        self.bind(division_offset=self.update_desired_position)

        # Configure the modbus communication
        self.configure_device()

        Clock.schedule_interval(self.update, 1.0 / 25)
        Clock.schedule_interval(self.blinker, 1.0 / 4)
        return self.home


if __name__ == '__main__':
    MainApp().run()
