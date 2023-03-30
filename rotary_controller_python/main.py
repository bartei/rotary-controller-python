from decimal import Decimal
import logging
from typing import Literal

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (
    StringProperty,
    NumericProperty,
    ConfigParserProperty,
    BooleanProperty,
    ListProperty,
    DictProperty,
)
from kivy.uix.boxlayout import BoxLayout

from rotary_controller_python.utils import communication
from rotary_controller_python.config import config
from kivy.logger import Logger, ConsoleHandler

from rotary_controller_python.utils.communication import DeviceManager

log = Logger
handler = next(iter([item for item in log.handlers if type(item) == ConsoleHandler]), None)
handler.formatter = logging.Formatter(fmt="[%(levelname)s] %(module)s(%(lineno)d) %(funcName)s: %(message)s")


"""
    %(name)s            Name of the logger (logging channel)
    %(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL)
    %(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                        "WARNING", "ERROR", "CRITICAL")
    %(pathname)s        Full pathname of the source file where the logging
                        call was issued (if available)
    %(filename)s        Filename portion of pathname
    %(module)s          Module (name portion of filename)
    %(lineno)d          Source line number where the logging call was issued
                        (if available)
    %(funcName)s        Function name
    %(created)f         Time when the LogRecord was created (time.time()
                        return value)
    %(asctime)s         Textual time when the LogRecord was created
    %(msecs)d           Millisecond portion of the creation time
    %(relativeCreated)d Time in milliseconds when the LogRecord was created,
                        relative to the time the logging module was loaded
                        (typically at application startup time)
    %(thread)d          Thread ID (if available)
    %(threadName)s      Thread name (if available)
    %(process)d         Process ID (if available)
    %(message)s         The result of record.getMessage(), computed just as
                        the record is emitted
"""



class Home(BoxLayout):
    pass


class MainApp(App):
    display_color = ConfigParserProperty(defaultvalue="#ffffffff", section="formatting", key="display_color", config=config)
    metric_pos_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="metric", config=config)
    metric_speed_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="metric_speed", config=config)
    imperial_pos_format = ConfigParserProperty(defaultvalue="{:+0.4f}", section="formatting", key="imperial", config=config)
    imperial_speed_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="imperial_speed", config=config)
    angle_format = ConfigParserProperty(defaultvalue="{:+0.3f}", section="formatting", key="angle", config=config)
    pos_format = StringProperty("{}")
    speed_format = StringProperty("{}")

    address = ConfigParserProperty(defaultvalue=17, section="device", key="address", config=config, val_type=int)
    baudrate = ConfigParserProperty(defaultvalue=115200, section="device", key="baudrate", config=config, val_type=int)
    serial_port = ConfigParserProperty(defaultvalue="/dev/serial0", section="device", key="serial_port", config=config, val_type=str)

    # min_speed = ConfigParserProperty(defaultvalue="150.0", section="rotary", key="min_speed", config=config, val_type=float)
    # max_speed = ConfigParserProperty(defaultvalue="3600.0", section="rotary", key="max_speed", config=config, val_type=float)
    # acceleration = ConfigParserProperty(defaultvalue="5.0", section="rotary", key="acceleration", config=config, val_type=float)
    # ratio_num = ConfigParserProperty(defaultvalue="360", section="rotary", key="ratio_num", config=config, val_type=int)
    # ratio_den = ConfigParserProperty(defaultvalue="1600", section="rotary", key="ratio_den", config=config, val_type=int)

    divisions = NumericProperty(16)
    division_index = NumericProperty(0)
    division_offset = NumericProperty(0.0)
    index_mode = BooleanProperty(False)

    jog_speed = NumericProperty(0.1)
    jog_accel = NumericProperty(0.01)
    jog_forward = BooleanProperty(False)
    jog_backward = BooleanProperty(False)
    jog_mode = BooleanProperty(True)

    # syn_ratio_num = NumericProperty(defaultvalue=1024)
    # syn_ratio_den = NumericProperty(defaultvalue=36000)

    status = NumericProperty(0)
    blink = BooleanProperty(False)
    connected = BooleanProperty(False)
    error = BooleanProperty(False)
    rq_index_init = BooleanProperty(False)
    rq_synchro_init = BooleanProperty(False)
    mode_index = BooleanProperty(False)
    mode_synchro = BooleanProperty(False)

    current_position = NumericProperty(0)
    final_position = NumericProperty(1)

    current_units = ConfigParserProperty(defaultvalue="mm", section="global", key="current_units", config=config, val_type=str)
    abs_inc = ConfigParserProperty(defaultvalue="ABS", section="global", key="abs_inc", config=config, val_type=str)
    unit_factor = NumericProperty(1.0)
    tool = ConfigParserProperty(defaultvalue=0, section="global", key="tool", config=config, val_type=int)
    origin = ConfigParserProperty(defaultvalue=0, section="global", key="origin", config=config, val_type=int)

    device = None
    task_update_scales = None

    scale_positions = ListProperty([0, 0, 0, 0])
    scale_sync = ListProperty([False, False])
    scales = DictProperty({})
    home = Home()

    def on_current_units(self, instance, value):
        if value == "in":
            self.pos_format = self.imperial_pos_format
            self.speed_format = self.imperial_speed_format
            self.unit_factor = 25.4
        else:
            self.pos_format = self.metric_pos_format
            self.speed_format = self.metric_speed_format
            self.unit_factor = 1

    def request_syn_mode(self):
        if self.connected:
            self.device.syn_ratio_num = self.syn_ratio_num
            self.device.syn_ratio_den = self.syn_ratio_den
            self.device.status = communication.MODE_SYNCHRO_INIT

    def request_index_mode(self):
        if self.connected:
            self.device.status = communication.MODE_INDEX_INIT

    def on_syn_ratio_num(self, instance, value):
        self.device.syn_ratio_num = value

    def on_syn_ratio_den(self, instance, value):
        self.device.syn_ratio_den = value

    def blinker(self, *args):
        self.blink = not self.blink

    def enable_axis_sync(self, input_id: int, state: Literal["normal", "down"]):
        mask = communication.MODE_BIT_SYNC_INPUT_START << input_id
        if state == "normal":
            log.warning(f"Setting axis {input_id} to state OFF")
            self.device.status = communication.set_bit(self.device.status, mask=mask, value=False)

        elif state == "down":
            self.device.status = communication.set_bit(self.device.status,mask=mask, value=True)
            log.warning(f"Setting axis {input_id} to state ON")

    def update_scales(self, *args):
        if self.device is not None:
            self.scale_positions = self.device.scales
        else:
            try:
                self.device = DeviceManager(
                    serial_device="/dev/serial0",
                    baudrate=115200,
                    address=17
                )
                self.task_update_scales.timeout = 1.0 / 25
            except Exception as e:
                logging.error(e.__str__())
                self.device = None
                self.task_update_scales.timeout = 2.0
                self.scale_positions[0] += 1

    def update_fast(self, *args):
        # Skip if we got no connection
        if self.device is None or not self.device.connected:
            return
        #
        # for index, item in enumerate(self.device.scales):
        #     self.scales[str(index)] = item
        #
        # self.status = self.device.status
        # self.spindle_position = self.device.spindle_position
        # self.enable = communication.get_bit(self.status, communication.MODE_BIT_GLOBAL_ENABLE)
        # self.servo_enable = communication.get_bit(self.status, communication.MODE_BIT_SERVO_ENABLE)
        #
        # self.sync_input = [
        #     communication.get_bit(self.status, communication.MODE_BIT_SYNC_INPUT_1),
        #     communication.get_bit(self.status, communication.MODE_BIT_SYNC_INPUT_2),
        #     communication.get_bit(self.status, communication.MODE_BIT_SYNC_INPUT_3),
        #     communication.get_bit(self.status, communication.MODE_BIT_SYNC_INPUT_4),
        # ]
        #
        # self.set_encoder = communication.get_bit(self.status, communication.MODE_BIT_SYNC_INPUT_4),
        # self.rq_synchro_init = communication.get_bit(self.status, communication.MODE_BIT_RQ_SYNCHRO_INIT),
        # self.rq_index_init = communication.get_bit(self.status, communication.MODE_BIT_RQ_INDEX_INIT),
        # self.mode_synchro = communication.get_bit(self.status, communication.MODE_BIT_MODE_SYNCHRO),
        # self.mode_index = communication.get_bit(self.status, communication.MODE_BIT_MODE_INDEX),
        # end = timeit.default_timer()
        # print(end - start)

    def build(self):
        self.home = Home()
        if self.current_units == "mm":
            self.pos_format = self.metric_pos_format
            self.speed_format = self.metric_speed_format
            self.unit_factor = 1.0
        else:
            self.pos_format = self.imperial_pos_format
            self.speed_format = self.imperial_speed_format
            self.unit_factor = 25.4

        self.task_update_scales = Clock.schedule_interval(self.update_scales, 1.0 / 25)
        Clock.schedule_interval(self.blinker, 1.0 / 4)
        return self.home


if __name__ == '__main__':
    MainApp().run()
