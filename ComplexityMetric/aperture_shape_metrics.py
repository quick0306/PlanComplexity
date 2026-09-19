"""Shared AAV/LSV primitives; aggregation remains specific to each metric family."""

from typing import Sequence


def maximum_aperture_area(apertures: Sequence) -> float:
    """Sum each slot's raw bank-extrema gap times its maximum jaw-exposed height.

    This is the maximum-aperture normalization, not a geometric union of all
    delivered rectangles. Raw bank extrema retain the established X-jaw
    convention. Taking the maximum height over the full series makes the
    denominator independent of control-point order with moving Y jaws.
    Stacked inputs keep their separate layer slots and cached jaw clipping.
    """
    extents = {}
    for aperture in apertures:
        for index, pair in enumerate(aperture.leaf_pairs):
            if pair.is_outside_jaw():
                continue
            left, right, height = extents.get(index, (pair.left, pair.right, 0.0))
            extents[index] = (min(left, pair.left), max(right, pair.right),
                              max(height, pair.open_leaf_width()))
    return float(sum(max(right - left, 0.0) * height for left, right, height in extents.values()))


def bank_sequence_variability(positions: Sequence[float]) -> float:
    if len(positions) < 2:
        return 1.0
    span = max(positions) - min(positions)
    if span == 0.0:
        return 1.0
    variation = sum(span - abs(current - following)
                    for current, following in zip(positions[:-1], positions[1:]))
    return float(variation / ((len(positions) - 1) * span))


def leaf_sequence_variability(aperture) -> float:
    active = [pair for pair in aperture.leaf_pairs
              if not pair.is_outside_jaw() and pair.field_size() > 0.0]
    if len(active) < 2:
        return 1.0 if active else 0.0
    return (bank_sequence_variability([pair.left for pair in active])
            * bank_sequence_variability([pair.right for pair in active]))
