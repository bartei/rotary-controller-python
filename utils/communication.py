from enum import Enum

import minimalmodbus
import logging
import struct
import ctypes


log = logging.getLogger(__file__)

# typedef struct {
# 0    uint16_t mode;
# 2    int32_t current_position;
# 4    int32_t final_position;
# 6    int16_t spindle_position;
# 8    int32_t x_position;
# 10    uint16_t acc;
# 12    int32_t step;
# 14    int32_t total_steps;
# 16    float max_speed;
# 18    float min_speed;
# 20    float current_speed;
# 22    float acceleration;
# 24    int32_t step_ratio_num;
# 26    int32_t step_ratio_den;
# 28    float step_ratio;
# 30    int32_t syn_ratio_num;
# 32    int32_t syn_ratio_den;
# 34    controller_status_t status;
# 36    controller_control_t control;
# } rotary_controller_t;

REG_MODE = 0
REG_CURRENT_POSITION = 2
REG_FINAL_POSITION = 4
REG_SPINDLE_POSITION = 6
REG_X_POSITION = 8
REG_STEP = 12
REG_TOTAL_STEPS = 14
REG_MAX_SPEED = 16
REG_MIN_SPEED = 18
REG_CURRENT_SPEED = 20
REG_ACCELERATION = 22
REG_RATIO_NUM = 24
REG_RATIO_DEN = 26
REG_STEP_RATIO = 28
REG_SYN_RATIO_NUM = 30
REG_SYN_RATIO_DEN = 32
REG_CTRL_STATUS = 34
REG_CTRL_CONTROL = 36


class ControllerStatus(ctypes.BigEndianStructure):
    """
    unsigned int ready : 1;
    unsigned int alarm : 1;
    unsigned int run_index : 1;
    unsigned int run_sync : 1;
    unsigned int unused : 12;
    """
    _fields_ = [
        ("unused", ctypes.c_uint32, 12),
        ("run_sync", ctypes.c_uint32, 1),
        ("run_index", ctypes.c_uint32, 1),
        ("alarm", ctypes.c_uint32, 1),
        ("ready", ctypes.c_uint32, 1),
    ]


class ControllerControl(ctypes.BigEndianStructure):
    """
    unsigned int reset : 1;
    unsigned int emergency : 1;
    unsigned int enable : 1;
    unsigned int request_sync_init: 1;
    unsigned int unused : 12;
    """
    _fields_ = [
        ("unused", ctypes.c_uint32, 12),
        ("request_sync_init", ctypes.c_uint32, 1),
        ("enable", ctypes.c_uint32, 1),
        ("emergency", ctypes.c_uint32, 1),
        ("reset", ctypes.c_uint32, 1),
    ]


class DeviceMode(Enum):
    OFF = 0
    DIRECT = 1
    DIVIDE = 2
    DIVIDE_SYNC = 3


class DeviceManager:
    def __init__(self, serial_device="/dev/serial0", baudrate=57600, address=17, debug=False):
        self.device: minimalmodbus.Instrument = minimalmodbus.Instrument(
            port=serial_device,
            slaveaddress=address,
            debug=debug
        )
        self.device.serial.baudrate = baudrate

    @property
    def status(self) -> ControllerStatus:
        try:
            value = self.device.read_long()
            value = self.device.read_register(REG_CTRL_STATUS)
            cs = ControllerStatus()
            struct.pack_into(
                '!H',
                cs,
                0,
                value
            )

            return cs
        except Exception as e:
            # Log error at debug level with stack trace
            log.debug(e.__str__(), stack_info=True)
            cs = ControllerStatus()
            return cs

    @property
    def control(self) -> ControllerControl:
        try:
            value = self.device.read_long(
                REG_CTRL_CONTROL,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=False
            )
            # value = self.device.read_register(REG_CTRL_CONTROL)
            cs = ControllerControl()
            struct.pack_into(
                '!H',
                cs,
                0,
                value
            )
            return cs
        except Exception as e:
            # Log error at debug level with stack trace
            log.debug(e.__str__(), stack_info=True)
            cs = ControllerControl()
            return cs

    @control.setter
    def control(self, value: ControllerControl):
        try:
            cs_value, = struct.unpack_from('!H', value)
            self.device.write_long(
                REG_CTRL_CONTROL,
                cs_value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            # self.device.write_register(
            #     REG_CTRL_CONTROL,
            #     cs_value,
            # )
        except Exception as e:
            log.exception(e.__str__())

    def request_sync_init(self):
        control = self.control
        control.request_sync_init = 1
        self.control = control


    @property
    def mode(self):
        try:
            value = self.device.read_register(REG_MODE)
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @property
    def x_position(self):
        try:
            value = self.device.read_long(
                REG_X_POSITION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @mode.setter
    def mode(self, value: int):
        try:
            self.device.write_register(
                REG_MODE,
                value,
            )
        except Exception as e:
            log.exception(e.__str__())

    @property
    def current_position(self):
        try:
            value = self.device.read_long(
                REG_CURRENT_POSITION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @current_position.setter
    def current_position(self, value):
        try:
            if self.mode != 0:
                raise Exception("Current position can be changed only if mode is 0")

            self.device.write_long(
                REG_CURRENT_POSITION,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
        except Exception as e:
            log.exception(e.__str__())

    @property
    def final_position(self):
        try:
            value = self.device.read_long(
                REG_FINAL_POSITION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @final_position.setter
    def final_position(self, value):
        try:
            self.device.write_long(
                REG_FINAL_POSITION,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
        except Exception as e:
            log.exception(e.__str__())

    @property
    def spindle_position(self):
        try:
            value = self.device.read_register(
                REG_SPINDLE_POSITION,
                signed=False
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @spindle_position.setter
    def spindle_position(self, value):
        try:
            self.device.write_register(
                REG_SPINDLE_POSITION,
                value,
            )
        except Exception as e:
            log.exception(e.__str__())

    @property
    def step(self):
        try:
            value = self.device.read_long(
                REG_STEP,
                signed=True
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @property
    def total_steps(self):
        try:
            value = self.device.read_long(
                REG_TOTAL_STEPS,
                signed=True
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @property
    def max_speed(self):
        try:
            value = self.device.read_float(
                REG_MAX_SPEED,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @max_speed.setter
    def max_speed(self, value):
        try:
            self.device.write_float(
                REG_MAX_SPEED,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
        except Exception as e:
            log.exception(e.__str__())

    @property
    def min_speed(self):
        try:
            value = self.device.read_float(
                REG_MIN_SPEED,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @min_speed.setter
    def min_speed(self, value):
        try:
            self.device.write_float(
                REG_MIN_SPEED,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
        except Exception as e:
            log.exception(e.__str__())

    @property
    def current_speed(self):
        try:
            value = self.device.read_float(
                REG_CURRENT_SPEED,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @property
    def acceleration(self):
        try:
            value = self.device.read_float(
                REG_ACCELERATION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @acceleration.setter
    def acceleration(self, value):
        try:
            self.device.write_float(
                REG_ACCELERATION,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
        except Exception as e:
            log.exception(e.__str__())

    @property
    def ratio_num(self):
        try:
            value = self.device.read_long(
                REG_RATIO_NUM,
                signed=True
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @ratio_num.setter
    def ratio_num(self, value):
        try:
            self.device.write_long(
                REG_RATIO_NUM,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
        except Exception as e:
            log.exception(e.__str__())

    @property
    def ratio_den(self):
        try:
            value = self.device.read_long(
                REG_RATIO_DEN,
                signed=True
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @ratio_den.setter
    def ratio_den(self, value):
        try:
            self.device.write_long(
                REG_RATIO_DEN,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
        except Exception as e:
            log.exception(e.__str__())

    @property
    def syn_ratio_num(self):
        try:
            value = self.device.read_long(
                REG_SYN_RATIO_NUM,
                signed=True
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @syn_ratio_num.setter
    def syn_ratio_num(self, value):
        try:
            self.device.write_long(
                REG_SYN_RATIO_NUM,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
        except Exception as e:
            log.exception(e.__str__())

    @property
    def syn_ratio_den(self):
        try:
            value = self.device.read_long(
                REG_SYN_RATIO_DEN,
                signed=True
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    @syn_ratio_den.setter
    def syn_ratio_den(self, value):
        try:
            self.device.write_long(
                REG_SYN_RATIO_DEN,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
        except Exception as e:
            log.exception(e.__str__())
