import inspect
from typing import Optional, Callable, List, Any

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


class VariableDefinition(BaseModel):
    name: str
    address: int
    type: TypeDefinition
    count: int = 1

    def __getitem__(self, item):
        item -= 1
        if not isinstance(item, int):
            raise Exception("Specify a number to pick an item from an array type variable")
        if item > self.count:
            raise Exception("Index out of range for array access")

        return VariableDefinition(
            name=self.name,
            address=self.address + self.type.length * item,
            type=self.type
        )


class VariableDefinitionList(BaseModel):
    types: List[TypeDefinition]


variable_definitions = VariableDefinitionList(types=[
    TypeDefinition(name="TIM_HandleTypeDef", length=2, read_function=communication.read_long, write_function=communication.write_long),
    TypeDefinition(name="uint16_t", length=1, read_function=communication.read_unsigned, write_function=communication.write_unsigned),
    TypeDefinition(name="uint32_t", length=2, read_function=communication.read_long, write_function=communication.write_long),
    TypeDefinition(name="int32_t", length=2, read_function=communication.read_long, write_function=communication.write_long),
    TypeDefinition(name="bool", length=1, read_function=communication.read_unsigned, write_function=communication.write_unsigned),
    TypeDefinition(name="float", length=2, read_function=communication.read_float, write_function=communication.write_float),
    TypeDefinition(name="input_mode_t", length=1, read_function=communication.read_unsigned, write_function=communication.write_unsigned),
])


class BaseDevice:
    definition = ""

    def __init__(self, device, base_address):
        from rotary_controller_python.utils.communication import DeviceManager
        self.base_address = base_address
        self.size = 0
        self.dm: DeviceManager = device
        self.variables: List[VariableDefinition] = []
        self.parse_addresses_from_definition()

    def __getattr__(self, key):
        if key in ["variables"]:
            return self.__getattribute__(key)

        try:
            var = [item for item in self.variables if item.name == key][0]
        except Exception as e:
            raise f"Variable with name: {key} not found"

        return var.type.read_function(self.dm, var.address + self.base_address)

    # def __setattr__(self, key, value):
    #     self.variables[key] = value

    @classmethod
    def register_type(cls) -> TypeDefinition:
        current_address = 0
        size = 0
        name = None
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
                matching_type = [item for item in variable_definitions.types if item.name == tokens[0]][0]
            except Exception as e:
                raise Exception(f"Unable to find a matching type for: {tokens[0]}")
            current_address = current_address + matching_type.length
            size = current_address

        if name is None:
            raise "Unable to identify the typedef name from the provided definition"

        return TypeDefinition(
            name=name,
            length=size,
            read_function=cls,
            write_function=cls,
        )

    def parse_addresses_from_definition(self):
        current_address = 0
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
                    for item in variable_definitions.types
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
                    continue

                # Handle array definition
                if "[" in identified_name:
                    name, count = identified_name.split("[")
                    count, _ = count.split("]")
                    count = int(count)

                    self.variables.append(VariableDefinition(
                        name=identified_name,
                        address=current_address,
                        type=matching_type,
                        count=count
                    ))
                    current_address += matching_type.length * count

                self.variables.append(VariableDefinition(
                    name=identified_name,
                    address=current_address,
                    type=matching_type
                ))
                current_address += matching_type.length

            except Exception as e:
                raise Exception(f"Unable to find a matching type for: {tokens[0]}: {e.__str__()}")

        self.size = current_address
