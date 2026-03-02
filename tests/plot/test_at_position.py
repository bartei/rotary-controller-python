import math

import pytest


def compute_at_position(
    tool_x: float,
    tool_y: float,
    active_points: list,
    selected_point: int,
    tolerance: float,
) -> bool:
    """Reproduce the at_position logic from FloatView.update_tick()."""
    if not active_points:
        return False
    if not (0 <= selected_point < len(active_points)):
        return False
    pt = active_points[selected_point]
    dist = math.hypot(tool_x - pt[0], tool_y - pt[1])
    return dist <= tolerance


class TestAtPosition:
    def test_tool_exactly_on_point(self):
        points = [(10.0, 20.0), (30.0, 40.0)]
        assert compute_at_position(10.0, 20.0, points, 0, 0.05) is True

    def test_tool_within_tolerance(self):
        points = [(10.0, 20.0)]
        assert compute_at_position(10.03, 20.04, points, 0, 0.05) is True

    def test_tool_outside_tolerance(self):
        points = [(10.0, 20.0)]
        assert compute_at_position(10.1, 20.1, points, 0, 0.05) is False

    def test_no_points(self):
        assert compute_at_position(0.0, 0.0, [], 0, 0.05) is False

    def test_invalid_selected_index(self):
        points = [(1.0, 2.0)]
        assert compute_at_position(1.0, 2.0, points, 5, 0.05) is False

    def test_custom_tolerance_large(self):
        points = [(0.0, 0.0)]
        # Distance is ~1.414, within tolerance of 2.0
        assert compute_at_position(1.0, 1.0, points, 0, 2.0) is True

    def test_custom_tolerance_small(self):
        points = [(0.0, 0.0)]
        # Distance is 0.01, outside tolerance of 0.005
        assert compute_at_position(0.01, 0.0, points, 0, 0.005) is False

    def test_selected_second_point(self):
        points = [(0.0, 0.0), (5.0, 5.0)]
        # Far from first point but on second point
        assert compute_at_position(5.0, 5.0, points, 1, 0.05) is True

    def test_at_boundary(self):
        points = [(0.0, 0.0)]
        # Distance exactly equal to tolerance
        assert compute_at_position(0.05, 0.0, points, 0, 0.05) is True
