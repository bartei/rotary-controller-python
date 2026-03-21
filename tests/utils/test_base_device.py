from unittest.mock import MagicMock

import pytest

from rcp.utils.base_device import BaseDevice, TypeDefinition, VariableDefinition
from rcp.utils.devices import (
    Int16, UInt16, Int32, Uint32T, Float, Bool,
    TimHandleTypeDef, Scale, Servo, FastData, Global,
    SCALES_COUNT,
)
from rcp.utils import communication


@pytest.fixture
def mock_cm():
    cm = MagicMock()
    cm.definitions = [Int16, UInt16, Int32, Uint32T, Float, Bool, TimHandleTypeDef]
    return cm


class TestTypeDefinition:
    def test_int16_type(self):
        assert Int16.name == "int16_t"
        assert Int16.length == 1
        assert Int16.struct_unpack_string == "h"

    def test_uint16_type(self):
        assert UInt16.name == "uint16_t"
        assert UInt16.length == 1
        assert UInt16.struct_unpack_string == "H"

    def test_int32_type(self):
        assert Int32.name == "int32_t"
        assert Int32.length == 2
        assert Int32.struct_unpack_string == "l"

    def test_uint32_type(self):
        assert Uint32T.name == "uint32_t"
        assert Uint32T.length == 2
        assert Uint32T.struct_unpack_string == "L"

    def test_float_type(self):
        assert Float.name == "float"
        assert Float.length == 2
        assert Float.struct_unpack_string == "f"

    def test_bool_type(self):
        assert Bool.name == "bool"
        assert Bool.length == 1


class TestVariableDefinition:
    def test_default_count_is_1(self):
        v = VariableDefinition(name="test", address=0, type=Int32)
        assert v.count == 1

    def test_array_count(self):
        v = VariableDefinition(name="arr", address=0, type=Int32, count=4)
        assert v.count == 4


class TestBaseDeviceParsing:
    def test_servo_struct_parsing(self, mock_cm):
        """Servo struct should parse all fields with correct addresses."""
        # Add Servo's own type to definitions for nested structs
        servo_type = Servo.register_type(mock_cm.definitions)
        mock_cm.definitions.append(servo_type)

        device = Servo(mock_cm, base_address=0)
        var_names = [v.name for v in device.variables]
        assert "maxSpeed" in var_names
        assert "currentSpeed" in var_names
        assert "jogSpeed" in var_names
        assert "acceleration" in var_names
        assert "direction" in var_names
        assert "destinationSteps" in var_names
        assert "currentSteps" in var_names
        assert "desiredSteps" in var_names

    def test_scale_struct_parsing(self, mock_cm):
        """Scale (input_t) struct should parse including comma-separated vars."""
        scale_type = Scale.register_type(mock_cm.definitions)
        mock_cm.definitions.append(scale_type)

        device = Scale(mock_cm, base_address=0)
        var_names = [v.name for v in device.variables]
        # comma-separated: syncRatioNum, syncRatioDen
        assert "syncRatioNum" in var_names
        assert "syncRatioDen" in var_names
        assert "syncEnable" in var_names
        assert "position" in var_names

    def test_fast_data_struct_parsing(self, mock_cm):
        """FastData struct should parse arrays correctly."""
        fast_type = FastData.register_type(mock_cm.definitions)
        mock_cm.definitions.append(fast_type)

        device = FastData(mock_cm, base_address=0)
        var_names = [v.name for v in device.variables]
        assert "scaleCurrent" in var_names
        assert "scaleSpeed" in var_names
        assert "servoEnable" in var_names

        # scaleCurrent should be array of 4
        scale_current = [v for v in device.variables if v.name == "scaleCurrent"][0]
        assert scale_current.count == 4

    def test_base_address_offset(self, mock_cm):
        """Variables should be relative to device, base_address used for I/O."""
        servo_type = Servo.register_type(mock_cm.definitions)
        mock_cm.definitions.append(servo_type)

        device = Servo(mock_cm, base_address=100)
        assert device.base_address == 100
        # First variable address should be 0 (relative)
        assert device.variables[0].address == 0

    def test_size_computed_correctly(self, mock_cm):
        """Device size should equal sum of all field lengths."""
        servo_type = Servo.register_type(mock_cm.definitions)
        mock_cm.definitions.append(servo_type)

        device = Servo(mock_cm, base_address=0)
        assert device.size > 0
        # Servo: 4 floats (2 each) + 1 int32 (2) + 3 uint32 (2 each) = 16
        assert device.size == 16


class TestRegisterType:
    def test_servo_register_type(self):
        """register_type should produce a TypeDefinition with correct name."""
        defs = [Int16, UInt16, Int32, Uint32T, Float, Bool, TimHandleTypeDef]
        servo_type = Servo.register_type(defs)
        assert servo_type.name == "servo_t"
        assert servo_type.length > 0

    def test_scale_register_type(self):
        defs = [Int16, UInt16, Int32, Uint32T, Float, Bool, TimHandleTypeDef]
        scale_type = Scale.register_type(defs)
        assert scale_type.name == "input_t"

    def test_fast_data_register_type(self):
        defs = [Int16, UInt16, Int32, Uint32T, Float, Bool, TimHandleTypeDef]
        fast_type = FastData.register_type(defs)
        assert fast_type.name == "fastData_t"


class TestSetFastData:
    def test_simple_struct(self, mock_cm):
        """set_fast_data should map values to variable names."""
        servo_type = Servo.register_type(mock_cm.definitions)
        mock_cm.definitions.append(servo_type)

        device = Servo(mock_cm, base_address=0)
        # Servo has 8 fields; provide matching values
        values = [1.0, 2.0, 3.0, 4.0, 5, 6, 7, 8]
        result = device.set_fast_data(values)
        assert result["maxSpeed"] == 1.0
        assert result["currentSpeed"] == 2.0
        assert result["direction"] == 5

    def test_array_field(self, mock_cm):
        """Array fields should produce lists in fast_data."""
        fast_type = FastData.register_type(mock_cm.definitions)
        mock_cm.definitions.append(fast_type)

        device = FastData(mock_cm, base_address=0)
        # FastData: servoCurrent(1) + servoDesired(1) + stepsToGo(1) + servoSpeed(1) +
        #           scaleCurrent[4](4) + scaleSpeed[4](4) + cycles(1) + executionInterval(1) + servoEnable(1)
        values = [100, 200, 300, 1.5, 10, 20, 30, 40, 50, 60, 70, 80, 999, 888, 1]
        result = device.set_fast_data(values)
        assert result["scaleCurrent"] == [10, 20, 30, 40]
        assert result["scaleSpeed"] == [50, 60, 70, 80]
        assert result["servoEnable"] == 1


class TestConstants:
    def test_scales_count(self):
        assert SCALES_COUNT == 4
