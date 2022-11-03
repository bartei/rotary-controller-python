import struct
from typing import Callable, Dict

import minimalmodbus
import cachetools.func
import logging


log = logging.getLogger(__file__)


def bits_to_dict(value, structure_class: Callable):
    cs = structure_class()
    struct.pack_into(
        cs.pack_format,
        cs,
        0,
        value
    )
    fields = [item[0] for item in cs._fields_]
    result = {field: getattr(cs, field) for field in fields}
    return result
    # cs


def dict_to_bits(values: Dict, structure_class: Callable) -> int:
    cs = structure_class()
    [setattr(cs, item, value) for item, value in values.items()]

    value = struct.unpack_from(
        cs.pack_format,
        cs,
        0
    )[0]
    return value


class BaseStructureManager:
    def __init__(self, device: minimalmodbus.Instrument, control_structure: Callable, register_address):
        self.device = device
        self.control_structure = control_structure
        self.register_address = register_address

    @cachetools.func.ttl_cache(ttl=0.1)
    def get_register(self) -> int:
        """
        Gets the register value and keeps the value in the cache for reuse for .1 seconds
        """
        try:
            value = self.device.read_register(self.register_address)
            return value
        except Exception as e:
            log.exception(e.__str__())
            return 999999

    def set_register(self, value: int):
        """
        Sets the register value to the given value
        """
        try:
            self.device.write_register(self.register_address, value=value)
        except Exception as e:
            log.exception(e.__str__())

    def _set_bit_value(self, bit_name: str, value: bool):
        """
        Updates the value of the given bit name with the specified value
        """
        register_value = self.get_register()
        status = bits_to_dict(register_value, self.control_structure)
        status[bit_name] = value
        register_value = dict_to_bits(status, self.control_structure)
        self.set_register(register_value)

    def _get_bit_value(self, bit_name: str) -> bool:
        """
        Returns the bit value for the specified bit
        """
        register_value = self.get_register()
        status = bits_to_dict(register_value, self.control_structure)
        return status[bit_name]
