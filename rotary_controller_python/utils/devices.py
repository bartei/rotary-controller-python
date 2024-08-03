import copy
import inspect

import sys
import time

from rotary_controller_python.utils.base_device import BaseDevice
from rotary_controller_python.utils.communication import ConnectionManager
from rotary_controller_python.utils.base_device import variable_definitions

SCALES_COUNT = 4


# class Index(BaseDevice):
#     definition = """
# typedef struct {
#   int32_t divisions;
#   int32_t index;
# } index_t;
# """


class Servo(BaseDevice):
    definition = """
typedef struct {
  float maxSpeed;
  float currentSpeed;
  float acceleration;
  int32_t direction;
  uint32_t destinationSteps;
  uint32_t currentSteps;
  uint32_t desiredSteps;
} servo_t;
"""


class Global(BaseDevice):
    definition = """
typedef struct {
  uint32_t executionInterval;
  uint32_t executionIntervalPrevious;
  uint32_t executionIntervalCurrent;
  uint32_t executionCycles;
  servo_t servo;
  input_t scales[4];
  fastData_t fastData;
} rampsSharedData_t;
"""


class Scale(BaseDevice):
    definition = """
typedef struct {
  TIM_HandleTypeDef *timerHandle;
  int32_t position;
  int32_t speed;
  int32_t syncRatioNum, syncRatioDen;
  uint16_t syncEnable;
  uint16_t spare;
} input_t;
"""


class FastData(BaseDevice):
    definition = """
typedef struct {
  uint32_t servoCurrent;
  uint32_t servoDesired;
  uint32_t stepsToGo;
  float servoSpeed;
  int32_t scaleCurrent[4];
  int32_t scaleSpeed[4];
  uint32_t cycles;
  uint32_t executionInterval;
  uint16_t servoEnable;
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


if __name__ == "__main__":
    from rotary_controller_python.utils import communication

    connection_manager = communication.ConnectionManager()
    device = Global(connection_manager=connection_manager, base_address=0)

    while True:
        time.sleep(0.5)
        # values = device['fastData'].refresh()
        # print(
        #     device['executionInterval'],
        #     device['executionIntervalPrevious'],
        #     device['executionIntervalCurrent'],
        #     device['executionCycles']
        # )
        values = device['servo'].refresh()
        print(values)

  # float maxSpeed;
  # float currentSpeed;
  # float acceleration;
  # int32_t direction;
  # uint32_t destinationSteps;
  # uint32_t currentSteps;
  # uint32_t desiredSteps;