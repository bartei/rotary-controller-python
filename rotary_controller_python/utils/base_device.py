import minimalmodbus
from loguru import logger as log


class BaseDevice:
    def __init__(self, device):
        from rotary_controller_python.utils.communication import DeviceManager

        self.dm: DeviceManager = device

    def read_float(self, address) -> float:
        try:
            value = self.dm.device.read_float(
                address, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.dm.connected = True
            return value
        except Exception as e:
            self.dm.connected = False
            log.error(e.__str__())
            return 0

    def write_float(self, address, value):
        try:
            self.dm.device.write_float(
                address, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP, value=value
            )
            self.dm.connected = True
        except Exception as e:
            self.dm.connected = False
            log.error(e.__str__())

    def read_long(self, address) -> int:
        try:
            value = self.dm.device.read_long(
                address, signed=True, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.dm.connected = True
            return value
        except Exception as e:
            self.dm.connected = False
            log.error(e.__str__())
            return 0

    def write_long(self, address, value):
        try:
            self.dm.device.write_long(
                address,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                value=int(value),
            )
            self.dm.connected = True
            log.info(f"Written {int(value)} to address {address}")
        except Exception as e:
            self.dm.connected = False
            log.error(e.__str__())

    def read_unsigned(self, address):
        try:
            value = self.dm.device.read_register(address, signed=False)
            self.dm.connected = True
            return value
        except Exception as e:
            self.dm.connected = False
            log.error(e.__str__())
            return 0

    def write_unsigned(self, address, value):
        try:
            self.dm.device.write_register(address, signed=False, value=int(value))
            self.dm.connected = True
        except Exception as e:
            self.dm.connected = False
            log.error(e.__str__())

    def read_signed(self, address):
        try:
            value = self.dm.device.read_register(address, signed=True)
            self.dm.connected = True
            return value
        except Exception as e:
            self.dm.connected = False
            log.error(e.__str__())
            return 0

    def write_signed(self, address, value):
        try:
            self.dm.device.write_register(address, signed=True, value=int(value))
            self.dm.connected = True
        except Exception as e:
            self.dm.connected = False
            log.error(e.__str__())
