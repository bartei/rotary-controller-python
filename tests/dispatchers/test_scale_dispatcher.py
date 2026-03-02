from fractions import Fraction
from unittest.mock import MagicMock, patch

import pytest

from tests.dispatchers.conftest import MockBoard, MockFormats, MockOffsetProvider
from rcp.dispatchers.servo import ServoDispatcher
from rcp.dispatchers.scale import ScaleDispatcher


@pytest.fixture
def board():
    b = MockBoard()
    b.device = MagicMock()
    return b


@pytest.fixture
def formats():
    return MockFormats()


@pytest.fixture
def offset_provider():
    return MockOffsetProvider()


@pytest.fixture
def servo(board, formats, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    return ServoDispatcher(board=board, formats=formats, id_override="0")


@pytest.fixture
def scale(board, formats, servo, offset_provider, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    return ScaleDispatcher(
        board=board, formats=formats, servo=servo,
        offset_provider=offset_provider, inputIndex=0, id_override="0",
    )


class TestScaleDispatcherFilename:
    def test_yaml_filename_is_coordbar(self, scale):
        assert scale.filename.name == "CoordBar-0.yaml"

    def test_different_indices_different_files(self, board, formats, servo, offset_provider, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        s0 = ScaleDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputIndex=0, id_override="0",
        )
        s1 = ScaleDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputIndex=1, id_override="1",
        )
        assert s0.filename.name == "CoordBar-0.yaml"
        assert s1.filename.name == "CoordBar-1.yaml"


class TestPositionTracking:
    def test_update_tick_tracks_encoder_delta(self, scale):
        scale.board.connected = True
        scale.board.fast_data_values = {
            'scaleCurrent': [100, 0, 0, 0],
        }
        scale.encoderCurrent = 0
        scale.on_update_tick()
        assert scale.position == 100

    def test_update_tick_ignores_when_disconnected(self, scale):
        scale.board.connected = False
        scale.board.fast_data_values = {
            'scaleCurrent': [100, 0, 0, 0],
        }
        original_pos = scale.position
        scale.on_update_tick()
        assert scale.position == original_pos


class TestSetCurrentPosition:
    def test_offset_0_resets_absolute_position(self, scale):
        scale.offset_provider.currentOffset = 0
        scale.formats.factor = Fraction(1, 1)
        scale.ratioNum = 1
        scale.ratioDen = 1
        scale.set_current_position(50.0)
        assert scale.position == pytest.approx(50.0)
        assert scale.offsets[0] == 0

    def test_nonzero_offset_stores_offset(self, scale):
        scale.offset_provider.currentOffset = 1
        scale.formats.factor = Fraction(1, 1)
        scale.ratioNum = 1
        scale.ratioDen = 1
        scale.position = 100
        scale.set_current_position(25.0)
        # offset = value/factor - position*ratio = 25 - 100 = -75
        assert scale.offsets[1] == pytest.approx(-75.0)


class TestZeroPosition:
    def test_zero_sets_position_to_zero(self, scale):
        scale.motion_detected = True
        scale.offset_provider.currentOffset = 0
        scale.formats.factor = Fraction(1, 1)
        scale.ratioNum = 1
        scale.ratioDen = 1
        scale.position = 100
        scale.zero_position()
        assert scale.position == pytest.approx(0.0)

    def test_zero_toggle_restores_previous(self, scale):
        scale.offset_provider.currentOffset = 0
        scale.formats.factor = Fraction(1, 1)
        scale.ratioNum = 1
        scale.ratioDen = 1
        scale.position = 100
        scale.update_scaledPosition()

        # First zero
        scale.zero_position()
        assert scale.position == pytest.approx(0.0)

        # Toggle back (motion_detected is False after set_current_position)
        scale.zero_position()
        assert scale.position == pytest.approx(100.0)


class TestSetSyncRatio:
    def test_sync_ratio_non_spindle_non_els(self, scale):
        scale.board.connected = True
        scale.spindleMode = False
        scale.servo.elsMode = False
        scale.ratioNum = 1000
        scale.ratioDen = 1
        scale.servo.ratioNum = 400
        scale.servo.ratioDen = 360
        scale.syncRatioNum = 1
        scale.syncRatioDen = 1
        scale.formats.factor = Fraction(1, 1)
        scale.set_sync_ratio()
        # scale_ratio = 1000/1 * 1/1 = 1000
        # servo_ratio = 400/360
        # sync = 1/1
        # final = 1000 * 1 / (400/360) = 1000 * 360/400 = 900
        scale.board.device['scales'][0].__setitem__.assert_called()

    def test_sync_ratio_skips_when_disconnected(self, scale):
        scale.board.connected = False
        scale.board.device['scales'][0].__setitem__.reset_mock()
        scale.set_sync_ratio()
        scale.board.device['scales'][0].__setitem__.assert_not_called()

    def test_denominator_zero_corrected(self, scale):
        scale.board.connected = True
        scale.syncRatioDen = 0
        scale.set_sync_ratio()
        assert scale.syncRatioDen == 1


class TestSpeedCalculation:
    def test_speed_mm_mode(self, scale):
        scale.spindleMode = False
        scale.stepsPerMM = 1000
        scale.formats.current_format = "MM"
        scale.board.fast_data_values = {
            'scaleSpeed': [1000, 0, 0, 0],
        }
        scale.speed_task()
        # 1000 steps/s * 60 * (1/1000) * (1/1000) = 0.06
        assert scale.speed == pytest.approx(0.06)

    def test_speed_spindle_mode(self, scale):
        scale.spindleMode = True
        scale.ratioDen = 1000
        scale.board.fast_data_values = {
            'scaleSpeed': [1000, 0, 0, 0],
        }
        scale.speed_task()
        # 1000 / 1000 * 60 = 60 RPM
        assert scale.speed == pytest.approx(60.0)

    def test_speed_skips_when_no_data(self, scale):
        scale.board.fast_data_values = None
        scale.speed_task()
        # Should not crash


class TestScaledPosition:
    def test_non_spindle_position(self, scale):
        scale.spindleMode = False
        scale.ratioNum = 1
        scale.ratioDen = 1
        scale.position = 100
        scale.formats.factor = Fraction(1, 1)
        scale.offset_provider.currentOffset = 0
        scale.update_scaledPosition()
        assert scale.scaledPosition == pytest.approx(100.0)

    def test_spindle_mode_position(self, scale):
        scale.spindleMode = True
        scale.ratioNum = 360
        scale.ratioDen = 1000
        scale.position = 500
        scale.offset_provider.currentOffset = 0
        scale.update_scaledPosition()
        assert scale.scaledPosition == pytest.approx(500 * Fraction(360, 1000))
