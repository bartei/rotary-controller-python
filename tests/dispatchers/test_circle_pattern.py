import math

import pytest

from rcp.dispatchers.circle_pattern import CirclePatternDispatcher


@pytest.fixture
def pattern(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    p = CirclePatternDispatcher(id_override="test_circle")
    p.recalculate()
    return p


class TestCirclePatternDefaults:
    def test_default_holes_count(self, pattern):
        assert pattern.holes_count == 6

    def test_default_diameter(self, pattern):
        assert pattern.diameter == 120.0

    def test_default_angles(self, pattern):
        assert pattern.start_angle == 0
        assert pattern.end_angle == 360

    def test_default_origin(self, pattern):
        assert pattern.origin_x == 0
        assert pattern.origin_y == 0


class TestFullCircle:
    def test_correct_number_of_points(self, pattern):
        """Full circle (360°) should produce exactly holes_count points."""
        assert len(pattern.points) == 6

    def test_points_on_circle(self, pattern):
        """All points should be at radius = diameter/2 from origin."""
        r = pattern.diameter / 2
        for x, y in pattern.points:
            dist = math.sqrt((x - pattern.origin_x) ** 2 + (y - pattern.origin_y) ** 2)
            assert dist == pytest.approx(r, abs=0.01)

    def test_first_point_at_start_angle(self, pattern):
        """First point should be at start_angle (0°) = rightmost."""
        r = pattern.diameter / 2
        assert pattern.points[0][0] == pytest.approx(r, abs=0.01)
        assert pattern.points[0][1] == pytest.approx(0, abs=0.01)

    def test_evenly_spaced(self, pattern):
        """Points should be evenly spaced angularly."""
        angles = []
        for x, y in pattern.points:
            angles.append(math.atan2(y, x))
        # Sort and compute differences
        angles.sort()
        diffs = [angles[i + 1] - angles[i] for i in range(len(angles) - 1)]
        for d in diffs:
            assert d == pytest.approx(2 * math.pi / 6, abs=0.01)


class TestPartialArc:
    def test_arc_has_extra_point(self, pattern):
        """Partial arc (not 360°) should have holes_count + 1 points."""
        pattern.start_angle = 0
        pattern.end_angle = 180
        pattern.holes_count = 4
        pattern.recalculate()
        assert len(pattern.points) == 5

    def test_first_and_last_point_positions(self, pattern):
        """First point at start_angle, last at end_angle."""
        pattern.start_angle = 0
        pattern.end_angle = 90
        pattern.holes_count = 2
        pattern.diameter = 100
        pattern.origin_x = 0
        pattern.origin_y = 0
        pattern.recalculate()

        r = 50
        # First point at 0°
        assert pattern.points[0][0] == pytest.approx(r, abs=0.01)
        assert pattern.points[0][1] == pytest.approx(0, abs=0.01)
        # Last point at 90°
        assert pattern.points[-1][0] == pytest.approx(0, abs=0.01)
        assert pattern.points[-1][1] == pytest.approx(r, abs=0.01)


class TestOriginOffset:
    def test_origin_shifts_all_points(self, pattern):
        pattern.origin_x = 10
        pattern.origin_y = 20
        pattern.recalculate()
        r = pattern.diameter / 2
        for x, y in pattern.points:
            dist = math.sqrt((x - 10) ** 2 + (y - 20) ** 2)
            assert dist == pytest.approx(r, abs=0.01)


class TestStartAngle:
    def test_rotated_start(self, pattern):
        """start_angle=90 should place first point at top."""
        pattern.start_angle = 90
        pattern.end_angle = 450  # 90+360
        pattern.diameter = 100
        pattern.origin_x = 0
        pattern.origin_y = 0
        pattern.recalculate()
        # First point at 90° = (0, 50)
        assert pattern.points[0][0] == pytest.approx(0, abs=0.01)
        assert pattern.points[0][1] == pytest.approx(50, abs=0.01)


class TestEdgeCases:
    def test_single_hole(self, pattern):
        pattern.holes_count = 1
        pattern.recalculate()
        assert len(pattern.points) == 1

    def test_two_holes(self, pattern):
        pattern.holes_count = 2
        pattern.recalculate()
        assert len(pattern.points) == 2
        # Should be diametrically opposite
        x0, y0 = pattern.points[0]
        x1, y1 = pattern.points[1]
        dist = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
        assert dist == pytest.approx(pattern.diameter, abs=0.01)
