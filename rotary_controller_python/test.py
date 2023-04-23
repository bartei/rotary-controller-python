import time

import minimalmodbus
import serial

from loguru import logger as log


adam = minimalmodbus.Instrument(
    port="/dev/serial0",
    slaveaddress=17,
    debug=False
)

adam.serial.baudrate = 57600
adam.serial.bytesize = 8
adam.serial.parity = serial.PARITY_NONE
adam.serial.stopbits = 1
adam.serial.timeout = 1


# typedef struct {
#     uint16_t mode;
#     float current_position;
#     float final_position;
#     int16_t spindle_position;
#     int32_t x_position;
#     uint16_t acc;
#     int32_t step;
#     int32_t total_steps;
#     float max_speed;
#     float min_speed;
#     float current_speed;
#     float acceleration;
#     int32_t step_ratio_num;
#     int32_t step_ratio_den;
# } rotary_controller_t;


REG_MODE = 0
REG_CURRENT_POSITION = 2
REG_FINAL_POSITION = 4
REG_SPINDLE_POSITION = 6
REG_STEP = 12
REG_TOTAL_STEPS = 14
REG_MAX_SPEED = 16
REG_MIN_SPEED = 18
REG_CURRENT_SPEED = 20
REG_ACCELERATION = 22
REG_RATIO_NUM = 24
REG_RATIO_DEN = 26


def set_final_position(value: float):
    try:
        adam.write_float(REG_FINAL_POSITION, value, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except Exception as e:
        log.exception(e.__str__())


def set_acceleration(value: float):
    try:
        adam.write_float(REG_ACCELERATION, value, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except Exception as e:
        log.exception(e.__str__())


def set_min_speed(value: float):
    try:
        adam.write_float(REG_MIN_SPEED, value, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except Exception as e:
        log.exception(e.__str__())


def set_max_speed(value: float):
    try:
        adam.write_float(REG_MAX_SPEED, value, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except Exception as e:
        log.exception(e.__str__())


def set_ratio(numerator, denominator):
    try:
        adam.write_long(REG_RATIO_NUM, numerator, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
        adam.write_long(REG_RATIO_DEN, denominator, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
    except Exception as e:
        log.exception(e.__str__())


def get_final_position() -> float or None:
    try:
        value = adam.read_float(REG_FINAL_POSITION, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
        return value
    except Exception as e:
        log.exception(e.__str__())
        return None


def get_current_position() -> float or None:
    try:
        value = adam.read_float(REG_CURRENT_POSITION, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
        return value
    except Exception as e:
        log.exception(e.__str__())
        return None


def get_acceleration() -> float or None:
    try:
        value = adam.read_float(REG_ACCELERATION, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
        return value
    except Exception as e:
        log.exception(e.__str__())
        return None


def get_current_speed() -> float or None:
    try:
        value = adam.read_float(REG_CURRENT_SPEED, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
        return value
    except Exception as e:
        log.exception(e.__str__())
        return None

def get_step() -> int or None:
    try:
        value = adam.read_long(REG_STEP, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
        return value
    except Exception as e:
        log.exception(e.__str__())
        return None

def get_total_steps() -> int or None:
    try:
        value = adam.read_long(REG_TOTAL_STEPS, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP)
        return value
    except Exception as e:
        log.exception(e.__str__())
        return None


if __name__ == '__main__':
    while True:
        # address = input("Register address: ")
        # print("Value BIG: ", adam.read_float(int(address), byteorder=minimalmodbus.BYTEORDER_BIG))
        # print("Value BIG_SWAP: ", adam.read_float(int(address), byteorder=minimalmodbus.BYTEORDER_BIG_SWAP))
        # print("Value LITTLE: ", adam.read_float(int(address), byteorder=minimalmodbus.BYTEORDER_LITTLE))
        # print("Value LITTLE_SWAP: ", adam.read_float(int(address), byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP))
        # print("Value LITTLE_SWAP int32: ", adam.read_long(int(address), signed=True, byteorder=minimalmodbus.BYTEORDER_LITTLE_SWAP))
        print(f"Current position: {get_current_position()}")
        print(f"Current position: {get_final_position()}")
        destination = input("Destination: ")
        # acc = input("Acceleration: ")
        set_ratio(360, 1600)
        set_acceleration(1.5)
        set_max_speed(360.0 * 8)
        set_min_speed(60.0)
        # set_min_speed(100.0)
        set_final_position(float(destination))
        cur = get_current_position()
        while get_step() != get_total_steps():
            print(f"Current Position: {get_current_position()}, acc: {get_acceleration()}, speed: {get_current_speed()}")
            time.sleep(.1)

