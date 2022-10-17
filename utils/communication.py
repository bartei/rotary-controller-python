import ctypes
import decimal
import time
from enum import Enum

import minimalmodbus
import struct
import logging

from threading import Thread, Event
from pydantic import BaseModel

log = logging.getLogger(__file__)
terminate_event = Event()

REG_MODE = 0
REG_CURRENT_POSITION = 2
REG_FINAL_POSITION = 4
REG_SPINDLE_POSITION = 6
REG_X_POSITION_UNITS = 7
REG_ACCELERATION = 11


class DeviceMode(Enum):
    DIRECT = 0
    DIVIDE = 1
    DIVIDE_SYNC = 2


class DeviceRegisters(BaseModel):
    mode: DeviceMode = DeviceMode.DIRECT
    current_position: decimal.Decimal
    desired_position: decimal.Decimal
    spindle_position: decimal.Decimal
    x_position: decimal.Decimal


class DeviceManager:
    def __init__(self):
        self.device: minimalmodbus.Instrument = minimalmodbus.Instrument(
            port="/dev/serial0",
            slaveaddress=17,
            debug=False
        )
        self.device.serial.baudrate = 9600

    def get_final_position(self) -> int or None:
        try:
            value = self.device.read_register(REG_FINAL_POSITION)
            value = value + self.device.read_register(REG_FINAL_POSITION + 1) << 16
            return ctypes.c_long(value).value
        except Exception as e:
            log.exception(e.__str__())
            return None

    def set_final_position(self, value: int):
        try:
            values = [
                value & 0xFFFF,
                value >> 16 & 0xFFFF
            ]
            self.device.write_registers(REG_FINAL_POSITION, values)
        except Exception as e:
            log.exception(e.__str__())

    def get_current_position(self) -> int or None:
        try:
            value = self.device.read_register(REG_CURRENT_POSITION)
            value = value + (self.device.read_register(REG_CURRENT_POSITION + 1) << 16)
            return ctypes.c_long(value).value
        except Exception as e:
            log.exception(e.__str__())
            return None

    def set_current_position(self, value: int):
        try:
            values = [
                value & 0xFFFF,
                value >> 16 & 0xFFFF
            ]
            self.device.write_registers(REG_CURRENT_POSITION, values)
        except Exception as e:
            log.exception(e.__str__())

    def get_acceleration(self) -> int or None:
        try:
            value = self.device.read_register(REG_ACCELERATION, 0)
            return value
        except Exception as e:
            log.exception(e.__str__())
            return None

    def set_acceleration(self, value: int):
        try:
            self.device.write_register(REG_ACCELERATION, value)
        except Exception as e:
            log.exception(e.__str__())
