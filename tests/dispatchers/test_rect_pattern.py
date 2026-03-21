import math

import pytest

from rcp.dispatchers.rect_pattern import RectPatternDispatcher


@pytest.fixture
def pattern(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rcp.dispatchers.saving_dispatcher.Path.home",
        lambda: tmp_path,
    )
    p = RectPatternDispatcher(id_override="test_rect")
    p.recalculate()
    return p


class TestRectPatternDefaults:
    def test_default_grid(self, pattern):
        assert pattern.columns == 3
        assert pattern.rows == 3

    def test_default_spacing(self, pattern):
        assert pattern.spacing_x == 25.0
        assert pattern.spacing_y == 25.0

    def test_default_angle(self, pattern):
        assert pattern.angle == 0

    def test_default_origin(self, pattern):
        assert pattern.origin_x == 0
        assert pattern.origin_y == 0


class TestGridGeneration:
    def test_correct_number_of_points(self, pattern):
        """3x3 grid should produce 9 points."""
        assert len(pattern.points) == 9

    def test_custom_grid_size(self, pattern):
        pattern.columns = 4
        pattern.rows = 2
        pattern.recalculate()
        assert len(pattern.points) == 8

    def test_single_point(self, pattern):
        pattern.columns = 1
        pattern.rows = 1
        pattern.recalculate()
        assert len(pattern.points) == 1
        assert pattern.points[0] == pytest.approx((0, 0), abs=0.01)


class TestCentering:
    def test_grid_centered_on_origin(self, pattern):
        """3x3 grid with spacing 25 should be centered: -25 to +25."""
        xs = [p[0] for p in pattern.points]
        ys = [p[1] for p in pattern.points]
        assert min(xs) == pytest.approx(-25.0, abs=0.01)
        assert max(xs) == pytest.approx(25.0, abs=0.01)
        assert min(ys) == pytest.approx(-25.0, abs=0.01)
        assert max(ys) == pytest.approx(25.0, abs=0.01)

    def test_center_of_mass_at_origin(self, pattern):
        """Center of all points should be at origin."""
        avg_x = sum(p[0] for p in pattern.points) / len(pattern.points)
        avg_y = sum(p[1] for p in pattern.points) / len(pattern.points)
        assert avg_x == pytest.approx(0, abs=0.01)
        assert avg_y == pytest.approx(0, abs=0.01)


class TestOriginOffset:
    def test_origin_shifts_all_points(self, pattern):
        pattern.origin_x = 100
        pattern.origin_y = 200
        pattern.recalculate()
        avg_x = sum(p[0] for p in pattern.points) / len(pattern.points)
        avg_y = sum(p[1] for p in pattern.points) / len(pattern.points)
        assert avg_x == pytest.approx(100, abs=0.01)
        assert avg_y == pytest.approx(200, abs=0.01)


class TestSpacing:
    def test_column_spacing(self, pattern):
        """Adjacent columns should differ by spacing_x."""
        pattern.columns = 3
        pattern.rows = 1
        pattern.spacing_x = 10
        pattern.recalculate()
        xs = sorted([p[0] for p in pattern.points])
        for i in range(len(xs) - 1):
            assert xs[i + 1] - xs[i] == pytest.approx(10, abs=0.01)

    def test_row_spacing(self, pattern):
        """Adjacent rows should differ by spacing_y."""
        pattern.columns = 1
        pattern.rows = 3
        pattern.spacing_y = 15
        pattern.recalculate()
        ys = sorted([p[1] for p in pattern.points])
        for i in range(len(ys) - 1):
            assert ys[i + 1] - ys[i] == pytest.approx(15, abs=0.01)


class TestRotation:
    def test_90_degree_rotation(self, pattern):
        """90° rotation should swap x and y axes."""
        pattern.columns = 2
        pattern.rows = 1
        pattern.spacing_x = 20
        pattern.angle = 0
        pattern.recalculate()
        unrotated = list(pattern.points)

        pattern.angle = 90
        pattern.recalculate()
        rotated = list(pattern.points)

        for (ux, uy), (rx, ry) in zip(unrotated, rotated):
            # After 90° rotation: new_x = -old_y, new_y = old_x
            assert rx == pytest.approx(-uy, abs=0.01)
            assert ry == pytest.approx(ux, abs=0.01)

    def test_rotation_preserves_distances(self, pattern):
        """Rotation should not change distances between points."""
        pattern.angle = 0
        pattern.recalculate()
        dist_0 = math.sqrt(
            (pattern.points[0][0] - pattern.points[1][0]) ** 2 +
            (pattern.points[0][1] - pattern.points[1][1]) ** 2
        )

        pattern.angle = 45
        pattern.recalculate()
        dist_45 = math.sqrt(
            (pattern.points[0][0] - pattern.points[1][0]) ** 2 +
            (pattern.points[0][1] - pattern.points[1][1]) ** 2
        )

        assert dist_0 == pytest.approx(dist_45, abs=0.01)

    def test_360_degree_same_as_0(self, pattern):
        """360° rotation should produce same points as 0°."""
        pattern.angle = 0
        pattern.recalculate()
        pts_0 = list(pattern.points)

        pattern.angle = 360
        pattern.recalculate()
        pts_360 = list(pattern.points)

        for p0, p360 in zip(pts_0, pts_360):
            assert p0[0] == pytest.approx(p360[0], abs=0.01)
            assert p0[1] == pytest.approx(p360[1], abs=0.01)
