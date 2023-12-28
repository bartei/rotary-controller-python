SCALES_COUNT = 4


class ScaleAddresses:
    #     typedef struct {
    #     TIM_HandleTypeDef * timerHandle;
    #     uint16_t encoderPrevious;
    #     uint16_t encoderCurrent;
    #     int32_t ratioNum;
    #     int32_t ratioDen;
    #     int32_t maxValue;
    #     int32_t minValue;
    #     int32_t position;
    #     int32_t error;
    #     int32_t syncRatioNum, syncRatioDen;
    #     bool syncMotion;
    # } input_t;
    def __init__(self, base_address):
        self.base_address = base_address
        self.timer_handle = 0 + base_address
        self.encoder_previous = 2 + base_address
        self.encoder_current = 3 + base_address
        self.ratio_num = 4 + base_address
        self.ratio_den = 6 + base_address
        self.max_value = 8 + base_address
        self.min_value = 10 + base_address
        self.position = 12 + base_address
        self.error = 14 + base_address
        self.sync_ratio_num = 16 + base_address
        self.sync_ratio_den = 18 + base_address
        self.sync_motion = 20 + base_address
        self.end = 22 + base_address


class IndexAddresses:
    def __init__(self, base_address):
        self.base_address = base_address
        self.divisions = 0 + base_address
        self.index = 2 + base_address
        self.end = 4 + base_address


class GlobalAddresses:
    # typedef struct {
    #     uint32_t execution_interval;
    #     uint32_t execution_interval_previous;
    #     uint32_t execution_interval_current;
    #     uint32_t execution_cycles;
    #     index_t index;
    #     servo_t servo;
    #     input_t scales[SCALES_COUNT];
    # } rampsSharedData_t;

    def __init__(self, base_address):
        self.base_address = base_address
        self.execution_interval = 0 + base_address
        self.execution_interval_previous = 2 + base_address
        self.execution_interval_current = 4 + base_address
        self.execution_cycles = 6 + base_address
        self.index_structure_offset = IndexAddresses(
            self.execution_cycles + base_address + 2
        )
        self.servo_structure_offset = ServoAddresses(self.index_structure_offset.end)
        end = self.servo_structure_offset.end
        self.scales = []

        for item in range(SCALES_COUNT):
            scale = ScaleAddresses(end)
            end = scale.end
            self.scales.append(scale)


class ServoAddresses:
    #     typedef struct {
    #     float minSpeed;
    #     float maxSpeed;
    #     float currentSpeed;
    #     float acceleration;
    #     float absoluteOffset;
    #     float indexOffset;
    #     float syncOffset;
    #     float desiredPosition;
    #     float currentPosition;
    #     int32_t currentSteps;
    #     int32_t desiredSteps;
    #     int32_t ratioNum;
    #     int32_t ratioDen;
    #     int32_t maxValue;
    #     int32_t minValue;
    #     float breakingSpace, breakingTime;
    #     float allowedError;
    # } servo_t;
    def __init__(self, base_address):
        self.base_address = base_address
        self.min_speed = 0 + base_address
        self.max_speed = 2 + base_address
        self.current_speed = 4 + base_address
        self.acceleration = 6 + base_address
        self.absolute_offset = 8 + base_address
        self.index_offset = 10 + base_address
        self.sync_offset = 12 + base_address
        self.desired_position = 14 + base_address
        self.current_position = 16 + base_address
        self.current_steps = 18 + base_address
        self.desired_steps = 20 + base_address
        self.ratio_num = 22 + base_address
        self.ratio_den = 24 + base_address
        self.max_value = 26 + base_address
        self.min_value = 28 + base_address
        self.breaking_space = 30 + base_address
        self.breaking_time = 32 + base_address
        self.allowed_error = 34 + base_address
        self.end = 36 + base_address


class FastDataAddresses:
    # typedef struct {
    #   float servoCurrent;
    #   float servoDesired;
    #   int32_t scaleCurrent[SCALES_COUNT];
    #   uint32_t cycles;
    # } fastData_t;
    def __init__(self, base_address):
        self.base_address = base_address
        self.servo_current = 0 + base_address
        self.servo_desired = 2 + base_address
        self.scale_current = 4 + base_address
        self.cycles = self.scale_current + (2 * SCALES_COUNT)
        self.end = self.cycles + 2

        import struct

        self.struct_map = "<ff" + "l" * SCALES_COUNT + "l"
