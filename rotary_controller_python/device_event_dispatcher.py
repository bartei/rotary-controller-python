import logging
import timeit

from kivy.event import EventDispatcher
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, ConfigParserProperty, DictProperty, ListProperty, \
    BooleanProperty

from rotary_controller_python.utils import communication
from rotary_controller_python.config import config

log = logging.getLogger(__name__)


class DeviceEventDispatcher(EventDispatcher):
    refresh_task = None
    refresh_interval = NumericProperty(1)
    device: communication.DeviceManager = ObjectProperty(None)

    address = ConfigParserProperty(defaultvalue=17, section="device", key="address", config=config, val_type=int)
    baudrate = ConfigParserProperty(defaultvalue=115200, section="device", key="baudrate", config=config, val_type=int)
    serial_port = ConfigParserProperty(defaultvalue="/dev/serial0", section="device", key="serial_port", config=config, val_type=str)

    status = NumericProperty(0)
    acceleration = NumericProperty(0)
    current_position = NumericProperty(0)
    current_speed = NumericProperty(0)
    encoder_preset_index = NumericProperty(0)
    encoder_preset_value = NumericProperty(0)
    final_position = NumericProperty(0)
    max_speed = NumericProperty(0)
    min_speed = NumericProperty(0)
    ratio_num = NumericProperty(0)
    ratio_den = NumericProperty(0)
    spindle_position = NumericProperty(0)
    syn_ratio_num = NumericProperty(0)
    syn_ratio_den = NumericProperty(0)
    position = ListProperty([0, 0, 0, 0, ])

    enable = BooleanProperty(False)
    servo_enable = BooleanProperty(False)
    sync_input = ListProperty([False, False, False, False])
    set_encoder = BooleanProperty(False)
    rq_synchro_init = BooleanProperty(False)
    rq_index_init = BooleanProperty(False)
    mode_index = BooleanProperty(False)
    mode_synchro = BooleanProperty(False)
    connected = BooleanProperty(True)
    error = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_task = Clock.schedule_interval(self.refresh, timeout=self.refresh_interval)

    def refresh(self, instance, **kwargs):
        # Create a device if needed
        start = timeit.default_timer()
        if self.device is None:
            try:
                self.device = communication.DeviceManager(
                    serial_device=self.serial_port,
                    baudrate=self.baudrate,
                    address=17,
                    debug=False
                )
                self.refresh_task.timeout = 0.1
                self.connected = True
            except Exception as e:
                log.error(e, exc_info=True)
                self.device = None
                self.refresh_task.timeout = 2.0
                self.connected = False
                self.mode_synchro = not self.mode_synchro
                self.position = [
                    self.position[0] + 0.01,
                    self.position[1] + 0.02,
                    self.position[2] + 0.03,
                    self.position[3] + 0.04,
                ]

        # Skip if we got no connection
        if self.device is None or not self.device.connected:
            return

        self.current_position = self.device.current_position
        self.status = self.device.status
        # self.spindle_position = self.device.spindle_position
        self.position = self.device.scales
        # self.enable = communication.get_bit(self.status, communication.MODE_BIT_GLOBAL_ENABLE)
        # self.servo_enable = communication.get_bit(self.status, communication.MODE_BIT_SERVO_ENABLE)

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
        end = timeit.default_timer()
        print(end-start)

    def set_encoder_value(self, encoder_index: int, encoder_value: int):
        log.warning(f"Set New position for input {encoder_index} to {encoder_value}")
        if self.device is not None and self.device.connected and not self.set_encoder:
            self.device.encoder_preset_index = encoder_index
            self.device.encoder_preset_value = encoder_value
            self.device.status = communication.set_bit(
                self.device.status,
                mask=communication.MODE_BIT_SET_ENCODER,
                value=True
            )

    def set_sync(self, encoder_index: int, sync_status: bool):
        log.error(f"Updating sync for axis {encoder_index}: {sync_status}")
        if self.device is not None and self.device.connected:
            self.device.status = communication.set_bit(
                self.device.status,
                mask=communication.MODE_BIT_SYNC_INPUT_START << encoder_index,
                value=sync_status
            )

    def on_final_position(self, instance, value):
        if self.device is None:
            log.error("Cannot update desired position, device not connected")
            self.current_position = value
            return
        try:
            log.warning(f"Update desired position to: {value}")
            self.device.min_speed = self.min_speed
            self.device.max_speed = self.max_speed
            self.device.acceleration = self.acceleration
            self.device.ratio_num = self.ratio_num
            self.device.ratio_den = self.ratio_den
            # Send the destination converted to steps
            self.device.final_position = int(value / self.ratio_num * self.ratio_den)
            self.device.request_index()
        except Exception as e:
            log.exception(e.__str__())
