"""
Unit tests for compound infeed mode calculations.

Covers:
- _get_compound_angle_degrees: all thread types, offset subtraction
- _get_compound_z_offset_encoder: outer/inner magnitude equality, zero at surface, known value
- Direction: saddle shift sign for RHT/LHT and positive/negative scale
- _get_threading_servo_delta_steps: recalculated per pass, decreases when saddle shifts
- Stop-overshoot guard in _send_thread_latch
"""

from math import radians, tan
from fractions import Fraction
from unittest.mock import MagicMock

import pytest

from tests.components.home.assisted_threading.conftest import make_wizard
from rcp.components.home.assisted_threading.thread_type import ThreadType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _w_compound(
    thread_type: str = "ISO Metric",
    offset_degrees: float = 1.0,
    cross_encoderCurrent: int = 0,
    material_width: int = 0,
    inner_thread: bool = False,
    left_hand_thread: bool = False,
    ratioNum: int = 1,
    ratioDen: int = 6926,
):
    """Wizard with compound infeed enabled."""
    wizard, bar, saddle_inp, cross_inp, app = make_wizard(
        ratioNum=ratioNum,
        ratioDen=ratioDen,
        cross_encoderCurrent=cross_encoderCurrent,
        inner_thread=inner_thread,
        left_hand_thread=left_hand_thread,
    )
    bar.thread_profile_type = thread_type
    bar.compound_infeed_mode = True
    bar.compound_infeed_offset_degrees = offset_degrees
    bar.material_width = material_width
    return wizard, bar, saddle_inp, cross_inp, app


# ---------------------------------------------------------------------------
# 1. _get_compound_angle_degrees
# ---------------------------------------------------------------------------

class TestGetCompoundAngleDegrees:
    def test_iso_metric_default_offset(self):
        """ISO Metric: half-angle=30°, offset=1° → effective=29°."""
        wizard, bar, *_ = _w_compound("ISO Metric", offset_degrees=1.0)
        assert wizard._get_compound_angle_degrees() == pytest.approx(29.0)

    def test_unified_default_offset(self):
        """Unified: half-angle=30°, offset=1° → effective=29°."""
        wizard, bar, *_ = _w_compound("Unified", offset_degrees=1.0)
        assert wizard._get_compound_angle_degrees() == pytest.approx(29.0)

    def test_whitworth_default_offset(self):
        """Whitworth: half-angle=27.5°, offset=1° → effective=26.5°."""
        wizard, bar, *_ = _w_compound("Whitworth", offset_degrees=1.0)
        assert wizard._get_compound_angle_degrees() == pytest.approx(26.5)

    def test_acme_default_offset(self):
        """ACME: half-angle=14.5°, offset=1° → effective=13.5°."""
        wizard, bar, *_ = _w_compound("ACME", offset_degrees=1.0)
        assert wizard._get_compound_angle_degrees() == pytest.approx(13.5)

    def test_zero_offset(self):
        """Zero offset → effective angle equals the half-angle."""
        wizard, bar, *_ = _w_compound("ISO Metric", offset_degrees=0.0)
        assert wizard._get_compound_angle_degrees() == pytest.approx(30.0)

    def test_max_offset(self):
        """Max slider value (5°) → effective = 25° for ISO Metric."""
        wizard, bar, *_ = _w_compound("ISO Metric", offset_degrees=5.0)
        assert wizard._get_compound_angle_degrees() == pytest.approx(25.0)

    def test_fractional_offset(self):
        """2.5° offset → 27.5° effective for ISO Metric."""
        wizard, bar, *_ = _w_compound("ISO Metric", offset_degrees=2.5)
        assert wizard._get_compound_angle_degrees() == pytest.approx(27.5)


# ---------------------------------------------------------------------------
# 2. _get_compound_z_offset_encoder — magnitude
# ---------------------------------------------------------------------------

class TestGetCompoundZOffsetEncoder:
    def test_disabled_returns_zero(self):
        """compound_infeed_mode=False → always 0."""
        wizard, bar, saddle_inp, cross_inp, app = make_wizard(cross_encoderCurrent=-693)
        bar.material_width = 0
        bar.compound_infeed_mode = False
        bar.compound_infeed_offset_degrees = 1.0
        bar.thread_profile_type = "ISO Metric"
        assert wizard._get_compound_z_offset_encoder() == 0

    def test_at_material_surface_returns_zero(self):
        """Cross-slide at material_width (no depth yet) → ΔZ = 0."""
        wizard, bar, *_ = _w_compound(cross_encoderCurrent=0, material_width=0)
        assert wizard._get_compound_z_offset_encoder() == 0

    def test_outer_and_inner_same_magnitude(self):
        """Inner thread moves X outward (+693), outer moves X inward (-693).
        Physical depth is the same → ΔZ encoder magnitude must be equal."""
        depth_enc = 693  # ~0.1 mm at 6926 counts/mm

        wizard_out, bar_out, *_ = _w_compound(
            cross_encoderCurrent=-depth_enc, material_width=0, inner_thread=False
        )
        wizard_in, bar_in, *_ = _w_compound(
            cross_encoderCurrent=depth_enc, material_width=0, inner_thread=True
        )

        z_outer = wizard_out._get_compound_z_offset_encoder()
        z_inner = wizard_in._get_compound_z_offset_encoder()

        assert z_outer > 0, "Z offset should be positive (applied in threading direction)"
        assert z_inner > 0, "Z offset should be positive (applied in threading direction)"
        assert z_outer == z_inner, (
            f"Outer ({z_outer}) and inner ({z_inner}) Z offsets should be equal magnitude"
        )

    def test_known_value_iso_metric_1mm_0_3mm_depth(self):
        """
        ISO Metric, 1mm pitch, 1° offset → compound angle = 29°.
        X depth = 0.3 mm → ΔX_enc = round(0.3 * 6926) = 2078 counts
        delta_x_mm = 2078 * 1.0 / (6926/1) ≈ 0.3 mm
        ΔZ = 0.3 × tan(29°) ≈ 0.1663 mm
        z_encoder = round(0.1663 * 6926) ≈ 1152
        """
        depth_enc = round(0.3 * 6926)  # outer: moved inward
        wizard, bar, saddle_inp, cross_inp, app = _w_compound(
            thread_type="ISO Metric",
            offset_degrees=1.0,
            cross_encoderCurrent=-depth_enc,
            material_width=0,
            inner_thread=False,
        )

        result = wizard._get_compound_z_offset_encoder()

        delta_z_mm = 0.3 * tan(radians(29.0))
        expected = round(delta_z_mm * 6926)
        assert abs(result - expected) <= 2, (
            f"Expected ~{expected}, got {result}"
        )

    def test_larger_depth_gives_larger_z_offset(self):
        """Deeper X cut → proportionally larger ΔZ."""
        enc_shallow = round(0.1 * 6926)
        enc_deep = round(0.3 * 6926)

        w1, *_ = _w_compound(cross_encoderCurrent=-enc_shallow, material_width=0)
        w2, *_ = _w_compound(cross_encoderCurrent=-enc_deep, material_width=0)

        assert w2._get_compound_z_offset_encoder() > w1._get_compound_z_offset_encoder()

    def test_diameter_mode_gives_half_z_offset(self):
        """Diameter mode: MM_FRACTION includes 2× → must halve delta_x_mm for radial depth."""
        depth_enc = round(0.3 * 6926)

        w_radius, *_ = _w_compound(cross_encoderCurrent=-depth_enc, material_width=0)
        z_radius = w_radius._get_compound_z_offset_encoder()

        w_diameter, *_ = _w_compound(cross_encoderCurrent=-depth_enc, material_width=0)
        w_diameter.app.els.at_cross_slide_diameter_mode = True
        z_diameter = w_diameter._get_compound_z_offset_encoder()

        assert z_radius > 0
        assert z_diameter == pytest.approx(z_radius / 2, abs=2)


# ---------------------------------------------------------------------------
# 2b. _get_compound_z_offset_encoder — retraction past material surface
# ---------------------------------------------------------------------------

class TestCompoundZOffsetRetraction:
    def test_outer_retracted_past_surface_returns_zero(self):
        """Outer thread: cross-slide moved outward past material_width (positive encoder,
        opposite to cutting direction) → no compound shift."""
        depth_enc = round(0.3 * 6926)
        # Outer thread with positive ratioNum: cutting direction is inward (negative encoder).
        # Moving outward (+depth_enc) is a retraction past the surface.
        wizard, bar, *_ = _w_compound(
            cross_encoderCurrent=depth_enc, material_width=0, inner_thread=False
        )
        assert wizard._get_compound_z_offset_encoder() == 0

    def test_inner_retracted_past_surface_returns_zero(self):
        """Inner thread: cross-slide moved inward past material_width (negative encoder,
        opposite to cutting direction) → no compound shift."""
        depth_enc = round(0.3 * 6926)
        # Inner thread with positive ratioNum: cutting direction is outward (positive encoder).
        # Moving inward (-depth_enc) is a retraction past the surface.
        wizard, bar, *_ = _w_compound(
            cross_encoderCurrent=-depth_enc, material_width=0, inner_thread=True
        )
        assert wizard._get_compound_z_offset_encoder() == 0


# ---------------------------------------------------------------------------
# 3. Direction: ΔZ applied in saddle threading direction
# ---------------------------------------------------------------------------

class TestCompoundZDirection:
    def test_rht_positive_scale_z_applied_in_negative_direction(self):
        """RHT + positive scale → effective_dir = -1 → target = start + (-1 * z_offset)."""
        depth_enc = round(0.3 * 6926)
        wizard, bar, saddle_inp, *_ = _w_compound(
            cross_encoderCurrent=-depth_enc, material_width=0,
            left_hand_thread=False, ratioNum=1, ratioDen=6926,
        )
        bar.start_position = 0

        z_offset = wizard._get_compound_z_offset_encoder()
        effective_dir = wizard._get_saddle_scale_effective_dir()

        target = bar.start_position + effective_dir * z_offset
        assert target < bar.start_position, (
            f"RHT saddle should move negative (toward chuck), got target={target}"
        )

    def test_lht_positive_scale_z_applied_in_positive_direction(self):
        """LHT + positive scale → effective_dir = +1 → target = start + (+1 * z_offset)."""
        depth_enc = round(0.3 * 6926)
        wizard, bar, saddle_inp, *_ = _w_compound(
            cross_encoderCurrent=-depth_enc, material_width=0,
            left_hand_thread=True, ratioNum=1, ratioDen=6926,
        )
        bar.start_position = 0

        z_offset = wizard._get_compound_z_offset_encoder()
        effective_dir = wizard._get_saddle_scale_effective_dir()

        target = bar.start_position + effective_dir * z_offset
        assert target > bar.start_position, (
            f"LHT saddle should move positive (away from chuck), got target={target}"
        )

    def test_rht_negative_scale_z_applied_in_positive_direction(self):
        """RHT + negative scale → effective_dir = +1.
        With ratioNum=-1 on outer threading, cross_dir = +1, so encoder must
        INCREASE to cut deeper. Use +depth_enc to represent a real cutting depth."""
        depth_enc = round(0.3 * 6926)
        wizard, bar, *_ = _w_compound(
            cross_encoderCurrent=+depth_enc, material_width=0,
            left_hand_thread=False, ratioNum=-1, ratioDen=6926,
        )
        bar.start_position = 0

        z_offset = wizard._get_compound_z_offset_encoder()
        effective_dir = wizard._get_saddle_scale_effective_dir()

        target = bar.start_position + effective_dir * z_offset
        assert target > bar.start_position


# ---------------------------------------------------------------------------
# 4. threadRemainingSteps recalculated per pass
# ---------------------------------------------------------------------------

class TestThreadRemainingStepsRecalculated:
    def test_steps_from_start_to_stop(self):
        """Saddle at start_position=0, stop=-6926 (1 mm). With equal ratios,
        delta_steps == delta_enc."""
        wizard, bar, saddle_inp, *_ = make_wizard(ratioNum=1, ratioDen=6926)
        wizard.servo.ratioNum = 1
        wizard.servo.ratioDen = 6926
        saddle_inp.encoderCurrent = 0
        bar.start_position = 0
        bar.stop_position = -6926

        result = wizard._get_threading_servo_delta_steps()

        assert result == -6926

    def test_steps_decrease_when_saddle_shifted_toward_stop(self):
        """After a ΔZ move, saddle is closer to stop → threadRemainingSteps smaller."""
        wizard, bar, saddle_inp, *_ = make_wizard(ratioNum=1, ratioDen=6926)
        wizard.servo.ratioNum = 1
        wizard.servo.ratioDen = 6926
        bar.stop_position = -6926

        saddle_inp.encoderCurrent = 0
        steps_before = wizard._get_threading_servo_delta_steps()

        saddle_inp.encoderCurrent = -100  # shifted 100 counts toward stop
        steps_after = wizard._get_threading_servo_delta_steps()

        assert abs(steps_after) < abs(steps_before), (
            f"Steps should decrease after Z shift: before={steps_before}, after={steps_after}"
        )

    def test_steps_change_proportional_to_z_shift(self):
        """Step delta difference equals the encoder shift."""
        wizard, bar, saddle_inp, *_ = make_wizard(ratioNum=1, ratioDen=6926)
        wizard.servo.ratioNum = 1
        wizard.servo.ratioDen = 6926
        bar.stop_position = -100_000

        saddle_inp.encoderCurrent = 0
        steps_before = wizard._get_threading_servo_delta_steps()

        shift = 500
        saddle_inp.encoderCurrent = -shift
        steps_after = wizard._get_threading_servo_delta_steps()

        assert abs(steps_before) - abs(steps_after) == shift


# ---------------------------------------------------------------------------
# 5. Stop-overshoot guard in _send_thread_latch
# ---------------------------------------------------------------------------

class TestStopOvershootGuard:
    def _wizard_for_latch(self, saddle_current: int, stop_position: int, left_hand_thread: bool = False):
        wizard, bar, saddle_inp, cross_inp, app = make_wizard(
            ratioNum=1, ratioDen=6926, left_hand_thread=left_hand_thread
        )
        wizard.servo.ratioNum = 1
        wizard.servo.ratioDen = 6926
        saddle_inp.encoderCurrent = saddle_current
        bar.start_position = 0
        bar.stop_position = stop_position
        bar.compound_infeed_mode = False  # guard is mode-independent
        wizard._threading_started = False
        wizard._threading_active_confirmed = False
        return wizard, bar, app

    def test_no_guard_when_saddle_before_stop(self):
        """Saddle at 0, stop at -6926 (RHT) → remaining > 0, no popup."""
        from rcp.components.widgets.custom_popup import CustomPopup
        CustomPopup.reset_mock()

        wizard, bar, app = self._wizard_for_latch(0, -6926)
        app.board.device = MagicMock()
        wizard._send_thread_latch()

        CustomPopup.assert_not_called()

    def test_guard_triggers_when_saddle_at_stop(self):
        """Saddle exactly at stop → remaining == 0 → popup shown."""
        from rcp.components.widgets.custom_popup import CustomPopup
        CustomPopup.reset_mock()

        wizard, bar, app = self._wizard_for_latch(-6926, -6926)
        app.board.device = MagicMock()
        wizard._send_thread_latch()

        CustomPopup.assert_called_once()

    def test_guard_triggers_when_saddle_past_stop(self):
        """Saddle past stop (RHT: more negative than stop) → popup shown."""
        from rcp.components.widgets.custom_popup import CustomPopup
        CustomPopup.reset_mock()

        wizard, bar, app = self._wizard_for_latch(-7000, -6926)
        app.board.device = MagicMock()
        wizard._send_thread_latch()

        CustomPopup.assert_called_once()
