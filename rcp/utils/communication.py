import copy
import inspect
import time
from typing import Optional

import minimalmodbus
from kivy.logger import Logger
log = Logger.getChild(__name__)


class ConnectionManager:
    def __init__(
        self, serial_device="/dev/ttyUSB0", baudrate=115200, address=17, debug=False
    ):
        self.serial_device = serial_device
        self.baudrate = baudrate
        self.address = address
        self.debug = debug
        self.device: minimalmodbus.Instrument | None = None
        self._connected = False

        self._last_error_message: str | None = None

        self.definitions = []
        self.structures = dict()
        self._load_structures()

    @property
    def connected(self) -> bool:
        return self._connected

    @connected.setter
    def connected(self, value: bool):
        if value == self._connected:
            return
        self._connected = value
        if value:
            self._last_error_message = None
            log.info(f"Communication restored with {self.serial_device}")
        else:
            log.warning(f"Communication lost with {self.serial_device}")

    def _log_error_once(self, message: str):
        """Log an error message only if it differs from the last one logged."""
        if message != self._last_error_message:
            self._last_error_message = message
            log.error(message)

    def connect(self):
        if self.connected:
            return
        if self.device is not None:
            return
        try:
            self.device = minimalmodbus.Instrument(
                port=self.serial_device, slaveaddress=self.address, debug=self.debug
            )
            self.device.serial.timeout = 0.1
            self.device.serial.write_timeout = 0.1
            self.device.serial.baudrate = self.baudrate
        except Exception as e:
            self.device = None
            self.connected = False
            self._log_error_once(f"Failed to connect to {self.serial_device}: {str(e)}")

    def _load_structures(self):
        from rcp.utils import devices
        from rcp.utils.base_device import BaseDevice, TypeDefinition

        # First we load and add to our definitions all the base types
        base_types = [
            item
            for item in inspect.getmembers(devices)
            if isinstance(item[1], TypeDefinition)
        ]
        self.definitions += [item[1] for item in base_types]

        # Then we build the complex types
        device_classes = [
            item
            for item in inspect.getmembers(devices, inspect.isclass)
            if issubclass(item[1], BaseDevice) and item[0] != "BaseDevice"
        ]

        unloaded_list = copy.deepcopy(device_classes)
        iterations_limit = 3
        while len(unloaded_list) > 0 and iterations_limit > 0:
            failure_list = []
            for my_class in unloaded_list:
                # my_class[1]: BaseDevice
                try:
                    definition = my_class[1].register_type(self.definitions)
                    self.definitions.append(definition)
                    if my_class[1].root_structure is True:
                        self.structures[my_class[0]] = my_class[1](
                            connection_manager=self,
                            base_address=0
                        )

                    log.info(f"Loaded definition for {my_class[0]}")
                    iterations_limit = 3
                except IndexError:
                    failure_list.append(my_class)
            unloaded_list = copy.deepcopy(failure_list)
            iterations_limit -= 1

    def __getitem__(self, key):
        return self.structures[key]


def read_float(dm: ConnectionManager, address) -> float:
    try:
        value = dm.device.read_float(
            address, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
        )
        dm.connected = True
        return value
    except Exception as e:
        dm.connected = False
        dm._log_error_once(str(e))
        return 0


def write_float(dm, address, value, variable_name: Optional[str] = ""):
    try:
        dm.device.write_float(
            address, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP, value=value
        )
        dm.connected = True
        log.info(f"Write {variable_name}: float {value} to address {address}")
    except Exception as e:
        dm.connected = False
        dm._log_error_once(str(e))


def read_long(dm, address) -> int:
    try:
        value = dm.device.read_long(
            address, signed=True, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
        )
        dm.connected = True
        return value
    except Exception as e:
        dm.connected = False
        dm._log_error_once(str(e))
        return 0


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
        dm._log_error_once(str(e))


def read_unsigned(dm, address):
    try:
        value = dm.device.read_register(address, signed=False)
        dm.connected = True
        return value
    except Exception as e:
        dm.connected = False
        dm._log_error_once(str(e))
        return 0


def write_unsigned(dm, address, value, variable_name: Optional[str] = ""):
    try:
        dm.device.write_register(address, signed=False, value=int(value))
        dm.connected = True
        log.info(f"Write {variable_name}: unsigned {value} to address {address}")
    except Exception as e:
        dm.connected = False
        dm._log_error_once(str(e))


def read_signed(dm, address):
    try:
        value = dm.device.read_register(address, signed=True)
        dm.connected = True
        return value
    except Exception as e:
        dm.connected = False
        dm._log_error_once(str(e))
        return 0


def write_signed(dm, address, value, variable_name: Optional[str] = ""):
    try:
        dm.device.write_register(address, signed=True, value=int(value))
        dm.connected = True
        log.info(f"Write {variable_name}: signed {value} to address {address}")
    except Exception as e:
        dm.connected = False
        dm._log_error_once(str(e))


if __name__ == "__main__":
    connection_manager = ConnectionManager()
    connection_manager.connect()
    device = connection_manager['Global']

    while True:
        time.sleep(0.5)
        values = device['servo'].refresh()
        print(values)
