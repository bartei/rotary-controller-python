"""
Pure-data axis transform layer.

All transforms are linear combinations of scale inputs, making them
trivially invertible. No Kivy dependencies — easy to test in isolation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction


class TransformType(str, Enum):
    IDENTITY = "identity"
    SCALING = "scaling"
    WEIGHTED_SUM = "weighted_sum"
    ANGLE_COS = "angle_cos"
    ANGLE_SIN = "angle_sin"


@dataclass(frozen=True)
class ScaleWeight:
    """A single term in the linear combination: weight * scale[input_index]."""
    input_index: int
    weight: Fraction

    def to_dict(self) -> dict:
        return {
            "input_index": self.input_index,
            "weight_num": self.weight.numerator,
            "weight_den": self.weight.denominator,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ScaleWeight:
        return cls(
            input_index=d["input_index"],
            weight=Fraction(d["weight_num"], d["weight_den"]),
        )


@dataclass(frozen=True)
class AxisTransform:
    """
    Defines how an axis value is derived from physical scale inputs.

    axis_value = sum(contribution.weight * scale_position[contribution.input_index])

    Because this is a linear combination, the inverse operations
    (sync ratio decomposition, position set) are straightforward.
    """
    contributions: tuple[ScaleWeight, ...]
    transform_type: TransformType = TransformType.IDENTITY
    angle_degrees: float = 0.0

    @property
    def primary_input(self) -> int:
        """The first (or only) contributing scale input index."""
        return self.contributions[0].input_index

    @property
    def input_indices(self) -> set[int]:
        """All scale input indices used by this transform."""
        return {c.input_index for c in self.contributions}

    # ── Factory methods ──────────────────────────────────────────────

    @classmethod
    def identity(cls, idx: int) -> AxisTransform:
        return cls(
            contributions=(ScaleWeight(idx, Fraction(1)),),
            transform_type=TransformType.IDENTITY,
        )

    @classmethod
    def scaling(cls, idx: int, factor: Fraction) -> AxisTransform:
        return cls(
            contributions=(ScaleWeight(idx, factor),),
            transform_type=TransformType.SCALING,
        )

    @classmethod
    def weighted_sum(cls, weights: list[tuple[int, Fraction]]) -> AxisTransform:
        return cls(
            contributions=tuple(ScaleWeight(idx, w) for idx, w in weights),
            transform_type=TransformType.WEIGHTED_SUM,
        )

    @classmethod
    def angle_projection(cls, idx: int, degrees: float, use_cos: bool) -> AxisTransform:
        radians = math.radians(degrees)
        trig_value = math.cos(radians) if use_cos else math.sin(radians)
        weight = Fraction(trig_value).limit_denominator(10000)
        return cls(
            contributions=(ScaleWeight(idx, weight),),
            transform_type=TransformType.ANGLE_COS if use_cos else TransformType.ANGLE_SIN,
            angle_degrees=degrees,
        )

    # ── Forward computation ──────────────────────────────────────────

    def compute(self, scale_positions: dict[int, float]) -> float:
        """Compute axis value from scale positions: axis = sum(w_i * scale_i)."""
        total = 0.0
        for c in self.contributions:
            total += float(c.weight) * scale_positions.get(c.input_index, 0.0)
        return total

    # ── Reverse operations ───────────────────────────────────────────

    def decompose_sync_ratio(self, desired: Fraction) -> dict[int, Fraction]:
        """
        Reverse: given the user's desired sync ratio for this axis,
        compute the hardware sync ratio needed per contributing scale.

        For each scale: hw_ratio = weight * desired_ratio
        Only the primary scale actually drives sync (hardware constraint),
        so for multi-input transforms we return the primary's ratio.
        """
        result: dict[int, Fraction] = {}
        for c in self.contributions:
            result[c.input_index] = c.weight * desired
        return result

    def reverse_position_set(
        self, desired_value: float, current_positions: dict[int, float]
    ) -> dict[int, float]:
        """
        Reverse: compute new scale positions so that
        compute(new_positions) == desired_value.

        Strategy: adjust the primary input to achieve the desired value,
        keeping all other inputs at their current positions.
        """
        primary = self.contributions[0]
        other_contribution = 0.0
        for c in self.contributions[1:]:
            other_contribution += float(c.weight) * current_positions.get(c.input_index, 0.0)

        if primary.weight == 0:
            return dict(current_positions)

        new_primary = (desired_value - other_contribution) / float(primary.weight)
        result = dict(current_positions)
        result[primary.input_index] = new_primary
        return result

    # ── Serialization ────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "transform_type": self.transform_type.value,
            "angle_degrees": self.angle_degrees,
            "contributions": [c.to_dict() for c in self.contributions],
        }

    @classmethod
    def from_dict(cls, d: dict) -> AxisTransform:
        return cls(
            transform_type=TransformType(d["transform_type"]),
            angle_degrees=d.get("angle_degrees", 0.0),
            contributions=tuple(
                ScaleWeight.from_dict(c) for c in d["contributions"]
            ),
        )
