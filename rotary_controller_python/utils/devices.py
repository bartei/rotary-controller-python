import copy
import inspect

import sys
from rotary_controller_python.utils.addresses import FastDataAddresses, SCALES_COUNT
from rotary_controller_python.utils.base_device import BaseDevice
from rotary_controller_python.utils.communication import DeviceManager
from rotary_controller_python.utils.base_device import variable_definitions


class Index(BaseDevice):
    definition = """
typedef struct {
  int32_t divisions;
  int32_t index;
} index_t;    
"""


class Servo(BaseDevice):
    definition = """
typedef struct {
    float minSpeed;
    float maxSpeed;
    float currentSpeed;
    float acceleration;
    float absoluteOffset;
    float indexOffset;
    float syncOffset;
    float desiredPosition;
    float currentPosition;
    int32_t currentSteps;
    int32_t desiredSteps;
    int32_t ratioNum;
    int32_t ratioDen;
    int32_t maxValue;
    int32_t minValue;
    float breakingSpace, breakingTime;
    float allowedError;
} servo_t;
"""


class Global(BaseDevice):
    definition = """
typedef struct {
  uint32_t executionInterval;
  uint32_t executionIntervalPrevious;
  uint32_t executionIntervalCurrent;
  uint32_t executionCycles;
  index_t index;
  servo_t servo;
  input_t scales[4];
  fastData_t fastData;
} rampsSharedData_t;
"""


class Scale(BaseDevice):
    definition = """
typedef struct {
    TIM_HandleTypeDef *timerHandle;
    uint16_t encoderPrevious;
    uint16_t encoderCurrent;
    int32_t ratioNum;
    int32_t ratioDen;
    int32_t maxValue;
    int32_t minValue;
    int32_t position;
    int32_t speed;
    int32_t error;
    int32_t syncRatioNum, syncRatioDen;
    bool syncMotion;
    input_mode_t mode;
} input_t;    
"""


class FastData(BaseDevice):
    definition = """
typedef struct {
  float servoCurrent;
  float servoDesired;
  float servoSpeed;
  int32_t scaleCurrent[SCALES_COUNT];
  int32_t scaleSpeed[SCALES_COUNT];
  uint32_t cycles;
  uint32_t executionInterval;
} fastData_t;
"""
    # def __init__(self, device: DeviceManager, base_address: int):
    #     super().__init__(device=device)
    #     from rotary_controller_python.utils.addresses import IndexAddresses
    #
    #     self.addresses = FastDataAddresses(base_address)
    #     self.scale_current = [0, 0, 0, 0]
    #     self.scale_speed = [0, 0, 0, 0]
    #     self.servo_current = 0
    #     self.servo_desired = 0
    #     self.servo_speed = 0
    #     self.cycles = 0
    #     self.execution_interval = 0
    #     self.bytes_count = self.addresses.end - self.addresses.base_address
    #
    # def refresh(self):
    #     raw_data = self.dm.device.read_registers(
    #         registeraddress=self.addresses.base_address,
    #         number_of_registers=int(self.bytes_count),
    #     )
    #
    #     raw_bytes = struct.pack("<" + "H" * int(self.bytes_count), *raw_data)
    #
    #     converted_data = struct.unpack(self.addresses.struct_map, raw_bytes)
    #     self.servo_current, self.servo_desired, self.servo_speed = converted_data[0:3]
    #     for i in range(SCALES_COUNT):
    #         self.scale_current[i] = converted_data[3 + i] / 1000
    #     for i in range(SCALES_COUNT):
    #         self.scale_speed[i] = converted_data[3 + i + SCALES_COUNT] / 1000
    #     self.cycles = converted_data[3 + SCALES_COUNT + SCALES_COUNT]
    #     self.execution_interval = converted_data[3 + SCALES_COUNT + SCALES_COUNT + 1]


current_module = sys.modules[__name__]
clsmembers = [
    item
    for item in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if issubclass(item[1], BaseDevice) and item[0] != "BaseDevice"
]

unloaded_list = copy.deepcopy(clsmembers)
iterations_limit = 3
while len(unloaded_list) > 0 and iterations_limit > 0:
    failure_list = []
    for my_class in unloaded_list:
        my_class[1]: BaseDevice
        try:
            definition = my_class[1].register_type()
            variable_definitions.types.append(definition)
        except Exception as e:
            failure_list.append(my_class)
    unloaded_list = copy.deepcopy(failure_list)
    iterations_limit -= 1


def test_scale_structure():
    dm = DeviceManager()
    global_data = Global(device=dm, base_address=0)
    global_data["servo"]["ratioNum"] = 12345
    result = global_data["servo"]["ratioNum"]
    print(result)
    assert result == 12345
