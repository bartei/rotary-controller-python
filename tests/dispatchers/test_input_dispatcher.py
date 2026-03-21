from unittest.mock import MagicMock

import pytest
import yaml

from tests.dispatchers.conftest import MockBoard
from rcp.dispatchers.input import InputDispatcher


@pytest.fixture
def board():
    b = MockBoard()
    b.device = MagicMock()
    return b


@pytest.fixture
def inp(board, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    return InputDispatcher(
        board=board, inputIndex=0, id_override="0",
    )


class TestInputDispatcherFilename:
    def test_yaml_filename_is_coordbar(self, inp):
        assert inp.filename.name == "CoordBar-0.yaml"

    def test_different_indices_different_files(self, board, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        i0 = InputDispatcher(board=board, inputIndex=0, id_override="0")
        i1 = InputDispatcher(board=board, inputIndex=1, id_override="1")
        assert i0.filename.name == "CoordBar-0.yaml"
        assert i1.filename.name == "CoordBar-1.yaml"


class TestEncoderTracking:
    def test_update_tick_tracks_encoder_delta(self, inp):
        inp.board.connected = True
        inp.board.fast_data_values = {
            'scaleCurrent': [100, 0, 0, 0],
        }
        inp.encoderCurrent = 0
        inp._on_update_tick()
        assert inp.position == 100

    def test_update_tick_ignores_when_disconnected(self, inp):
        inp.board.connected = False
        inp.board.fast_data_values = {
            'scaleCurrent': [100, 0, 0, 0],
        }
        original_pos = inp.position
        inp._on_update_tick()
        assert inp.position == original_pos

    def test_accumulates_multiple_deltas(self, inp):
        inp.board.connected = True
        inp.encoderCurrent = 0
        inp.board.fast_data_values = {'scaleCurrent': [50, 0, 0, 0]}
        inp._on_update_tick()
        inp.board.fast_data_values = {'scaleCurrent': [80, 0, 0, 0]}
        inp._on_update_tick()
        assert inp.position == 80


class TestScaledValue:
    def test_scaled_value_equals_position_times_ratio(self, inp):
        inp.ratioNum = 360
        inp.ratioDen = 1000
        inp.position = 500
        inp._update_scaled_value()
        assert inp.scaled_value == pytest.approx(500 * 360 / 1000)

    def test_scaled_value_reactive_to_ratio_change(self, inp):
        inp.position = 100
        inp.ratioNum = 1
        inp.ratioDen = 1
        assert inp.scaled_value == pytest.approx(100.0)
        inp.ratioNum = 2
        assert inp.scaled_value == pytest.approx(200.0)

    def test_unit_ratio(self, inp):
        inp.ratioNum = 1
        inp.ratioDen = 1
        inp.position = 42
        inp._update_scaled_value()
        assert inp.scaled_value == pytest.approx(42.0)


class TestSpindleIdentity:
    """In spindle mode, InputDispatcher passes raw position (identity)."""

    def test_scaled_value_equals_position(self, inp):
        inp.encoder_ppr = 1000
        inp.spindleMode = True
        inp.position = 500
        inp._update_scaled_value()
        assert inp.scaled_value == pytest.approx(500.0)

    def test_ratio_ignored_in_spindle_mode(self, inp):
        """ratioNum/ratioDen should NOT affect scaled_value in spindle mode."""
        inp.encoder_ppr = 1000
        inp.spindleMode = True
        inp.ratioNum = 360
        inp.ratioDen = 1000
        inp.position = 500
        inp._update_scaled_value()
        assert inp.scaled_value == pytest.approx(500.0)  # not 180

    def test_non_spindle_still_uses_ratio(self, inp):
        inp.spindleMode = False
        inp.ratioNum = 360
        inp.ratioDen = 1000
        inp.position = 500
        inp._update_scaled_value()
        assert inp.scaled_value == pytest.approx(180.0)


class TestSpindleWrapping:
    """Spindle wrapping prevents unbounded position growth."""

    def test_large_position_wraps(self, inp):
        inp.encoder_ppr = 1000
        inp.spindleMode = True
        inp.position = 5500
        inp._update_scaled_value()
        assert 0 <= inp.position < 1000
        assert inp.scaled_value == pytest.approx(float(inp.position))

    def test_negative_position_wraps(self, inp):
        inp.encoder_ppr = 1000
        inp.spindleMode = True
        inp.position = -200
        inp._update_scaled_value()
        assert 0 <= inp.position < 1000

    def test_exact_multiple_wraps_to_zero(self, inp):
        inp.encoder_ppr = 1000
        inp.spindleMode = True
        inp.position = 3000
        inp._update_scaled_value()
        assert inp.position == 0
        assert inp.scaled_value == pytest.approx(0.0)

    def test_position_within_range_unchanged(self, inp):
        inp.encoder_ppr = 1000
        inp.spindleMode = True
        inp.position = 500
        inp._update_scaled_value()
        assert inp.position == 500
        assert inp.scaled_value == pytest.approx(500.0)

    def test_no_wrapping_when_not_spindle(self, inp):
        """Non-spindle mode has zero wrap steps, no wrapping."""
        inp.spindleMode = False
        inp.ratioNum = 360
        inp.ratioDen = 1000
        inp.position = 100_000
        inp._update_scaled_value()
        assert inp.scaled_value == pytest.approx(100_000 * 360 / 1000)

    def test_wrap_steps_self_computed(self, inp):
        """_spindle_wrap_steps auto-computed from encoder_ppr * gear_ratio_num."""
        inp.encoder_ppr = 500
        inp.gear_ratio_num = 3
        inp.spindleMode = True
        assert inp._spindle_wrap_steps == 1500

    def test_wrap_steps_cleared_when_not_spindle(self, inp):
        inp.encoder_ppr = 1000
        inp.spindleMode = True
        assert inp._spindle_wrap_steps == 1000
        inp.spindleMode = False
        assert inp._spindle_wrap_steps == 0


class TestSpeed:
    def test_speed_from_fast_data(self, inp):
        inp.board.fast_data_values = {
            'scaleSpeed': [1000, 0, 0, 0],
        }
        inp._speed_task()
        assert inp.steps_per_second == pytest.approx(1000.0)

    def test_speed_rolling_average(self, inp):
        inp.board.fast_data_values = {'scaleSpeed': [100, 0, 0, 0]}
        inp._speed_task()
        inp.board.fast_data_values = {'scaleSpeed': [200, 0, 0, 0]}
        inp._speed_task()
        assert inp.steps_per_second == pytest.approx(150.0)

    def test_speed_skips_when_no_data(self, inp):
        inp.board.fast_data_values = None
        inp._speed_task()  # should not crash
        assert inp.steps_per_second == 0


class TestSaveRestore:
    def test_round_trip_ratio(self, board, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        i1 = InputDispatcher(board=board, inputIndex=2, id_override="test_rt")
        i1.ratioNum = 360
        i1.ratioDen = 1000
        i1.stepsPerMM = 500

        i2 = InputDispatcher(board=board, inputIndex=2, id_override="test_rt")
        assert i2.ratioNum == 360
        assert i2.ratioDen == 1000
        assert i2.stepsPerMM == 500

    def test_old_yaml_keys_silently_ignored(self, board, tmp_path, monkeypatch):
        """Old CoordBar YAML keys (offsets, syncRatioNum, axisName) should be silently ignored."""
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        config_dir = tmp_path / ".config" / "rotary-controller-python"
        config_dir.mkdir(parents=True)
        yaml_file = config_dir / "CoordBar-test_old.yaml"
        yaml_file.write_text(yaml.dump({
            "ratioNum": 720,
            "ratioDen": 2000,
            "stepsPerMM": 400,
            "offsets": [0] * 100,
            "syncRatioNum": 360,
            "syncRatioDen": 100,
            "axisName": "X",
            "spindleMode": True,
        }))

        inp = InputDispatcher(board=board, inputIndex=0, id_override="test_old")
        assert inp.ratioNum == 720
        assert inp.ratioDen == 2000
        assert inp.stepsPerMM == 400
        # Old keys should not cause errors, and input-only properties are loaded

    def test_spindle_mode_persists(self, board, tmp_path, monkeypatch):
        """spindleMode is now persisted (not transient)."""
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        i1 = InputDispatcher(board=board, inputIndex=0, id_override="test_spindle_persist")
        i1.spindleMode = True
        i1.encoder_ppr = 2000
        i1.gear_ratio_num = 3
        i1.gear_ratio_den = 2

        i2 = InputDispatcher(board=board, inputIndex=0, id_override="test_spindle_persist")
        assert i2.spindleMode is True
        assert i2.encoder_ppr == 2000
        assert i2.gear_ratio_num == 3
        assert i2.gear_ratio_den == 2

    def test_yaml_contains_only_input_properties(self, board, tmp_path, monkeypatch):
        """YAML file should only contain InputDispatcher properties after save."""
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        inp = InputDispatcher(board=board, inputIndex=0, id_override="test_clean")
        inp.ratioNum = 100

        with open(inp.filename) as f:
            data = yaml.safe_load(f)

        # Should contain input properties
        assert "ratioNum" in data
        assert "ratioDen" in data
        assert "stepsPerMM" in data
        assert "inputIndex" in data
        assert "spindleMode" in data
        assert "encoder_ppr" in data
        assert "gear_ratio_num" in data
        assert "gear_ratio_den" in data

        # Should NOT contain old scale properties
        assert "offsets" not in data
        assert "syncRatioNum" not in data
        assert "axisName" not in data
        assert "syncButtonColor" not in data

    def test_default_values_when_no_yaml(self, board, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "rcp.dispatchers.saving_dispatcher.Path.home",
            lambda: tmp_path,
        )
        inp = InputDispatcher(board=board, inputIndex=0, id_override="test_defaults")
        assert inp.ratioNum == 1
        assert inp.ratioDen == 1
        assert inp.stepsPerMM == 1000
