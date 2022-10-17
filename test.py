import logging
import time
import ctypes

import minimalmodbus
import serial

logging.basicConfig()
log = logging.getLogger(__file__)


adam = minimalmodbus.Instrument(
    port="/dev/serial0",
    slaveaddress=17,
    debug=False
)

adam.serial.baudrate = 9600
adam.serial.bytesize = 8
adam.serial.parity = serial.PARITY_NONE
adam.serial.stopbits = 1
adam.serial.timeout = 1

REG_MODE = 0
REG_CURRENT_POSITION = 2
REG_FINAL_POSITION = 4
REG_SPINDLE_POSITION = 6
REG_X_POSITION_UNITS = 7
REG_ACCELERATION = 11


def set_final_position(final_position_steps: int):
    try:
        values = [
            final_position_steps & 0xFFFF,
            final_position_steps >> 16 & 0xFFFF
        ]
        adam.write_registers(REG_FINAL_POSITION, values)
    except Exception as e:
        log.exception(e.__str__())


def set_acceleration(value: int):
    try:
        adam.write_register(REG_ACCELERATION, value)
    except Exception as e:
        log.exception(e.__str__())


def get_final_position() -> int or None:
    try:
        value = adam.read_register(REG_FINAL_POSITION)
        value = value + adam.read_register(REG_FINAL_POSITION + 1) << 16
        return ctypes.c_long(value).value
    except Exception as e:
        log.exception(e.__str__())
        return None


def get_current_position() -> int or None:
    try:
        value = adam.read_register(REG_CURRENT_POSITION)
        value = value + (adam.read_register(REG_CURRENT_POSITION + 1) << 16)
        return ctypes.c_long(value).value
    except Exception as e:
        log.exception(e.__str__())
        return None


def get_acceleration() -> int or None:
    try:
        value = adam.read_register(REG_ACCELERATION, 0)
        return value
    except Exception as e:
        log.exception(e.__str__())
        return None


if __name__ == '__main__':
    while True:
        print(f"Current position: {get_current_position()}")
        destination = input("Destination: ")
        acc = input("Acceleration: ")
        set_acceleration(int(acc))
        set_final_position(int(destination))
        cur = get_current_position()
        while cur != int(destination):
            cur = get_current_position()
            print(f"Current Position: {cur}, acc: {get_acceleration()}")
            time.sleep(.01)

