import csv
from types import SimpleNamespace

import pydicom
import pytest
from pydicom.dataset import FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian

import ucomx_service
from tests.test_aurora_parser import build_fake_aurora_rtplan
from ucomx_models import AnalysisMode


def write_aurora_plan(tmp_path, *, include_mlcx2=True):
    dataset = build_fake_aurora_rtplan(include_mlcx2=include_mlcx2)
    dataset.file_meta = FileMetaDataset()
    dataset.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    path = tmp_path / "aurora.dcm"
    pydicom.dcmwrite(path, dataset, enforce_file_format=True)
    return str(path), dataset


@pytest.mark.parametrize("include_mlcx2", [True, False])
def test_metadata_detected_aurora_uses_aurora_metrics_and_validation(
    tmp_path, monkeypatch, include_mlcx2
):
    path, dataset = write_aurora_plan(tmp_path, include_mlcx2=include_mlcx2)
    expected = ucomx_service.analyze_plan_file(path, requested_mode=AnalysisMode.AURORA)
    # Exercise the metadata fallback after the initial file detector misses Aurora.
    monkeypatch.setattr(ucomx_service, "detect_mode_from_file", lambda _: AnalysisMode.VMAT_IMRT)
    plan_dict = {
        "patient_id": "synthetic", "patient_name": "", "plan_name": "Aurora",
        "label": "AURORA", "calculation_model": "DeepPlan", "rxdose": 0,
        "Plan_MU": 100, "beam_type": "DYNAMIC", "beam_number": 1,
        "beams": {1: {"MLCX1": {}}},
    }
    monkeypatch.setattr(
        ucomx_service, "RTPlan",
        lambda **_: SimpleNamespace(ds=dataset, to_plan_dict=lambda: plan_dict),
    )
    monkeypatch.setattr(
        ucomx_service, "calculate_core_metrics_with_warnings",
        lambda *args, **kwargs: ({"em": 0.5}, []),
    )

    actual = ucomx_service.analyze_plan_file(path)

    assert actual.mode == AnalysisMode.AURORA
    assert actual.supported == expected.supported
    assert actual.flattened_metrics == expected.flattened_metrics
    assert actual.warnings == expected.warnings
    assert "em" not in actual.metrics


def test_auto_aurora_exports_its_own_metrics_and_column_reference(tmp_path):
    path, _ = write_aurora_plan(tmp_path)
    result = ucomx_service.analyze_plan_file(path)
    output = tmp_path / "metrics.csv"
    ucomx_service.export_results_to_csv([result], str(output))

    with output.open(encoding="utf-8-sig", newline="") as handle:
        record, = csv.DictReader(handle)
    with output.with_name("metrics_columns.csv").open(encoding="utf-8-sig", newline="") as handle:
        columns = {row["column_name"] for row in csv.DictReader(handle)}

    assert record["mode"] == "AURORA"
    assert record["status"] == "READY"
    assert float(record["projection_pitch_mean"]) == result.metrics["projection_pitch_mean"]
    assert columns == set(result.flattened_metrics)
    assert "projection_pitch_mean" in columns
    assert "em" not in record
