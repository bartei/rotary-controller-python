import pytest

from rcp.utils.ctype_calc import uint32_subtract_to_int32


class TestUint32SubtractToInt32:
    def test_simple_positive_delta(self):
        assert uint32_subtract_to_int32(100, 50) == 50

    def test_simple_negative_delta(self):
        assert uint32_subtract_to_int32(50, 100) == -50

    def test_zero_delta(self):
        assert uint32_subtract_to_int32(100, 100) == 0

    def test_both_zero(self):
        assert uint32_subtract_to_int32(0, 0) == 0

    def test_wraparound_forward(self):
        """Encoder wraps from max uint32 to small value (forward motion)."""
        # 0xFFFFFFFF + 10 wraps to 9 in uint32
        assert uint32_subtract_to_int32(9, 0xFFFFFFFF) == 10

    def test_wraparound_backward(self):
        """Encoder wraps from small value back past zero (backward motion)."""
        assert uint32_subtract_to_int32(0xFFFFFFFF, 9) == -10

    def test_large_values(self):
        a = 0x80000000
        b = 0x7FFFFFFF
        assert uint32_subtract_to_int32(a, b) == 1

    def test_max_positive_int32(self):
        assert uint32_subtract_to_int32(0x7FFFFFFF, 0) == 0x7FFFFFFF

    def test_max_negative_int32(self):
        # 0 - 0x80000000 in uint32 = 0x80000000, interpreted as int32 = -2147483648
        assert uint32_subtract_to_int32(0, 0x80000000) == -2147483648

    def test_single_step_forward(self):
        assert uint32_subtract_to_int32(1, 0) == 1

    def test_single_step_backward(self):
        assert uint32_subtract_to_int32(0, 1) == -1
