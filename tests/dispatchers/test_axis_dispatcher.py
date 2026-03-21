from fractions import Fraction
from unittest.mock import MagicMock

import pytest
import yaml

from tests.dispatchers.conftest import MockBoard, MockFormats, MockOffsetProvider
from rcp.dispatchers.axis import AxisDispatcher
from rcp.dispatchers.axis_transform import AxisTransform, TransformType
from rcp.dispatchers.servo import ServoDispatcher
from rcp.dispatchers.input import InputDispatcher


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
def inputs(board, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    result = []
    for i in range(4):
        inp = InputDispatcher(
            board=board, inputIndex=i,
            id_override=f"test_input_{i}",
        )
        result.append(inp)
    return result


@pytest.fixture
def axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    return AxisDispatcher(
        board=board, formats=formats, servo=servo,
        offset_provider=offset_provider, inputs=inputs,
        transform=AxisTransform.identity(0),
        id_override="test_axis_0",
    )


def _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch, transform, id_override):
    """Helper to create an AxisDispatcher with tmp_path monkeypatched."""
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    return AxisDispatcher(
        board=board, formats=formats, servo=servo,
        offset_provider=offset_provider, inputs=inputs,
        transform=transform,
        id_override=id_override,
    )


class TestAxisDispatcherFilename:
    def test_yaml_filename_is_axis(self, axis):
        assert axis.filename.name == "Axis-test_axis_0.yaml"


class TestIdentityAxisMirrorsInput:
    def test_position_mirrors_input(self, axis, inputs):
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(100.0)

    def test_with_ratio(self, axis, inputs):
        inputs[0].ratioNum = 360
        inputs[0].ratioDen = 1000
        inputs[0].position = 500
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(180.0)

    def test_formatted_position_updates(self, axis, inputs):
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 42
        axis._update_position()
        assert axis.formattedPosition != "--"


class TestFactorApplication:
    def test_mm_factor_passthrough(self, axis, inputs):
        """factor=1 (MM) passes ratio-units through."""
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        axis.formats.factor = Fraction(1, 1)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(100.0)

    def test_in_factor_applied(self, axis, inputs):
        """factor=10/254 (IN) scales ratio-units."""
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 254
        axis.formats.factor = Fraction(10, 254)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(10.0)

    def test_spindle_mode_ignores_factor(self, axis, inputs):
        """Spindle mode does not apply factor (degrees are unit-less)."""
        axis.spindleMode = True
        inputs[0].spindleMode = True
        inputs[0].encoder_ppr = 1000
        inputs[0].position = 500
        axis.formats.factor = Fraction(10, 254)
        axis._update_position()
        # 500 steps / 1000 spr * 360 = 180°
        assert axis.scaledPosition == pytest.approx(180.0)


class TestSpeedConversion:
    def test_speed_spindle_rpm(self, axis, inputs):
        axis.spindleMode = True
        inputs[0].spindleMode = True
        inputs[0].encoder_ppr = 1000
        inputs[0].steps_per_second = 1000
        axis._update_position()
        # 1000 sps / 1000 spr * 60 = 60 RPM
        assert axis.speed == pytest.approx(60.0)

    def test_speed_spindle_rpm_with_gear_ratio(self, axis, inputs):
        """1:2 gear (encoder at half spindle speed): RPM should double."""
        axis.spindleMode = True
        inputs[0].spindleMode = True
        inputs[0].encoder_ppr = 1000
        inputs[0].gear_ratio_num = 1
        inputs[0].gear_ratio_den = 2
        inputs[0].steps_per_second = 500
        axis._update_position()
        # spr = 1000 * 1 / 2 = 500. RPM = 500/500 * 60 = 60
        assert axis.speed == pytest.approx(60.0)

    def test_speed_spindle_rpm_gear_2_to_1(self, axis, inputs):
        """2:1 gear (encoder 2x spindle speed)."""
        axis.spindleMode = True
        inputs[0].spindleMode = True
        inputs[0].encoder_ppr = 1000
        inputs[0].gear_ratio_num = 2
        inputs[0].gear_ratio_den = 1
        inputs[0].steps_per_second = 2000
        axis._update_position()
        # spr = 1000 * 2 / 1 = 2000. RPM = 2000/2000 * 60 = 60
        assert axis.speed == pytest.approx(60.0)

    def test_speed_mm_mode(self, axis, inputs):
        axis.spindleMode = False
        inputs[0].stepsPerMM = 1000
        inputs[0].steps_per_second = 1000
        axis.formats.current_format = "MM"
        axis._update_position()
        # 1000 * 60 * (1/1000) * (1/1000) = 0.06
        assert axis.speed == pytest.approx(0.06)

    def test_speed_in_mode(self, axis, inputs):
        axis.spindleMode = False
        inputs[0].stepsPerMM = 1000
        inputs[0].steps_per_second = 1000
        axis.formats.current_format = "IN"
        axis._update_position()
        expected = 1000 * 60 * (1 / 1000) * (1 / 1000) * (120 / 254)
        assert axis.speed == pytest.approx(expected)


class TestSpindlePosition:
    def test_spindle_position_in_degrees(self, axis, inputs):
        """Spindle mode converts steps to degrees."""
        axis.spindleMode = True
        inputs[0].spindleMode = True
        inputs[0].encoder_ppr = 1000
        inputs[0].position = 250
        axis._update_position()
        # 250 / 1000 * 360 = 90°
        assert axis.scaledPosition == pytest.approx(90.0)

    def test_spindle_wraps_at_360(self, axis, inputs):
        """Position wraps at 360° regardless of gear ratio."""
        axis.spindleMode = True
        inputs[0].spindleMode = True
        inputs[0].encoder_ppr = 1000
        inputs[0].position = 1500
        axis._update_position()
        # 1500 / 1000 * 360 = 540° → 540 % 360 = 180°
        assert axis.scaledPosition == pytest.approx(180.0)

    def test_spindle_gear_ratio_position(self, axis, inputs):
        """Gear ratio affects steps-to-degrees conversion."""
        axis.spindleMode = True
        inputs[0].spindleMode = True
        inputs[0].encoder_ppr = 1000
        inputs[0].gear_ratio_num = 2
        inputs[0].gear_ratio_den = 1
        inputs[0].position = 500
        axis._update_position()
        # spr = 1000 * 2 / 1 = 2000. degrees = 500 / 2000 * 360 = 90°
        assert axis.scaledPosition == pytest.approx(90.0)

    def test_spindle_gear_ratio_half_speed(self, axis, inputs):
        """1:2 gear — encoder at half spindle speed."""
        axis.spindleMode = True
        inputs[0].spindleMode = True
        inputs[0].encoder_ppr = 1000
        inputs[0].gear_ratio_num = 1
        inputs[0].gear_ratio_den = 2
        inputs[0].position = 250
        axis._update_position()
        # spr = 1000 * 1 / 2 = 500. degrees = 250 / 500 * 360 = 180°
        assert axis.scaledPosition == pytest.approx(180.0)

    def test_spindle_set_current_position(self, axis, inputs):
        """set_current_position converts degrees to steps for offset."""
        axis.spindleMode = True
        inputs[0].spindleMode = True
        inputs[0].encoder_ppr = 1000
        inputs[0].position = 500
        axis.set_current_position(0)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.1)

    def test_spindle_set_position_with_gear_ratio(self, axis, inputs):
        """set_current_position works with non-1:1 gear ratio."""
        axis.spindleMode = True
        inputs[0].spindleMode = True
        inputs[0].encoder_ppr = 1000
        inputs[0].gear_ratio_num = 2
        inputs[0].gear_ratio_den = 1
        inputs[0].position = 1000  # = 180° with spr=2000
        axis.set_current_position(0)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.1)

    def test_spindle_wrap_steps_self_computed_on_input(self, axis, inputs):
        """InputDispatcher self-computes _spindle_wrap_steps from its own properties."""
        inputs[0].encoder_ppr = 1000
        inputs[0].gear_ratio_num = 2
        inputs[0].spindleMode = True
        assert inputs[0]._spindle_wrap_steps == 2000  # ppr * gear_num

    def test_spindle_disabling_clears_wrap_steps(self, axis, inputs):
        """Disabling spindle mode clears _spindle_wrap_steps on input."""
        inputs[0].spindleMode = True
        inputs[0].spindleMode = False
        assert inputs[0]._spindle_wrap_steps == 0


class TestSumAxis:
    def test_combines_two_inputs(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        ax = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_axis_sum")
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 10
        inputs[1].ratioNum = 1
        inputs[1].ratioDen = 1
        inputs[1].position = 20
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(30.0)

    def test_set_position_stores_offset_not_input(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        """Setting position on a SUM axis stores an axis-level offset, not modifying inputs."""
        ax = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_sum_offset")
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 10
        inputs[1].ratioNum = 1
        inputs[1].ratioDen = 1
        inputs[1].position = 20

        pos0_before = inputs[0].position
        pos1_before = inputs[1].position

        ax.set_current_position(100.0)
        ax._update_position()

        assert inputs[0].position == pos0_before
        assert inputs[1].position == pos1_before
        assert ax.scaledPosition == pytest.approx(100.0, abs=0.1)

    def test_zero_sum_axis_stores_offset(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        ax = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_sum_zero")
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 50
        inputs[1].ratioNum = 1
        inputs[1].ratioDen = 1
        inputs[1].position = 30
        ax._update_position()

        pos0_before = inputs[0].position
        pos1_before = inputs[1].position

        ax.zero_position()
        ax._update_position()

        assert inputs[0].position == pos0_before
        assert inputs[1].position == pos1_before
        assert ax.scaledPosition == pytest.approx(0.0, abs=0.1)


class TestSumAxisOffsetSwitching:
    def test_switching_offset_preserves_sum_axis_value(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        ax = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_sum_offswitch")
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        inputs[1].ratioNum = 1
        inputs[1].ratioDen = 1
        inputs[1].position = 200
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(300.0)

        offset_provider.currentOffset = 1
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(300.0)

    def test_zero_on_offset_1_then_switch_back(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        ax = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_sum_off_back")
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        inputs[1].ratioNum = 1
        inputs[1].ratioDen = 1
        inputs[1].position = 200
        ax._update_position()

        ax.zero_position()
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(0.0, abs=0.1)

        offset_provider.currentOffset = 1
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(300.0)

        ax.zero_position()
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(0.0, abs=0.1)

        offset_provider.currentOffset = 0
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(0.0, abs=0.1)

    def test_sum_axis_no_double_offset(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        ax = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 1), id_override="test_sum_no_dbl")
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 50
        inputs[1].ratioNum = 1
        inputs[1].ratioDen = 1
        inputs[1].position = 50
        ax._update_position()

        ax.set_current_position(200.0)
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(200.0, abs=0.1)

        offset_provider.currentOffset = 1
        ax._update_position()
        assert ax.scaledPosition == pytest.approx(100.0)


class TestUnifiedPositionSet:
    def test_identity_offset0_no_longer_modifies_input(self, axis, inputs):
        """IDENTITY offset0 no longer modifies input.position — behavioral change."""
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        pos_before = inputs[0].position

        axis.set_current_position(50.0)
        axis._update_position()

        # Input position should be UNCHANGED
        assert inputs[0].position == pos_before
        # Axis should show the requested value
        assert axis.scaledPosition == pytest.approx(50.0, abs=0.1)

    def test_zero_position(self, axis, inputs):
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        axis.zero_position()
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.01)

    def test_set_custom_position_offset(self, axis, inputs, offset_provider):
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        offset_provider.currentOffset = 1
        axis._update_position()
        axis.set_current_position(25.0)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(25.0, abs=0.1)


class TestOffsetInRatioUnits:
    def test_offset_stored_in_ratio_units(self, axis, inputs):
        """Offset = value/factor - raw, stored in ratio-units not display-units."""
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        axis.formats.factor = Fraction(10, 254)  # IN mode
        axis.set_current_position(0)  # zero in IN
        axis._update_position()
        # raw = 100, target_ratio = 0 / (10/254) = 0, offset = 0 - 100 = -100 (ratio-units)
        assert axis.offsets[0] == pytest.approx(-100.0)
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.01)

    def test_mm_to_in_preserves_zeroed_position(self, axis, inputs):
        """Zero in MM, switch to IN — should still show 0."""
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        axis.formats.factor = Fraction(1, 1)
        axis.zero_position()
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.01)

        # Switch to IN
        axis.formats.factor = Fraction(10, 254)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.01)

    def test_mm_to_in_converts_offset_correctly(self, axis, inputs):
        """Set 25.4mm, switch to IN — should show ~1.0in."""
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 0
        axis.formats.factor = Fraction(1, 1)
        axis.set_current_position(25.4)  # set to 25.4mm
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(25.4, abs=0.01)

        # Switch to IN
        axis.formats.factor = Fraction(10, 254)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(1.0, abs=0.01)


class TestSyncRatio:
    def test_sync_ratio_written_to_hardware(self, axis, board):
        board.connected = True
        axis.syncRatioNum = 360
        axis.syncRatioDen = 100
        axis._set_sync_ratio()
        board.device['scales'][0].__setitem__.assert_called()


class TestSyncConflict:
    def test_conflict_blocks_enable(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        ax1 = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                         transform=AxisTransform.identity(0), id_override="test_conflict_0")
        ax2 = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                         transform=AxisTransform.identity(0), id_override="test_conflict_1")
        board.connected = True

        board.device['scales'][0].__getitem__ = MagicMock(return_value=False)
        ax1.syncEnable = True

        ax2.syncEnable = False
        ax2.toggle_sync(all_axes=[ax1, ax2])
        assert ax2.syncEnable is False

    def test_no_conflict_on_different_inputs(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        ax1 = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                         transform=AxisTransform.identity(0), id_override="test_noconflict_0")
        ax2 = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                         transform=AxisTransform.identity(1), id_override="test_noconflict_1")
        board.connected = True
        ax1.syncEnable = True

        scale_1_mock = MagicMock()
        scale_1_mock.__getitem__ = MagicMock(return_value=False)
        board.device['scales'].__getitem__ = MagicMock(return_value=scale_1_mock)
        ax2.toggle_sync(all_axes=[ax1, ax2])
        assert ax2.syncEnable is True


class TestPersistence:
    def test_axis_saves_and_restores_name(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputs=inputs,
            transform=AxisTransform.identity(0),
            id_override="test_persist",
        )
        ax.axis_name = "TestAxis"

        ax2 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputs=inputs,
            id_override="test_persist",
        )
        assert ax2.axis_name == "TestAxis"

    def test_property_change_preserves_transform_config(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        ax = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 2), id_override="test_prop_preserves")

        ax.axis_name = "Modified"

        with open(ax.filename) as f:
            data = yaml.safe_load(f)
        assert "transform_config" in data
        assert data["transform_config"]["transform_type"] == "sum"
        assert data["transform_config"]["contributions"] == [0, 2]

    def test_sum_transform_survives_round_trip(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputs=inputs,
            transform=AxisTransform.sum(1, 3),
            id_override="test_roundtrip",
        )

        ax2 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputs=inputs,
            id_override="test_roundtrip",
        )
        assert ax2.transform.transform_type == TransformType.SUM
        assert ax2.transform.contributions == (1, 3)

    def test_transform_change_then_property_change_preserves_both(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputs=inputs,
            transform=AxisTransform.identity(0),
            id_override="test_both",
        )

        ax.transform = AxisTransform.sum(1, 2)
        ax.syncRatioNum = 720

        ax2 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputs=inputs,
            id_override="test_both",
        )
        assert ax2.syncRatioNum == 720
        assert ax2.transform.transform_type == TransformType.SUM
        assert ax2.transform.contributions == (1, 2)

    def test_multiple_property_changes_dont_corrupt_file(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        ax = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                        transform=AxisTransform.sum(0, 3), id_override="test_multi_change")

        ax.axis_name = "MyAxis"
        ax.syncRatioNum = 500
        ax.syncRatioDen = 200
        ax.spindleMode = True

        ax2 = _make_axis(board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch,
                         transform=None, id_override="test_multi_change")
        assert ax2.axis_name == "MyAxis"
        assert ax2.syncRatioNum == 500
        assert ax2.syncRatioDen == 200
        assert ax2.spindleMode is True
        assert ax2.transform.transform_type == TransformType.SUM
        assert ax2.transform.contributions == (0, 3)

    def test_offsets_persist_correctly(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        """Offsets (including non-zero slots) survive save/restore."""
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputs=inputs,
            transform=AxisTransform.identity(0),
            id_override="test_offsets",
        )
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100

        # Set offset on slot 0
        ax.set_current_position(0)

        # Set offset on slot 1
        offset_provider.currentOffset = 1
        ax.set_current_position(50.0)

        # Restore
        ax2 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputs=inputs,
            id_override="test_offsets",
        )
        assert ax2.offsets[0] == ax.offsets[0]
        assert ax2.offsets[1] == ax.offsets[1]


class TestAbsOffset:
    def test_abs_offset_included_in_position(self, axis, inputs):
        """abs_offset adds to raw before tool offset and factor."""
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        axis.abs_offset = 10
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(110.0)

    def test_abs_mode_zero_modifies_abs_offset(self, axis, inputs, offset_provider):
        """Zeroing in ABS mode changes abs_offset, not tool offset."""
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        offset_provider.abs_mode = True
        axis.zero_position()
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.01)
        assert axis.abs_offset == pytest.approx(-100.0)
        assert axis.offsets[0] == 0  # tool offset unchanged

    def test_inc_mode_zero_modifies_tool_offset(self, axis, inputs, offset_provider):
        """Zeroing in INC mode changes tool offset, not abs_offset."""
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 100
        axis.abs_offset = 10
        offset_provider.abs_mode = False
        axis.zero_position()
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.01)
        assert axis.abs_offset == 10  # abs_offset unchanged
        assert axis.offsets[0] == pytest.approx(-110.0)

    def test_abs_calibration_propagates_to_all_tools(self, axis, inputs, offset_provider):
        """After setting tool offsets, ABS recalibration shifts all tools uniformly."""
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1

        # Zero tool 0 at position 100
        inputs[0].position = 100
        offset_provider.abs_mode = False
        axis.zero_position()
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.01)

        # Zero tool 1 at position 200
        offset_provider.currentOffset = 1
        inputs[0].position = 200
        axis.zero_position()
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.01)

        # Now recalibrate ABS: set to 50 at position 200, tool 1 active
        offset_provider.abs_mode = True
        axis.set_current_position(50.0)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(50.0, abs=0.1)

        # Switch to tool 0 — should reflect ABS shift equally
        offset_provider.currentOffset = 0
        axis._update_position()
        # Tool 0 was zeroed at pos=100, tool 1 at pos=200
        # At pos=200, tool 0 raw+abs+offset[0]: 200 + abs + (-100)
        # Tool 0 should show 100 + abs_shift (same shift as tool 1 got)
        tool0_pos = axis.scaledPosition
        # The key invariant: both tools shifted by the same amount
        # Tool 1 went from 0 to 50, so tool 0 should go from 100 to 150
        assert tool0_pos == pytest.approx(150.0, abs=0.1)

    def test_abs_offset_persisted(self, board, formats, servo, offset_provider, inputs, tmp_path, monkeypatch):
        """abs_offset survives save/restore cycle."""
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        ax = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputs=inputs,
            transform=AxisTransform.identity(0),
            id_override="test_abs_persist",
        )
        ax.abs_offset = -42.5

        ax2 = AxisDispatcher(
            board=board, formats=formats, servo=servo,
            offset_provider=offset_provider, inputs=inputs,
            id_override="test_abs_persist",
        )
        assert ax2.abs_offset == pytest.approx(-42.5)

    def test_abs_offset_with_factor(self, axis, inputs, offset_provider):
        """abs_offset stored in ratio-units, factor applied after."""
        inputs[0].ratioNum = 1
        inputs[0].ratioDen = 1
        inputs[0].position = 254
        axis.formats.factor = Fraction(10, 254)  # IN mode
        offset_provider.abs_mode = True
        axis.zero_position()
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.01)
        # abs_offset should be in ratio-units
        assert axis.abs_offset == pytest.approx(-254.0)

        # Switch to MM — still zero
        axis.formats.factor = Fraction(1, 1)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.01)

    def test_abs_offset_with_spindle_mode(self, axis, inputs, offset_provider):
        """abs_offset works in spindle mode (ratio-units = steps)."""
        axis.spindleMode = True
        inputs[0].spindleMode = True
        inputs[0].encoder_ppr = 1000
        inputs[0].position = 500  # = 180 degrees (500/1000*360)
        offset_provider.abs_mode = True
        axis.set_current_position(0)
        axis._update_position()
        assert axis.scaledPosition == pytest.approx(0.0, abs=0.1)
