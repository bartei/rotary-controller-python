import logging
import time

from kivy.event import EventDispatcher
from kivy.properties import ConfigParserProperty, NumericProperty, BooleanProperty
from kivy.app import App

from rotary_controller_python.components.appsettings import config
from rotary_controller_python.utils import communication
from rotary_controller_python.utils.communication import DeviceManager
from decimal import Decimal

log = logging.getLogger(__name__)


class ServoData(EventDispatcher):
    name = ConfigParserProperty(defaultvalue="R", section="rotary", key="name", config=config, val_type=str)
    min_speed = ConfigParserProperty(defaultvalue="150.0", section="rotary", key="min_speed", config=config, val_type=float)
    max_speed = ConfigParserProperty(defaultvalue="3600.0", section="rotary", key="max_speed", config=config, val_type=float)
    acceleration = ConfigParserProperty(defaultvalue="5.0", section="rotary", key="acceleration", config=config, val_type=float)
    ratio_num = ConfigParserProperty(defaultvalue="360", section="rotary", key="ratio_num", config=config, val_type=int)
    ratio_den = ConfigParserProperty(defaultvalue="1600", section="rotary", key="ratio_den", config=config, val_type=int)

    current_position = NumericProperty(0.0)
    desired_position = NumericProperty(0.0)

    # Offset to add to the sync and index calculated values
    offset = ConfigParserProperty(defaultvalue="0.0", section="rotary", key="offset", config=config, val_type=float)
    divisions = ConfigParserProperty(defaultvalue="0", section="rotary", key="divisions", config=config, val_type=int)
    index = ConfigParserProperty(defaultvalue="0", section="rotary", key="index", config=config, val_type=int)
    enable = BooleanProperty(False)
    # def on_index(self, instance, value):
    #     self.index = self.index % self.divisions

    def on_desired_position(self, instance, value):
        app = App.get_running_app()
        device: DeviceManager = app.device

        # No device no action!
        if device is None:
            log.error("Merda!")
            return

        try:
            log.warning(f"Update desired position to: {value}")
            device.min_speed = self.min_speed
            device.max_speed = self.max_speed
            device.acceleration = self.acceleration
            device.ratio_num = self.ratio_num
            device.ratio_den = self.ratio_den
            # Send the destination converted to steps
            device.final_position = int(Decimal(value) / Decimal(self.ratio_num) * Decimal(self.ratio_den))
            log.warning(f"Start index mode")
            # Handshake
            log.warning("Raise flag to request index mode")
            device.control = communication.set_bit(device.control, communication.CONTROL_BIT_RQ_INDEX, True)
            while not communication.get_bit(device.status, communication.STATUS_BIT_ACK_INDEX_MODE):
                time.sleep(0.1)
            device.control = communication.set_bit(device.control, communication.CONTROL_BIT_RQ_INDEX, False)
            log.warning("Lower flag to request index mode")

        except Exception as e:
            log.exception(e.__str__())

    def on_index(self, instance, value):
        log.warning(f"Index to: {value}")
        self.desired_position = (360.0 / self.divisions * self.index) + self.offset

    def on_offset(self, instance, value):
        self.desired_position = (360.0 / self.divisions * self.index) + self.offset

    def on_enable(self, instance, value):
        app = App.get_running_app()
        device: DeviceManager = app.device

        if device is None:
            log.error("Merda!")
            return

        try:
            device.enable = value
        except Exception as e:
            log.exception(e.__str__())
