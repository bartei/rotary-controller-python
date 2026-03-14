"""
AxisDispatcher — abstraction layer between raw scale inputs and the UI.

An axis derives its value from one or more ScaleDispatchers via an
AxisTransform (linear combination). It exposes scaledPosition,
formattedPosition, sync ratio management, and offset management to
the UI, replacing the direct ScaleDispatcher → CoordBar mapping.
"""

from fractions import Fraction

from kivy.logger import Logger
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)

from rcp.dispatchers.axis_transform import AxisTransform
from rcp.dispatchers.saving_dispatcher import SavingDispatcher

log = Logger.getChild(__name__)


class AxisDispatcher(SavingDispatcher):
    _save_class_name = "Axis"

    # ── Persisted properties ─────────────────────────────────────────
    axis_name = StringProperty("?")
    axis_index = NumericProperty(0)
    syncRatioNum = NumericProperty(360)
    syncRatioDen = NumericProperty(100)
    spindleMode = BooleanProperty(False)
    offsets = ListProperty([0 for _ in range(100)])

    # ── Transient properties (skip save) ─────────────────────────────
    scaledPosition = NumericProperty(0)
    formattedPosition = StringProperty("--")
    formattedSpeed = StringProperty("--")
    speed = NumericProperty(0)
    syncEnable = BooleanProperty(False)

    _skip_save = [
        "scaledPosition",
        "formattedPosition",
        "formattedSpeed",
        "speed",
        "syncEnable",
    ]
    _force_save = ["offsets"]

    # transform_config is saved/loaded manually (not a Kivy property)

    def __init__(self, board, formats, servo, offset_provider, scales, transform=None, **kv):
        self.board = board
        self.formats = formats
        self.servo = servo
        self.offset_provider = offset_provider
        self.scales = scales
        self._transform = transform or AxisTransform.identity(0)

        super().__init__(**kv)

        # Load persisted transform config after SavingDispatcher.__init__
        # reads settings (which may populate transform_config)
        self._load_transform_config()

        # Bindings
        self.offset_provider.bind(currentOffset=self._update_position)
        self.formats.bind(factor=self._update_position)
        self.formats.bind(factor=self._set_sync_ratio)
        self.board.bind(update_tick=self._on_update_tick)
        self.board.bind(connected=self._init_connection)
        self.bind(syncRatioNum=self._set_sync_ratio)
        self.bind(syncRatioDen=self._set_sync_ratio)
        self.bind(spindleMode=self._propagate_spindle_mode)

        self._propagate_spindle_mode()
        self._update_position()

    # ── Transform management ─────────────────────────────────────────

    @property
    def transform(self) -> AxisTransform:
        return self._transform

    @transform.setter
    def transform(self, value: AxisTransform):
        self._transform = value
        self._propagate_spindle_mode()
        self._save_transform_config()
        self._update_position()

    def _propagate_spindle_mode(self, *args):
        """Push spindleMode to the primary scale for correct speed/position computation."""
        primary_idx = self._transform.primary_input
        if primary_idx < len(self.scales):
            self.scales[primary_idx].spindleMode = self.spindleMode

    def _load_transform_config(self):
        """Load transform from persisted YAML (if available)."""
        config = self._read_extra_config("transform_config")
        if config:
            try:
                self._transform = AxisTransform.from_dict(config)
            except (KeyError, ValueError) as e:
                log.error(f"Failed to load transform config for axis {self.axis_name}: {e}")

    def _save_transform_config(self):
        """Persist the transform config to the YAML file."""
        self._write_extra_config("transform_config", self._transform.to_dict())

    def _read_extra_config(self, key: str):
        """Read extra config from the YAML settings file."""
        from rcp.dispatchers.saving_dispatcher import read_settings
        data = read_settings(self.filename)
        if data and key in data:
            return data[key]
        return None

    def _write_extra_config(self, key: str, value):
        """Write extra config into the YAML settings file."""
        from rcp.dispatchers.saving_dispatcher import read_settings, write_settings
        data = read_settings(self.filename) or {}
        data[key] = value
        write_settings(self.filename, data, triggered_by=key)

    # ── Connection ───────────────────────────────────────────────────

    def _init_connection(self, *args, **kv):
        primary_idx = self._transform.primary_input
        if primary_idx < len(self.scales):
            self.syncEnable = self.board.device['scales'][primary_idx]['syncEnable']
        self._set_sync_ratio()

    # ── Tick / position update ───────────────────────────────────────

    def _on_update_tick(self, *args, **kv):
        self._update_position()

    def _update_position(self, *args, **kv):
        try:
            # Gather scaledPosition from contributing scales
            scale_positions = {}
            for c in self._transform.contributions:
                idx = c.input_index
                if idx < len(self.scales):
                    scale_positions[idx] = self.scales[idx].scaledPosition

            # Compute axis value through the transform
            raw_axis_value = self._transform.compute(scale_positions)

            # Apply axis-level offset
            current_offset = self.offset_provider.currentOffset
            raw_axis_value += self.offsets[current_offset]

            self.scaledPosition = raw_axis_value

            # Derive speed from primary scale
            primary_idx = self._transform.primary_input
            if primary_idx < len(self.scales):
                self.speed = self.scales[primary_idx].speed

            # Format — only update StringProperty when text actually changes
            # to avoid triggering Kivy texture regeneration on every tick
            if self.spindleMode:
                fp = self.formats.angle_speed_format.format(self.speed)
                fs = self.formats.position_format.format(self.scaledPosition)
            else:
                fp = self.formats.position_format.format(self.scaledPosition)
                fs = self.formats.speed_format.format(self.speed)
            if fp != self.formattedPosition:
                self.formattedPosition = fp
            if fs != self.formattedSpeed:
                self.formattedSpeed = fs
        except Exception as e:
            log.error(f"Error updating axis {self.axis_name}: {e}")

    # ── Sync ratio ───────────────────────────────────────────────────

    def _set_sync_ratio(self, *args, **kv):
        if not self.board.connected:
            return

        if self.syncRatioDen == 0:
            self.syncRatioDen = 1

        user_sync = Fraction(self.syncRatioNum, self.syncRatioDen)

        # Decompose through the transform to get per-scale hardware ratios
        hw_ratios = self._transform.decompose_sync_ratio(user_sync)

        # Only write sync to the primary input (hardware constraint)
        primary_idx = self._transform.primary_input
        if primary_idx < len(self.scales):
            scale = self.scales[primary_idx]

            if self.spindleMode:
                scale_ratio = Fraction(scale.ratioNum, scale.ratioDen)
            else:
                scale_ratio = Fraction(scale.ratioNum, scale.ratioDen) * self.formats.factor

            if self.servo.elsMode:
                servo_ratio = Fraction(self.servo.ratioNum, self.servo.ratioDen) * self.formats.factor
            else:
                servo_ratio = Fraction(self.servo.ratioNum, self.servo.ratioDen)

            hw_sync = hw_ratios.get(primary_idx, user_sync)
            final_ratio = scale_ratio * hw_sync / servo_ratio
            self.board.device['scales'][primary_idx]['syncRatioNum'] = final_ratio.numerator
            self.board.device['scales'][primary_idx]['syncRatioDen'] = final_ratio.denominator

    # ── Sync toggle with conflict detection ──────────────────────────

    def toggle_sync(self, all_axes: list | None = None):
        """
        Toggle sync mode for this axis.

        If all_axes is provided, checks for conflicts (shared physical
        inputs across axes with sync enabled). Blocks with warning if
        another axis using the same physical input has sync enabled.
        """
        if not self.board.connected:
            return

        primary_idx = self._transform.primary_input

        # Check for conflicts
        if all_axes and not self.syncEnable:
            for other in all_axes:
                if other is self:
                    continue
                if other.syncEnable and primary_idx in other.transform.input_indices:
                    log.warning(
                        f"Sync conflict: axis '{other.axis_name}' already uses "
                        f"input {primary_idx} with sync enabled. "
                        f"Disable sync on '{other.axis_name}' first."
                    )
                    return

        self.syncEnable = not self.board.device['scales'][primary_idx]['syncEnable']
        self.board.device['scales'][primary_idx]['syncEnable'] = self.syncEnable
        if self.syncEnable:
            self._set_sync_ratio()

    # ── Position set / zero ──────────────────────────────────────────

    def set_current_position(self, value):
        """Set the axis to display the given value by adjusting offsets."""
        current_offset = self.offset_provider.currentOffset

        if current_offset == 0:
            # For offset 0: reverse through the transform to set scale positions
            scale_positions = {}
            for c in self._transform.contributions:
                if c.input_index < len(self.scales):
                    scale_positions[c.input_index] = self.scales[c.input_index].scaledPosition
            new_positions = self._transform.reverse_position_set(value, scale_positions)

            # Set each contributing scale to its new position
            primary_idx = self._transform.primary_input
            if primary_idx < len(self.scales):
                self.scales[primary_idx].set_current_position(
                    new_positions[primary_idx]
                )
            self.offsets[current_offset] = 0
        else:
            # For non-zero offsets: use axis-level offset
            self.offsets[current_offset] = value - (self.scaledPosition - self.offsets[current_offset])
            self.save_settings()

        self._update_position()

    def update_position(self):
        """Show keypad to set a custom position (non-spindle axes only)."""
        if not self.spindleMode:
            from rcp.components.popups.keypad import Keypad
            Keypad().show_with_callback(self.set_current_position, self.scaledPosition)

    def zero_position(self):
        """Zero the axis, saving the current position for undo."""
        self._previous_position = self.scaledPosition
        self.set_current_position(0)

    def undo_zero(self):
        """Restore the position saved before the last zero operation."""
        if hasattr(self, '_previous_position'):
            self.set_current_position(self._previous_position)
