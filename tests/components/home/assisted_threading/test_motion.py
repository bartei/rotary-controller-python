"""
Unit tests for AssistedThreadingMotionMixin methods.
"""

from unittest.mock import MagicMock

import pytest

from tests.components.home.assisted_threading.conftest import make_wizard


# ---------------------------------------------------------------------------
# 10. _encoder_is_stable — full state machine
# ---------------------------------------------------------------------------

class TestEncoderIsStable:
    def test_first_call_returns_false_and_initialises(self):
        wizard, _, saddle_inp, _, _ = make_wizard()
        saddle_inp.encoderCurrent = 100
        wizard._reset_encoder_stability_check()

        assert wizard._encoder_is_stable(tolerance=5, samples=3) is False
        assert wizard._last_saddle_encoder_value == 100
        assert wizard._stable_count == 0

    def test_stable_for_n_samples_returns_true(self):
        wizard, _, saddle_inp, _, _ = make_wizard()
        wizard._reset_encoder_stability_check()
        saddle_inp.encoderCurrent = 100

        wizard._encoder_is_stable(5, 3)  # initialise
        wizard._encoder_is_stable(5, 3)
        wizard._encoder_is_stable(5, 3)
        result = wizard._encoder_is_stable(5, 3)

        assert result is True
        assert wizard._stable_count >= 3

    def test_jump_outside_tolerance_resets_count(self):
        wizard, _, saddle_inp, _, _ = make_wizard()
        wizard._reset_encoder_stability_check()
        saddle_inp.encoderCurrent = 100

        wizard._encoder_is_stable(5, 3)  # initialise
        wizard._encoder_is_stable(5, 3)  # count=1

        saddle_inp.encoderCurrent = 200  # jump > 5
        result = wizard._encoder_is_stable(5, 3)

        assert result is False
        assert wizard._stable_count == 0

    def test_within_tolerance_does_not_reset(self):
        wizard, _, saddle_inp, _, _ = make_wizard()
        wizard._reset_encoder_stability_check()
        saddle_inp.encoderCurrent = 100

        wizard._encoder_is_stable(5, 3)  # init
        saddle_inp.encoderCurrent = 103  # within 5
        wizard._encoder_is_stable(5, 3)  # count=1
        saddle_inp.encoderCurrent = 105  # within 5 of 103
        wizard._encoder_is_stable(5, 3)  # count=2

        assert wizard._stable_count == 2

    def test_reset_clears_state(self):
        wizard, _, saddle_inp, _, _ = make_wizard()
        saddle_inp.encoderCurrent = 100
        wizard._encoder_is_stable(5, 3)  # prime some state

        wizard._reset_encoder_stability_check()

        assert wizard._last_saddle_encoder_value is None
        assert wizard._stable_count == 0


# ---------------------------------------------------------------------------
# TestFinishGoToStart (new)
# ---------------------------------------------------------------------------

class TestFinishGoToStart:
    """Tests for _finish_go_to_start() in AssistedThreadingMotionMixin."""

    def test_not_at_depth_goes_to_next_step(self):
        """When cross slide is NOT at final cutting depth, advance by 1 step."""
        wizard, _, _, _, _ = make_wizard()
        wizard.current_step = 5
        wizard.goto_step = MagicMock()
        wizard._reset_servo_watch_callback = MagicMock()
        wizard._is_cross_slide_at_final_cutting_depth = MagicMock(return_value=False)

        wizard._finish_go_to_start()

        wizard.goto_step.assert_called_once_with(6)

    def test_at_depth_skips_to_step_8(self):
        """When cross slide IS at final cutting depth, skip step 7 → go to step 8."""
        wizard, _, _, _, _ = make_wizard()
        wizard.current_step = 5
        wizard.goto_step = MagicMock()
        wizard._reset_servo_watch_callback = MagicMock()
        wizard._is_cross_slide_at_final_cutting_depth = MagicMock(return_value=True)

        wizard._finish_go_to_start()

        wizard.goto_step.assert_called_once_with(7)

    def test_sets_preloaded_flag(self):
        """_start_position_preloaded must be True after the call."""
        wizard, _, _, _, _ = make_wizard()
        wizard.current_step = 5
        wizard.goto_step = MagicMock()
        wizard._reset_servo_watch_callback = MagicMock()
        wizard._is_cross_slide_at_final_cutting_depth = MagicMock(return_value=False)
        wizard._start_position_preloaded = False

        wizard._finish_go_to_start()

        assert wizard._start_position_preloaded is True

    def test_resets_servo_watch_callback(self):
        """The servo watch callback must be cleared before advancing."""
        wizard, _, _, _, app = make_wizard()
        cb = MagicMock()
        wizard._servo_watch_callback = cb
        wizard.current_step = 5
        wizard.goto_step = MagicMock()
        wizard._is_cross_slide_at_final_cutting_depth = MagicMock(return_value=False)

        wizard._finish_go_to_start()

        assert wizard._servo_watch_callback is None
        app.board.unbind.assert_called_once_with(update_tick=cb)
