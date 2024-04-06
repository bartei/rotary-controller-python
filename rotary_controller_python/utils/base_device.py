import inspect
import struct
from typing import Optional, Callable, List, Any, Tuple

import minimalmodbus
from rotary_controller_python.utils import communication

import logging
from pydantic import BaseModel

log = logging.getLogger(__name__)


class TypeDefinition(BaseModel):
    name: str
    length: int
    read_function: Any
    write_function: Optional[Any]
    struct_unpack_string: str


class VariableDefinition(BaseModel):
    name: str
    address: int
    type: TypeDefinition
    count: int = 1


variable_definitions = [
    TypeDefinition(
        name="TIM_HandleTypeDef",
        length=2,
        struct_unpack_string="L",
        read_function=communication.read_long,
        write_function=communication.write_long
    ),
    TypeDefinition(
        name="uint16_t",
        length=1,
        struct_unpack_string="h",
        read_function=communication.read_unsigned,
        write_function=communication.write_unsigned
    ),
    TypeDefinition(
        name="uint32_t",
        length=2,
        struct_unpack_string="L",
        read_function=communication.read_long,
        write_function=communication.write_long
    ),
    TypeDefinition(
        name="int32_t",
        length=2,
        struct_unpack_string="l",
        read_function=communication.read_long,
        write_function=communication.write_long
    ),
    TypeDefinition(
        name="bool",
        length=1,
        struct_unpack_string="H",
        read_function=communication.read_unsigned,
        write_function=communication.write_unsigned
    ),
    TypeDefinition(
        name="float",
        length=2,
        struct_unpack_string="f",
        read_function=communication.read_float,
        write_function=communication.write_float
    ),
    TypeDefinition(
        name="input_mode_t",
        length=1,
        struct_unpack_string="H",
        read_function=communication.read_unsigned,
        write_function=communication.write_unsigned
    ),
]


class BaseDevice:
    definition = ""

    def __init__(self, device, base_address):
        from rotary_controller_python.utils.communication import DeviceManager
        self.base_address = base_address
        self.size = 0
        self.struct_unpack_string = ""
        self.fast_data = dict()
        self.dm: DeviceManager = device
        self.variables: List[VariableDefinition or BaseDevice] = []
        self.parse_addresses_from_definition()

    def __getitem__(self, key):
        try:
            var: VariableDefinition = [item for item in self.variables if item.name == key][0]
        except Exception as e:
            raise f"Variable with name: {key} not found"

        if var.count > 1:
            list_type = list()
            for i in range(var.count):
                list_type.append(
                    var.type.read_function(self.dm, var.address + self.base_address + var.type.length * i)
                )
            return list_type
        else:
            return var.type.read_function(self.dm, var.address + self.base_address)

    def __setitem__(self, key, value):
        try:
            var = [item for item in self.variables if item.name == key][0]
        except Exception as e:
            raise f"Variable with name: {key} not found"

        var.type.write_function(self.dm, var.address + self.base_address, value)
        return

    @classmethod
    def register_type(cls) -> TypeDefinition:
        current_address = 0
        size = 0
        name = None
        struct_unpack_string = ""
        for line in cls.definition.split(sep="\n"):
            tokens = [item.replace(";", "") for item in line.split(" ") if len(item) > 0]
            # Skip lines that don't represent a type definition
            if "typedef" in tokens:
                continue
            if "}" in tokens:
                name = tokens[1]
                continue
            if "{" in tokens:
                continue
            if len(tokens) == 0:
                continue

            # Find type match
            try:
                matching_type = [item for item in variable_definitions if item.name == tokens[0]][0]
            except Exception as e:
                raise Exception(f"Unable to find a matching type for: {tokens[0]}")
            current_address = current_address + matching_type.length
            struct_unpack_string += matching_type.struct_unpack_string
            size = current_address

        if name is None:
            raise "Unable to identify the typedef name from the provided definition"

        return TypeDefinition(
            name=name,
            length=size,
            struct_unpack_string=struct_unpack_string,
            read_function=cls,
            write_function=cls,
        )

    def parse_addresses_from_definition(self):
        current_address = 0
        self.struct_unpack_string = ""
        self.variables = []
        for line in self.definition.split(sep="\n"):
            tokens = [item for item in line.split(" ") if len(item) > 0]
            tokens = [item.replace(";", "") for item in tokens]
            tokens = [item.replace("*", "") for item in tokens]

            # Skip lines that don't represent a type definition
            if "typedef" in tokens:
                continue
            if "}" in tokens:
                continue
            if "{" in tokens:
                continue
            if len(tokens) == 0:
                continue

            # Find type match
            try:
                identified_type = tokens[0]
                identified_name ="".join(tokens[1:])

                matching_type = [
                    item
                    for item in variable_definitions
                    if item.name == identified_type
                ][0]

                # Handle multi var definition separated by comma
                if "," in identified_name:
                    for name in identified_name.replace(" ", "").split(","):
                        self.variables.append(VariableDefinition(
                            name=name,
                            address=current_address,
                            type=matching_type
                        ))
                        current_address += matching_type.length
                        self.struct_unpack_string += matching_type.struct_unpack_string
                    continue

                # Handle array definition
                if "[" in identified_name:
                    name, count = identified_name.split("[")
                    count, _ = count.split("]")
                    count = int(count)

                    self.variables.append(VariableDefinition(
                        name=name,
                        address=current_address,
                        type=matching_type,
                        count=count
                    ))
                    current_address += matching_type.length * count
                    self.struct_unpack_string += matching_type.struct_unpack_string * count
                    continue

                self.variables.append(VariableDefinition(
                    name=identified_name,
                    address=current_address,
                    type=matching_type
                ))
                current_address += matching_type.length
                self.struct_unpack_string += matching_type.struct_unpack_string

            except Exception as e:
                raise Exception(f"Unable to find a matching type for: {tokens[0]}: {e.__str__()}")

        self.size = current_address

    def set_fast_data(self, values: List):
        self.fast_data = dict()
        sorted_keys: List[VariableDefinition] = sorted(self.variables, key=lambda v: v.address)
        for item in sorted_keys:
            item
            if hasattr(item.type.read_function, "set_fast_data"):
                if item.count > 1:
                    fd_list = list()
                    for i in range(item.count):
                        fd_list.append(
                            item.type.read_function(self.dm, item.address + item.type.length * i).set_fast_data(values)
                        )
                    self.fast_data[item.name] = fd_list
                else:
                    self.fast_data[item.name] = item.type.read_function(self.dm, item.address).set_fast_data(values)
            else:
                if item.count > 1:
                    fd_list = list()
                    for i in range(item.count):
                        fd_list.append(values[0])
                        values = values[1:]

                    self.fast_data[item.name] = fd_list
                else:
                    self.fast_data[item.name] = values[0]
                    values = values[1:]

        return self.fast_data

    def refresh(self):
        remaining_size = self.size
        max_size = 32
        raw_data = []
        remaining_address = self.base_address
        while remaining_size > max_size:
            try:
                part_data = self.dm.device.read_registers(
                    registeraddress=self.base_address,
                    number_of_registers=max_size
                )
                remaining_size -= max_size
                remaining_address += max_size
                raw_data += part_data
            except Exception as e:
                log.error(e.__str__())
                self.dm.connected = False
                return

        if remaining_size > 0:
            part_data = self.dm.device.read_registers(
                registeraddress=remaining_address,
                number_of_registers=remaining_size
            )
            remaining_address += remaining_size
            remaining_size = 0
            raw_data += part_data

        raw_bytes = struct.pack("<" + "H" * self.size, *raw_data)
        values = list(struct.unpack("<" + self.struct_unpack_string, raw_bytes))
        return self.set_fast_data(values)

        # raw_data = self.dm.device.read_registers(
        #     registeraddress=self.addresses.base_address,
        #     number_of_registers=int(self.bytes_count),
        # )
        #
        # raw_bytes = struct.pack("<" + "H" * int(self.bytes_count), *raw_data)
        #
        # converted_data = struct.unpack(self.addresses.struct_map, raw_bytes)
        # self.servo_current, self.servo_desired, self.servo_speed = converted_data[0:3]
        # for i in range(SCALES_COUNT):
        #     self.scale_current[i] = converted_data[3 + i] / 1000
        # for i in range(SCALES_COUNT):
        #     self.scale_speed[i] = converted_data[3 + i + SCALES_COUNT] / 1000
        # self.cycles = converted_data[3 + SCALES_COUNT + SCALES_COUNT]
        # self.execution_interval = converted_data[3 + SCALES_COUNT + SCALES_COUNT + 1]