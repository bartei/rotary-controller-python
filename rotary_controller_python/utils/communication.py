import logging
from typing import Optional

import minimalmodbus
from keke import ktrace

log = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(
        self, serial_device="/dev/ttyUSB0", baudrate=115200, address=17, debug=False
    ):
        try:
            self.device: minimalmodbus.Instrument = minimalmodbus.Instrument(
                port=serial_device, slaveaddress=address, debug=debug
            )
            self.device.serial.timeout = 0.1
            self.device.serial.write_timeout = 0.1
            self.device.serial.baudrate = baudrate
            self.connected = True
        except Exception as e:
            log.error(e.__str__())
            self.connected = False

@ktrace("address")
def read_float(dm: ConnectionManager, address) -> float:
    try:
        value = dm.device.read_float(
            address, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
        )
        dm.connected = True
        return value
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())
        return 0


@ktrace("address")
def write_float(dm, address, value, variable_name: Optional[str] = ""):
    try:
        dm.device.write_float(
            address, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP, value=value
        )
        dm.connected = True
        log.info(f"Write {variable_name}: float {value} to address {address}")
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())


@ktrace("address")
def read_long(dm, address) -> int:
    try:
        value = dm.device.read_long(
            address, signed=True, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
        )
        dm.connected = True
        return value
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())
        return 0


@ktrace("address")
def write_long(dm, address, value, variable_name: Optional[str] = ""):
    try:
        dm.device.write_long(
            address,
            signed=True,
            byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
            value=int(value),
        )
        dm.connected = True
        log.info(f"Write {variable_name}: long {value} to address {address}")
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())


@ktrace("address")
def read_unsigned(dm, address):
    try:
        value = dm.device.read_register(address, signed=False)
        dm.connected = True
        return value
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())
        return 0


@ktrace("address")
def write_unsigned(dm, address, value, variable_name: Optional[str] = ""):
    try:
        dm.device.write_register(address, signed=False, value=int(value))
        dm.connected = True
        log.info(f"Write {variable_name}: unsigned {value} to address {address}")
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())


@ktrace("address")
def read_signed(dm, address):
    try:
        value = dm.device.read_register(address, signed=True)
        dm.connected = True
        return value
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())
        return 0


@ktrace("address")
def write_signed(dm, address, value, variable_name: Optional[str] = ""):
    try:
        dm.device.write_register(address, signed=True, value=int(value))
        dm.connected = True
        log.info(f"Write {variable_name}: signed {value} to address {address}")
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())
