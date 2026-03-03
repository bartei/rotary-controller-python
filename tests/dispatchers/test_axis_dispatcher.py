from fractions import Fraction
from unittest.mock import MagicMock

import pytest

from tests.dispatchers.conftest import MockBoard, MockFormats, MockOffsetProvider
from rcp.dispatchers.axis import AxisDispatcher
from rcp.dispatchers.axis_transform import AxisTransform
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
    return ServoDispatcher(board=board, formats=formats, id_override="test_servo")


@pytest.fixture
def scales(board, formats, servo, offset_provider, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    result = []
    for i in range(4):
        s = ScaleDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputIndex=i,
            id_override=f"test_scale_{i}",
        )
        result.append(s)
    return result


@pytest.fixture
def axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    return AxisDispatcher(
        board=board, formats=formats, servo=servo,
        offset_provider=offset_provider, scales=scales,
        transform=AxisTransform.identity(0),
        id_override="test_axis_0",
    )


class TestAxisDispatcherFilename:
    def test_yaml_filename_is_axis(self, axis):
        assert axis.filename.name == "Axis-test_axis_0.yaml"


class TestIdentityAxisMirrorsScale:
    def test_position_mirrors_scale(self, axis, scales):
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].position = 100
        scales[0].update_scaledPosition()
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(scales[0].scaledPosition)

    def test_formatted_position_updates(self, axis, scales):
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].position = 42
        scales[0].update_scaledPosition()
        axis._update_position()
        assert axis.formattedPosition != "--"


class TestScalingAxis:
    def test_scaled_axis_applies_weight(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            transform=AxisTransform.scaling(0, Fraction(1, 2)),
            id_override="test_axis_scaled",
        )
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].position = 100
        scales[0].update_scaledPosition()
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(50.0)


class TestWeightedSumAxis:
    def test_combines_two_scales(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            transform=AxisTransform.weighted_sum([
                (0, Fraction(1, 1)),
                (1, Fraction(1, 1)),
            ]),
            id_override="test_axis_sum",
        )
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].position = 10
        scales[0].update_scaledPosition()
        scales[1].ratioNum = 1
        scales[1].ratioDen = 1
        scales[1].position = 20
        scales[1].update_scaledPosition()
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(30.0)


class TestSyncRatio:
    def test_sync_ratio_written_to_hardware(self, axis, board):
        board.connected = True
        axis.syncRatioNum = 360
        axis.syncRatioDen = 100
        axis._set_sync_ratio()
        # Verify the device was written to
        board.device['scales'][0].__setitem__.assert_called()


class TestSyncConflict:
    def test_conflict_blocks_enable(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax1 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            transform=AxisTransform.identity(0),
            id_override="test_conflict_0",
        )
        ax2 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            transform=AxisTransform.identity(0),
            id_override="test_conflict_1",
        )
        board.connected = True

        # Enable sync on ax1
        board.device['scales'][0].__getitem__ = MagicMock(return_value=False)
        ax1.syncEnable = True

        # Try to enable sync on ax2 — should be blocked
        ax2.syncEnable = False
        ax2.toggle_sync(all_axes=[ax1, ax2])
        assert ax2.syncEnable is False

    def test_no_conflict_on_different_inputs(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax1 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            transform=AxisTransform.identity(0),
            id_override="test_noconflict_0",
        )
        ax2 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            transform=AxisTransform.identity(1),
            id_override="test_noconflict_1",
        )
        board.connected = True
        ax1.syncEnable = True

        # ax2 uses input 1, ax1 uses input 0 — no conflict
        # Mock device so that scales[1]['syncEnable'] returns False (currently off)
        scale_1_mock = MagicMock()
        scale_1_mock.__getitem__ = MagicMock(return_value=False)
        board.device['scales'].__getitem__ = MagicMock(return_value=scale_1_mock)
        ax2.toggle_sync(all_axes=[ax1, ax2])
        assert ax2.syncEnable is True


class TestPositionSet:
    def test_zero_position(self, axis, scales):
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].formats.factor = Fraction(1, 1)
        scales[0].position = 100
        scales[0].update_scaledPosition()
        axis._motion_detected = True
        axis.zero_position()
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.01)

    def test_set_custom_position_offset(self, axis, scales, offset_provider):
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].formats.factor = Fraction(1, 1)
        scales[0].position = 100
        scales[0].update_scaledPosition()
        offset_provider.currentOffset = 1
        axis._update_position()
        axis.set_current_position(25.0)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(25.0, abs=0.1)


class TestPersistence:
    def test_axis_saves_and_restores_name(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            transform=AxisTransform.identity(0),
            id_override="test_persist",
        )
        ax.axis_name = "TestAxis"

        # Create a new instance that should load from the same file
        ax2 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            id_override="test_persist",
        )
        assert ax2.axis_name == "TestAxis"
