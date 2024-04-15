import copy
import inspect

import sys
import time

from rotary_controller_python.utils.base_device import BaseDevice
from rotary_controller_python.utils.communication import ConnectionManager
from rotary_controller_python.utils.base_device import variable_definitions

SCALES_COUNT = 4


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
  float desiredPosition;
  float currentPosition;
  int32_t currentSteps;
  int32_t desiredSteps;
  int32_t ratioNum;
  int32_t ratioDen;
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
  uint16_t syncEnable;
  uint16_t mode;
} input_t;
"""


class FastData(BaseDevice):
    definition = """
typedef struct {
  float servoCurrent;
  float servoDesired;
  float servoSpeed;
  int32_t scaleCurrent[4];
  int32_t scaleSpeed[4];
  uint32_t cycles;
  uint32_t executionInterval;
  uint16_t servoEnable;
  int16_t servoDirection;
} fastData_t;
"""


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
            variable_definitions.append(definition)
        except Exception as e:
            failure_list.append(my_class)
    unloaded_list = copy.deepcopy(failure_list)
    iterations_limit -= 1


# import time
# from rotary_controller_python.utils.communication import ConnectionManager
# def test_scale_structure():
#     dm = DeviceManager()
#     global_data = Global(device=dm, base_address=0)
#     global_data["servo"]["ratioNum"] = 12345
#     result = global_data["servo"]["ratioNum"]
#     print(result)
#     assert result == 12345
#
#
# def test_get_item_from_array_definition():
#     dm = DeviceManager()
#     global_data = Global(device=dm, base_address=0)
#     global_data['scales'][1]['ratioDen'] = 111
#     result = global_data['scales'][1]['ratioDen']
#     assert result == 111
#
#
# def test_scale_fast_data():
#     dm = DeviceManager()
#     dm.device.read_registers(0, 10)
#     global_data = Global(device=dm, base_address=0)
#     global_data.refresh()


# if __name__ == "__main__":
#     dm = DeviceManager()
#     global_data = Global(device=dm, base_address=0)
#     while True:
#         time.sleep(0.1)
#         values = global_data['fastData'].refresh()
#         print(values)
