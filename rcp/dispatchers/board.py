import os
from pathlib import Path

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, ListProperty

from rcp.components.appsettings import config
from rcp.dispatchers.axis import AxisDispatcher
from rcp.dispatchers.axis_transform import AxisTransform
from rcp.dispatchers.saving_dispatcher import read_settings
from rcp.dispatchers.scale import ScaleDispatcher
from rcp.dispatchers.servo import ServoDispatcher
from rcp.utils.communication import ConnectionManager

from kivy.logger import Logger
log = Logger.getChild(__name__)


class Board(EventDispatcher):
    connected = BooleanProperty(False)
    update_tick = NumericProperty(0)
    blink = BooleanProperty(False)
    device = ObjectProperty(None, allownone=True)
    servo = ObjectProperty(None, allownone=True)
    scales = ListProperty()
    axes = ListProperty()

    def __init__(self, formats, offset_provider, **kv):
        super().__init__(**kv)
        self.formats = formats
        self.offset_provider = offset_provider
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

        self.servo = ServoDispatcher(board=self, formats=formats, id_override="0")
        for i in range(4):
            self.scales.append(ScaleDispatcher(
                board=self, formats=formats, servo=self.servo,
                offset_provider=offset_provider,
                inputIndex=i, id_override=f"{i}",
            ))

        self._create_axes()

        self.task_update = Clock.schedule_interval(self.update, 1.0 / 30)
        Clock.schedule_interval(self.blinker, 1.0 / 4)

    def _settings_folder(self) -> Path:
        return Path.home() / ".config" / "rotary-controller-python"

    def _create_axes(self):
        """Create AxisDispatchers, migrating from scale configs if needed."""
        settings_folder = self._settings_folder()
        axis_files = sorted(settings_folder.glob("Axis-*.yaml")) if settings_folder.exists() else []

        max_id = -1
        if axis_files:
            # Load existing axes from YAML files
            for f in axis_files:
                # Extract the id_override from filename: "Axis-{id}.yaml"
                axis_id = f.stem.replace("Axis-", "")
                try:
                    max_id = max(max_id, int(axis_id))
                except ValueError:
                    pass
                ax = AxisDispatcher(
                    board=self, formats=self.formats, servo=self.servo,
                    offset_provider=self.offset_provider,
                    scales=list(self.scales),
                    id_override=axis_id,
                )
                self.axes.append(ax)
        else:
            # Migration: create 4 identity axes from existing scale configs
            log.info("No Axis YAML files found — migrating from scale configs")
            for i in range(4):
                scale = self.scales[i]
                ax = AxisDispatcher(
                    board=self, formats=self.formats, servo=self.servo,
                    offset_provider=self.offset_provider,
                    scales=list(self.scales),
                    transform=AxisTransform.identity(i),
                    id_override=f"{i}",
                    axis_name=scale.axisName,
                    axis_index=i,
                    syncRatioNum=scale.syncRatioNum,
                    syncRatioDen=scale.syncRatioDen,
                    spindleMode=scale.spindleMode,
                )
                ax._save_transform_config()
                self.axes.append(ax)
            max_id = 3

        self._next_axis_id = max_id + 1

    def add_axis(self, transform: AxisTransform | None = None, axis_name: str = "?") -> AxisDispatcher:
        """Add a new axis with the given transform (defaults to identity on first unused input)."""
        axis_id = self._next_axis_id
        self._next_axis_id += 1

        if transform is None:
            # Pick first unused scale input
            used_inputs = set()
            for ax in self.axes:
                used_inputs |= ax.transform.input_indices
            available = [i for i in range(len(self.scales)) if i not in used_inputs]
            input_idx = available[0] if available else 0
            transform = AxisTransform.identity(input_idx)

        ax = AxisDispatcher(
            board=self, formats=self.formats, servo=self.servo,
            offset_provider=self.offset_provider,
            scales=list(self.scales),
            transform=transform,
            id_override=f"{axis_id}",
            axis_name=axis_name,
            axis_index=len(self.axes),
        )
        ax._save_transform_config()
        self.axes.append(ax)
        return ax

    def remove_axis(self, axis: "AxisDispatcher"):
        """Remove the given axis and delete its config file."""
        try:
            self.axes.remove(axis)
        except ValueError:
            log.warning(f"Axis '{axis.axis_name}' not found in axes list")
            return
        config_file = axis.filename
        if config_file.exists():
            os.remove(config_file)
            log.info(f"Removed axis config: {config_file}")

    def get_spindle_scale(self):
        filtered = [s for s in self.scales if s.spindleMode is True]
        if len(filtered) != 1:
            return None
        return filtered[0]

    def get_spindle_axis(self):
        """Find the axis with spindleMode=True."""
        filtered = [a for a in self.axes if a.spindleMode is True]
        if len(filtered) != 1:
            return None
        return filtered[0]

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
