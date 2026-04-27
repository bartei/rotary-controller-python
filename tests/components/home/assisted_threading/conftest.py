"""
Shared fixtures for AssistedThreadingWizard tests.

All test modules in this directory can use make_wizard() directly — pytest
discovers conftest.py automatically and makes module-level names available
when imported explicitly.  The factory is also exported as a pytest fixture.
"""

from fractions import Fraction
from unittest.mock import MagicMock

import pytest

from rcp.components.home.assisted_threading.wizard import AssistedThreadingWizard


# ---------------------------------------------------------------------------
# Builder helpers
# ---------------------------------------------------------------------------

def _make_input(ratioNum: int, ratioDen: int, encoderCurrent: int = 0):
    """Create a mock InputDispatcher (raw encoder)."""
    inp = MagicMock()
    inp.ratioNum = ratioNum
    inp.ratioDen = ratioDen
    inp.encoderCurrent = encoderCurrent
    inp.stepsPerMM = abs(ratioDen / ratioNum)
    inp.inputIndex = 0
    return inp


def _make_axis(inp, scaledPosition: float = 0.0):
    """Create a mock AxisDispatcher that delegates to *inp* via _primary_input()."""
    axis = MagicMock()
    axis.scaledPosition = scaledPosition
    axis.offsets = [0] * 100
    axis._primary_input.return_value = inp
    return axis


def make_wizard(
    ratioNum: int = 1,
    ratioDen: int = 6926,
    saddle_encoderCurrent: int = 0,
    cross_encoderCurrent: int = 0,
    left_hand_thread: bool = False,
    inner_thread: bool = False,
    metric_mode: bool = True,
    is_metric_format: bool = True,
):
    """Create an AssistedThreadingWizard with mocked dependencies.

    Returns (wizard, bar, saddle_input, cross_input, app).
    Note: saddle_scale and cross_slide_scale (AxisDispatchers) are accessible
    via app.els.get_z_axis() and app.els.get_x_axis() respectively.
    """
    bar = MagicMock()
    bar.left_hand_thread = left_hand_thread
    bar.inner_thread = inner_thread
    bar.metric_mode = metric_mode
    bar.start_position = 0
    bar.stop_position = 0
    bar.material_width = 0
    bar.cutting_depth = 0
    bar.last_cutting_depth = 0
    bar.reversing_speed = 500
    bar.selected_pitch = "1.5"
    bar.thread_profile_type = "ISO Metric"
    bar.compound_infeed_mode = False
    bar.compound_infeed_offset_degrees = 1.0

    saddle_inp = _make_input(ratioNum, ratioDen, saddle_encoderCurrent)
    cross_inp = _make_input(ratioNum, ratioDen, cross_encoderCurrent)

    saddle_axis = _make_axis(saddle_inp)
    cross_axis = _make_axis(cross_inp)

    els = MagicMock()
    els.get_z_axis.return_value = saddle_axis
    els.get_x_axis.return_value = cross_axis
    els.get_spindle_axis.return_value = None   # override per-test when needed
    # Machine config properties (moved from bar in v1.3.0)
    els.at_saddle_backlash_distance = 0.5      # mm
    els.at_backlash_cushion = 0.1              # mm
    els.at_metric_distances = True
    els.at_threading_max_speed = 2000
    els.at_reversing_speed = 500
    els.at_cross_slide_diameter_mode = False

    board = MagicMock()
    board.connected = True
    board.fast_data_values = {"stepsToGo": 0, "scaleSpeed": [0] * 4, "servoCurrent": 0}

    app = MagicMock()
    app.formats.factor = Fraction(1, 1)
    app.formats.MM_FRACTION = Fraction(1, 1)
    app.formats.INCHES_FRACTION = Fraction(10, 254)
    app.formats.current_format = "MM" if is_metric_format else "IN"
    app.currentOffset = 0
    app.els = els
    app.board = board

    wizard = AssistedThreadingWizard.__new__(AssistedThreadingWizard)
    wizard.bar = bar
    wizard.app = app
    wizard.servo = MagicMock()
    wizard.servo.ratioNum = 1
    wizard.servo.ratioDen = 1
    wizard.current_step = 0
    wizard._threading_started = False
    wizard._threading_active_confirmed = False
    wizard._current_callback = None
    wizard._servo_watch_callback = None
    wizard.manual_stop_length = None
    wizard.manual_cutting_depth = None
    wizard._last_saddle_encoder_value = None
    wizard._stable_count = 0
    wizard._start_position_preloaded = False
    wizard._isStartPositionMetricMode = True
    wizard._startScaledPosition = 0.0

    return wizard, bar, saddle_inp, cross_inp, app
