from kivy.logger import Logger

from rcp.components.home.assisted_threading.calculations import MM_PER_INCH
from rcp.components.widgets.custom_popup import CustomPopup
from rcp.utils.devices import SCALES_COUNT

log = Logger.getChild(__name__)


class AssistedThreadingSafetyMixin:
    # ---------------------------------------------------------------------------
    # Button condition functions (enable/disable action buttons)
    # ---------------------------------------------------------------------------

    def _is_valid_stop_position(self):
        """Check if the stop position is valid given the start position and thread direction.
         - For right-hand threads, stop must be less than start.
         - For left-hand threads, stop must be greater than start.
         - Stop position must be greater than the backlash cushion distance from start position - if stop is too small, the saddle may not have enough room to cut properly.
         - Depending on sign of the scale ratioNum/ratioDen, this will also affect the calculation"""

        effective_dir = self._get_saddle_scale_effective_dir()
        backlash_cushion = abs(self._get_backlash_cusion_encoder_steps())
        stop = self._get_stop_position_units()
        min_stop = self.bar.start_position + effective_dir * backlash_cushion
        return (stop - min_stop) * effective_dir > 0

    def _is_cross_slide_retracted(self):
        """
        Check if the cross slide is safely retracted when the saddle has moved beyond the threading start position.
        """
        log.debug("Checking if cross slide is retracted for threading start...")

        # --- Saddle direction check (Z axis) ---
        saddle_dir = self._get_saddle_scale_effective_dir()

        saddle_delta = self.saddle_input.encoderCurrent - self.bar.start_position
        saddle_beyond_start = saddle_delta * saddle_dir > 0

        if not saddle_beyond_start:
            log.debug("Saddle is not beyond start position, no need to check cross slide")
            return True

        log.debug("Saddle is beyond start position, checking cross slide retraction")

        # --- Cross-slide retraction check (X axis) ---
        retract_dir = -self._get_cross_slide_scale_effective_dir()

        cross_delta = self.cross_slide_input.encoderCurrent - self.bar.material_width
        return cross_delta * retract_dir > 0

    def _is_cross_slide_at_final_cutting_depth(self):
        """Check if the cross slide is at or more than the final cutting depth position."""
        effective_dir = self._get_cross_slide_scale_effective_dir()
        current = self.cross_slide_input.encoderCurrent
        log.info(f"Checking if at cutting depth: last_cutting_depth={self.bar.last_cutting_depth}, cutting_depth={self.bar.cutting_depth}, effective_dir={effective_dir}")
        return (self.bar.last_cutting_depth - self.bar.cutting_depth) * effective_dir >= 0

    # ---------------------------------------------------------------------------
    # Pre-threading safety checks
    # ---------------------------------------------------------------------------

    def _check_saddle_not_past_stop(self) -> bool:
        """Return True if the saddle has not moved past (or to) the stop position.
        Protects against the compound infeed ΔZ shift consuming all remaining thread length.
        Shows a warning popup and redirects to step 6 if not."""
        effective_dir = self._get_saddle_scale_effective_dir()
        current_saddle = self.saddle_input.encoderCurrent
        remaining = (self.bar.stop_position - current_saddle) * effective_dir
        if remaining <= 0:
            log.warning(
                f"Saddle at or past stop position "
                f"(current={current_saddle}, stop={self.bar.stop_position}, "
                f"effective_dir={effective_dir}) — aborting threading"
            )
            CustomPopup(
                title="Warning",
                message="Compound infeed shift has consumed the remaining thread length. "
                        "Reduce infeed depth or increase thread start clearance.",
                button_text="Got it",
                on_dismiss_callback=lambda: self.goto_step(5),
            ).open()
            return False
        return True

    def _check_valid_start_position(self) -> bool:
        """Return True if the saddle is within the backlash cushion of the start position.
        Shows a warning popup and redirects to step 6 if not. Sanity check in case the
        start_position_preloaded flag was bypassed or the saddle moved after preload."""
        backlash_cushion = abs(self._get_backlash_cusion_encoder_steps())
        log.info(
            f"Validating start position: current={self.saddle_input.encoderCurrent}, "
            f"start={self.bar.start_position}, "
            f"backlash_cushion={backlash_cushion}"
        )
        delta = abs(self.saddle_input.encoderCurrent - self.bar.start_position)
        if delta > backlash_cushion:
            message = (
                "Not at valid start position including backlash cushion. "
                "Aborting threading operation. Go back to start position."
            )
            log.warning(message)
            CustomPopup(
                title="Warning",
                message=message,
                button_text="Got it",
                on_dismiss_callback=lambda: self.goto_step(5),
            ).open()
            return False
        return True

    def _check_spindle_turning_forward(self) -> bool:
        """Return True if the spindle scale exists and is turning in the right/positive/CCW direction.
        Shows a warning popup and redirects to step 6 if not."""
        spindle_axis = self.app.els.get_spindle_axis()
        spindle_inp = spindle_axis._primary_input() if spindle_axis is not None else None
        if spindle_inp is None:
            log.warning("No spindle scale configured — cannot verify spindle direction")
            CustomPopup(
                title="Warning",
                message="No spindle scale configured. Cannot verify spindle is turning.",
                button_text="Got it",
                on_dismiss_callback=lambda: self.goto_step(5),
            ).open()
            return False

        spindle_speed = self.app.board.fast_data_values.get('scaleSpeed', [0] * SCALES_COUNT)[spindle_inp.inputIndex]
        log.info(f"Validating spindle direction: scaleSpeed[{spindle_inp.inputIndex}]={spindle_speed}")

        if spindle_speed <= 0:
            message = (
                "Spindle is not turning in the right/positive/CCW direction. "
                "Ensure the spindle is running forward before starting the threading operation."
            )
            log.warning(message)
            CustomPopup(
                title="Warning",
                message=message,
                button_text="Got it",
                on_dismiss_callback=lambda: self.goto_step(5),
            ).open()
            return False
        return True

    def _check_spindle_speed_for_pitch(self) -> bool:
        """Return True if the current spindle RPM is within the servo's speed limit
        for the selected pitch. Shows a warning popup and redirects to step 6 if not."""
        from fractions import Fraction

        spindle_axis = self.app.els.get_spindle_axis()
        spindle_inp = spindle_axis._primary_input() if spindle_axis is not None else None
        if spindle_inp is None:
            return True  # already caught by _check_spindle_turning_forward

        spindle_steps_per_sec = self.app.board.fast_data_values.get('scaleSpeed', [0] * SCALES_COUNT)[spindle_inp.inputIndex]

        try:
            pitch_str = self.bar.selected_pitch.strip()
            if not pitch_str:
                return True  # no pitch selected yet — skip
            pitch_val = float(pitch_str)
        except ValueError:
            log.warning(f"Cannot parse selected_pitch={self.bar.selected_pitch!r} — skipping speed check")
            return True

        if self.bar.metric_mode:
            pitch_mm = pitch_val
        else:
            if pitch_val == 0:
                return True
            pitch_mm = MM_PER_INCH / pitch_val  # TPI → mm/rev

        spindle_rev_per_sec = spindle_steps_per_sec / spindle_inp.ratioDen
        feed_mm_per_sec = spindle_rev_per_sec * pitch_mm
        encoder_steps_per_sec = feed_mm_per_sec * self.saddle_input.stepsPerMM

        scale_ratio = Fraction(abs(self.saddle_input.ratioNum), abs(self.saddle_input.ratioDen))
        servo_ratio = Fraction(abs(self.servo.ratioNum), abs(self.servo.ratioDen))
        required = float(encoder_steps_per_sec * scale_ratio / servo_ratio)

        steps_per_mm_per_rev = pitch_mm * self.saddle_input.stepsPerMM * float(scale_ratio / servo_ratio)
        max_rpm = (self.app.els.at_threading_max_speed / steps_per_mm_per_rev) * 60 if steps_per_mm_per_rev > 0 else 0

        log.info(
            f"Spindle speed check: spindle={spindle_steps_per_sec} steps/s, "
            f"pitch={pitch_mm:.4f} mm, feed={feed_mm_per_sec:.4f} mm/s, "
            f"required_servo={required:.1f} steps/s, max={self.app.els.at_threading_max_speed}, "
            f"max_rpm={max_rpm:.1f}, greater={required > self.app.els.at_threading_max_speed}"
        )

        if required > self.app.els.at_threading_max_speed:
            spindle_rpm = spindle_rev_per_sec * 60
            pitch_label = f"{pitch_mm:.3g} mm" if self.bar.metric_mode else f"{self.bar.selected_pitch} TPI"
            message = (
                f"Spindle speed ({spindle_rpm:.0f} RPM) is too fast for {pitch_label} pitch. "
                f"Required servo speed ({required:.0f} steps/s) exceeds the threading limit "
                f"({self.app.els.at_threading_max_speed} steps/s). "
                f"Max allowed spindle speed for this pitch is {max_rpm:.0f} RPM. "
                "Reduce spindle speed or increase the threading max speed limit."
            )
            log.warning(message)
            CustomPopup(
                title="Warning",
                message=message,
                button_text="Got it",
                on_dismiss_callback=lambda: self.goto_step(5),
            ).open()
            return False
        return True
