from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class StackedLeafPair:
    """Immutable layer-aware leaf-pair view for non-physical diagnostics."""

    left: float
    right: float
    width: float
    top: float
    bottom: float
    layer_id: str
    slot_id: int
    _outside_jaw: bool
    _field_size: float
    _open_leaf_width: float

    def is_outside_jaw(self) -> bool:
        return self._outside_jaw

    def field_size(self) -> float:
        return self._field_size

    def open_leaf_width(self) -> float:
        return self._open_leaf_width

    def field_area(self) -> float:
        return self._field_size * self._open_leaf_width

    def is_open(self) -> bool:
        return self._field_size > 0.0


@dataclass(frozen=True)
class StackedAperture:
    """Concatenated MLCX1/MLCX2 metric input; not a transmission aperture."""

    leaf_pairs: Tuple[StackedLeafPair, ...]
    gantry_angle: float
    jaw: object
    layer_boundary_index: int

    def area(self) -> float:
        return float(sum(pair.field_area() for pair in self.leaf_pairs))

    @property
    def active_pair_count(self) -> int:
        return sum(pair.field_size() > 0.0 for pair in self.leaf_pairs)

    @property
    def artificial_boundary_count(self) -> int:
        return int(0 < self.layer_boundary_index < len(self.leaf_pairs))


def stack_dual_layer_apertures(distal, proximal) -> StackedAperture:
    """Stack jaw-evaluated slots in MLCX1-then-MLCX2 order."""

    distal_pairs = tuple(_pair_view(pair, "MLCX1", index) for index, pair in enumerate(distal.leaf_pairs))
    proximal_pairs = tuple(
        _pair_view(pair, "MLCX2", index) for index, pair in enumerate(proximal.leaf_pairs)
    )
    return StackedAperture(
        leaf_pairs=distal_pairs + proximal_pairs,
        gantry_angle=float(distal.gantry_angle),
        jaw=distal.jaw,
        layer_boundary_index=len(distal_pairs),
    )


def _pair_view(pair, layer_id: str, slot_id: int) -> StackedLeafPair:
    return StackedLeafPair(
        left=float(pair.left),
        right=float(pair.right),
        width=float(pair.width),
        top=float(pair.top),
        bottom=float(pair.bottom),
        layer_id=layer_id,
        slot_id=slot_id,
        _outside_jaw=bool(pair.is_outside_jaw()),
        _field_size=float(pair.field_size()),
        _open_leaf_width=float(pair.open_leaf_width()),
    )
