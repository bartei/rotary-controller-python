from fractions import Fraction
from unittest.mock import MagicMock

import pytest
import yaml

from tests.dispatchers.conftest import MockBoard, MockFormats, MockOffsetProvider
from rcp.dispatchers.axis import AxisDispatcher
from rcp.dispatchers.axis_transform import AxisTransform, TransformType
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


def _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch, transform, id_override):
    """Helper to create an AxisDispatcher with tmp_path monkeypatched."""
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    return AxisDispatcher(
        board=board, formats=formats, servo=servo,
        offset_provider=offset_provider, scales=scales,
        transform=transform,
        id_override=id_override,
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


class TestSumAxis:
    def test_combines_two_scales(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        ax = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_axis_sum")
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

    def test_set_position_stores_offset_not_scale(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        """Setting position on a SUM axis stores an axis-level offset, not modifying scales."""
        ax = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_sum_offset")
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].position = 10
        scales[0].update_scaledPosition()
        scales[1].ratioNum = 1
        scales[1].ratioDen = 1
        scales[1].position = 20
        scales[1].update_scaledPosition()
        ax._update_position()

        # Record scale positions before set
        pos0_before = scales[0].position
        pos1_before = scales[1].position

        ax.set_current_position(100.0)
        ax._update_position()

        # Scale positions should be unchanged
        assert scales[0].position == pos0_before
        assert scales[1].position == pos1_before
        # Axis should show the requested value
        assert ax.scaledPosition == pytest.approx(100.0, abs=0.1)

    def test_zero_sum_axis_stores_offset(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        """Zeroing a SUM axis uses an offset, leaving scales unchanged."""
        ax = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_sum_zero")
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].position = 50
        scales[0].update_scaledPosition()
        scales[1].ratioNum = 1
        scales[1].ratioDen = 1
        scales[1].position = 30
        scales[1].update_scaledPosition()
        ax._update_position()

        pos0_before = scales[0].position
        pos1_before = scales[1].position

        ax.zero_position()
        ax._update_position()

        assert scales[0].position == pos0_before
        assert scales[1].position == pos1_before
        assert ax.scaledPosition == pytest.approx(0.0, abs=0.1)


class TestSumAxisOffsetSwitching:
    def test_switching_offset_preserves_sum_axis_value(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        """Switching to a different offset slot on a SUM axis should keep the raw sum visible until zeroed."""
        ax = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_sum_offswitch")
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].position = 100
        scales[0].update_scaledPosition()
        scales[1].ratioNum = 1
        scales[1].ratioDen = 1
        scales[1].position = 200
        scales[1].update_scaledPosition()
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(300.0)

        # Switch to offset 1 — no axis offset set yet, should still show raw sum
        offset_provider.currentOffset = 1
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(300.0)

    def test_zero_on_offset_1_then_switch_back(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        """Zeroing on offset 1, then switching back to offset 0, should restore original value."""
        ax = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_sum_off_back")
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].position = 100
        scales[0].update_scaledPosition()
        scales[1].ratioNum = 1
        scales[1].ratioDen = 1
        scales[1].position = 200
        scales[1].update_scaledPosition()
        ax._update_position()

        # Zero on offset 0
        ax.zero_position()
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(0.0, abs=0.1)

        # Switch to offset 1 — should show raw sum (300) since offset 1 is still 0
        offset_provider.currentOffset = 1
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(300.0)

        # Zero on offset 1
        ax.zero_position()
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(0.0, abs=0.1)

        # Switch back to offset 0 — should still show 0 (offset 0 was zeroed earlier)
        offset_provider.currentOffset = 0
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(0.0, abs=0.1)

    def test_sum_axis_no_double_offset(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        """Axis offsets should not double-count scale-level offsets."""
        ax = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_sum_no_dbl")
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].position = 50
        scales[0].update_scaledPosition()
        scales[1].ratioNum = 1
        scales[1].ratioDen = 1
        scales[1].position = 50
        scales[1].update_scaledPosition()
        ax._update_position()

        # Set axis to show 200
        ax.set_current_position(200.0)
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(200.0, abs=0.1)

        # Switch to offset 1 — should show raw sum (100), NOT double-offset
        offset_provider.currentOffset = 1
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(100.0)


class TestIdentityPositionSet:
    def test_identity_set_position_modifies_scale(self, axis, scales):
        """Setting position on an IDENTITY axis at offset 0 modifies the underlying scale."""
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].formats.factor = Fraction(1, 1)
        scales[0].position = 100
        scales[0].update_scaledPosition()
        axis.set_current_position(50.0)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(50.0, abs=0.1)

    def test_zero_position(self, axis, scales):
        scales[0].ratioNum = 1
        scales[0].ratioDen = 1
        scales[0].formats.factor = Fraction(1, 1)
        scales[0].position = 100
        scales[0].update_scaledPosition()
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
        ax1 = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                         transform=AxisTransform.identity(0), id_override="test_conflict_0")
        ax2 = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                         transform=AxisTransform.identity(0), id_override="test_conflict_1")
        board.connected = True

        # Enable sync on ax1
        board.device['scales'][0].__getitem__ = MagicMock(return_value=False)
        ax1.syncEnable = True

        # Try to enable sync on ax2 — should be blocked
        ax2.syncEnable = False
        ax2.toggle_sync(all_axes=[ax1, ax2])
        assert ax2.syncEnable is False

    def test_no_conflict_on_different_inputs(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        ax1 = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                         transform=AxisTransform.identity(0), id_override="test_noconflict_0")
        ax2 = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                         transform=AxisTransform.identity(1), id_override="test_noconflict_1")
        board.connected = True
        ax1.syncEnable = True

        # ax2 uses input 1, ax1 uses input 0 — no conflict
        scale_1_mock = MagicMock()
        scale_1_mock.__getitem__ = MagicMock(return_value=False)
        board.device['scales'].__getitem__ = MagicMock(return_value=scale_1_mock)
        ax2.toggle_sync(all_axes=[ax1, ax2])
        assert ax2.syncEnable is True


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

    def test_property_change_preserves_transform_config(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        """Changing a Kivy property must not wipe transform_config from the YAML file."""
        ax = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 2), id_override="test_prop_preserves")

        # Changing axis_name triggers save_settings()
        ax.axis_name = "Modified"

        # Verify the YAML file still contains the transform_config
        with open(ax.filename) as f:
            data = yaml.safe_load(f)
        assert "transform_config" in data
        assert data["transform_config"]["transform_type"] == "sum"
        assert data["transform_config"]["contributions"] == [0, 2]

    def test_sum_transform_survives_round_trip(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        """A SUM transform must survive save → reload."""
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            transform=AxisTransform.sum(1, 3),
            id_override="test_roundtrip",
        )

        # Reload from the same file
        ax2 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            id_override="test_roundtrip",
        )
        assert ax2.transform.transform_type == TransformType.SUM
        assert ax2.transform.contributions == (1, 3)

    def test_transform_change_then_property_change_preserves_both(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        """Changing the transform, then changing a property, must preserve the new transform."""
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            transform=AxisTransform.identity(0),
            id_override="test_both",
        )

        # Change the transform
        ax.transform = AxisTransform.sum(1, 2)

        # Then change a property (triggers save_settings)
        ax.syncRatioNum = 720

        # Reload and verify both survived
        ax2 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, scales=scales,
            id_override="test_both",
        )
        assert ax2.syncRatioNum == 720
        assert ax2.transform.transform_type == TransformType.SUM
        assert ax2.transform.contributions == (1, 2)

    def test_multiple_property_changes_dont_corrupt_file(self, board, formats, servo, offset_provider, scales, tmp_path, monkeypatch):
        """Multiple rapid property changes should all be saved and transform preserved."""
        ax = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 3), id_override="test_multi_change")

        ax.axis_name = "MyAxis"
        ax.syncRatioNum = 500
        ax.syncRatioDen = 200
        ax.spindleMode = True

        # Reload and verify everything
        ax2 = _make_axis(board, formats, servo, offset_provider, scales, tmp_path, monkeypatch,
                         transform=None, id_override="test_multi_change")
        assert ax2.axis_name == "MyAxis"
        assert ax2.syncRatioNum == 500
        assert ax2.syncRatioDen == 200
        assert ax2.spindleMode is True
        assert ax2.transform.transform_type == TransformType.SUM
        assert ax2.transform.contributions == (0, 3)
