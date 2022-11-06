import minimalmodbus
import logging

log = logging.getLogger(__file__)

# typedef struct {
# 0    uint16_t mode;
# 2    int32_t current_position;
# 4    int32_t final_position;
# 6    int16_t spindle_position;
# 8    int32_t x_position;
# 10    uint16_t acc;
# 12    int32_t step;
# 14    int32_t total_steps;
# 16    float max_speed;
# 18    float min_speed;
# 20    float current_speed;
# 22    float acceleration;
# 24    int32_t step_ratio_num;
# 26    int32_t step_ratio_den;
# 28    float step_ratio;
# 30    int32_t syn_ratio_num;
# 32    int32_t syn_ratio_den;
# 34    controller_status_t status;
# 36    controller_control_t control;
# } rotary_controller_t;

REG_MODE = 0
REG_CURRENT_POSITION = 2
REG_FINAL_POSITION = 4
REG_UNUSED_6 = 6
REG_ENCODER_POSITION = 8
REG_STEP = 12
REG_TOTAL_STEPS = 14
REG_MAX_SPEED = 16
REG_MIN_SPEED = 18
REG_CURRENT_SPEED = 20
REG_ACCELERATION = 22
REG_RATIO_NUM = 24
REG_RATIO_DEN = 26
REG_STEP_RATIO = 28
REG_SYN_RATIO_NUM = 30
REG_SYN_RATIO_DEN = 32


class DeviceManager:
    def __init__(self, serial_device="/dev/serial0", baudrate=57600, address=17, debug=False):
        self.device: minimalmodbus.Instrument = minimalmodbus.Instrument(
            port=serial_device,
            slaveaddress=address,
            debug=debug
        )
        self.device.serial.baudrate = baudrate
        self.connected = True
        self.last_error = ""

    @property
    def mode(self):
        try:
            value = self.device.read_register(REG_MODE)
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @property
    def x_position(self):
        try:
            value = self.device.read_long(
                REG_ENCODER_POSITION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @mode.setter
    def mode(self, value: int):
        try:
            self.device.write_register(REG_MODE, value)
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def current_position(self):
        try:
            value = self.device.read_long(
                REG_CURRENT_POSITION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @current_position.setter
    def current_position(self, value):
        try:
            if self.mode != 0:
                raise Exception("Current position can be changed only if mode is 0")

            self.device.write_long(
                REG_CURRENT_POSITION,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def final_position(self):
        try:
            value = self.device.read_long(
                REG_FINAL_POSITION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @final_position.setter
    def final_position(self, value):
        try:
            self.device.write_long(
                REG_FINAL_POSITION,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP,
                signed=True
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def spindle_position(self):
        try:
            value = self.device.read_register(
                REG_UNUSED_6,
                signed=False
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @spindle_position.setter
    def spindle_position(self, value):
        try:
            self.device.write_register(
                REG_UNUSED_6,
                value,
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def step(self):
        try:
            value = self.device.read_long(
                REG_STEP,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @property
    def total_steps(self):
        try:
            value = self.device.read_long(
                REG_TOTAL_STEPS,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @property
    def max_speed(self):
        try:
            value = self.device.read_float(
                REG_MAX_SPEED,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @max_speed.setter
    def max_speed(self, value):
        try:
            self.device.write_float(
                REG_MAX_SPEED,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def min_speed(self):
        try:
            value = self.device.read_float(
                REG_MIN_SPEED,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @min_speed.setter
    def min_speed(self, value):
        try:
            self.device.write_float(
                REG_MIN_SPEED,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def current_speed(self):
        try:
            value = self.device.read_float(
                REG_CURRENT_SPEED,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @property
    def acceleration(self):
        try:
            value = self.device.read_float(
                REG_ACCELERATION,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @acceleration.setter
    def acceleration(self, value):
        try:
            self.device.write_float(
                REG_ACCELERATION,
                value,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def ratio_num(self):
        try:
            value = self.device.read_long(
                REG_RATIO_NUM,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @ratio_num.setter
    def ratio_num(self, value):
        try:
            self.device.write_long(
                REG_RATIO_NUM,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def ratio_den(self):
        try:
            value = self.device.read_long(
                REG_RATIO_DEN,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @ratio_den.setter
    def ratio_den(self, value):
        try:
            self.device.write_long(
                REG_RATIO_DEN,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def syn_ratio_num(self):
        try:
            value = self.device.read_long(
                REG_SYN_RATIO_NUM,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @syn_ratio_num.setter
    def syn_ratio_num(self, value):
        try:
            self.device.write_long(
                REG_SYN_RATIO_NUM,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()

    @property
    def syn_ratio_den(self):
        try:
            value = self.device.read_long(
                REG_SYN_RATIO_DEN,
                signed=True
            )
            self.connected = True
            return value
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
            return 0

    @syn_ratio_den.setter
    def syn_ratio_den(self, value):
        try:
            self.device.write_long(
                REG_SYN_RATIO_DEN,
                value,
                signed=True,
                byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP
            )
            self.connected = True
        except Exception as e:
            self.connected = False
            self.last_error = e.__str__()
