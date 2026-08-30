from pathlib import Path

import numpy as np
import pytest

from analysis_exports import BASE_HEADER, build_standard_row
from analysis_helpers import calculate_core_metrics, calculate_core_metrics_with_warnings
from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.leaf_gap import LeafGap
from ComplexityMetric.mean_asymmetry_distance import MeanAsymmetryDistance
from ComplexityMetric.small_aperture_score import SmallApertureScore
from ucomx_service import analyze_plan_file, build_export_record
from vcomx_vmat_metrics import calculate_vcomx_supplemental_metrics


TRUEBEAM_BASELINE_PLAN = Path(
    "data/TrueBeam/RP.1.2.246.352.71.5.438107252159.547748.20170216161111.dcm"
)


def test_representative_truebeam_preserves_legacy_metric_values():
    if not TRUEBEAM_BASELINE_PLAN.exists():
        pytest.skip("Representative TrueBeam RTPLAN fixture is unavailable")

    result = analyze_plan_file(str(TRUEBEAM_BASELINE_PLAN))

    assert {
        key: float(result.flattened_metrics[key])
        for key in ("mcsv", "aav", "lsv", "pa", "ja", "lt", "nl")
    } == {
        "mcsv": 0.32,
        "aav": 0.37,
        "lsv": 0.86,
        "pa": 3209.64,
        "ja": 12440.02,
        "lt": 37.47,
        "nl": 35.62,
    }


def _aperture(left, right):
    return PyAperture(
        leaf_positions=np.asarray([left, right], dtype=float),
        leaf_widths=np.asarray([5.0] * len(left), dtype=float),
        jaw=[-20.0, 20.0, 20.0, -20.0],
        gantry_angle=0.0,
    )


def _plan(apertures, *, machine="TrueBeam"):
    control_point_count = len(apertures) // 2 if machine == "Halcyon" else len(apertures)
    beam = {
        "TreatmentDeliveryType": "TREATMENT",
        "TreatmentMachineName": machine,
        "MU": 4.0,
        "PrimaryDosimeterUnit": "MU",
        "DoseRateSet": 600.0,
        "GantryRotationAngle": 0.0,
        "ControlPointSequence": [object()] * control_point_count,
        "_cached_apertures": apertures,
        "_cached_cp_metersets": np.asarray([1.0, 3.0], dtype=float),
        "_cached_cumulative_metersets": np.asarray([0.0, 4.0], dtype=float),
    }
    return {"machine_id": machine, "beams": {1: beam}}


def test_public_mad_lg_and_sas_use_control_point_mu_weighting():
    first = _aperture([0.0, 1.0], [2.0, 5.0])
    second = _aperture([-1.0, 0.0], [9.0, 0.0])
    plan = _plan([first, second])

    assert MeanAsymmetryDistance().calculate_for_plan(plan) == 3.5
    assert LeafGap().calculate_for_plan(plan) == (8.25, 3.07)
    assert SmallApertureScore().calculate_for_plan(plan, x=5) == 0.25


def test_dual_layer_public_metrics_keep_layer_tuple_shape():
    distal_first = _aperture([-1.0, -2.0], [1.0, 2.0])
    proximal_first = _aperture([-2.0, -3.0], [2.0, 3.0])
    distal_second = _aperture([-5.0, 0.0], [5.0, 0.0])
    proximal_second = _aperture([-4.0, 0.0], [4.0, 0.0])
    plan = _plan(
        [distal_first, proximal_first, distal_second, proximal_second],
        machine="Halcyon",
    )

    assert isinstance(MeanAsymmetryDistance().calculate_for_plan(plan), tuple)
    assert isinstance(LeafGap().calculate_for_plan(plan), tuple)
    assert isinstance(SmallApertureScore().calculate_for_plan(plan, x=5), tuple)


def test_supplemental_metrics_distinguish_leaf_travel_and_leaf_counts():
    first = _aperture([0.0, 1.0], [2.0, 5.0])
    second = _aperture([-1.0, 0.0], [9.0, 0.0])

    metrics = calculate_vcomx_supplemental_metrics(_plan([first, second]))

    assert metrics["lt"] == 14.0
    assert metrics["lt_mean_leaf"] == 3.5
    assert metrics["nl"] == metrics["nl_pairs"] == 1.25
    assert metrics["nl_leaves"] == 2.5


def test_core_metrics_keep_mapping_api_and_report_weight_fallbacks():
    first = _aperture([0.0], [2.0])
    second = _aperture([-1.0], [9.0])
    plan = _plan([first, second])
    plan["beams"][1]["_cached_cp_metersets"] = np.asarray([np.nan, np.nan])

    assert isinstance(calculate_core_metrics(plan), dict)
    metrics, warnings = calculate_core_metrics_with_warnings(plan)

    assert isinstance(metrics, dict)
    assert any(warning.startswith("[METRIC_WEIGHT_FALLBACK]") for warning in warnings)


def test_vmat_analysis_and_exports_include_formula_provenance():
    if not TRUEBEAM_BASELINE_PLAN.exists():
        pytest.skip("Representative TrueBeam RTPLAN fixture is unavailable")

    result = analyze_plan_file(str(TRUEBEAM_BASELINE_PLAN))
    export_record = build_export_record(result)

    assert result.metadata["metric_formula_version"] == "hybrid-v2"
    assert export_record["metric_formula_version"] == "hybrid-v2"
    assert "Metric_Formula_Version" in BASE_HEADER
    assert build_standard_row(result.metadata, {})[7] == "hybrid-v2"
