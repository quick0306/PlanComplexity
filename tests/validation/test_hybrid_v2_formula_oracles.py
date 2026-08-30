import math

import numpy as np

from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.aperture_series_metrics import (
    active_pair_count,
    mean_asymmetry_distance,
    mean_leaf_travel,
    small_aperture_score,
    weighted_gap_moments,
)
from validation.hybrid_v2_formula_oracles import get_hybrid_v2_formula_oracles


def _aperture(left, right):
    return PyAperture(
        np.asarray([left, right], dtype=float),
        np.asarray([5.0] * len(left), dtype=float),
        [-20.0, 20.0, 20.0, -20.0],
        0.0,
    )


def test_hybrid_v2_hand_calculated_formula_oracles():
    expected = get_hybrid_v2_formula_oracles()
    gaps_first = _aperture([-1.0, -2.0], [1.0, 2.0])
    gaps_second = _aperture([-5.0, 0.0], [5.0, 0.0])
    moments = weighted_gap_moments([gaps_first, gaps_second], [1.0, 3.0])

    assert moments.mean == expected["weighted_gap_mean_mm"]
    assert math.isclose(moments.standard_deviation**2, expected["weighted_gap_variance_mm2"])
    assert small_aperture_score(
        [_aperture([-1.0, -4.0], [1.0, 4.0]), _aperture([-2.0, 0.0], [2.0, 0.0])],
        [1.0, 3.0],
        5.0,
    ).value == expected["weighted_sas_5mm"]
    assert mean_asymmetry_distance(
        [_aperture([-4.0, -2.0], [6.0, 8.0])], [1.0]
    ).value == expected["mad_opening_center_mm"]
    assert mean_leaf_travel(
        [_aperture([-5.0, -3.0], [5.0, 3.0]), _aperture([-1.0, -3.0], [11.0, 3.0])]
    ) == expected["mean_leaf_travel_mm"]
    count = active_pair_count([gaps_first, gaps_second], [1.0, 1.0]).value
    assert count == expected["nl_pairs"]
    assert 2.0 * count == expected["nl_leaves"]
