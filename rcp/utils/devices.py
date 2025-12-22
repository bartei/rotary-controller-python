import copy
import inspect
import logging

import sys
import time
from pprint import pprint

from rcp.utils.base_device import BaseDevice
from rcp.utils.communication import ConnectionManager
from rcp.utils.base_device import variable_definitions

SCALES_COUNT = 4


class DeltaPosError(BaseDevice):
    definition = """
typedef struct {
    int32_t delta;
    uint32_t oldPosition;
    uint32_t position;
    int32_t scaledDelta;
    int32_t error;
} deltaPosError_t;
"""


class Servo(BaseDevice):
    definition = """
typedef struct {
    float maxSpeed;
    float currentSpeed;
    float jogSpeed;
    float acceleration;
    int32_t stepsToGo;
    uint32_t destinationSteps;
    uint32_t previousSteps;
    uint32_t currentSteps;
    uint32_t desiredSteps;
    int32_t currentDirection;
    int32_t previousDirection;
    GPIO_TypeDef *stepPort;
    GPIO_TypeDef *dirPort;
    uint16_t stepPin;
    uint16_t dirPin;
    bool syncEnable;
    uint16_t unused;
    uint32_t syncScaleIndex;
    int32_t syncRatioNum;
    int32_t syncRatioDen;
    deltaPosError_t syncDeltaPos;
} servo_t;
"""


class Global(BaseDevice):
    definition = """
typedef struct {
    uint32_t executionInterval;
    uint32_t executionIntervalPrevious;
    uint32_t executionIntervalCurrent;
    uint32_t executionCycles;
    GPIO_TypeDef *enaPort;
    GPIO_TypeDef *usrLedPort;
    uint16_t usrLedPin;
    uint16_t enaPin;
    servo_t servo[1];
    input_t scales[5];
    fastData_t fastData;
    TIM_HandleTypeDef *synchroRefreshTimer;
    UART_HandleTypeDef *modbusUart;
    deltaPosError_t rampsDeltaPos;
    uint16_t servoCycles;
    uint16_t servoCyclesCounter;
} rampsHandler_t;
"""


class Scale(BaseDevice):
    definition = """
typedef struct {
    TIM_HandleTypeDef *timerHandle;
    int32_t position;
    int32_t speed;
    deltaPosError_t scalesDeltaPos;
    deltaPosError_t scalesSpeed;
} input_t;
"""


class FastData(BaseDevice):
    definition = """
typedef struct {
    uint32_t servoCurrent[1];
    uint32_t servoDesired[1];
    uint32_t stepsToGo[1];
    float servoSpeed[1];
    int32_t scaleCurrent[5];
    int32_t scaleSpeed[5];
    uint32_t cycles;
    uint32_t executionInterval;
    uint16_t servoMode;
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
            logging.error(e.__str__())
            failure_list.append(my_class)
    unloaded_list = copy.deepcopy(failure_list)
    iterations_limit -= 1


if __name__ == "__main__":
    from rcp.utils import communication
    from loguru import logger as log

    connection_manager = communication.ConnectionManager(serial_device="/dev/ttyUSB1", baudrate=115200, address=17, debug=False)
    device = Global(connection_manager=connection_manager, base_address=0)
    log.info("Starting test routine for serial modbus communication")
    # while True:
    time.sleep(0.5)
    print(f"Ena Port(0x40020800): {device['enaPort']:x}")
    print(f"Ena Pin(1024): {device['enaPin']}")
    print(f"User Led Port(0x40020000): {device['usrLedPort']:x}")
    print(f"User Led Pin(1024): {device['usrLedPin']}")

    print(f"Scale 0 Timer Handle(0x200019d4): {device['scales'][0]['timerHandle']:x}")
    print(f"Scale 1 Timer Handle(0x2000198c): {device['scales'][1]['timerHandle']:x}")
    print(f"Scale 2 Timer Handle(0x20001944): {device['scales'][2]['timerHandle']:x}")
    print(f"Scale 3 Timer Handle(0x200018fc): {device['scales'][3]['timerHandle']:x}")
    print(f"Scale 4 Timer Handle(0x200018b4): {device['scales'][4]['timerHandle']:x}")

    device['servoCycles'] = 0
    count = 10
    while count > 0:
        fastData = device['fastData'].refresh()
        pprint(fastData)
