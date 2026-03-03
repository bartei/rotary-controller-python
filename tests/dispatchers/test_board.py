from unittest.mock import patch, MagicMock

import pytest

from tests.dispatchers.conftest import MockFormats, MockOffsetProvider
from rcp.dispatchers.axis import AxisDispatcher
from rcp.dispatchers.board import Board
from rcp.dispatchers.servo import ServoDispatcher
from rcp.dispatchers.scale import ScaleDispatcher


@pytest.fixture
def formats():
    return MockFormats()


@pytest.fixture
def offset_provider():
    return MockOffsetProvider()


@pytest.fixture
def board(formats, offset_provider, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    with patch("rcp.dispatchers.board.ConnectionManager") as MockCM, \
         patch("rcp.dispatchers.board.Clock"):
        mock_cm = MagicMock()
        mock_cm.__getitem__ = MagicMock(return_value=MagicMock())
        MockCM.return_value = mock_cm
        b = Board(formats=formats, offset_provider=offset_provider)
    return b


class TestBoardCreation:
    def test_creates_servo_dispatcher(self, board):
        assert isinstance(board.servo, ServoDispatcher)

    def test_creates_four_scale_dispatchers(self, board):
        assert len(board.scales) == 4
        for s in board.scales:
            assert isinstance(s, ScaleDispatcher)

    def test_scales_have_correct_input_indices(self, board):
        for i, s in enumerate(board.scales):
            assert s.inputIndex == i

    def test_creates_four_axis_dispatchers(self, board):
        assert len(board.axes) == 4
        for a in board.axes:
            assert isinstance(a, AxisDispatcher)


class TestGetSpindleScale:
    def test_returns_none_when_no_spindle(self, board):
        for s in board.scales:
            s.spindleMode = False
        assert board.get_spindle_scale() is None

    def test_returns_spindle_scale(self, board):
        board.scales[2].spindleMode = True
        result = board.get_spindle_scale()
        assert result is board.scales[2]

    def test_returns_none_when_multiple_spindles(self, board):
        board.scales[0].spindleMode = True
        board.scales[1].spindleMode = True
        assert board.get_spindle_scale() is None


class TestGetSpindleAxis:
    def test_returns_none_when_no_spindle(self, board):
        for a in board.axes:
            a.spindleMode = False
        assert board.get_spindle_axis() is None

    def test_returns_spindle_axis(self, board):
        board.axes[2].spindleMode = True
        result = board.get_spindle_axis()
        assert result is board.axes[2]

    def test_returns_none_when_multiple_spindles(self, board):
        board.axes[0].spindleMode = True
        board.axes[1].spindleMode = True
        assert board.get_spindle_axis() is None

    def test_spindle_propagates_to_primary_scale(self, board):
        board.axes[2].spindleMode = True
        assert board.scales[2].spindleMode is True
