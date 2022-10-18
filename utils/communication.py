from enum import Enum

import minimalmodbus
import logging

log = logging.getLogger(__file__)

# typedef struct {
#     uint16_t mode;
#     float current_position;
#     float final_position;
#     int16_t spindle_position;
#     int32_t x_position;
#     uint16_t acc;
#     int32_t step;
#     int32_t total_steps;
#     float max_speed;
#     float min_speed;
#     float current_speed;
#     float acceleration;
#     int32_t step_ratio_num;
#     int32_t step_ratio_den;
# } rotary_controller_t;

REG_MODE = 0
REG_CURRENT_POSITION = 2
REG_FINAL_POSITION = 4
REG_SPINDLE_POSITION = 6
REG_STEP = 12
REG_TOTAL_STEPS = 14
REG_MAX_SPEED = 16
REG_MIN_SPEED = 18
REG_CURRENT_SPEED = 20
REG_ACCELERATION = 22
REG_RATIO_NUM = 24
REG_RATIO_DEN = 26


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
    def mode(self):
        try:
            value = self.device.read_register(REG_MODE)
            return value
        except Exception as e:
            log.exception(e.__str__())
            return None

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
            value = self.device.read_float(
                REG_CURRENT_POSITION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return None

    @current_position.setter
    def current_position(self, value):
        try:
            if self.mode != 0:
                raise Exception("Current position can be changed only if mode is 0")

            self.device.write_float(
                REG_CURRENT_POSITION,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
        except Exception as e:
            log.exception(e.__str__())

    @property
    def final_position(self):
        try:
            value = self.device.read_float(
                REG_FINAL_POSITION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            return value
        except Exception as e:
            log.exception(e.__str__())
            return None

    @final_position.setter
    def final_position(self, value):
        try:
            self.device.write_float(
                REG_FINAL_POSITION,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
            return None

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
