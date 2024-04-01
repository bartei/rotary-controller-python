import logging
import minimalmodbus

from rotary_controller_python.utils.addresses import GlobalAddresses, SCALES_COUNT

log = logging.getLogger(__name__)


class DeviceManager:
    def __init__(
        self, serial_device="/dev/ttyUSB0", baudrate=57600, address=17, debug=False
    ):
        from rotary_controller_python.utils.devices import (
            Global,
            Index,
            Servo,
            Scale,
            FastData,
        )

        self.addresses = GlobalAddresses(0)
        self.base = Global(device=self, base_address=self.addresses.base_address)
        self.index = Index(
            device=self, base_address=self.addresses.index_structure_offset.base_address
        )
        self.servo = Servo(
            device=self, base_address=self.addresses.servo_structure_offset.base_address
        )
        self.scales = []
        for i in range(SCALES_COUNT):
            self.scales.append(
                Scale(device=self, base_address=self.addresses.scales[i].base_address)
            )
        self.fast_data = FastData(
            device=self, base_address=self.scales[SCALES_COUNT - 1].addresses.end
        )

        try:
            self.device: minimalmodbus.Instrument = minimalmodbus.Instrument(
                port=serial_device, slaveaddress=address, debug=debug
            )
            self.device.serial.timeout = 0.1
            self.device.serial.write_timeout = 0.1
            self.device.serial.baudrate = baudrate
            self.connected = True
        except Exception as e:
            log.error(e.__str__())
            self.connected = False
