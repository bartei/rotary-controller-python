"""
Pure-data axis transform layer.

Two modes:
- IDENTITY: axis mirrors a single scale input.
- SUM: axis = scale[idx0] + scale[idx1].

No Kivy dependencies — easy to test in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kivy.logger import Logger

log = Logger.getChild(__name__)


class TransformType(str, Enum):
    IDENTITY = "identity"
    SUM = "sum"


@dataclass(frozen=True)
class AxisTransform:
    """
    Defines how an axis value is derived from physical scale inputs.

    IDENTITY: axis_value = scale[contributions[0]]
    SUM:      axis_value = scale[contributions[0]] + scale[contributions[1]]
    """
    contributions: tuple[int, ...]
    transform_type: TransformType = TransformType.IDENTITY

    @property
    def primary_input(self) -> int:
        """The first (or only) contributing scale input index."""
        return self.contributions[0]

    @property
    def input_indices(self) -> set[int]:
        """All scale input indices used by this transform."""
        return set(self.contributions)

    # ── Factory methods ──────────────────────────────────────────────

    @classmethod
    def identity(cls, idx: int) -> AxisTransform:
        return cls(
            contributions=(idx,),
            transform_type=TransformType.IDENTITY,
        )

    @classmethod
    def sum(cls, idx0: int, idx1: int) -> AxisTransform:
        return cls(
            contributions=(idx0, idx1),
            transform_type=TransformType.SUM,
        )

    # ── Forward computation ──────────────────────────────────────────

    def compute(self, scale_positions: dict[int, float]) -> float:
        """Compute axis value from scale positions."""
        total = 0.0
        for idx in self.contributions:
            total += scale_positions.get(idx, 0.0)
        return total

    # ── Serialization ────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "transform_type": self.transform_type.value,
            "contributions": list(self.contributions),
        }

    @classmethod
    def from_dict(cls, d: dict) -> AxisTransform:
        raw_type = d.get("transform_type", "identity")
        contributions = d.get("contributions", [])

        # Backward compatibility: old format used dicts with input_index/weight_num/weight_den
        if contributions and isinstance(contributions[0], dict):
            contributions = [c["input_index"] for c in contributions]

        if not contributions:
            return cls.identity(0)

        # Map old transform types to IDENTITY or SUM
        if raw_type in ("identity", "scaling", "angle_cos", "angle_sin"):
            if raw_type != "identity":
                log.info(f"Migrating transform type '{raw_type}' → identity")
            return cls.identity(contributions[0])
        elif raw_type in ("sum", "weighted_sum"):
            if len(contributions) < 2:
                return cls.identity(contributions[0])
            if raw_type == "weighted_sum":
                log.info("Migrating transform type 'weighted_sum' → sum")
            return cls.sum(contributions[0], contributions[1])
        else:
            log.warning(f"Unknown transform type '{raw_type}', falling back to identity")
            return cls.identity(contributions[0])
