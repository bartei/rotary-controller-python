"""
Unit tests for AssistedThreadingSafetyMixin methods.
"""

from unittest.mock import MagicMock

import pytest

from tests.components.home.assisted_threading.conftest import make_wizard


# ---------------------------------------------------------------------------
# 4. _is_valid_stop_position
# ---------------------------------------------------------------------------

class TestIsValidStopPosition:
    def test_rht_saddle_moved_past_cushion_returns_true(self):
        """RHT, saddle moved 2672 counts (-0.39 mm) past start — beyond the
        0.1 mm cushion (693 counts), so the stop is valid."""
        wizard, bar, saddle_inp, _, app = make_wizard(left_hand_thread=False)
        bar.start_position = -90140
        app.els.at_backlash_cushion = 0.1
        app.els.at_metric_distances = True
        saddle_inp.encoderCurrent = -92812  # 2672 counts past start in -ve dir
        wizard.manual_stop_length = None

        assert wizard._is_valid_stop_position() is True

    def test_rht_saddle_not_moved_enough_returns_false(self):
        """RHT, saddle moved only 100 counts — less than 693-count cushion."""
        wizard, bar, saddle_inp, _, app = make_wizard(left_hand_thread=False)
        bar.start_position = -90140
        app.els.at_backlash_cushion = 0.1
        app.els.at_metric_distances = True
        saddle_inp.encoderCurrent = -90240  # only 100 counts past start
        wizard.manual_stop_length = None

        assert wizard._is_valid_stop_position() is False

    def test_lht_stop_must_be_in_positive_direction(self):
        """LHT: effective_dir=+1, so stop must be greater than start+cushion."""
        wizard, bar, saddle_inp, _, app = make_wizard(left_hand_thread=True)
        bar.start_position = 0
        app.els.at_backlash_cushion = 0.1
        app.els.at_metric_distances = True
        saddle_inp.encoderCurrent = 5000    # well past cushion in +ve dir
        wizard.manual_stop_length = None

        assert wizard._is_valid_stop_position() is True

    def test_stop_exactly_at_min_stop_returns_false(self):
        """Stop equal to min_stop gives (stop - min_stop)*dir == 0 → False."""
        wizard, bar, saddle_inp, _, app = make_wizard(left_hand_thread=False)
        bar.start_position = 0
        app.els.at_backlash_cushion = 0.1   # 693 counts
        app.els.at_metric_distances = True
        # effective_dir = -1, min_stop = 0 + (-1)*693 = -693
        saddle_inp.encoderCurrent = -693    # exactly at min_stop
        wizard.manual_stop_length = None

        assert wizard._is_valid_stop_position() is False

    def test_axis_offset_does_not_affect_stop_validation(self):
        """v1.3.0 fix: DRO zero offset on the axis must NOT inflate the cushion.
        With offset=-12.885 a legitimate 2672-count stop must still be valid."""
        wizard, bar, saddle_inp, _, app = make_wizard(left_hand_thread=False)
        bar.start_position = -90140
        app.els.at_backlash_cushion = 0.1
        app.els.at_metric_distances = True
        axis = app.els.get_z_axis()
        axis.offsets[0] = -12.885           # simulate DRO zero
        saddle_inp.encoderCurrent = -92812
        wizard.manual_stop_length = None

        assert wizard._is_valid_stop_position() is True


# ---------------------------------------------------------------------------
# 12. _is_cross_slide_retracted
# ---------------------------------------------------------------------------

class TestIsCrossSlideRetracted:
    def test_saddle_not_beyond_start_returns_true_without_checking_cross(self):
        """Saddle hasn't moved past start → True (cross slide check skipped)."""
        wizard, bar, saddle_inp, _, _ = make_wizard(left_hand_thread=False)
        bar.start_position = 0
        # effective_dir = -1 (RHT), "beyond start" means negative encoder
        saddle_inp.encoderCurrent = 100  # positive — NOT beyond start for RHT

        assert wizard._is_cross_slide_retracted() is True

    def test_saddle_beyond_start_cross_retracted_returns_true(self):
        """Saddle past start; cross slide moved in retract direction → True."""
        wizard, bar, saddle_inp, cross_inp, _ = make_wizard(
            left_hand_thread=False,   # saddle effective_dir=-1
            inner_thread=False,       # cross effective_dir=-1, retract_dir=+1
        )
        bar.start_position = 0
        saddle_inp.encoderCurrent = -1000   # beyond start (RHT)
        bar.material_width = 0
        cross_inp.encoderCurrent = 500      # moved +500 from material_width → retracted

        assert wizard._is_cross_slide_retracted() is True

    def test_saddle_beyond_start_cross_not_retracted_returns_false(self):
        """Saddle past start; cross slide still in cutting direction → False."""
        wizard, bar, saddle_inp, cross_inp, _ = make_wizard(
            left_hand_thread=False,
            inner_thread=False,
        )
        bar.start_position = 0
        saddle_inp.encoderCurrent = -1000
        bar.material_width = 0
        cross_inp.encoderCurrent = -500  # moved in cutting direction → not retracted

        assert wizard._is_cross_slide_retracted() is False


# ---------------------------------------------------------------------------
# 13. _is_cross_slide_at_final_cutting_depth
# ---------------------------------------------------------------------------

class TestIsCrossSlideAtFinalCuttingDepth:
    def test_at_depth_returns_true(self):
        """External thread (inner=False, ratio +ve) → effective_dir=-1.
        last_cutting_depth more negative than cutting_depth → at depth."""
        wizard, bar, _, cross, _ = make_wizard(inner_thread=False)
        bar.last_cutting_depth = -1000   # deeper (more negative)
        bar.cutting_depth = -800

        # (last - cutting) * dir = (-1000 - -800) * -1 = 200 >= 0 → True
        assert wizard._is_cross_slide_at_final_cutting_depth() is True

    def test_not_yet_at_depth_returns_false(self):
        wizard, bar, _, cross, _ = make_wizard(inner_thread=False)
        bar.last_cutting_depth = -500
        bar.cutting_depth = -800

        # (-500 - -800) * -1 = -300 < 0 → False
        assert wizard._is_cross_slide_at_final_cutting_depth() is False

    def test_exactly_at_depth_returns_true(self):
        """Equal values → difference is 0 → 0 * dir = 0 >= 0 → True."""
        wizard, bar, _, cross, _ = make_wizard(inner_thread=False)
        bar.last_cutting_depth = -800
        bar.cutting_depth = -800

        assert wizard._is_cross_slide_at_final_cutting_depth() is True

    def test_internal_thread_flips_direction(self):
        """Internal thread → effective_dir=+1, so cutting goes in + direction."""
        wizard, bar, _, cross, _ = make_wizard(inner_thread=True)
        bar.last_cutting_depth = 1000    # deeper in + direction
        bar.cutting_depth = 800

        # (1000 - 800) * 1 = 200 >= 0 → True
        assert wizard._is_cross_slide_at_final_cutting_depth() is True


# ---------------------------------------------------------------------------
# 14. _check_spindle_speed_for_pitch
# ---------------------------------------------------------------------------

class TestCheckSpindleSpeedForPitch:
    """Uses servo ratioDen=6926 (same as scale) so scale/servo ratio = 1."""

    def _make_spindle_wizard(self, spindle_speed: int, pitch: str = "1.5",
                              max_speed: int = 2000):
        wizard, bar, saddle_inp, _, app = make_wizard()
        wizard.servo.ratioNum = 1
        wizard.servo.ratioDen = 6926

        spindle_inp = MagicMock()
        spindle_inp.ratioDen = 1000     # 1000 counts per revolution
        spindle_inp.inputIndex = 0
        spindle_axis = MagicMock()
        spindle_axis._primary_input.return_value = spindle_inp
        app.els.get_spindle_axis.return_value = spindle_axis
        app.board.fast_data_values = {"scaleSpeed": [spindle_speed, 0, 0, 0]}

        bar.selected_pitch = pitch
        bar.metric_mode = True
        app.els.at_threading_max_speed = max_speed
        saddle_inp.stepsPerMM = 6926    # already set by factory but make explicit

        return wizard

    def test_spindle_too_fast_returns_false(self):
        """300 steps/s / 1000 cpr = 0.3 rev/s × 1.5mm × 6926 = 3117 steps/s > 2000."""
        wizard = self._make_spindle_wizard(spindle_speed=300)
        assert wizard._check_spindle_speed_for_pitch() is False

    def test_spindle_within_limit_returns_true(self):
        """100 steps/s / 1000 = 0.1 rev/s × 1.5mm × 6926 = 1039 steps/s < 2000."""
        wizard = self._make_spindle_wizard(spindle_speed=100)
        assert wizard._check_spindle_speed_for_pitch() is True

    def test_no_spindle_scale_returns_true(self):
        """No spindle configured → skip check."""
        wizard, _, _, _, app = make_wizard()
        app.els.get_spindle_axis.return_value = None

        assert wizard._check_spindle_speed_for_pitch() is True

    def test_empty_pitch_returns_true(self):
        """Empty pitch string → skip check."""
        wizard = self._make_spindle_wizard(spindle_speed=300, pitch="")
        assert wizard._check_spindle_speed_for_pitch() is True


# ---------------------------------------------------------------------------
# 17. Inch-mode coverage — _is_valid_stop_position with inch cushion
# ---------------------------------------------------------------------------

class TestIsValidStopPositionInches:
    def test_rht_inch_cushion_saddle_past_cushion_returns_true(self):
        """RHT, saddle moved 2672 counts.  0.004 inch cushion ≈ 704 counts → valid."""
        wizard, bar, saddle_inp, _, app = make_wizard(
            left_hand_thread=False, is_metric_format=False
        )
        bar.start_position = -90140
        app.els.at_backlash_cushion = 0.004
        app.els.at_metric_distances = False
        saddle_inp.encoderCurrent = -92812   # 2672 counts past start
        wizard.manual_stop_length = None

        assert wizard._is_valid_stop_position() is True

    def test_rht_inch_cushion_saddle_not_moved_enough_returns_false(self):
        """RHT, saddle moved only 100 counts — less than the 704-count cushion."""
        wizard, bar, saddle_inp, _, app = make_wizard(
            left_hand_thread=False, is_metric_format=False
        )
        bar.start_position = -90140
        app.els.at_backlash_cushion = 0.004
        app.els.at_metric_distances = False
        saddle_inp.encoderCurrent = -90240   # only 100 counts
        wizard.manual_stop_length = None

        assert wizard._is_valid_stop_position() is False

    def test_lht_inch_cushion_valid_stop_in_positive_direction(self):
        """LHT (effective_dir=+1), stop 5000 counts in +ve direction, 704-count cushion."""
        wizard, bar, saddle_inp, _, app = make_wizard(
            left_hand_thread=True, is_metric_format=False
        )
        bar.start_position = 0
        app.els.at_backlash_cushion = 0.004
        app.els.at_metric_distances = False
        saddle_inp.encoderCurrent = 5000
        wizard.manual_stop_length = None

        assert wizard._is_valid_stop_position() is True


# ---------------------------------------------------------------------------
# 20. Inch-mode coverage — spindle speed check with TPI pitch
# ---------------------------------------------------------------------------

class TestCheckSpindleSpeedForPitchTpi:
    def _make_tpi_wizard(self, spindle_speed: int, tpi: str = "16",
                         max_speed: int = 2000):
        wizard, bar, saddle_inp, _, app = make_wizard()
        wizard.servo.ratioNum = 1
        wizard.servo.ratioDen = 6926

        spindle_inp = MagicMock()
        spindle_inp.ratioDen = 1000
        spindle_inp.inputIndex = 0
        spindle_axis = MagicMock()
        spindle_axis._primary_input.return_value = spindle_inp
        app.els.get_spindle_axis.return_value = spindle_axis
        app.board.fast_data_values = {"scaleSpeed": [spindle_speed, 0, 0, 0]}

        bar.selected_pitch = tpi
        bar.metric_mode = False
        app.els.at_threading_max_speed = max_speed
        saddle_inp.stepsPerMM = 6926

        return wizard

    def test_tpi_pitch_too_fast_returns_false(self):
        """300 steps/s / 1000 cpr = 0.3 rev/s × 1.5875mm × 6926 = 3298 steps/s > 2000."""
        wizard = self._make_tpi_wizard(spindle_speed=300)
        assert wizard._check_spindle_speed_for_pitch() is False

    def test_tpi_pitch_within_limit_returns_true(self):
        """50 steps/s / 1000 = 0.05 rev/s × 1.5875mm × 6926 = 550 steps/s < 2000."""
        wizard = self._make_tpi_wizard(spindle_speed=50)
        assert wizard._check_spindle_speed_for_pitch() is True

    def test_tpi_boundary_exactly_at_limit_returns_true(self):
        """Required == max_speed: condition is `required > max`, so equal → True."""
        wizard = self._make_tpi_wizard(spindle_speed=181)
        assert wizard._check_spindle_speed_for_pitch() is True

    def test_non_numeric_tpi_skips_check(self):
        """Unparseable TPI value → skips check and returns True."""
        wizard = self._make_tpi_wizard(spindle_speed=9999, tpi="bad")
        assert wizard._check_spindle_speed_for_pitch() is True


# ---------------------------------------------------------------------------
# TestCheckValidStartPosition (new)
# ---------------------------------------------------------------------------

class TestCheckValidStartPosition:
    """Tests for _check_valid_start_position() in AssistedThreadingSafetyMixin."""

    def test_within_cushion_returns_true(self):
        """Saddle delta < backlash cushion → True, no popup opened."""
        from rcp.components.widgets.custom_popup import CustomPopup
        CustomPopup.reset_mock()

        wizard, bar, saddle_inp, _, app = make_wizard()
        bar.start_position = 0
        app.els.at_backlash_cushion = 0.1   # ~693 counts
        app.els.at_metric_distances = True
        saddle_inp.encoderCurrent = 100      # 100 counts delta — well within cushion

        result = wizard._check_valid_start_position()

        assert result is True
        CustomPopup.assert_not_called()

    def test_outside_cushion_returns_false_and_opens_popup(self):
        """Saddle delta > backlash cushion → False, CustomPopup instantiated."""
        from rcp.components.widgets.custom_popup import CustomPopup
        CustomPopup.reset_mock()

        wizard, bar, saddle_inp, _, app = make_wizard()
        bar.start_position = 0
        app.els.at_backlash_cushion = 0.1   # ~693 counts
        app.els.at_metric_distances = True
        saddle_inp.encoderCurrent = 5000     # 5000 counts — far outside cushion

        result = wizard._check_valid_start_position()

        assert result is False
        CustomPopup.assert_called_once()

    def test_exactly_at_boundary_returns_true(self):
        """delta == cushion → True (condition is strict `>`, not `>=`)."""
        wizard, bar, saddle_inp, _, app = make_wizard()
        bar.start_position = 0
        app.els.at_backlash_cushion = 0.1   # 693 counts
        app.els.at_metric_distances = True
        saddle_inp.encoderCurrent = 693      # exactly at cushion boundary

        result = wizard._check_valid_start_position()

        assert result is True


# ---------------------------------------------------------------------------
# TestCheckSpindleTurningForward (new)
# ---------------------------------------------------------------------------

class TestCheckSpindleTurningForward:
    """Tests for _check_spindle_turning_forward() in AssistedThreadingSafetyMixin."""

    def _setup(self, spindle_speed: int):
        wizard, _, _, _, app = make_wizard()
        spindle_inp = MagicMock()
        spindle_inp.inputIndex = 0
        spindle_axis = MagicMock()
        spindle_axis._primary_input.return_value = spindle_inp
        app.els.get_spindle_axis.return_value = spindle_axis
        app.board.fast_data_values = {
            "scaleSpeed": [spindle_speed, 0, 0, 0],
            "stepsToGo": 0,
            "servoCurrent": 0,
        }
        return wizard

    def test_positive_speed_returns_true(self):
        from rcp.components.widgets.custom_popup import CustomPopup
        CustomPopup.reset_mock()

        wizard = self._setup(spindle_speed=100)
        assert wizard._check_spindle_turning_forward() is True
        CustomPopup.assert_not_called()

    def test_zero_speed_returns_false(self):
        from rcp.components.widgets.custom_popup import CustomPopup
        CustomPopup.reset_mock()

        wizard = self._setup(spindle_speed=0)
        assert wizard._check_spindle_turning_forward() is False
        CustomPopup.assert_called_once()

    def test_negative_speed_returns_false(self):
        from rcp.components.widgets.custom_popup import CustomPopup
        CustomPopup.reset_mock()

        wizard = self._setup(spindle_speed=-50)
        assert wizard._check_spindle_turning_forward() is False
        CustomPopup.assert_called_once()

    def test_no_spindle_axis_returns_false(self):
        from rcp.components.widgets.custom_popup import CustomPopup
        CustomPopup.reset_mock()

        wizard, _, _, _, app = make_wizard()
        app.els.get_spindle_axis.return_value = None

        assert wizard._check_spindle_turning_forward() is False
        CustomPopup.assert_called_once()
