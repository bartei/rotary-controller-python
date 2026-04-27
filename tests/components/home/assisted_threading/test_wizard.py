"""
Unit tests for AssistedThreadingWizard core methods (lifecycle, step management).
"""

from unittest.mock import MagicMock

import pytest

from tests.components.home.assisted_threading.conftest import make_wizard


# ---------------------------------------------------------------------------
# 5. _capture_initial_position
# ---------------------------------------------------------------------------

class TestCaptureInitialPosition:
    def test_records_encoder_and_scaled_position(self):
        wizard, bar, saddle_inp, _, app = make_wizard()
        saddle_inp.encoderCurrent = -90140
        app.els.get_z_axis().scaledPosition = -13.0  # scaledPosition on AxisDispatcher

        wizard._capture_initial_position()

        assert bar.start_position == -90140
        assert wizard._isStartPositionMetricMode is True
        assert wizard._startScaledPosition == -13.0

    def test_records_inch_format_flag(self):
        wizard, bar, saddle_inp, _, _ = make_wizard(is_metric_format=False)
        saddle_inp.encoderCurrent = 500

        wizard._capture_initial_position()

        assert wizard._isStartPositionMetricMode is False
        assert bar.start_position == 500

    def test_returns_true_to_advance_step(self):
        wizard, _, saddle_inp, _, _ = make_wizard()
        saddle_inp.encoderCurrent = 0

        result = wizard._capture_initial_position()

        assert result is True


# ---------------------------------------------------------------------------
# 6. _capture_material_width_position
# ---------------------------------------------------------------------------

class TestCaptureMaterialWidthPosition:
    def test_records_cross_encoder_as_material_width(self):
        wizard, bar, _, cross_inp, _ = make_wizard()
        cross_inp.encoderCurrent = 5000

        wizard._capture_material_width_position()

        assert bar.material_width == 5000

    def test_initialises_last_cutting_depth_to_material_width(self):
        wizard, bar, _, cross_inp, _ = make_wizard()
        cross_inp.encoderCurrent = 5000

        wizard._capture_material_width_position()

        assert bar.last_cutting_depth == 5000

    def test_returns_true_to_advance_step(self):
        wizard, _, _, cross_inp, _ = make_wizard()
        cross_inp.encoderCurrent = 0

        result = wizard._capture_material_width_position()

        assert result is True


# ---------------------------------------------------------------------------
# 15. stop() — resets all wizard state
# ---------------------------------------------------------------------------

class TestStop:
    def test_stop_resets_running_state(self):
        wizard, _, _, _, app = make_wizard()
        app.board.connected = True
        wizard._threading_started = True
        wizard._current_callback = MagicMock()

        wizard.stop()

        assert wizard._threading_started is False
        assert wizard._current_callback is None

    def test_stop_clears_bar_labels(self):
        wizard, bar, _, _, app = make_wizard()
        app.board.connected = False

        wizard.stop()

        assert bar.label_text == ""
        assert bar.action_button_condition_fn is None
        assert bar.retract_button_visible is False

    def test_stop_when_disconnected_does_not_write_device(self):
        wizard, _, _, _, app = make_wizard()
        app.board.connected = False

        wizard.stop()

        app.board.device.__getitem__.assert_not_called()

    def test_stop_resets_servo_watch_callback(self):
        wizard, _, _, _, app = make_wizard()
        app.board.connected = False
        cb = MagicMock()
        wizard._servo_watch_callback = cb

        wizard.stop()

        assert wizard._servo_watch_callback is None
        app.board.unbind.assert_called_once_with(update_tick=cb)


# ---------------------------------------------------------------------------
# TestGotoNextStep (new)
# ---------------------------------------------------------------------------

class TestGotoNextStep:
    """Tests for goto_next_step() in AssistedThreadingWizard."""

    def test_callback_true_advances(self):
        """Callback returns True + bar.is_running=True → goto_step(current+1)."""
        wizard, bar, _, _, _ = make_wizard()
        wizard.current_step = 3
        wizard.goto_step = MagicMock()
        bar.is_running = True
        wizard._current_callback = MagicMock(return_value=True)

        wizard.goto_next_step()

        wizard.goto_step.assert_called_once_with(4)

    def test_callback_false_stays(self):
        """Callback returns False → step must NOT advance."""
        wizard, bar, _, _, _ = make_wizard()
        wizard.current_step = 3
        wizard.goto_step = MagicMock()
        bar.is_running = True
        wizard._current_callback = MagicMock(return_value=False)

        wizard.goto_next_step()

        wizard.goto_step.assert_not_called()

    def test_callback_none_advances(self):
        """Callback returns None (not False) → advances."""
        wizard, bar, _, _, _ = make_wizard()
        wizard.current_step = 2
        wizard.goto_step = MagicMock()
        bar.is_running = True
        wizard._current_callback = MagicMock(return_value=None)

        wizard.goto_next_step()

        wizard.goto_step.assert_called_once_with(3)

    def test_no_callback_advances(self):
        """No callback set → advances directly."""
        wizard, bar, _, _, _ = make_wizard()
        wizard.current_step = 1
        wizard.goto_step = MagicMock()
        bar.is_running = True
        wizard._current_callback = None

        wizard.goto_next_step()

        wizard.goto_step.assert_called_once_with(2)

    def test_bar_not_running_does_not_advance(self):
        """Callback returns True but bar.is_running=False → no advance."""
        wizard, bar, _, _, _ = make_wizard()
        wizard.current_step = 3
        wizard.goto_step = MagicMock()
        bar.is_running = False
        wizard._current_callback = MagicMock(return_value=True)

        wizard.goto_next_step()

        wizard.goto_step.assert_not_called()

    def test_past_last_step_calls_stop(self):
        """Advancing past the last valid step index triggers stop()."""
        wizard, bar, _, _, _ = make_wizard()
        wizard.current_step = 7  # last index (0-based, 8 steps)
        bar.is_running = True
        wizard._current_callback = MagicMock(return_value=True)

        # goto_step(8) calls stop() because 8 >= len(self._steps)
        # We need the real goto_step but mock stop()
        wizard.stop = MagicMock()
        # Rebuild the steps list so goto_step works without Kivy
        wizard._steps = [MagicMock() for _ in range(8)]

        wizard.goto_next_step()

        wizard.stop.assert_called_once()
