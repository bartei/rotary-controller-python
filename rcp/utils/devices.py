from rcp.utils.base_device import BaseDevice, TypeDefinition
from rcp.utils import communication
SCALES_COUNT = 4
SERVOS_COUNT = 3

TimHandleTypeDef = TypeDefinition(
    name = "TIM_HandleTypeDef",
    length = 2,
    struct_unpack_string = "L",
    read_function = communication.read_long,
    write_function = communication.write_long,
)

Int16 = TypeDefinition(
    name = "int16_t",
    length = 1,
    struct_unpack_string = "h",
    read_function = communication.read_signed,
    write_function = communication.write_signed,
)

UInt16 = TypeDefinition(
    name ="uint16_t",
    length=1,
    struct_unpack_string="H",
    read_function=communication.read_unsigned,
    write_function=communication.write_unsigned,
)

Bool = TypeDefinition(
    name="bool",
    length=1,
    struct_unpack_string="H",
    read_function=communication.read_unsigned,
    write_function=communication.write_unsigned
)

Uint32T = TypeDefinition(
    name="uint32_t",
    length=2,
    struct_unpack_string="L",
    read_function=communication.read_long,
    write_function=communication.write_long
)

Int32 = TypeDefinition(
    name="int32_t",
    length=2,
    struct_unpack_string="l",
    read_function=communication.read_long,
    write_function=communication.write_long
)

Float = TypeDefinition(
    name="float",
    length=2,
    struct_unpack_string="f",
    read_function=communication.read_float,
    write_function=communication.write_float
)


class Servo(BaseDevice):
    definition = """
typedef struct {
  float maxSpeed;
  float currentSpeed;
  float jogSpeed;
  float acceleration;
  int32_t direction;
  uint32_t destinationSteps;
  uint32_t currentSteps;
  uint32_t desiredSteps;
} servo_t;
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


class Global(BaseDevice):
    root_structure = True
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
