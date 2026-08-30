from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.leaf_gap import LeafGap
from ComplexityMetric.mean_asymmetry_distance import MeanAsymmetryDistance
from ComplexityMetric.small_aperture_score import SmallApertureScore
from halcyon_dual_layer_metrics import _layer_contributions


@dataclass(frozen=True)
class FormulaOracle:
    oracle_id: str
    metric_key: str
    platform: str
    expected: float
    observe: Callable[[], float]
    notes: str


def run_formula_oracles(abs_tol: float = 1.0e-9) -> dict[str, object]:
    rows = [_evaluate_oracle(oracle, abs_tol=abs_tol) for oracle in _built_in_oracles()]
    failures = sum(1 for row in rows if row["status"] == "fail")
    return {
        "summary": {
            "oracles_total": len(rows),
            "failures": failures,
            "formula_oracle_green": failures == 0,
        },
        "oracles": rows,
    }


def _evaluate_oracle(oracle: FormulaOracle, *, abs_tol: float) -> dict[str, object]:
    observed = float(oracle.observe())
    abs_diff = abs(observed - oracle.expected)
    return {
        "oracle_id": oracle.oracle_id,
        "platform": oracle.platform,
        "metric_key": oracle.metric_key,
        "status": "pass" if abs_diff <= abs_tol else "fail",
        "expected": oracle.expected,
        "observed": observed,
        "abs_diff": abs_diff,
        "abs_tol": abs_tol,
        "notes": oracle.notes,
    }


def _built_in_oracles() -> list[FormulaOracle]:
    return [
        FormulaOracle(
            oracle_id="vmat_mean_asymmetry_distance_hand_case",
            platform="VMAT_IMRT",
            metric_key="mad",
            expected=2.0,
            observe=_observe_mean_asymmetry_distance,
            notes="Two-pair hand case using the hybrid-v2 opening-center distance definition.",
        ),
        FormulaOracle(
            oracle_id="vmat_leaf_gap_summary_hand_case",
            platform="VMAT_IMRT",
            metric_key="lg",
            expected=11.0,
            observe=_observe_leaf_gap_mean,
            notes="Two active gaps of 10 and 12 mm; expected mean is 11 mm.",
        ),
        FormulaOracle(
            oracle_id="vmat_small_aperture_fraction_hand_case",
            platform="VMAT_IMRT",
            metric_key="sas_5mm",
            expected=2.0 / 3.0,
            observe=_observe_small_aperture_fraction,
            notes="Two of three active gaps are below the 5 mm threshold.",
        ),
        FormulaOracle(
            oracle_id="dicom_standard_mlc_device_type_selection",
            platform="VMAT_IMRT",
            metric_key="mlc_position_parser",
            expected=4.0,
            observe=_observe_standard_mlc_parser_first_left_bank_sum,
            notes="Jaw item is last in the sequence; MLC must still be selected by RTBeamLimitingDeviceType.",
        ),
        FormulaOracle(
            oracle_id="halcyon_identical_layers_have_zero_uncovered_exposure",
            platform="VMAT_IMRT",
            metric_key="ul",
            expected=0.0,
            observe=_observe_halcyon_identical_layer_uncovered,
            notes="Identical proximal/distal edges share aperture weight but create no uncovered-layer exposure.",
        ),
    ]


def _sample_aperture() -> PyAperture:
    return PyAperture(
        leaf_positions=np.array([[-4.0, -2.0], [6.0, 8.0]]),
        leaf_widths=np.array([5.0, 5.0]),
        jaw=[-10.0, 10.0, 10.0, -10.0],
        gantry_angle=0.0,
    )


def _observe_mean_asymmetry_distance() -> float:
    return float(MeanAsymmetryDistance().calculate_mean_asymmetry_distance(_sample_aperture()))


def _observe_leaf_gap_mean() -> float:
    aperture = PyAperture(
        leaf_positions=np.array([[-5.0, -4.0], [5.0, 8.0]]),
        leaf_widths=np.array([5.0, 5.0]),
        jaw=[-10.0, 10.0, 10.0, -10.0],
        gantry_angle=0.0,
    )
    gaps = LeafGap.get_aperture_leaf_gaps([aperture])
    mean_gap, _std_gap = LeafGap().summarize(gaps)
    return float(mean_gap)


def _observe_small_aperture_fraction() -> float:
    aperture = PyAperture(
        leaf_positions=np.array([[-1.0, -4.0, -2.0], [1.0, 8.0, 2.5]]),
        leaf_widths=np.array([5.0, 5.0, 5.0]),
        jaw=[-10.0, 10.0, 10.0, -10.0],
        gantry_angle=0.0,
    )
    small_count, total_count = SmallApertureScore.count_aperture_leaf_gaps([aperture], x=5)
    return float(small_count / total_count)


def _observe_standard_mlc_parser_first_left_bank_sum() -> float:
    from pydicom.dataset import Dataset
    from pydicom.sequence import Sequence

    mlc_item = Dataset()
    mlc_item.RTBeamLimitingDeviceType = "MLCX"
    mlc_item.LeafJawPositions = [-4.0, -3.0, 4.0, 3.0]
    jaw_item = Dataset()
    jaw_item.RTBeamLimitingDeviceType = "ASYMY"
    jaw_item.LeafJawPositions = [-10.0, 10.0]
    control_point = Dataset()
    control_point.BeamLimitingDevicePositionSequence = Sequence([mlc_item, jaw_item])
    positions = AperturesFromBeamCreator().get_leaf_positions(control_point)
    if positions is None:
        return float("nan")
    return float(positions[1, 0])


def _observe_halcyon_identical_layer_uncovered() -> float:
    positions = np.array([[-5.0, -4.0], [5.0, 6.0]])
    aperture = PyAperture(
        leaf_positions=positions,
        leaf_widths=np.array([5.0, 5.0]),
        jaw=[-10.0, 10.0, 10.0, -10.0],
        gantry_angle=0.0,
    )
    _distal_weight, _proximal_weight, distal_ul, proximal_ul = _layer_contributions(
        aperture,
        positions,
        positions,
    )
    return float(distal_ul + proximal_ul)


__all__ = ["FormulaOracle", "run_formula_oracles"]
