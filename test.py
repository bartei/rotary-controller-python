import logging
import time

import minimalmodbus
import serial

logging.basicConfig()
log = logging.getLogger(__file__)


adam = minimalmodbus.Instrument(
    port="/dev/serial0",
    slaveaddress=17,
    debug=False
)

adam.serial.baudrate = 38400
adam.serial.bytesize = 8
adam.serial.parity = serial.PARITY_NONE
adam.serial.stopbits = 1
adam.serial.timeout = 1

REG_MODE = 0
REG_CURRENT_POSITION = 1
REG_FINAL_POSITION = 2
REG_SPINDLE_POSITION = 3
REG_X_POSITION_UNITS = 4
REG_X_POSITION_DECIMALS = 5
REG_SPARE_1 = 6
REG_SPARE_2 = 7


def set_final_position(final_position_steps: int):
    try:
        adam.write_string(0, b''.decode(encoding="LATIN1"))
        adam.write_register(REG_FINAL_POSITION, final_position_steps)
    except Exception as e:
        log.exception(e.__str__())


def get_final_position() -> int or None:
    try:
        value = adam.read_register(REG_FINAL_POSITION)
        return value
    except Exception as e:
        log.exception(e.__str__())
        return None


def get_current_position() -> int or None:
    try:
        value = adam.read_register(REG_CURRENT_POSITION)
        return value
    except Exception as e:
        log.exception(e.__str__())
        return None


if __name__ == '__main__':
    import struct
    values = adam.read_string(0, 8)
    converted_values = struct.unpack(">HllHl", bytes(values, encoding="LATIN1"))
    print(converted_values)
    while True:
        destination = input("Destination")
        set_final_position(int(destination))
        while get_current_position() != int(destination):
            print(f"Current Position: {get_current_position()}")
            time.sleep(.1)
    # try:
    #     adam.write_register(0, new_value)
    #     (
    #         mode,
    #         current_position,
    #         final_position,
    #         spindle_position,
    #         x_position_units,
    #         x_position_decimals,
    #         spare_1,
    #         spare_2
    #     ) = adam.read_registers(0, 8)
    #
    #     if read_back == new_value:
    #         # pass
    #         print(f"OK: {read_back}")
    #     else:
    #         print(f"ERROR: {read_back} != {new_value}")
    # except Exception as e:
    #     print(f"Error: {e.__str__()}")
    #     pass
