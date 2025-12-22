import copy
import inspect
import time
from typing import Optional

import minimalmodbus
from keke import ktrace
from loguru import logger as log


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

        self.definitions = []
        self.structures = dict()
        self._load_structures()

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


if __name__ == "__main__":
    connection_manager = ConnectionManager()
    device = connection_manager['Global']

    while True:
        time.sleep(0.5)
        values = device['servo'].refresh()
        print(values)
