from fractions import Fraction
from unittest.mock import MagicMock

import pytest

from tests.dispatchers.conftest import MockBoard, MockFormats
from rcp.dispatchers.servo import ServoDispatcher


@pytest.fixture
def board():
    b = MockBoard()
    b.device = MagicMock()
    return b


@pytest.fixture
def formats():
    return MockFormats()


@pytest.fixture
def servo(board, formats, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    return ServoDispatcher(board=board, formats=formats, id_override="0")


class TestServoDispatcherFilename:
    def test_yaml_filename_is_servobar(self, servo):
        assert servo.filename.name == "ServoBar-0.yaml"


class TestUpdatePositions:
    def test_positions_computed_for_divisions(self, servo):
        servo.divisions = 4
        servo.ratioNum = 400
        servo.ratioDen = 360
        servo.update_positions()
        assert len(servo.positions) == 4
        assert len(servo.step_positions) == 4
        assert servo.positions[0] == 0.0
        assert servo.positions[1] == pytest.approx(90.0)
        assert servo.positions[2] == pytest.approx(180.0)
        assert servo.positions[3] == pytest.approx(270.0)

    def test_divisions_clamped_to_minimum_1(self, servo):
        servo.divisions = 0
        servo.update_positions()
        assert servo.divisions == 1

    def test_step_positions_match_ratio(self, servo):
        servo.divisions = 4
        servo.ratioNum = 1
        servo.ratioDen = 1
        servo.update_positions()
        assert servo.step_positions[0] == 0
        assert servo.step_positions[1] == 90
        assert servo.step_positions[2] == 180
        assert servo.step_positions[3] == 270


class TestGoNextPrevious:
    def test_go_next_increments_index(self, servo):
        servo.divisions = 4
        servo.update_positions()
        servo.go_next()
        assert servo.index == 1
        assert servo.preferredDirection == 1

    def test_go_previous_decrements_index(self, servo):
        servo.divisions = 4
        servo.update_positions()
        servo.index = 2
        servo.previousIndex = 2
        servo.go_previous()
        assert servo.index == 1
        assert servo.preferredDirection == -1

    def test_go_next_wraps_around(self, servo):
        servo.divisions = 4
        servo.update_positions()
        servo.index = 3
        servo.previousIndex = 3
        servo.go_next()
        assert servo.index == 0

    def test_go_previous_wraps_around(self, servo):
        servo.divisions = 4
        servo.update_positions()
        servo.index = 0
        servo.previousIndex = 0
        servo.go_previous()
        assert servo.index == 3


class TestScaledPosition:
    def test_angle_mode_position(self, servo):
        servo.elsMode = False
        servo.ratioNum = 1
        servo.ratioDen = 1
        servo.position = 45
        servo.update_scaledPosition(servo, None)
        assert servo.scaledPosition == pytest.approx(45.0)
        assert "45" in servo.formattedPosition

    def test_angle_mode_wraps_at_units_per_turn(self, servo):
        servo.elsMode = False
        servo.ratioNum = 1
        servo.ratioDen = 1
        servo.position = 370
        servo.update_scaledPosition(servo, None)
        assert servo.scaledPosition == pytest.approx(10.0)

    def test_els_mode_position(self, servo):
        servo.elsMode = True
        servo.ratioNum = 1
        servo.ratioDen = 1
        servo.position = 100
        formats = servo.formats
        formats.factor = Fraction(1, 1)
        servo.update_scaledPosition(servo, None)
        assert servo.scaledPosition == pytest.approx(100.0)


class TestConfigureLeadScrewRatio:
    def test_metric_lead_screw(self, servo):
        servo.elsMode = True
        servo.leadScrewPitch = 2.0
        servo.leadScrewPitchIn = False
        servo.leadScrewPitchSteps = 800
        servo.configure_lead_screw_ratio(servo, None)
        expected = Fraction(2) * Fraction(1, 800)
        assert servo.ratioNum == expected.numerator
        assert servo.ratioDen == expected.denominator

    def test_imperial_lead_screw(self, servo):
        servo.elsMode = True
        servo.leadScrewPitch = 0.25
        servo.leadScrewPitchIn = True
        servo.leadScrewPitchSteps = 800
        servo.configure_lead_screw_ratio(servo, None)
        expected = Fraction(0.25) * Fraction(254, 10) * Fraction(1, 800)
        assert servo.ratioNum == expected.numerator
        assert servo.ratioDen == expected.denominator

    def test_non_els_mode_skips(self, servo):
        servo.elsMode = False
        original_num = servo.ratioNum
        original_den = servo.ratioDen
        servo.configure_lead_screw_ratio(servo, None)
        assert servo.ratioNum == original_num
        assert servo.ratioDen == original_den


class TestOnIndex:
    def test_delta_computed_and_written_to_device(self, servo):
        servo.divisions = 4
        servo.ratioNum = 1
        servo.ratioDen = 1
        servo.update_positions()
        servo.preferredDirection = 1
        servo.index = 1
        # on_index should write to device
        servo.board.device['servo'].__setitem__.assert_called()

    def test_no_write_when_delta_is_zero(self, servo):
        servo.divisions = 4
        servo.ratioNum = 1
        servo.ratioDen = 1
        servo.update_positions()
        # index is already 0, previousIndex is 0, delta should be 0
        servo.board.device['servo'].__setitem__.reset_mock()
        servo.previousIndex = 0
        servo.on_index(servo, 0)
        servo.board.device['servo'].__setitem__.assert_not_called()


class TestSetCurrentPosition:
    def test_back_computes_position(self, servo):
        servo.ratioNum = 400
        servo.ratioDen = 360
        servo.set_current_position(180.0)
        ratio = Fraction(400, 360)
        expected = int(180.0 / ratio)
        assert servo.position == expected


class TestOnConnected:
    def test_reads_fast_data_and_writes_device(self, servo):
        servo.board.fast_data_values = {
            'servoCurrent': 1000,
            'servoEnable': 1,
        }
        servo.board.connected = True
        assert servo.encoderCurrent == 1000
        assert servo.servoEnable == 1

    def test_disableControls_true_when_servo_disabled(self, servo):
        servo.board.fast_data_values = {
            'servoCurrent': 0,
            'servoEnable': 0,
        }
        servo.board.connected = True
        assert servo.disableControls is True

    def test_disableControls_false_when_servo_enabled(self, servo):
        servo.board.fast_data_values = {
            'servoCurrent': 0,
            'servoEnable': 1,
        }
        servo.board.connected = True
        assert servo.disableControls is False


class TestToggleEnable:
    def test_toggle_when_disconnected(self, servo):
        servo.board.connected = False
        servo.servoEnable = 1
        servo.toggle_enable()
        assert servo.servoEnable == 0

    def test_toggle_on(self, servo):
        servo.board.connected = True
        servo.servoEnable = 0
        servo.toggle_enable()
        assert servo.servoEnable == 1

    def test_toggle_off(self, servo):
        servo.board.connected = True
        servo.servoEnable = 1
        servo.toggle_enable()
        assert servo.servoEnable == 0
