from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, ObjectProperty, StringProperty

from rcp.dispatchers.saving_dispatcher import SavingDispatcher
from rcp.utils.devices import SCALES_COUNT, SERVOS_COUNT
from rcp.utils.communication import ConnectionManager

from kivy.logger import Logger
log = Logger.getChild(__name__)


class Scale(EventDispatcher):
    connected = BooleanProperty(False)
    position = NumericProperty(0)
    speed = NumericProperty(0)

    def __init__(self, *, device, **kv):
        super().__init__(**kv)
        self.device = device

    def on_connected(self, instance, value):
        pass


class Servo(EventDispatcher):
    connected = BooleanProperty(False)
    maxSpeed = NumericProperty(0)
    currentSpeed = NumericProperty(0)
    jogSpeed = NumericProperty(0)
    acceleration = NumericProperty(0)
    stepsToGo = NumericProperty(0)
    destinationSteps = NumericProperty(0)
    previousSteps = NumericProperty(0)
    currentSteps = NumericProperty(0)
    desiredSteps = NumericProperty(0)

    currentDirection = NumericProperty(0)
    previousDirection = NumericProperty(0)
    syncEnable = BooleanProperty(False)
    syncScaleIndex = NumericProperty(0)
    syncRatioNum = NumericProperty(0)
    syncRatioDen = NumericProperty(0)

    def __init__(self, *, device, **kv):
        super().__init__(**kv)
        self.device = device

    def on_connected(self, instance, value):
        pass

class Status(EventDispatcher):
    connected = BooleanProperty(False)
    executionInterval = NumericProperty(0)
    executionCycles = NumericProperty(0)
    servoCycles = NumericProperty(0)

    def __init__(self, *, device, **kv):
        super().__init__(**kv)
        self.device = device

    def on_connected(self):
        pass

class FastData(EventDispatcher):
    connected = BooleanProperty(False)
    cycles = NumericProperty(0)
    executionInterval = NumericProperty(0)
    servoMode = NumericProperty(0)
    servoEnable = NumericProperty(0)
    servoCurrent = ListProperty([0 for _ in range(SERVOS_COUNT)])
    servoDesired = ListProperty([0 for _ in range(SERVOS_COUNT)])
    servoSpeed = ListProperty([0 for _ in range(SERVOS_COUNT)])
    stepsToGo = ListProperty([0 for _ in range(SERVOS_COUNT)])
    scaleCurrent = ListProperty([0 for _ in range(SCALES_COUNT)])
    scaleSpeed = ListProperty([0 for _ in range(SCALES_COUNT)])

    def __init__(self, *, device, **kv):
        super().__init__(**kv)
        self.device = device
        self._refresh_clock = Clock.schedule_interval(callback=self.refresh, timeout=1/30)

    def refresh(self, *args, **kv):
        try:
            fast_data = self.device['fastData'].refresh()
            self.stepsToGo = fast_data['stepsToGo']
            self.cycles = fast_data['cycles']
            self.servoEnable = fast_data['servoEnable']
            self.servoMode = fast_data['servoMode']
            self.servoSpeed = fast_data['servoSpeed']
            self.servoCurrent = fast_data['servoCurrent']
            self.servoDesired = fast_data['servoDesired']
            self.executionInterval = fast_data['executionInterval']
            self.scaleCurrent = fast_data['scaleCurrent']
            self.scaleSpeed = fast_data['scaleSpeed']
            self.connected = True
        except Exception as e:
            self.connected = False
            pass


class ConnectionSettings(SavingDispatcher):
    serial_port = StringProperty("/dev/ttyUSB0")


class Board(EventDispatcher):
    scales: list[Scale] = ListProperty()
    servos: list[Servo] = ListProperty()
    status: Status = ObjectProperty()
    fastData: FastData = ObjectProperty()
    connected: bool = BooleanProperty(False)
    connectionSettings: ConnectionSettings = ObjectProperty()

    def __init__(self, **kv):
        super().__init__(**kv)
        self.connectionSettings = ConnectionSettings()
        self.device = ConnectionManager(self.connectionSettings.serial_port)['global']
        self.scales = [Scale(device=self.device) for _ in range(SCALES_COUNT)]
        self.servos = [Servo(device=self.device) for _ in range(SERVOS_COUNT)]
        self.status = Status(device=self.device)
        self.fastData = FastData(device=self.device)
        self.fastData.bind(connected=self.update_connected)

    def update_connected(self, instance, value):
        self.connected = value
        # Explicitly propagate the connected status flag to all the children
        for scale in self.scales:
            scale.connected = value
        for servo in self.servos:
            servo.connected = value
        self.status.connected = value
