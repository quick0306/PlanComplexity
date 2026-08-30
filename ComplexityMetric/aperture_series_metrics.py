from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


@dataclass(frozen=True)
class MetricValue:
    value: float
    used_uniform_weights: bool = False


@dataclass(frozen=True)
class GapMoments:
    mean: float
    standard_deviation: float
    used_uniform_weights: bool = False


def active_leaf_pairs(aperture) -> list:
    return [
        leaf_pair
        for leaf_pair in aperture.leaf_pairs
        if not is_outside_y_jaw(leaf_pair) and raw_leaf_gap(leaf_pair) > 0.0
    ]


def raw_leaf_gap(leaf_pair) -> float:
    return float(leaf_pair.right) - float(leaf_pair.left)


def is_outside_y_jaw(leaf_pair) -> bool:
    layer_aware = getattr(leaf_pair, "is_outside_y_jaw", None)
    if callable(layer_aware):
        return bool(layer_aware())
    return bool(
        leaf_pair.jaw.top <= leaf_pair.bottom
        or leaf_pair.jaw.bottom >= leaf_pair.top
    )


def weighted_mean(values: Sequence[float], weights: Sequence[float]) -> MetricValue:
    values_array = np.asarray(values, dtype=float)
    if values_array.size == 0:
        return MetricValue(0.0)

    normalized, used_uniform = _normalized_weights(weights, len(values_array))
    value = float(np.sum(values_array * normalized))
    return MetricValue(_finite_or_zero(value), used_uniform)


def mean_asymmetry_distance(apertures: Sequence, cp_weights: Sequence[float]) -> MetricValue:
    values = []
    weights = []
    for aperture, weight in _paired_observations(apertures, cp_weights):
        active_pairs = active_leaf_pairs(aperture)
        if not active_pairs:
            continue
        values.append(float(np.mean([abs((pair.left + pair.right) / 2.0) for pair in active_pairs])))
        weights.append(weight)
    return weighted_mean(values, weights)


def weighted_gap_moments(apertures: Sequence, cp_weights: Sequence[float]) -> GapMoments:
    gap_groups = []
    weights = []
    for aperture, weight in _paired_observations(apertures, cp_weights):
        gaps = [raw_leaf_gap(pair) for pair in active_leaf_pairs(aperture)]
        if not gaps:
            continue
        gap_groups.append(np.asarray(gaps, dtype=float))
        weights.append(weight)

    if not gap_groups:
        return GapMoments(0.0, 0.0)

    normalized, used_uniform = _normalized_weights(weights, len(gap_groups))
    mean = float(
        np.sum(
            [group_weight * float(np.mean(gaps)) for group_weight, gaps in zip(normalized, gap_groups)]
        )
    )
    variance = float(
        np.sum(
            [
                group_weight * float(np.mean((gaps - mean) ** 2))
                for group_weight, gaps in zip(normalized, gap_groups)
            ]
        )
    )
    return GapMoments(
        _finite_or_zero(mean),
        _finite_or_zero(float(np.sqrt(max(variance, 0.0)))),
        used_uniform,
    )


def small_aperture_score(
    apertures: Sequence,
    cp_weights: Sequence[float],
    threshold_mm: float,
) -> MetricValue:
    values = []
    weights = []
    for aperture, weight in _paired_observations(apertures, cp_weights):
        active_pairs = active_leaf_pairs(aperture)
        if not active_pairs:
            continue
        values.append(
            sum(raw_leaf_gap(pair) < threshold_mm for pair in active_pairs) / len(active_pairs)
        )
        weights.append(weight)
    return weighted_mean(values, weights)


def active_pair_count(apertures: Sequence, cp_weights: Sequence[float]) -> MetricValue:
    values = [float(len(active_leaf_pairs(aperture))) for aperture in apertures]
    return weighted_mean(values, cp_weights)


def mean_leaf_travel(apertures: Sequence) -> float:
    if len(apertures) < 2:
        return 0.0

    pair_count = min(len(aperture.leaf_pairs) for aperture in apertures)
    if pair_count <= 0:
        return 0.0

    travel = np.zeros((2, pair_count), dtype=float)
    for first, second in zip(apertures[:-1], apertures[1:]):
        for index, (first_pair, second_pair) in enumerate(
            zip(first.leaf_pairs[:pair_count], second.leaf_pairs[:pair_count])
        ):
            if is_outside_y_jaw(first_pair) and is_outside_y_jaw(second_pair):
                continue
            travel[0, index] += abs(float(first_pair.left) - float(second_pair.left))
            travel[1, index] += abs(float(first_pair.right) - float(second_pair.right))

    moving = travel[travel > 0.0]
    if moving.size == 0:
        return 0.0
    return _finite_or_zero(float(np.mean(moving)))


def _paired_observations(apertures: Sequence, weights: Sequence[float]) -> Iterable[tuple[object, float]]:
    weight_values = list(weights) if weights is not None else []
    if len(weight_values) != len(apertures):
        weight_values = [float("nan")] * len(apertures)
    return zip(apertures, weight_values)


def _normalized_weights(weights: Sequence[float], count: int) -> tuple[np.ndarray, bool]:
    if count <= 0:
        return np.array([], dtype=float), False

    values = np.asarray(list(weights) if weights is not None else [], dtype=float)
    valid = (
        values.size == count
        and np.all(np.isfinite(values))
        and np.all(values >= 0.0)
        and float(np.sum(values)) > 0.0
    )
    if not valid:
        return np.full(count, 1.0 / count, dtype=float), True
    return values / float(np.sum(values)), False


def _finite_or_zero(value: float) -> float:
    return value if np.isfinite(value) else 0.0
