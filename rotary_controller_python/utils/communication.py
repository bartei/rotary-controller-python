import logging
import minimalmodbus

from rotary_controller_python.utils.addresses import GlobalAddresses, SCALES_COUNT

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


def write_float(dm, address, value):
    try:
        dm.device.write_float(
            address, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP, value=value
        )
        dm.connected = True
        log.info(f"Write float: {value} to address {address}")
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())


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


def write_long(dm, address, value):
    try:
        dm.device.write_long(
            address,
            signed=True,
            byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
            value=int(value),
        )
        dm.connected = True
        log.info(f"Write long: {value} to address {address}")
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())


def read_unsigned(dm, address):
    try:
        value = dm.device.read_register(address, signed=False)
        dm.connected = True
        return value
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())
        return 0


def write_unsigned(dm, address, value):
    try:
        dm.device.write_register(address, signed=False, value=int(value))
        dm.connected = True
        log.info(f"Write unsigned: {int(value)} to address {address}")
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())


def read_signed(dm, address):
    try:
        value = dm.device.read_register(address, signed=True)
        dm.connected = True
        return value
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())
        return 0


def write_signed(dm, address, value):
    try:
        dm.device.write_register(address, signed=True, value=int(value))
        dm.connected = True
        log.info(f"Write signed: {int(value)} to address {address}")
    except Exception as e:
        dm.connected = False
        log.error(e.__str__())
