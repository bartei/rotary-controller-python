"""
Unit tests for AssistedThreadingCalculationsMixin methods.
"""

from fractions import Fraction
from unittest.mock import MagicMock

import pytest

from tests.components.home.assisted_threading.conftest import make_wizard


# ---------------------------------------------------------------------------
# 1. _convert_distance_units_to_encoder
# ---------------------------------------------------------------------------

class TestConvertDistanceUnitsToEncoder:
    def test_mm_gives_correct_counts(self):
        """0.1 mm should give ~693 counts (0.1 * 6926)."""
        wizard, _, _, _, app = make_wizard()
        axis = app.els.get_z_axis()
        result = wizard._convert_distance_units_to_encoder(axis, 0.1, is_metric=True)
        assert result == 693  # round(0.1 * 6926)

    def test_non_zero_axis_offset_does_not_contaminate(self):
        """v1.3.0 fix: offset on the AxisDispatcher must NOT affect pure distance
        conversion.  With offset=-12.885 the result should still be ~693."""
        wizard, _, _, _, app = make_wizard()
        axis = app.els.get_z_axis()
        axis.offsets[0] = -12.885
        result = wizard._convert_distance_units_to_encoder(axis, 0.1, is_metric=True)
        assert abs(result) < 1_000, (
            f"Offset contamination: expected ~693, got {result}"
        )

    def test_inch_distance(self):
        """0.1 inch; INCHES_FRACTION=10/254 → counts = 0.1/(10/254)*6926 ≈ 17594."""
        wizard, _, _, _, app = make_wizard(is_metric_format=False)
        axis = app.els.get_z_axis()
        result = wizard._convert_distance_units_to_encoder(axis, 0.1, is_metric=False)
        expected = round(0.1 / (10 / 254) * 6926)
        assert result == expected

    def test_negative_ratio_inverts_direction(self):
        """A negative ratioNum should invert the sign of the result."""
        wizard, _, _, _, app = make_wizard(ratioNum=-1, ratioDen=6926)
        axis = app.els.get_z_axis()
        result = wizard._convert_distance_units_to_encoder(axis, 0.1, is_metric=True)
        # (0.1 / 1.0) * (6926 / -1) = -692.6 → -693
        assert result == -693


# ---------------------------------------------------------------------------
# 2. _get_saddle_scale_effective_dir
# ---------------------------------------------------------------------------

class TestGetSaddleScaleEffectiveDir:
    def test_rht_positive_ratio_gives_minus_one(self):
        wizard, bar, _, _, _ = make_wizard(left_hand_thread=False)
        assert wizard._get_saddle_scale_effective_dir() == -1

    def test_lht_positive_ratio_gives_plus_one(self):
        wizard, bar, _, _, _ = make_wizard(left_hand_thread=True)
        assert wizard._get_saddle_scale_effective_dir() == 1

    def test_rht_negative_ratio_gives_plus_one(self):
        wizard, bar, saddle, _, _ = make_wizard(left_hand_thread=False, ratioNum=-1)
        assert wizard._get_saddle_scale_effective_dir() == 1

    def test_lht_negative_ratio_gives_minus_one(self):
        wizard, bar, saddle, _, _ = make_wizard(left_hand_thread=True, ratioNum=-1)
        assert wizard._get_saddle_scale_effective_dir() == -1


# ---------------------------------------------------------------------------
# 3. _get_cross_slide_scale_effective_dir
# ---------------------------------------------------------------------------

class TestGetCrossSlideScaleEffectiveDir:
    def test_external_thread_positive_ratio_gives_minus_one(self):
        wizard, bar, _, _, _ = make_wizard(inner_thread=False)
        assert wizard._get_cross_slide_scale_effective_dir() == -1

    def test_internal_thread_positive_ratio_gives_plus_one(self):
        wizard, bar, _, _, _ = make_wizard(inner_thread=True)
        assert wizard._get_cross_slide_scale_effective_dir() == 1

    def test_external_thread_negative_ratio_gives_plus_one(self):
        wizard, bar, _, cross, _ = make_wizard(inner_thread=False, ratioNum=-1)
        assert wizard._get_cross_slide_scale_effective_dir() == 1

    def test_internal_thread_negative_ratio_gives_minus_one(self):
        wizard, bar, _, cross, _ = make_wizard(inner_thread=True, ratioNum=-1)
        assert wizard._get_cross_slide_scale_effective_dir() == -1


# ---------------------------------------------------------------------------
# 7. _get_backlash_cushion_encoder_steps / _get_saddle_backlash_distance_encoder_steps
# ---------------------------------------------------------------------------

class TestBacklashEncoderSteps:
    def test_cushion_gives_sane_counts(self):
        """0.1 mm backlash cushion at 6926 counts/mm → ~693 counts."""
        wizard, _, _, _, app = make_wizard()
        app.els.at_backlash_cushion = 0.1
        app.els.at_metric_distances = True

        result = wizard._get_backlash_cusion_encoder_steps()

        assert 600 < abs(result) < 800, f"Expected ~693, got {result}"

    def test_backlash_distance_gives_sane_counts(self):
        """0.5 mm saddle backlash distance → ~3463 counts."""
        wizard, _, _, _, app = make_wizard()
        app.els.at_saddle_backlash_distance = 0.5
        app.els.at_metric_distances = True

        result = wizard._get_saddle_backlash_distance_encoder_steps()

        assert 3000 < abs(result) < 4000, f"Expected ~3463, got {result}"

    def test_axis_offset_does_not_affect_cushion(self):
        """v1.3.0 fix: DRO zero offset must NOT inflate the cushion.
        With offset=-12.885 the result should still be ~693 (not ~89930)."""
        wizard, _, _, _, app = make_wizard()
        app.els.at_backlash_cushion = 0.1
        app.els.at_metric_distances = True
        app.els.get_z_axis().offsets[0] = -12.885

        result = wizard._get_backlash_cusion_encoder_steps()

        assert 600 < abs(result) < 800, (
            f"Offset contamination: expected ~693, got {result}"
        )

    def test_inch_backlash_cushion(self):
        """0.004 inch backlash cushion with inch scale factor → ~704 counts."""
        wizard, _, _, _, app = make_wizard(is_metric_format=False)
        app.els.at_backlash_cushion = 0.004
        app.els.at_metric_distances = False
        # encoder_factor = 10/254 ≈ 0.03937
        # counts = (0.004 / 0.03937) * 6926 ≈ 704
        result = wizard._get_backlash_cusion_encoder_steps()
        assert 600 < abs(result) < 800, f"Expected ~704, got {result}"


# ---------------------------------------------------------------------------
# 8. _get_stop_position_units — live encoder vs manual entry
# ---------------------------------------------------------------------------

class TestGetStopPositionUnits:
    def test_returns_live_encoder_when_no_manual_override(self):
        wizard, _, saddle_inp, _, _ = make_wizard()
        saddle_inp.encoderCurrent = -92812
        wizard.manual_stop_length = None

        assert wizard._get_stop_position_units() == -92812

    def test_manual_override_converts_distance_to_encoder(self):
        """User typed -14.665 mm; initial scaled position = -1.305 mm at
        encoder -90140.  Delta = -13.36 mm → result must be past start in -ve dir."""
        wizard, bar, _, _, app = make_wizard()
        bar.start_position = -90140
        wizard._isStartPositionMetricMode = True
        wizard._startScaledPosition = -1.305
        wizard.manual_stop_length = -14.665
        app.formats.current_format = "MM"
        app.formats.factor = Fraction(1, 1)
        app.formats.MM_FRACTION = Fraction(1, 1)

        result = wizard._get_stop_position_units()

        assert result < bar.start_position, (
            f"Manual stop {result} should be more negative than start {bar.start_position}"
        )


# ---------------------------------------------------------------------------
# 9. _calculate_thread_depth — all thread profiles
# ---------------------------------------------------------------------------

class TestCalculateThreadDepth:
    """Thread depth formulas (radial, metric pitch, metric display)."""

    def _w(self, pitch="1.5", profile="ISO Metric", metric_mode=True,
            diameter_mode=False, is_metric_format=True):
        wizard, bar, _, _, app = make_wizard(metric_mode=metric_mode,
                                             is_metric_format=is_metric_format)
        bar.selected_pitch = pitch
        bar.thread_profile_type = profile
        bar.metric_mode = metric_mode
        app.els.at_cross_slide_diameter_mode = diameter_mode  # moved to els in v1.3.0
        return wizard

    def test_iso_metric_1_5mm(self):
        w = self._w("1.5", "ISO Metric")
        assert abs(w._calculate_thread_depth() - 0.61343 * 1.5) < 0.001

    def test_unified_1_5mm(self):
        w = self._w("1.5", "Unified")
        assert abs(w._calculate_thread_depth() - 0.64952 * 1.5) < 0.001

    def test_whitworth_1_5mm(self):
        w = self._w("1.5", "Whitworth")
        assert abs(w._calculate_thread_depth() - 0.6403 * 1.5) < 0.001

    def test_acme_1_5mm(self):
        w = self._w("1.5", "ACME")
        assert abs(w._calculate_thread_depth() - 0.5 * 1.5) < 0.001

    def test_imperial_16_tpi_iso_metric(self):
        """16 TPI, display in inches → depth converted to inches (÷ 25.4).
        pitch_mm = 25.4/16; depth_in = 0.61343 × pitch_mm / 25.4 = 0.61343/16."""
        w = self._w("16", "ISO Metric", metric_mode=False, is_metric_format=False)
        pitch_mm = 25.4 / 16
        assert abs(w._calculate_thread_depth() - 0.61343 * pitch_mm / 25.4) < 0.001

    def test_diameter_mode_doubles_depth(self):
        w = self._w("1.5", "ISO Metric", diameter_mode=True)
        assert abs(w._calculate_thread_depth() - 0.61343 * 1.5 * 2) < 0.001

    def test_empty_pitch_returns_none(self):
        w = self._w("")
        assert w._calculate_thread_depth() is None

    def test_zero_pitch_returns_none(self):
        w = self._w("0")
        assert w._calculate_thread_depth() is None

    def test_non_numeric_pitch_returns_none(self):
        w = self._w("abc")
        assert w._calculate_thread_depth() is None

    def test_metric_pitch_displayed_in_inches(self):
        """Metric pitch but display in inches: depth converted by /25.4."""
        w = self._w("1.5", "ISO Metric", metric_mode=True, is_metric_format=False)
        depth_mm = 0.61343 * 1.5
        expected_in = depth_mm / 25.4
        assert abs(w._calculate_thread_depth() - expected_in) < 0.0001

    def test_imperial_tpi_displayed_in_mm(self):
        """TPI pitch, display in MM: depth stays in mm (no extra conversion)."""
        w = self._w("16", "ISO Metric", metric_mode=False, is_metric_format=True)
        expected = 0.61343 * (25.4 / 16)
        assert abs(w._calculate_thread_depth() - expected) < 0.001


# ---------------------------------------------------------------------------
# 11. _get_threading_servo_delta_steps
# ---------------------------------------------------------------------------

class TestGetThreadingServoDeltaSteps:
    def test_delta_equals_encoder_difference_when_ratios_equal(self):
        """When scale ratio == servo ratio the delta in servo steps equals
        the delta in encoder counts."""
        wizard, bar, saddle_inp, _, _ = make_wizard(ratioNum=1, ratioDen=6926)
        wizard.servo.ratioNum = 1
        wizard.servo.ratioDen = 6926  # same ratio → conversion factor = 1
        saddle_inp.encoderCurrent = -90140
        bar.stop_position = -92812    # 2672 counts away

        result = wizard._get_threading_servo_delta_steps()

        assert result == -2672

    def test_servo_ratio_scales_result(self):
        """If scale is 1:6926 and servo is 1:1 the servo steps are much smaller
        than encoder counts (factor = 1/6926)."""
        wizard, bar, saddle_inp, _, _ = make_wizard(ratioNum=1, ratioDen=6926)
        wizard.servo.ratioNum = 1
        wizard.servo.ratioDen = 1    # servo 1:1, scale 1:6926
        saddle_inp.encoderCurrent = -90140
        bar.stop_position = -92812   # delta_enc = -2672

        # delta_steps = -2672 * (1/6926) / (1/1) = -2672/6926 ≈ -0.39 → 0
        result = wizard._get_threading_servo_delta_steps()

        assert result == 0


# ---------------------------------------------------------------------------
# 16. Inch-mode coverage — backlash distance in inches
# ---------------------------------------------------------------------------

class TestBacklashEncoderStepsInches:
    """Complement to TestBacklashEncoderSteps — uses at_metric_distances=False."""

    def test_saddle_backlash_distance_in_inches(self):
        """0.02 inch saddle backlash distance.
        factor = 10/254; counts = (0.02 / (10/254)) * 6926 ≈ 3518."""
        wizard, _, _, _, app = make_wizard(is_metric_format=False)
        app.els.at_saddle_backlash_distance = 0.02
        app.els.at_metric_distances = False

        result = wizard._get_saddle_backlash_distance_encoder_steps()

        expected = round(0.02 / (10 / 254) * 6926)
        assert abs(result) == abs(expected), f"Expected {expected}, got {result}"

    def test_cushion_and_distance_proportional_in_inches(self):
        """Doubling the backlash cushion value should double the encoder count."""
        wizard, _, _, _, app = make_wizard(is_metric_format=False)
        app.els.at_metric_distances = False

        app.els.at_backlash_cushion = 0.004
        single = abs(wizard._get_backlash_cusion_encoder_steps())

        app.els.at_backlash_cushion = 0.008
        doubled = abs(wizard._get_backlash_cusion_encoder_steps())

        # Allow ±1 for integer rounding
        assert abs(doubled - single * 2) <= 1


# ---------------------------------------------------------------------------
# 18. Inch-mode coverage — manual stop position in inches
# ---------------------------------------------------------------------------

class TestGetStopPositionUnitsInches:
    def test_manual_override_in_inches(self):
        """Start captured at -0.5124 in (≈ -90140 counts).
        User enters -1.0 in → final encoder must be more negative than start."""
        wizard, bar, _, _, app = make_wizard(is_metric_format=False)
        bar.start_position = -90140
        wizard._isStartPositionMetricMode = False
        wizard._startScaledPosition = -90140 / (6926 * 25.4)
        wizard.manual_stop_length = -1.0
        app.formats.current_format = "IN"
        app.formats.factor = Fraction(10, 254)
        app.formats.INCHES_FRACTION = Fraction(10, 254)

        result = wizard._get_stop_position_units()

        assert result < bar.start_position, (
            f"Manual inch stop {result} should be more negative than start {bar.start_position}"
        )

    def test_manual_override_same_units_at_start_no_conversion_applied(self):
        """Start=0, both formats inches, -1.0 in → delta = -1.0in / factor * ratio."""
        wizard, bar, _, _, app = make_wizard(is_metric_format=False)
        bar.start_position = 0
        wizard._isStartPositionMetricMode = False
        wizard._startScaledPosition = 0.0
        wizard.manual_stop_length = -1.0
        app.formats.current_format = "IN"
        app.formats.factor = Fraction(10, 254)
        app.formats.INCHES_FRACTION = Fraction(10, 254)

        result = wizard._get_stop_position_units()

        expected = round(-1.0 / (10 / 254) * 6926)   # ≈ -175921
        assert result == expected, f"Expected {expected}, got {result}"


# ---------------------------------------------------------------------------
# 19. Inch-mode coverage — _calculate_thread_depth, remaining TPI profiles
# ---------------------------------------------------------------------------

class TestCalculateThreadDepthTpi:
    """All four thread profiles with TPI input and inch display."""

    def _w(self, pitch: str, profile: str, diameter_mode: bool = False):
        wizard, bar, _, _, app = make_wizard(metric_mode=False, is_metric_format=False)
        bar.selected_pitch = pitch
        bar.thread_profile_type = profile
        bar.metric_mode = False
        app.els.at_cross_slide_diameter_mode = diameter_mode
        return wizard

    def _pitch_in(self, tpi: str) -> float:
        """TPI → pitch in inches (= 1/TPI)."""
        return 1.0 / float(tpi)

    def test_unified_16_tpi_inch_display(self):
        w = self._w("16", "Unified")
        assert abs(w._calculate_thread_depth() - 0.64952 * self._pitch_in("16")) < 0.001

    def test_whitworth_16_tpi_inch_display(self):
        w = self._w("16", "Whitworth")
        assert abs(w._calculate_thread_depth() - 0.6403 * self._pitch_in("16")) < 0.001

    def test_acme_16_tpi_inch_display(self):
        w = self._w("16", "ACME")
        assert abs(w._calculate_thread_depth() - 0.5 * self._pitch_in("16")) < 0.001

    def test_diameter_mode_doubles_tpi_depth(self):
        w = self._w("16", "ISO Metric", diameter_mode=True)
        assert abs(w._calculate_thread_depth() - 0.61343 * self._pitch_in("16") * 2) < 0.001

    def test_zero_tpi_raises(self):
        """Zero TPI → ZeroDivisionError: the code does `25.4 / tpi` before the
        `pitch <= 0` guard, so zero TPI is not handled gracefully in this version.
        This documents the deficiency — the fixed branch should return None instead."""
        w = self._w("0", "ISO Metric")
        with pytest.raises(ZeroDivisionError):
            w._calculate_thread_depth()
