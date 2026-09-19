"""Hand values that two-decimal presentation would hide from validation."""
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.leaf_gap import LeafGap
from ComplexityMetric.plan_irregularity import PlanIrregularity
from ComplexityMetric.mean_field_area import MeanFieldArea
from ComplexityMetric.small_aperture_score import SmallApertureScore
from cyberknife_metrics import calculate_cyberknife_metrics
from ucomx_models import AnalysisMode, PlanAnalysisResult
from validation_runtime import analyze_validation_case
from ucomx_service import flatten_metrics
from halcyon_dual_layer_metrics import BeamPaperMetrics, _aggregate_beam_results
from DicomParse.dicom_rt import RTPlan
from pydicom.dataset import Dataset
from vcomx_vmat_metrics import calculate_vcomx_supplemental_metrics


def _plan():
    # Three equally weighted positive gaps: mean 16/3, population variance 104/9.
    aperture = PyAperture(np.array([[0., 0., 0.], [2., 4., 10.]]),
                         np.array([5., 5., 5.]), [-20., 20., 20., -20.], 0.)
    beam = {"TreatmentDeliveryType": "TREATMENT", "TreatmentMachineName": "TrueBeam",
            "MU": 1., "PrimaryDosimeterUnit": "MU", "DoseRateSet": 600.,
            "GantryRotationAngle": 0., "ControlPointSequence": [object(), object()],
            "_cached_apertures": [aperture, aperture],
            "_cached_cp_metersets": np.array([.5, .5]),
            "_cached_cumulative_metersets": np.array([0., 1.])}
    return {"machine_id": "TrueBeam", "beams": {1: beam}}


def test_plan_metrics_keep_exact_hand_values_when_full_precision_requested():
    plan = _plan()
    assert LeafGap().calculate_for_plan(plan) == (5.33, 3.4)
    assert LeafGap(full_precision=True).calculate_for_plan(plan) == pytest.approx(
        (16 / 3, np.sqrt(104) / 3), abs=1e-14)
    assert SmallApertureScore(full_precision=True).calculate_for_plan(plan, x=5) == 2 / 3
    raw_pi = PlanIrregularity(full_precision=True).calculate_for_plan(plan)
    assert raw_pi != round(raw_pi, 2)


def test_supplemental_precision_is_opt_in_and_does_not_change_display():
    plan = _plan()
    aperture = PyAperture(np.array([[0., 0., 0.], [2., 4., 10.]]),
                         np.array([4., 4., 4.]), [-20., 20., 20., -20.], 0.)
    plan["beams"][1]["_cached_apertures"] = [aperture, aperture]
    shown = calculate_vcomx_supplemental_metrics(plan)
    raw = calculate_vcomx_supplemental_metrics(plan, full_precision=True)
    assert raw["efs"] != shown["efs"]
    assert raw["efs"] == pytest.approx(64 / 11, abs=1e-14)
    assert round(raw["efs"], 2) == shown["efs"]


def test_cyberknife_segment_aggregation_keeps_full_precision():
    aperture = _plan()["beams"][1]["_cached_apertures"][0]
    beam = SimpleNamespace(interval_key=(0, 0), mu=1.,
                           segments=[SimpleNamespace(mu=1., aperture=aperture)])
    raw = calculate_cyberknife_metrics([beam], full_precision=True)
    shown = calculate_cyberknife_metrics([beam])
    assert raw["lg"] == 16 / 3
    assert raw["sas10"] == 2 / 3
    assert shown["lg"] == 5.33
    assert shown["sas10"] == .67


def test_validation_requests_unrounded_pipeline_and_preserves_small_error():
    # 0.004 is lost if the engine rounds before comparison.
    result = PlanAnalysisResult("synthetic", AnalysisMode.VMAT_IMRT,
                                {}, {"mcsv": .324}, {"mcsv": .324}, True)
    with patch("ucomx_service.analyze_plan_file", return_value=result) as analyze:
        observed = analyze_validation_case("synthetic", "VMAT_IMRT")
    analyze.assert_called_once_with("synthetic", requested_mode=AnalysisMode.VMAT_IMRT,
                                    full_precision=True)
    assert observed.metrics["mcsv"] == .324
    assert abs(observed.metrics["mcsv"] - .32) > .001


def test_numpy_mi_components_are_scalar_and_keep_precision_for_each_layer():
    values = np.array([1 / 3, 2 / 3, 1 / 7])
    single = flatten_metrics({"mi_0_2": values})
    dual = flatten_metrics({"mi_0_2": (values, values / 2)})
    assert single == dict(zip(("mi_0_2_mis", "mi_0_2_mia", "mi_0_2_mit"), values))
    assert len(dual) == 6
    assert dual["mi_0_2_mlcx2_mit"] == 1 / 14
    assert all(np.isscalar(value) for value in dual.values())


def test_halcyon_output_rounding_does_not_enter_full_precision_aggregation():
    beams = [BeamPaperMetrics({"aav_effective": .2}, 1.),
             BeamPaperMetrics({"aav_effective": .4}, 2.)]
    raw = _aggregate_beam_results(beams, full_precision=True)
    shown = _aggregate_beam_results(beams)
    assert raw["aav_effective"] == 1 / 3
    assert shown["aav_effective"] == .333333


def test_dicom_prescription_and_mu_do_not_lose_digits_before_calculation():
    ds = Dataset()
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.481.5"
    ds.RTPlanLabel = "SYNTHETIC"
    dose = Dataset()
    dose.DoseReferenceStructureType = "VOLUME"
    dose.TargetPrescriptionDose = "60.1234"
    ds.DoseReferenceSequence = [dose]
    beam = {"MU": 1.23456789}
    with patch("DicomParse.dicom_rt.dicom.dcmread", return_value=ds), \
         patch.object(RTPlan, "get_beams", return_value={1: beam}), \
         patch.object(RTPlan, "get_study_info", return_value={"description": ""}):
        raw = RTPlan("synthetic", full_precision=True).to_plan_dict()
        shown = RTPlan("synthetic").to_plan_dict()
    assert raw["rxdose"] == pytest.approx(6012.34, abs=1e-12)
    assert raw["Plan_MU"] == 1.23456789
    assert shown["rxdose"] == 6012
    assert shown["Plan_MU"] == 1.23


def test_default_rounding_preserves_each_legacy_scalar_dispatch_at_halfway_value():
    plan = _plan()
    aperture = PyAperture(np.array([[0.], [2.675]]), np.array([1.]),
                         [-20., 20., 20., -20.], 0.)
    plan["beams"][1]["_cached_apertures"] = [aperture, aperture]
    # Core weighted area used NumPy's rounding; LeafGap explicitly used float.
    assert MeanFieldArea().calculate_for_plan(plan) == 2.68
    assert LeafGap().calculate_for_plan(plan)[0] == 2.67
    assert MeanFieldArea(full_precision=True).calculate_for_plan(plan) == 2.675
    assert LeafGap(full_precision=True).calculate_for_plan(plan)[0] == 2.675
