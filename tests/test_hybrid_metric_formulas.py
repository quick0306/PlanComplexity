import math

import numpy as np

from ApertureMetric.aperture_geometry import PyAperture
from ApertureMetric.stacked_aperture import stack_dual_layer_apertures
from ComplexityMetric.aperture_series_metrics import (
    active_pair_count,
    mean_asymmetry_distance,
    mean_leaf_travel,
    small_aperture_score,
    weighted_gap_moments,
)


def _aperture(left, right, *, widths=None, jaw=None):
    widths = np.asarray(widths if widths is not None else [5.0] * len(left), dtype=float)
    jaw = jaw if jaw is not None else [-20.0, 20.0, 20.0, -20.0]
    return PyAperture(
        leaf_positions=np.asarray([left, right], dtype=float),
        leaf_widths=widths,
        jaw=jaw,
        gantry_angle=0.0,
    )


def test_mad_uses_opening_center_and_excludes_closed_and_outside_jaw():
    aperture = _aperture(
        [-8.0, -4.0, -2.0, 3.0, -7.0, -6.0],
        [8.0, 6.0, 8.0, 3.0, 7.0, 6.0],
        jaw=[-10.0, 10.0, 10.0, -5.0],
    )

    result = mean_asymmetry_distance([aperture], [1.0])

    assert result.value == 2.0
    assert not result.used_uniform_weights


def test_gap_moments_balance_each_control_point_before_mu_weighting():
    first = _aperture([-1.0, -2.0], [1.0, 2.0])
    second = _aperture([-5.0, 0.0], [5.0, 0.0])

    result = weighted_gap_moments([first, second], [1.0, 3.0])

    assert result.mean == 8.25
    assert math.isclose(result.standard_deviation, math.sqrt(9.4375))
    assert not result.used_uniform_weights


def test_sas_is_per_control_point_then_mu_weighted():
    first = _aperture([-1.0, -4.0], [1.0, 4.0])
    second = _aperture([-2.0, 0.0], [2.0, 0.0])

    result = small_aperture_score([first, second], [1.0, 3.0], threshold_mm=5.0)

    assert result.value == 0.875
    assert not result.used_uniform_weights


def test_sas_keeps_strict_threshold_boundary():
    aperture = _aperture([-2.5], [2.5])

    result = small_aperture_score([aperture], [1.0], threshold_mm=5.0)

    assert result.value == 0.0


def test_mean_leaf_travel_uses_raw_trajectory_and_moving_physical_leaves():
    first = _aperture([-5.0, -3.0], [5.0, 3.0])
    second = _aperture([-1.0, -3.0], [11.0, 3.0])

    assert mean_leaf_travel([first, second]) == 5.0


def test_mean_leaf_travel_counts_interval_when_pair_is_inside_jaw_at_either_endpoint():
    first = _aperture([-5.0], [5.0], jaw=[-20.0, 20.0, 5.0, 0.0])
    second = _aperture([-3.0], [8.0], jaw=[-20.0, 20.0, 5.0, -5.0])

    assert mean_leaf_travel([first, second]) == 2.5


def test_active_pair_count_includes_zero_as_valid_observation():
    closed = _aperture([0.0], [0.0])
    open_aperture = _aperture([-1.0], [1.0])

    result = active_pair_count([closed, open_aperture], [3.0, 1.0])

    assert result.value == 0.25
    assert not result.used_uniform_weights


def test_invalid_weights_use_uniform_fallback_and_report_it():
    two_open = _aperture([-1.0, -1.0], [1.0, 1.0])
    one_open = _aperture([-1.0, 0.0], [1.0, 0.0])

    result = active_pair_count([two_open, one_open], [float("nan"), -1.0])

    assert result.value == 1.5
    assert result.used_uniform_weights


def test_stacked_aperture_preserves_layer_geometry_and_jaw_state():
    distal = _aperture(
        [-2.0, -3.0],
        [2.0, 3.0],
        widths=[5.0, 5.0],
        jaw=[-20.0, 4.9, 20.0, -4.9],
    )
    proximal = _aperture(
        [-4.0, -5.0],
        [4.0, 5.0],
        widths=[5.0, 5.0],
        jaw=[-20.0, 4.9, 20.0, -4.9],
    )

    stacked = stack_dual_layer_apertures(distal, proximal)

    assert stacked.active_pair_count == 4
    assert math.isclose(stacked.area(), distal.area() + proximal.area())
    assert stacked.artificial_boundary_count == 1
    assert [pair.layer_id for pair in stacked.leaf_pairs] == ["MLCX1", "MLCX1", "MLCX2", "MLCX2"]
    assert [pair.slot_id for pair in stacked.leaf_pairs] == [0, 1, 0, 1]
    assert stacked.leaf_pairs[0].width == distal.leaf_pairs[0].width
    assert stacked.leaf_pairs[2].left == proximal.leaf_pairs[0].left
    assert stacked.leaf_pairs[2].right == proximal.leaf_pairs[0].right
    assert not any(pair.is_outside_jaw() for pair in stacked.leaf_pairs)
