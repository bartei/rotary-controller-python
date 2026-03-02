from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty

from rcp.components.appsettings import config
from rcp.utils.communication import ConnectionManager

from kivy.logger import Logger
log = Logger.getChild(__name__)


class Board(EventDispatcher):
    connected = BooleanProperty(False)
    update_tick = NumericProperty(0)
    blink = BooleanProperty(False)
    device = ObjectProperty(None, allownone=True)

    def __init__(self, **kv):
        super().__init__(**kv)
        self.fast_data_values = dict()

        serial_port = config.getdefault("device", "serial_port", "/dev/serial0")
        baudrate = int(config.getdefault("device", "baudrate", 115200))
        address = int(config.getdefault("device", "address", 17))

        self.connection_manager = ConnectionManager(
            serial_device=serial_port,
            baudrate=baudrate,
            address=address,
        )
        self.device = self.connection_manager['Global']
        self.connection_manager.connect()

        self.task_update = Clock.schedule_interval(self.update, 1.0 / 30)
        Clock.schedule_interval(self.blinker, 1.0 / 4)

    def update(self, *args):
        if not self.connection_manager.connected:
            self.connection_manager.connect()

        if not self.connection_manager.connected:
            self.connected = False
            self.task_update.timeout = 2.0
            self.update_tick = (self.update_tick + 1) % 100
            return

        try:
            self.fast_data_values = self.device['fastData'].refresh()
        except Exception as e:
            log.error(f"No connection: {str(e)}")
            self.connection_manager.connected = False
            self.connected = False
            self.task_update.timeout = 2.0
            self.update_tick = (self.update_tick + 1) % 100
            return

        # Handle state change disconnected -> connected
        if not self.connected and self.connection_manager.connected:
            self.task_update.timeout = 1.0 / 30

        self.connected = self.connection_manager.connected
        self.update_tick = (self.update_tick + 1) % 100

    def blinker(self, *args):
        self.blink = not self.blink
