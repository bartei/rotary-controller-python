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
        self.device.serial.baudrate = 38400
        self.device.serial.bytesize = 8
        self.device.serial.parity = serial.PARITY_NONE
        self.device.serial.stopbits = 1
        self.device.serial.timeout = 1

    def read_struct(self) -> DeviceRegisters:
        # STRUCTURE FROM STM32
        #     uint16_t mode;
        #     int32_t current_position;
        #     int32_t final_position;
        #     int16_t spindle_position;
        #     int32_t x_position;
        values = self.device.read_string(0, 8)
        (
            mode,
            current_position,
            desired_position,
            spindle_position,
            x_position
        ) = struct.unpack(">HllHl", bytes(values, encoding="LATIN1"))
        return DeviceRegisters(
            mode=mode,
            current_position=decimal.Decimal(current_position) / 100,
            desired_position=decimal.Decimal(desired_position) / 100,
            spindle_position=decimal.Decimal(spindle_position) / 10,
            x_position=decimal.Decimal(x_position) / 1000
        )

    def set_current_position(self, position: decimal.Decimal):
        value = int(position * 100)
        raw_string = struct.pack(">l", value).decode(encoding="LATIN1")
        try:
            self.device.write_string(1, raw_string, 2)
        except Exception as e:
            log.exception(f"Modbus Error: {e.__str__()}")

    def set_desired_position(self, position: decimal.Decimal):
        value = int(position * 100)
        raw_string = struct.pack(">l", value).decode(encoding="LATIN1")
        try:
            self.device.write_string(3, raw_string, 2)
        except Exception as e:
            log.exception(f"Modbus Error: {e.__str__()}")

    def set_mode(self, mode: DeviceMode):
        value = int(mode.value)
        raw_string = struct.pack(">H", value).decode(encoding="LATIN1")
        try:
            self.device.write_string(0, raw_string, 1)
        except Exception as e:
            log.exception(f"Modbus Error: {e.__str__()}")
