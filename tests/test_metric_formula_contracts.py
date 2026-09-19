"""Formula contracts and discriminating analytic examples, not baseline snapshots."""

import importlib.util
import math

import numpy as np
import pytest

from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.aperture_shape_metrics import bank_sequence_variability, maximum_aperture_area
from ComplexityMetric.edge_metric import EdgeMetric
from ComplexityMetric.modulation_complexity_score import ModulationComplexityScore
from ComplexityMetric.plan_modulation import PlanModulation
from metric_definition_catalog import build_metric_definition_catalog


def contracts():
    assert importlib.util.find_spec("metric_formula_contracts") is not None, "Explicit metric contract module is required"
    from metric_formula_contracts import build_metric_formula_contracts
    return {(c.platform, c.metric_key): c for c in build_metric_formula_contracts()}


def test_every_catalog_record_has_a_specific_versioned_contract():
    records = build_metric_definition_catalog()
    indexed = contracts()
    assert set(indexed) == {(r.platform, r.metric_key) for r in records}
    for key, contract in indexed.items():
        for field in ("formula", "sampling", "active_mask", "normalization", "unit", "aggregation", "missing_value", "formula_version", "representation"):
            value = getattr(contract, field)
            assert value.strip(), (key, field)
            assert "implementation_defined" not in value and "implementation-specific" not in value
        assert contract.source_anchors and all(":" in a for a in contract.source_anchors)
        assert contract.evidence_status in {"implementation_contract", "analytic_cases_checked", "research_variant_pending_review"}
        assert "externally verified" not in contract.evidence_status


@pytest.mark.parametrize("platform,key,unit", [
    ("VMAT_IMRT", "em", "mm^-1"), ("CYBERKNIFE_MLC", "em", "mm^-1"),
    ("VMAT_IMRT", "axjd", "mm"), ("VMAT_IMRT", "ayjd", "mm"),
    ("VMAT_IMRT", "dr", "MU/s"), ("VMAT_IMRT", "mdrv", "MU/(s*deg)"),
    ("TOMO", "couch_speed_mm_s", "mm/s"), ("TOMO", "lotv", "dimensionless"),
    ("TOMO", "elotv_1", "dimensionless"), ("TOMO", "klot", "dimensionless"),
    ("TOMO", "slot", "dimensionless"), ("TOMO", "ta", "leaf slots"),
    ("TOMO", "lengthcc", "leaf slots"), ("TOMO", "centroid", "leaf-index displacement"),
    ("TOMO", "l0ns", "proportion"),
])
def test_catalog_reports_the_actual_computed_units(platform, key, unit):
    record = next(r for r in build_metric_definition_catalog() if (r.platform, r.metric_key) == (platform, key))
    assert record.unit == unit


def test_near_projection_time_threshold_is_not_shadowed_by_short_lot_prefix():
    record = next(r for r in build_metric_definition_catalog() if (r.platform, r.metric_key) == ("TOMO", "clns_pt_10ms"))
    assert "LOT >" in record.mathematical_definition
    assert "projection time" in record.mathematical_definition


def shape(left, right, widths=None):
    widths = np.asarray(widths if widths is not None else [1.] * len(left))
    return PyAperture(np.asarray([left, right]), widths, [-100., 100., 100., -100.], 0.)


def test_envelope_is_not_union_and_pm_uses_a_third_normalizer():
    first, second = shape([0.], [2.]), shape([4.], [6.])
    # Two disjoint 2x1 rectangles: geometric union=4, bank envelope=6,
    # maximum single-slot area=2. These definitions must never share a name.
    assert maximum_aperture_area([first, second]) == 6.
    assert PlanModulation()._max_union_area([first, second]) == 2.
    assert PlanModulation().modulation_weighted_sum([1., 1.], [2., 2.], 2.) == 0.
    assert "max" in contracts()["VMAT_IMRT", "aav"].normalization
    assert "geometric union" in contracts()["VMAT_IMRT", "aav"].normalization


def test_bank_range_lsv_differs_from_maximum_adjacent_difference():
    assert bank_sequence_variability([0., 1., 2.]) == .5
    alternative = 1 - np.mean(np.abs(np.diff([0., 1., 2.]))) / max(np.abs(np.diff([0., 1., 2.])))
    assert alternative == 0.
    assert "max(x)-min(x)" in contracts()["VMAT_IMRT", "lsv"].normalization


def test_rectangle_discriminates_side_boundary_em_from_full_perimeter_variant():
    rectangle = shape([-10., -10.], [10., 10.], widths=[2.5, 2.5])
    assert rectangle.area() == 100.
    assert rectangle.perimeter() == 50.
    assert EdgeMetric().calculate_aperture_edge_metric(rectangle) == .4
    assert rectangle.perimeter() / (2 * rectangle.area()) == .25
    assert "horizontal" in contracts()["VMAT_IMRT", "em"].formula


def test_endpoint_product_of_means_is_not_mean_product_or_midpoint_geometry():
    first = shape([0., 0., 0.], [4., 4., 4.])
    second = shape([0., 2., 3.], [4., 4., 4.])
    midpoint = shape([0., 1., 1.5], [4., 4., 4.])
    metric = ModulationComplexityScore()
    denominator = 12.
    aav = [first.area() / denominator, second.area() / denominator]
    lsv = [1., .5]
    expected = np.mean(aav) * np.mean(lsv)
    assert metric.calculate_per_aperture([first, second])[0] == pytest.approx(expected)
    assert expected != pytest.approx(np.mean(np.asarray(aav) * lsv))
    midpoint_product = midpoint.area() / denominator * metric._calculate_cp_lsv(midpoint)
    assert expected != pytest.approx(midpoint_product)
    assert "endpoint" in contracts()["VMAT_IMRT", "mcsv"].sampling


def test_contracts_preserve_missing_data_and_evidence_limits():
    indexed = contracts()
    assert "uniform" in indexed["VMAT_IMRT", "alg"].missing_value
    assert "None" in indexed["AURORA", "projection_pitch_mean"].missing_value
    assert indexed["AURORA", "coupled_modulation_index"].evidence_status == "research_variant_pending_review"
    assert indexed["VMAT_IMRT", "em"].evidence_status == "analytic_cases_checked"


def test_validation_spec_units_and_normalizers_follow_contracts():
    from validation.utils.loaders import load_metric_specs
    indexed = contracts()
    for spec in load_metric_specs():
        contract = indexed[spec.platform, spec.metric_key]
        assert spec.unit == contract.unit
        assert spec.normalization_basis == contract.normalization


def test_gap_cp_balancing_and_raw_mask_differ_from_pooled_clipped_gaps():
    from ComplexityMetric.aperture_series_metrics import weighted_gap_moments, small_aperture_score
    first = shape([0., 0.], [2., 0.])
    second = shape([0., 0.], [8., 12.])
    # Equal CP MU gives means (2+10)/2=6, not pooled-pair mean 22/3.
    moments = weighted_gap_moments([first, second], [1., 1.])
    assert moments.mean == 6.
    assert moments.standard_deviation == pytest.approx(math.sqrt(18.))
    assert small_aperture_score([first, second], [1., 1.], 10.).value == .75
    # A raw opening outside X jaws remains eligible for raw-gap metrics.
    outside_x = PyAperture(np.asarray([[20.], [30.]]), np.asarray([1.]), [-5., 5., 5., -5.], 0.)
    assert outside_x.area() == 0.
    assert weighted_gap_moments([outside_x], [1.]).mean == 10.
    assert small_aperture_score([outside_x], [1.], 10.).value == 0.


def test_stable_native_layer_registry_coverage():
    from metric_registry import VMAT_DUAL_MLC_KEYS
    indexed = contracts()
    for key in ("bjar", "axjd", "ayjd", "ja", "sport"):
        assert key in VMAT_DUAL_MLC_KEYS
        assert ("VMAT_IMRT", key) in indexed
        for suffix in ("mlcx1", "mlcx2"):
            assert ("VMAT_IMRT", f"{key}_{suffix}") in indexed


def test_contract_source_anchors_resolve_to_real_symbols():
    import ast
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    for anchor in {a for c in contracts().values() for a in c.source_anchors}:
        path, symbol = anchor.split(":", 1)
        tree = ast.parse((root / path).read_text(encoding="utf-8-sig"))
        assert symbol in {n.name for n in ast.walk(tree) if isinstance(n, (ast.ClassDef, ast.FunctionDef))}, anchor
