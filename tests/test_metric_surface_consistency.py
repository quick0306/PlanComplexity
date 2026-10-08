"""Prevent calculated metrics disappearing from public definitions and exports.

All runtime examples are constructed here; no clinical RTPLAN files are read.
"""
import csv
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from ApertureMetric.aperture_geometry import PyAperture
from aurora_svmat_lab.metrics import (
    FIRST_PASS_METRIC_ORDER, calculate_beam_metrics, calculate_plan_metrics,
)
from aurora_svmat_lab.models import AuroraBeam, AuroraControlPoint
from cyberknife_metrics import calculate_cyberknife_metrics
from metric_definition_catalog import build_metric_definition_catalog, export_metric_definitions
from metric_formula_contracts import build_metric_formula_contracts, write_contract_document
from metric_registry import metric_descriptions_with_aliases, metric_gui_labels_with_aliases
from tomo_metrics import TomoPlan, calculate_tomo_metrics


ROOT = Path(__file__).resolve().parents[1]


def _catalog_keys(platform):
    return {r.metric_key for r in build_metric_definition_catalog() if r.platform == platform}


def test_vmat_single_and_dual_layer_runtime_and_flattening_cover_catalog():
    from analysis_helpers import calculate_core_metrics
    from ComplexityMetric.modulation_complexity_score import ModulationComplexityScore
    from pydicom.dataset import Dataset
    from ucomx_service import flatten_metrics

    def dataset(**values):
        result = Dataset()
        for key, value in values.items():
            setattr(result, key, value)
        return result

    observed = set()
    for dual in (False, True):
        layers = [("MLCX1", 28, -140), ("MLCX2", 29, -145)] if dual else [("MLCX", 28, -140)]
        devices = [dataset(
            RTBeamLimitingDeviceType=kind, NumberOfLeafJawPairs=n,
            LeafPositionBoundaries=np.arange(start, -start + 1, 10).tolist(),
        ) for kind, n, start in layers]
        cps = [dataset(
            CumulativeMetersetWeight=w, GantryAngle=30. * i,
            BeamLimitingDevicePositionSequence=[dataset(
                RTBeamLimitingDeviceType=kind, LeafJawPositions=[-5. + i] * n + [5. + i] * n,
            ) for kind, n, _ in layers],
        ) for i, w in enumerate((0., .5, 1.))]
        if dual:
            # Distal rectangle stays fixed; proximal rectangles move and widen.
            # Native layers and their physical intersection must have distinct MCS.
            for cp, (left, right) in zip(cps, ((0., 3.), (0., 8.), (-8., 3.))):
                cp.BeamLimitingDevicePositionSequence[0].LeafJawPositions = [-5.] * 28 + [5.] * 28
                cp.BeamLimitingDevicePositionSequence[1].LeafJawPositions = [left] * 29 + [right] * 29
        beam = dict(
            TreatmentDeliveryType="TREATMENT", TreatmentMachineName="Halcyon" if dual else "TrueBeam",
            MU=100., PrimaryDosimeterUnit="MU", DoseRateSet=600., GantryRotationAngle=60.,
            BeamLimitingDeviceSequence=devices, ControlPointSequence=cps,
        )
        plan = {"machine_id": beam["TreatmentMachineName"], "beams": {1: beam}}
        metrics = calculate_core_metrics(plan, full_precision=True)
        if dual:
            native = ModulationComplexityScore(full_precision=True).calculate_for_plan(plan)
            assert metrics["mcsv_mlcx1"] == pytest.approx(native[0])
            assert metrics["mcsv_mlcx2"] == pytest.approx(native[1])
            assert metrics["mcsv"] == pytest.approx(metrics["mcs5"])
            assert metrics["mcsv"] == pytest.approx(metrics["mcsv_effective"])
            assert any(abs(value - metrics["mcsv"]) > 1e-6 for value in native)
        observed.update(metrics)
        observed.update(flatten_metrics(metrics))
    # The catalog includes containers and scalar flattened keys. Each representation
    # is applicable to a subset, while the union must cover the whole inventory.
    assert observed == _catalog_keys("VMAT_IMRT")


def test_every_catalog_metric_has_gui_label_description_and_matching_formula_contract():
    labels = metric_gui_labels_with_aliases()
    descriptions = metric_descriptions_with_aliases()
    contracts = {(c.platform, c.metric_key): c for c in build_metric_formula_contracts()}
    records = build_metric_definition_catalog()
    assert len(contracts) == len(records)
    assert set(contracts) == {(r.platform, r.metric_key) for r in records}
    for record in records:
        identity = (record.platform, record.metric_key)
        assert labels.get(record.metric_key, "").strip(), identity
        assert descriptions.get(record.metric_key, "").strip(), identity
        contract = contracts[identity]
        assert contract.formula == record.mathematical_definition, identity
        assert contract.unit == record.unit, identity
        assert contract.formula_version.strip(), identity


def test_tomo_runtime_metric_keys_equal_catalog():
    plan = TomoPlan(
        source_path="synthetic", sinogram=np.array([[.2, .4, 0], [0, .6, .7], [.8, .9, .4]]),
        projection_time_s=.1, projections_per_rotation=51, field_width_mm=25.,
        pitch=.3, couch_translation_mm=100., fraction_dose_cgy=200.,
    )
    assert set(calculate_tomo_metrics(plan)) == _catalog_keys("TOMO")


@pytest.mark.parametrize("empty", [False, True])
def test_cyberknife_runtime_metric_keys_equal_catalog(empty):
    aperture = PyAperture(
        np.array([[-5., -5.], [5., 5.]]), np.array([5., 5.]),
        [-20., 20., 20., -20.], 0.,
    )
    beam = SimpleNamespace(
        interval_key=(0, 0), mu=10.,
        segments=[SimpleNamespace(aperture=aperture, mu=10.)],
    )
    assert set(calculate_cyberknife_metrics([] if empty else [beam])) == _catalog_keys("CYBERKNIFE_MLC")


def test_aurora_beam_plan_and_export_order_equal_catalog_even_if_inputs_unavailable():
    beam = AuroraBeam(control_points=[
        AuroraControlPoint(
            control_point_index=i, gantry_angle_deg=30. * i,
            axial_position_mm=10. * i, cumulative_meterset_weight=i / 2.,
            mlc_x1_positions_mm=(-5., -5.), mlc_x2_positions_mm=(5., 5.),
        ) for i in range(3)
    ])
    expected = _catalog_keys("AURORA")
    assert len(FIRST_PASS_METRIC_ORDER) == len(set(FIRST_PASS_METRIC_ORDER))
    assert set(FIRST_PASS_METRIC_ORDER) == expected
    assert set(calculate_beam_metrics(beam)) == expected
    assert set(calculate_plan_metrics([beam])) == expected
    assert set(calculate_plan_metrics([])) == expected


def test_generated_csv_preserves_all_catalog_keys_formulas_and_metadata(tmp_path):
    # output/*.csv is ignored: verify a fresh export, independent of local artifacts.
    records = export_metric_definitions(
        csv_path=tmp_path / "definitions.csv", markdown_path=tmp_path / "metric_definitions_all.md",
    )
    with (tmp_path / "definitions.csv").open(encoding="utf-8-sig", newline="") as handle:
        actual = list(csv.DictReader(handle))
    assert actual == [asdict(record) for record in records]


@pytest.mark.parametrize("filename", [
    "metric_definitions_all.md", "metric_definitions_vmat_imrt.md",
    "metric_definitions_tomo.md", "metric_definitions_cyberknife_mlc.md",
    "metric_definitions_aurora.md",
])
def test_checked_in_definition_documents_match_catalog_including_formulas(tmp_path, filename):
    export_metric_definitions(
        csv_path=tmp_path / "definitions.csv", markdown_path=tmp_path / "metric_definitions_all.md",
    )
    assert (ROOT / "docs" / filename).read_text(encoding="utf-8") == (
        tmp_path / filename
    ).read_text(encoding="utf-8"), f"Regenerate {filename} with tools/export_metric_definitions.py"


def test_checked_in_formula_contract_document_matches_current_contracts(tmp_path):
    target = tmp_path / "metric_formula_contracts.md"
    write_contract_document(target)
    assert (ROOT / "docs" / target.name).read_text(encoding="utf-8") == target.read_text(
        encoding="utf-8"
    ), "Regenerate docs/metric_formula_contracts.md with python -m metric_formula_contracts"
