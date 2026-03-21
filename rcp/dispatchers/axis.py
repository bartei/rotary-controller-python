"""
AxisDispatcher — abstraction layer between raw encoder inputs and the UI.

An axis derives its value from one or more InputDispatchers via an
AxisTransform. It owns offsets, formatting, sync ratio management,
speed conversion, and factor (MM/IN) application.

Offsets are stored in ratio-units (pre-factor) so that switching
MM<->IN does not corrupt zeroed positions.
"""

from fractions import Fraction

from kivy.logger import Logger
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
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
    abs_offset = NumericProperty(0)
    offsets = ListProperty([0 for _ in range(100)])

    # ── Transient properties (skip save) ─────────────────────────────
    scaledPosition = NumericProperty(0)
    formattedPosition = StringProperty("--")
    formattedSpeed = StringProperty("--")
    position_unit = StringProperty("")
    speed_unit = StringProperty("")
    speed = NumericProperty(0)
    syncEnable = BooleanProperty(False)

    _skip_save = [
        "scaledPosition",
        "formattedPosition",
        "formattedSpeed",
        "position_unit",
        "speed_unit",
        "speed",
        "syncEnable",
    ]
    _force_save = ["offsets"]

    # transform_config is saved/loaded manually (not a Kivy property)

    def __init__(self, board, formats, servo, offset_provider, inputs, transform=None, **kv):
        self.board = board
        self.formats = formats
        self.servo = servo
        self.offset_provider = offset_provider
        self.inputs = inputs
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

        self._update_position()

    # ── Transform management ─────────────────────────────────────────

    @property
    def transform(self) -> AxisTransform:
        return self._transform

    @transform.setter
    def transform(self, value: AxisTransform):
        self._transform = value
        self._save_transform_config()
        self._update_position()

    def _primary_input(self):
        """Return the primary InputDispatcher, or None if out of range."""
        idx = self._transform.primary_input
        return self.inputs[idx] if idx < len(self.inputs) else None

    def _get_extra_save_data(self) -> dict:
        """Include transform config in every save."""
        return {"transform_config": self._transform.to_dict()}

    def _load_transform_config(self):
        """Load transform from persisted YAML (if available)."""
        from rcp.dispatchers.saving_dispatcher import read_settings
        data = read_settings(self.filename)
        if data and "transform_config" in data:
            try:
                self._transform = AxisTransform.from_dict(data["transform_config"])
            except (KeyError, ValueError) as e:
                log.error(f"Failed to load transform config for axis {self.axis_name}: {e}")

    def _save_transform_config(self):
        """Persist the transform config to the YAML file."""
        self.save_settings()

    # ── Connection ───────────────────────────────────────────────────

    def _init_connection(self, *args, **kv):
        primary_idx = self._transform.primary_input
        if primary_idx < len(self.inputs):
            self.syncEnable = self.board.device['scales'][primary_idx]['syncEnable']
        self._set_sync_ratio()

    # ── Tick / position update ───────────────────────────────────────

    def _steps_per_revolution(self) -> float:
        """Encoder steps per spindle revolution."""
        inp = self._primary_input()
        if inp is None:
            return 0
        den = inp.gear_ratio_den
        if den == 0:
            return inp.encoder_ppr * inp.gear_ratio_num
        return inp.encoder_ppr * inp.gear_ratio_num / den

    def _on_update_tick(self, *args, **kv):
        self._update_position()

    def _raw_axis_value(self) -> float:
        """Current axis value before axis-level offset (in ratio-units)."""
        input_values = {}
        for idx in self._transform.contributions:
            if idx < len(self.inputs):
                input_values[idx] = self.inputs[idx].scaled_value
        return self._transform.compute(input_values)

    def _update_position(self, *args, **kv):
        try:
            raw = self._raw_axis_value()

            # Apply abs calibration offset + tool offset (both in ratio-units)
            current_offset = self.offset_provider.currentOffset
            raw += self.abs_offset + self.offsets[current_offset]

            # Apply factor for display (spindle mode uses degrees, no factor)
            if self.spindleMode:
                spr = self._steps_per_revolution()
                if spr > 0:
                    degrees = (raw / spr) * 360
                    self.scaledPosition = degrees % 360
                else:
                    self.scaledPosition = 0
            else:
                self.scaledPosition = raw * float(self.formats.factor)

            # Derive speed from primary input
            primary_idx = self._transform.primary_input
            if primary_idx < len(self.inputs):
                inp = self.inputs[primary_idx]
                self.speed = self._compute_speed(inp)

            # Format — only update StringProperty when text actually changes
            # to avoid triggering Kivy texture regeneration on every tick
            if self.spindleMode:
                fp = self.formats.angle_speed_format.format(self.speed)
                fs = self.formats.angle_format.format(self.scaledPosition) + "\u00b0"
                pu = "RPM"
                su = ""
            else:
                fp = self.formats.position_format.format(self.scaledPosition)
                fs = self.formats.speed_format.format(self.speed)
                pu = "mm" if self.formats.current_format == "MM" else "in"
                su = ""
            if fp != self.formattedPosition:
                self.formattedPosition = fp
            if fs != self.formattedSpeed:
                self.formattedSpeed = fs
            if pu != self.position_unit:
                self.position_unit = pu
            if su != self.speed_unit:
                self.speed_unit = su
        except Exception as e:
            log.error(f"Error updating axis {self.axis_name}: {e}")

    def _compute_speed(self, inp) -> float:
        """Convert input's steps_per_second to display speed."""
        sps = inp.steps_per_second
        if self.spindleMode:
            spr = self._steps_per_revolution()
            return (sps / spr) * 60 if spr != 0 else 0
        else:
            if inp.stepsPerMM == 0:
                return 0
            # m/min or ft/min depending on format
            if self.formats.current_format == "MM":
                return float(sps * 60 * (1 / inp.stepsPerMM) * (1 / 1000))
            else:
                return float(sps * 60 * (1 / inp.stepsPerMM) * (1 / 1000) * (120 / 254))

    # ── Sync ratio ───────────────────────────────────────────────────

    def _set_sync_ratio(self, *args, **kv):
        if not self.board.connected:
            return

        if self.syncRatioDen == 0:
            self.syncRatioDen = 1

        user_sync = Fraction(self.syncRatioNum, self.syncRatioDen)

        primary_idx = self._transform.primary_input
        if primary_idx < len(self.inputs):
            inp = self.inputs[primary_idx]

            if self.spindleMode:
                scale_ratio = Fraction(
                    360 * inp.gear_ratio_den,
                    inp.encoder_ppr * inp.gear_ratio_num,
                )
            else:
                scale_ratio = Fraction(inp.ratioNum, inp.ratioDen) * self.formats.factor

            if self.servo.elsMode:
                servo_ratio = Fraction(self.servo.ratioNum, self.servo.ratioDen) * self.formats.factor
            else:
                servo_ratio = Fraction(self.servo.ratioNum, self.servo.ratioDen)

            final_ratio = scale_ratio * user_sync / servo_ratio
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
        """Set the axis to display the given value by adjusting offsets.

        Offsets are stored in ratio-units (pre-factor). The value parameter
        is in display-units (post-factor), so we divide by factor first.

        In ABS mode, modifies abs_offset (calibration) so that the change
        applies uniformly across all tool offsets. In INC mode, modifies
        the current tool offset relative to the calibrated position.
        """
        if self.spindleMode:
            spr = self._steps_per_revolution()
            target_ratio_units = value / 360 * spr if spr else value
        else:
            factor = self.formats.factor
            target_ratio_units = value / float(factor) if factor else value

        raw = self._raw_axis_value()
        abs_mode = getattr(self.offset_provider, 'abs_mode', False)

        if abs_mode:
            current_offset = self.offset_provider.currentOffset
            self.abs_offset = target_ratio_units - raw - self.offsets[current_offset]
        else:
            current_offset = self.offset_provider.currentOffset
            self.offsets[current_offset] = target_ratio_units - raw - self.abs_offset

        self.save_settings()
        self._update_position()

    def update_position(self):
        """Show keypad to set a custom position."""
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
