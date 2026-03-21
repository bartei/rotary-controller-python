import pytest

from rcp.dispatchers.line_pattern import LinePatternDispatcher


@pytest.fixture
def pattern(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    p = LinePatternDispatcher(id_override="test_line")
    p.recalculate()
    return p


class TestLinePatternDefaults:
    def test_default_holes_count(self, pattern):
        assert pattern.holes_count == 5

    def test_default_origin(self, pattern):
        assert pattern.origin_x == 0
        assert pattern.origin_y == 0

    def test_default_end(self, pattern):
        assert pattern.end_x == 100.0
        assert pattern.end_y == 0.0


class TestHorizontalLine:
    def test_correct_number_of_points(self, pattern):
        assert len(pattern.points) == 5

    def test_first_point_at_origin(self, pattern):
        assert pattern.points[0] == pytest.approx((0, 0), abs=0.01)

    def test_last_point_at_end(self, pattern):
        assert pattern.points[-1] == pytest.approx((100, 0), abs=0.01)

    def test_evenly_spaced(self, pattern):
        """5 points from 0 to 100 should be at 0, 25, 50, 75, 100."""
        for i, (x, y) in enumerate(pattern.points):
            assert x == pytest.approx(i * 25, abs=0.01)
            assert y == pytest.approx(0, abs=0.01)


class TestDiagonalLine:
    def test_diagonal_points(self, pattern):
        pattern.origin_x = 0
        pattern.origin_y = 0
        pattern.end_x = 100
        pattern.end_y = 100
        pattern.holes_count = 3
        pattern.recalculate()

        assert len(pattern.points) == 3
        assert pattern.points[0] == pytest.approx((0, 0), abs=0.01)
        assert pattern.points[1] == pytest.approx((50, 50), abs=0.01)
        assert pattern.points[2] == pytest.approx((100, 100), abs=0.01)


class TestOriginOffset:
    def test_offset_origin(self, pattern):
        pattern.origin_x = 10
        pattern.origin_y = 20
        pattern.end_x = 110
        pattern.end_y = 20
        pattern.holes_count = 3
        pattern.recalculate()

        assert pattern.points[0] == pytest.approx((10, 20), abs=0.01)
        assert pattern.points[1] == pytest.approx((60, 20), abs=0.01)
        assert pattern.points[2] == pytest.approx((110, 20), abs=0.01)


class TestEdgeCases:
    def test_single_hole(self, pattern):
        """Single hole should be at origin."""
        pattern.holes_count = 1
        pattern.recalculate()
        assert len(pattern.points) == 1
        assert pattern.points[0] == pytest.approx((0, 0), abs=0.01)

    def test_two_holes(self, pattern):
        """Two holes should be at start and end."""
        pattern.holes_count = 2
        pattern.recalculate()
        assert len(pattern.points) == 2
        assert pattern.points[0] == pytest.approx((0, 0), abs=0.01)
        assert pattern.points[1] == pytest.approx((100, 0), abs=0.01)

    def test_zero_length_line(self, pattern):
        """All points at same position when origin == end."""
        pattern.end_x = 0
        pattern.end_y = 0
        pattern.holes_count = 3
        pattern.recalculate()
        for point in pattern.points:
            assert point == pytest.approx((0, 0), abs=0.01)
