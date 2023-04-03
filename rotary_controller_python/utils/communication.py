import struct
from typing import List

import minimalmodbus
import logging

log = logging.getLogger(__file__)

# Register addresses as per the current firmware version
REG_MODE = 0
REG_CURRENT_POSITION = 2
REG_FINAL_POSITION = 4
REG_UNUSED_6 = 6
REG_UNUSED_8 = 8
REG_ENCODER_PRESET_INDEX = 10
REG_ENCODER_PRESET_VALUE = 12
REG_UNUSED_14 = 14
REG_MAX_SPEED = 16
REG_MIN_SPEED = 18
REG_CURRENT_SPEED = 20
REG_ACCELERATION = 22
REG_RATIO_NUM = 24
REG_RATIO_DEN = 26
REG_UNUSED_28 = 28
REG_SYN_RATIO_NUM = 30
REG_SYN_RATIO_DEN = 32
REG_SYN_OFFSET = 34
REG_SYN_SCALE_INDEX = 36
REG_SCALE_1 = 38
# REG_SCALE_2 = 40
# REG_SCALE_3 = 42
# REG_SCALE_4 = 44

SCALES_COUNT = 4

# Summary of the currently available device modes from the current firmware
MODE_HALT = 0
MODE_INDEX = 10
MODE_INDEX_INIT = 11
MODE_SYNCHRO = 20
MODE_SYNCHRO_INIT = 21
MODE_JOG = 30
MODE_JOG_FW = 31
MODE_JOG_BW = 32
MODE_SET_ENCODER = 40
MODE_SYNCHRO_BAD_RATIO = 101
MODE_DISCONNECTED = 255


class DeviceManager:
    def __init__(self, serial_device="/dev/ttyUSB0", baudrate=115200, address=17, debug=False):
        self.device: minimalmodbus.Instrument = minimalmodbus.Instrument(
            port=serial_device,
            slaveaddress=address,
            debug=debug
        )
        self.device.serial.baudrate = baudrate
        self.connected = True
        self.last_error = ""

    @property
    def mode(self):
        try:
            value = self.device.read_register(REG_MODE)
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            print(self.last_error)
            return 0

    @mode.setter
    def mode(self, value: int):
        try:
            self.device.write_register(REG_MODE, value)
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def scales(self) -> List[int]:
            result = []
            try:
                raw_data = self.device.read_registers(REG_SCALE_1, SCALES_COUNT * 2)
                self.connected = True
            except Exception as e:
                self.connected = False
                self.last_error = e.__str__()
                result.append(0)
                return [0, 0, 0, 0]

            raw_byte = bytearray()
            format = ">"
            for i in range(SCALES_COUNT):
                raw_byte.append((raw_data[i*2+1] >> 8) & 255)
                raw_byte.append((raw_data[i*2+1]) & 255)
                raw_byte.append((raw_data[i*2] >> 8) & 255)
                raw_byte.append((raw_data[i*2]) & 255)
                format += "l"

            result = struct.unpack(format, raw_byte)
            return result

    @property
    def current_position(self):
        try:
            value = self.device.read_long(
                REG_CURRENT_POSITION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

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
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def final_position(self):
        try:
            value = self.device.read_long(
                REG_FINAL_POSITION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @final_position.setter
    def final_position(self, value):
        try:
            self.device.write_long(
                REG_FINAL_POSITION,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def spindle_position(self):
        try:
            value = self.device.read_register(
                REG_UNUSED_6,
                signed=False
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @spindle_position.setter
    def spindle_position(self, value):
        try:
            self.device.write_register(
                REG_UNUSED_6,
                value,
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()


    @property
    def max_speed(self):
        try:
            value = self.device.read_float(
                REG_MAX_SPEED,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @max_speed.setter
    def max_speed(self, value):
        try:
            self.device.write_float(
                REG_MAX_SPEED,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def min_speed(self):
        try:
            value = self.device.read_float(
                REG_MIN_SPEED,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @min_speed.setter
    def min_speed(self, value):
        try:
            self.device.write_float(
                REG_MIN_SPEED,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def current_speed(self):
        try:
            value = self.device.read_float(
                REG_CURRENT_SPEED,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @property
    def acceleration(self):
        try:
            value = self.device.read_float(
                REG_ACCELERATION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @acceleration.setter
    def acceleration(self, value):
        try:
            self.device.write_float(
                REG_ACCELERATION,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def ratio_num(self):
        try:
            value = self.device.read_long(
                REG_RATIO_NUM,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @ratio_num.setter
    def ratio_num(self, value):
        try:
            self.device.write_long(
                REG_RATIO_NUM,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def ratio_den(self):
        try:
            value = self.device.read_long(
                REG_RATIO_DEN,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @ratio_den.setter
    def ratio_den(self, value):
        try:
            self.device.write_long(
                REG_RATIO_DEN,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def syn_ratio_num(self):
        try:
            value = self.device.read_long(
                REG_SYN_RATIO_NUM,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @syn_ratio_num.setter
    def syn_ratio_num(self, value):
        try:
            self.device.write_long(
                REG_SYN_RATIO_NUM,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def syn_ratio_den(self):
        try:
            value = self.device.read_long(
                REG_SYN_RATIO_DEN,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @syn_ratio_den.setter
    def syn_ratio_den(self, value):
        try:
            self.device.write_long(
                REG_SYN_RATIO_DEN,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def encoder_preset_value(self):
        try:
            value = self.device.read_long(
                REG_ENCODER_PRESET_VALUE,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @encoder_preset_value.setter
    def encoder_preset_value(self, value):
        try:
            self.device.write_long(
                REG_ENCODER_PRESET_VALUE,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def encoder_preset_index(self):
        try:
            value = self.device.read_register(
                REG_ENCODER_PRESET_INDEX,
                signed=False
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @encoder_preset_index.setter
    def encoder_preset_index(self, value):
        try:
            self.device.write_register(
                REG_ENCODER_PRESET_INDEX,
                value,
                signed=False
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()


device: DeviceManager or None = None


def configure_device():
    global device
    try:
        device = DeviceManager()
    except Exception as e:
        # Retry in 5 seconds if the connection failed
        log.warning("Retry to connect")
        device = None
        log.error(e.__str__())

    if device is not None:
        log.warning(f"Device connection: {device.connected}")
