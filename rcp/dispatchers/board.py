from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty

from rcp.utils.communication import ConnectionManager

from kivy.logger import Logger
log = Logger.getChild(__name__)


class Board(EventDispatcher):
    connected = BooleanProperty(False)
    update_tick = NumericProperty(0)
    blink = BooleanProperty(False)

    def __init__(self, config=None, **kv):
        super().__init__(**kv)
        self.fast_data_values = dict()
        self.connection_manager = None
        self.device = None
        self.task_update = None

        serial_port = "/dev/serial0"
        baudrate = 115200
        address = 17

        if config is not None:
            try:
                serial_port = config.get("device", "serial_port")
            except Exception:
                pass
            try:
                baudrate = int(config.get("device", "baudrate"))
            except Exception:
                pass
            try:
                address = int(config.get("device", "address"))
            except Exception:
                pass

        try:
            self.connection_manager = ConnectionManager(
                serial_device=serial_port,
                baudrate=baudrate,
                address=address,
            )
            self.device = self.connection_manager['Global']
        except Exception as e:
            log.error(f"Communication cannot be started, will try again: {str(e)}")

        self.task_update = Clock.schedule_interval(self.update, 1.0 / 30)
        Clock.schedule_interval(self.blinker, 1.0 / 4)

    def update(self, *args):
        if self.connection_manager is None or self.device is None:
            return

        try:
            self.fast_data_values = self.device['fastData'].refresh()
        except Exception as e:
            log.error(f"No connection: {str(e)}")
            self.task_update.timeout = 2.0
            self.connection_manager.connected = False

        # Handle state change connected -> disconnected
        if not self.connection_manager.connected:
            self.connected = self.connection_manager.connected
            self.task_update.timeout = 2.0
            self.update_tick = (self.update_tick + 1) % 100

        # Handle state change disconnected -> connected
        if not self.connected and self.connection_manager.connected:
            self.task_update.timeout = 1.0 / 30
            self.connected = self.connection_manager.connected

        if self.connection_manager.connected:
            self.update_tick = (self.update_tick + 1) % 100

        self.connected = self.connection_manager.connected

    def blinker(self, *args):
        self.blink = not self.blink
