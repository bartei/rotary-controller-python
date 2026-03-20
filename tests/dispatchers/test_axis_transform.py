import pytest

from rcp.dispatchers.axis_transform import (
    AxisTransform,
    TransformType,
)


class TestIdentityTransform:
    def test_compute_returns_single_input(self):
        t = AxisTransform.identity(0)
        assert t.compute({0: 42.0}) == pytest.approx(42.0)

    def test_primary_input(self):
        t = AxisTransform.identity(2)
        assert t.primary_input == 2

    def test_input_indices(self):
        t = AxisTransform.identity(3)
        assert t.input_indices == {3}

    def test_transform_type(self):
        t = AxisTransform.identity(0)
        assert t.transform_type == TransformType.IDENTITY

    def test_missing_input_defaults_to_zero(self):
        t = AxisTransform.identity(5)
        assert t.compute({0: 100.0}) == pytest.approx(0.0)


class TestSumTransform:
    def test_compute_adds_two_inputs(self):
        t = AxisTransform.sum(0, 1)
        assert t.compute({0: 10.0, 1: 20.0}) == pytest.approx(30.0)

    def test_primary_input_is_first(self):
        t = AxisTransform.sum(2, 3)
        assert t.primary_input == 2

    def test_input_indices(self):
        t = AxisTransform.sum(1, 3)
        assert t.input_indices == {1, 3}

    def test_transform_type(self):
        t = AxisTransform.sum(0, 1)
        assert t.transform_type == TransformType.SUM

    def test_missing_second_input_defaults_to_zero(self):
        t = AxisTransform.sum(0, 1)
        assert t.compute({0: 10.0}) == pytest.approx(10.0)


class TestSerialization:
    def test_identity_round_trip(self):
        t = AxisTransform.identity(2)
        t2 = AxisTransform.from_dict(t.to_dict())
        assert t == t2

    def test_sum_round_trip(self):
        t = AxisTransform.sum(1, 3)
        t2 = AxisTransform.from_dict(t.to_dict())
        assert t == t2

    def test_to_dict_identity(self):
        t = AxisTransform.identity(0)
        d = t.to_dict()
        assert d == {"transform_type": "identity", "contributions": [0]}

    def test_to_dict_sum(self):
        t = AxisTransform.sum(0, 1)
        d = t.to_dict()
        assert d == {"transform_type": "sum", "contributions": [0, 1]}


class TestBackwardCompatibility:
    """Old YAML files used ScaleWeight dicts with weight_num/weight_den."""

    def test_old_identity_format(self):
        old = {
            "transform_type": "identity",
            "angle_degrees": 0.0,
            "contributions": [{"input_index": 2, "weight_num": 1, "weight_den": 1}],
        }
        t = AxisTransform.from_dict(old)
        assert t.transform_type == TransformType.IDENTITY
        assert t.primary_input == 2

    def test_old_weighted_sum_becomes_sum(self):
        old = {
            "transform_type": "weighted_sum",
            "angle_degrees": 0.0,
            "contributions": [
                {"input_index": 0, "weight_num": 2, "weight_den": 3},
                {"input_index": 1, "weight_num": 5, "weight_den": 8},
            ],
        }
        t = AxisTransform.from_dict(old)
        assert t.transform_type == TransformType.SUM
        assert t.contributions == (0, 1)

    def test_old_scaling_becomes_identity(self):
        old = {
            "transform_type": "scaling",
            "contributions": [{"input_index": 1, "weight_num": 3, "weight_den": 7}],
        }
        t = AxisTransform.from_dict(old)
        assert t.transform_type == TransformType.IDENTITY
        assert t.primary_input == 1

    def test_old_angle_cos_becomes_identity(self):
        old = {
            "transform_type": "angle_cos",
            "angle_degrees": 45.0,
            "contributions": [{"input_index": 2, "weight_num": 7071, "weight_den": 10000}],
        }
        t = AxisTransform.from_dict(old)
        assert t.transform_type == TransformType.IDENTITY
        assert t.primary_input == 2

    def test_old_angle_sin_becomes_identity(self):
        old = {
            "transform_type": "angle_sin",
            "angle_degrees": 30.0,
            "contributions": [{"input_index": 0, "weight_num": 1, "weight_den": 2}],
        }
        t = AxisTransform.from_dict(old)
        assert t.transform_type == TransformType.IDENTITY
        assert t.primary_input == 0

    def test_empty_contributions_fallback(self):
        t = AxisTransform.from_dict({"transform_type": "identity", "contributions": []})
        assert t.transform_type == TransformType.IDENTITY
        assert t.primary_input == 0

    def test_unknown_type_fallback(self):
        t = AxisTransform.from_dict({"transform_type": "future_thing", "contributions": [1]})
        assert t.transform_type == TransformType.IDENTITY
        assert t.primary_input == 1
