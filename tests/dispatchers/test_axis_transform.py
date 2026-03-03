import math
from fractions import Fraction

import pytest

from rcp.dispatchers.axis_transform import (
    AxisTransform,
    ScaleWeight,
    TransformType,
)


class TestScaleWeight:
    def test_roundtrip(self):
        sw = ScaleWeight(2, Fraction(3, 7))
        assert ScaleWeight.from_dict(sw.to_dict()) == sw

    def test_to_dict_fields(self):
        d = ScaleWeight(1, Fraction(5, 3)).to_dict()
        assert d == {"input_index": 1, "weight_num": 5, "weight_den": 3}


class TestIdentityTransform:
    def test_compute(self):
        t = AxisTransform.identity(0)
        assert t.compute({0: 42.5}) == pytest.approx(42.5)

    def test_primary_input(self):
        assert AxisTransform.identity(2).primary_input == 2

    def test_input_indices(self):
        assert AxisTransform.identity(3).input_indices == {3}

    def test_type(self):
        assert AxisTransform.identity(0).transform_type == TransformType.IDENTITY

    def test_missing_input_defaults_zero(self):
        t = AxisTransform.identity(0)
        assert t.compute({}) == pytest.approx(0.0)


class TestScalingTransform:
    def test_compute_half(self):
        t = AxisTransform.scaling(0, Fraction(1, 2))
        assert t.compute({0: 100.0}) == pytest.approx(50.0)

    def test_compute_double(self):
        t = AxisTransform.scaling(1, Fraction(2, 1))
        assert t.compute({1: 25.0}) == pytest.approx(50.0)

    def test_type(self):
        assert AxisTransform.scaling(0, Fraction(3, 4)).transform_type == TransformType.SCALING


class TestWeightedSumTransform:
    def test_compute_two_inputs(self):
        t = AxisTransform.weighted_sum([(0, Fraction(1, 1)), (1, Fraction(1, 1))])
        assert t.compute({0: 10.0, 1: 20.0}) == pytest.approx(30.0)

    def test_compute_weighted(self):
        t = AxisTransform.weighted_sum([(0, Fraction(2, 1)), (1, Fraction(3, 1))])
        assert t.compute({0: 5.0, 1: 10.0}) == pytest.approx(40.0)

    def test_input_indices(self):
        t = AxisTransform.weighted_sum([(0, Fraction(1)), (2, Fraction(1))])
        assert t.input_indices == {0, 2}

    def test_primary_is_first(self):
        t = AxisTransform.weighted_sum([(3, Fraction(1)), (1, Fraction(1))])
        assert t.primary_input == 3


class TestAngleProjection:
    def test_cos_zero_degrees(self):
        t = AxisTransform.angle_projection(0, 0.0, use_cos=True)
        # cos(0) = 1
        assert t.compute({0: 100.0}) == pytest.approx(100.0)

    def test_cos_90_degrees(self):
        t = AxisTransform.angle_projection(0, 90.0, use_cos=True)
        # cos(90) ~ 0
        assert t.compute({0: 100.0}) == pytest.approx(0.0, abs=0.02)

    def test_sin_90_degrees(self):
        t = AxisTransform.angle_projection(0, 90.0, use_cos=False)
        # sin(90) = 1
        assert t.compute({0: 100.0}) == pytest.approx(100.0)

    def test_cos_45_degrees(self):
        t = AxisTransform.angle_projection(0, 45.0, use_cos=True)
        expected = 100.0 * math.cos(math.radians(45.0))
        assert t.compute({0: 100.0}) == pytest.approx(expected, abs=0.02)

    def test_sin_30_degrees(self):
        t = AxisTransform.angle_projection(0, 30.0, use_cos=False)
        expected = 100.0 * math.sin(math.radians(30.0))
        assert t.compute({0: 100.0}) == pytest.approx(expected, abs=0.02)

    def test_type_cos(self):
        assert AxisTransform.angle_projection(0, 45.0, True).transform_type == TransformType.ANGLE_COS

    def test_type_sin(self):
        assert AxisTransform.angle_projection(0, 45.0, False).transform_type == TransformType.ANGLE_SIN

    def test_angle_degrees_stored(self):
        t = AxisTransform.angle_projection(0, 37.5, True)
        assert t.angle_degrees == 37.5


class TestDecomposeSyncRatio:
    def test_identity_passthrough(self):
        t = AxisTransform.identity(0)
        result = t.decompose_sync_ratio(Fraction(360, 100))
        assert result == {0: Fraction(360, 100)}

    def test_scaling_multiplies(self):
        t = AxisTransform.scaling(0, Fraction(1, 2))
        result = t.decompose_sync_ratio(Fraction(360, 100))
        assert result == {0: Fraction(180, 100)}

    def test_weighted_sum_per_input(self):
        t = AxisTransform.weighted_sum([(0, Fraction(2, 1)), (1, Fraction(3, 1))])
        result = t.decompose_sync_ratio(Fraction(1, 1))
        assert result == {0: Fraction(2, 1), 1: Fraction(3, 1)}


class TestReversePositionSet:
    def test_identity_direct(self):
        t = AxisTransform.identity(0)
        result = t.reverse_position_set(50.0, {0: 100.0})
        assert result[0] == pytest.approx(50.0)

    def test_scaling_reverse(self):
        t = AxisTransform.scaling(0, Fraction(1, 2))
        result = t.reverse_position_set(25.0, {0: 100.0})
        # 25 = 0.5 * x => x = 50
        assert result[0] == pytest.approx(50.0)

    def test_weighted_sum_adjusts_primary_only(self):
        t = AxisTransform.weighted_sum([(0, Fraction(1, 1)), (1, Fraction(1, 1))])
        result = t.reverse_position_set(30.0, {0: 10.0, 1: 20.0})
        # desired 30 = 1*x + 1*20 => x = 10 (no change needed)
        assert result[0] == pytest.approx(10.0)
        assert result[1] == pytest.approx(20.0)

    def test_weighted_sum_adjusts_primary(self):
        t = AxisTransform.weighted_sum([(0, Fraction(1, 1)), (1, Fraction(1, 1))])
        result = t.reverse_position_set(50.0, {0: 10.0, 1: 20.0})
        # desired 50 = 1*x + 1*20 => x = 30
        assert result[0] == pytest.approx(30.0)
        assert result[1] == pytest.approx(20.0)

    def test_zero_weight_returns_current(self):
        t = AxisTransform(
            contributions=(ScaleWeight(0, Fraction(0)),),
            transform_type=TransformType.SCALING,
        )
        result = t.reverse_position_set(100.0, {0: 42.0})
        assert result[0] == pytest.approx(42.0)


class TestSerialization:
    def test_identity_roundtrip(self):
        t = AxisTransform.identity(2)
        assert AxisTransform.from_dict(t.to_dict()) == t

    def test_scaling_roundtrip(self):
        t = AxisTransform.scaling(1, Fraction(7, 3))
        assert AxisTransform.from_dict(t.to_dict()) == t

    def test_weighted_sum_roundtrip(self):
        t = AxisTransform.weighted_sum([(0, Fraction(2, 5)), (3, Fraction(1, 7))])
        assert AxisTransform.from_dict(t.to_dict()) == t

    def test_angle_cos_roundtrip(self):
        t = AxisTransform.angle_projection(0, 45.0, use_cos=True)
        t2 = AxisTransform.from_dict(t.to_dict())
        assert t2.transform_type == TransformType.ANGLE_COS
        assert t2.angle_degrees == 45.0
        assert t2.contributions == t.contributions

    def test_angle_sin_roundtrip(self):
        t = AxisTransform.angle_projection(1, 30.0, use_cos=False)
        t2 = AxisTransform.from_dict(t.to_dict())
        assert t2.transform_type == TransformType.ANGLE_SIN
        assert t2.angle_degrees == 30.0

    def test_dict_structure(self):
        t = AxisTransform.identity(0)
        d = t.to_dict()
        assert "transform_type" in d
        assert "contributions" in d
        assert d["transform_type"] == "identity"
        assert len(d["contributions"]) == 1
