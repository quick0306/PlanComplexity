"""Synthetic-only coverage of versioned baseline identity and freeze safeguards."""

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from tools.freeze_reference_outputs import freeze_case
from tools.run_reference_suite import run_reference_suite
from validation.utils.loaders import load_reference_manifest
from validation_models import ValidationCaseResult


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_case(root, *, required_version=None, baseline_version=None, expected_supported=None):
    source = root / "synthetic.bin"
    source.write_bytes(b"synthetic geometry fixture; no patient data")
    case_dir = root / "cases" / "synthetic"
    case_dir.mkdir(parents=True)
    metrics_path = case_dir / "expected_metrics.json"
    metrics_path.write_text(json.dumps({"mcsv": 0.6}), encoding="utf-8")
    entry = {
        "case_id": "synthetic", "source_path": source.name,
        "domain": "VMAT_IMRT", "device_or_tps": "synthetic",
        "expected_mode": "VMAT_IMRT", "case_class": "canonical",
        "expected_metrics_source": "checked_in_json", "tolerance_overrides": {},
        "checksum": _sha256(source), "provenance": {"source_kind": "synthetic"},
        "notes": "",
    }
    if required_version is not None:
        entry["expected_formula_version"] = required_version
    if expected_supported is not None:
        entry["expected_supported"] = expected_supported
    (root / "manifest.yaml").write_text(yaml.safe_dump({"cases": [entry]}), encoding="utf-8")
    if baseline_version is not None:
        provenance = {
            "schema_version": 1, "formula_version": baseline_version,
            "case_id": "synthetic", "domain": "VMAT_IMRT", "mode": "VMAT_IMRT",
            "source_checksum": _sha256(source), "expected_metrics_checksum": _sha256(metrics_path),
            "generated_at": "2026-09-19T10:00:00Z",
        }
        metrics_path.with_name("expected_metrics_provenance.json").write_text(
            json.dumps(provenance), encoding="utf-8",
        )
    return metrics_path


def _load(root):
    with patch("validation.utils.loaders._REFERENCE_CASES_DIR", root):
        return load_reference_manifest()[0]


def _result(version="geometry-v3", metrics=None, **changes):
    record = ValidationCaseResult(
        source_path="synthetic.bin", domain="VMAT_IMRT", mode="VMAT_IMRT",
        supported=True, reason="", metadata={"metric_formula_version": version},
        metrics={"mcsv": 0.6} if metrics is None else metrics, warnings=(),
    )
    return replace(record, **changes)


def _run(root, case, result):
    with (
        patch("tools.run_reference_suite.load_reference_manifest", return_value=[case]),
        patch("tools.run_reference_suite.analyze_validation_case", return_value=result),
    ):
        return run_reference_suite("research", output_dir=root / "report", source_root=root)


def test_loader_retains_versioned_provenance_without_polluting_scalar_metrics(tmp_path):
    _write_case(tmp_path, required_version="geometry-v3", baseline_version="geometry-v3")
    case = _load(tmp_path)
    assert case.expected_formula_version == "geometry-v3"
    assert case.expected_metrics_provenance.formula_version == "geometry-v3"
    assert case.expected_metrics == {"mcsv": 0.6}


@pytest.mark.parametrize("field,value", [
    ("schema_version", 2), ("case_id", "another-case"), ("domain", "TOMO"),
    ("mode", "TOMO"), ("source_checksum", "f" * 64),
    ("expected_metrics_checksum", "f" * 64), ("generated_at", "yesterday"),
    ("formula_version", ""), ("unrecognized_metadata", "unsafe"),
])
def test_loader_rejects_invalid_or_misbound_provenance(tmp_path, field, value):
    path = _write_case(tmp_path, baseline_version="geometry-v3")
    sidecar = path.with_name("expected_metrics_provenance.json")
    payload = json.loads(sidecar.read_text())
    payload[field] = value
    sidecar.write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        _load(tmp_path)


def test_loader_rejects_scalar_changes_under_an_existing_version_stamp(tmp_path):
    path = _write_case(tmp_path, baseline_version="geometry-v3")
    path.write_text('{"mcsv": 0.7}')
    with pytest.raises(ValueError, match="expected.metrics.*checksum|checksum.*expected.metrics"):
        _load(tmp_path)


@pytest.mark.parametrize("required,baseline,observed", [
    ("geometry-v3", "geometry-v3", "geometry-v2"),
    ("geometry-v3", "geometry-v3", None),
    ("geometry-v3", "geometry-v2", "geometry-v2"),
    ("geometry-v3", None, "geometry-v3"),
    (None, "geometry-v3", "geometry-v2"),
])
def test_formula_mismatch_fails_strict_gate_even_when_scalars_match(tmp_path, required, baseline, observed):
    _write_case(tmp_path, required_version=required, baseline_version=baseline)
    report = _run(tmp_path, _load(tmp_path), _result(observed))
    assert report["summary"]["reference_exact_green"] is False
    assert report["summary"]["provenance_failures"] == 1
    assert report["cases"][0]["formula_version_status"] == "fail"
    assert report["metrics"][0]["status"] == "fail"
    assert report["metrics"][0]["abs_diff"] == 0.0
    assert "formula" in report["metrics"][0]["note"].lower()


def test_formula_mismatch_cannot_pass_when_profile_has_no_exact_metric_rows(tmp_path):
    _write_case(tmp_path, required_version="geometry-v3", baseline_version="geometry-v3")
    case = replace(_load(tmp_path), expected_metrics={})
    report = _run(tmp_path, case, _result("geometry-v2", metrics={}))
    assert report["summary"]["reference_exact_green"] is False


@pytest.mark.parametrize("required,baseline,status", [
    ("geometry-v3", "geometry-v3", "pass"), (None, None, "legacy-unversioned"),
])
def test_matching_versions_and_legacy_fixtures_remain_compatible(tmp_path, required, baseline, status):
    _write_case(tmp_path, required_version=required, baseline_version=baseline)
    report = _run(tmp_path, _load(tmp_path), _result())
    assert report["summary"]["reference_exact_green"] is True
    assert report["cases"][0]["formula_version_status"] == status
    assert report["cases"][0]["observed_formula_version"] == "geometry-v3"


def test_reference_rows_bind_full_precision_values_to_input_identity(tmp_path):
    _write_case(tmp_path, required_version="geometry-v3", baseline_version="geometry-v3")
    case = _load(tmp_path)
    result = _result(metadata={"metric_formula_version": "geometry-v3", "numeric_precision": "float64"})
    report = _run(tmp_path, case, result)
    assert report["metrics"][0]["source_checksum"] == case.checksum
    assert report["metrics"][0]["numeric_precision"] == "float64"
    assert report["cases"][0]["source_checksum"] == case.checksum


def test_freezer_refuses_first_version_stamp_without_explicit_migration(tmp_path):
    path = _write_case(tmp_path)
    before = path.read_bytes()
    with patch("tools.freeze_reference_outputs.analyze_validation_case", return_value=_result()):
        with pytest.raises(ValueError, match="formula.version"):
            freeze_case(_load(tmp_path), source_root=tmp_path)
    assert path.read_bytes() == before
    assert not path.with_name("expected_metrics_provenance.json").exists()


def test_freezer_writes_bound_sidecar_during_explicit_version_migration(tmp_path):
    path = _write_case(tmp_path, required_version="geometry-v3")
    with patch("tools.freeze_reference_outputs.analyze_validation_case", return_value=_result()):
        freeze_case(_load(tmp_path), source_root=tmp_path, allow_formula_version_change=True)
    payload = json.loads(path.with_name("expected_metrics_provenance.json").read_text())
    assert payload["formula_version"] == "geometry-v3"
    assert payload["expected_metrics_checksum"] == _sha256(path)
    assert payload["source_checksum"] == _sha256(tmp_path / "synthetic.bin")
    assert set(payload) == {
        "schema_version", "formula_version", "case_id", "domain", "mode",
        "source_checksum", "expected_metrics_checksum", "generated_at",
    }
    assert _load(tmp_path).expected_metrics_provenance.formula_version == "geometry-v3"


@pytest.mark.parametrize("observed", ["geometry-v2", None])
def test_freezer_never_bypasses_manifest_version_requirement(tmp_path, observed):
    path = _write_case(tmp_path, required_version="geometry-v3", baseline_version="geometry-v3")
    before = path.read_bytes()
    with patch("tools.freeze_reference_outputs.analyze_validation_case", return_value=_result(observed)):
        with pytest.raises(ValueError, match="formula.version"):
            freeze_case(_load(tmp_path), source_root=tmp_path, allow_formula_version_change=True)
    assert path.read_bytes() == before


@pytest.mark.parametrize("field,value", [("domain", "TOMO"), ("mode", "TOMO")])
def test_freezer_rejects_runtime_identity_mismatch(tmp_path, field, value):
    path = _write_case(tmp_path, baseline_version="geometry-v3")
    before = path.read_bytes()
    with patch("tools.freeze_reference_outputs.analyze_validation_case", return_value=_result(**{field: value})):
        with pytest.raises(ValueError, match="mismatch"):
            freeze_case(_load(tmp_path), source_root=tmp_path)
    assert path.read_bytes() == before


def test_freezer_requires_explicit_metric_schema_migration(tmp_path):
    path = _write_case(tmp_path, baseline_version="geometry-v3")
    before = path.read_bytes()
    with patch("tools.freeze_reference_outputs.analyze_validation_case", return_value=_result(metrics={"mcsv": 0.6, "area": 100.0})):
        with pytest.raises(ValueError, match="metric.*schema|metric.*keys"):
            freeze_case(_load(tmp_path), source_root=tmp_path)
        assert path.read_bytes() == before
        freeze_case(_load(tmp_path), source_root=tmp_path, allow_metric_schema_change=True)
    assert _load(tmp_path).expected_metrics == {"mcsv": 0.6, "area": 100.0}


def test_freezer_refuses_nonfinite_values_before_writing(tmp_path):
    path = _write_case(tmp_path, baseline_version="geometry-v3")
    before = path.read_bytes()
    with patch("tools.freeze_reference_outputs.analyze_validation_case", return_value=_result(metrics={"mcsv": float("nan")})):
        with pytest.raises(ValueError, match="finite|JSON"):
            freeze_case(_load(tmp_path), source_root=tmp_path)
    assert path.read_bytes() == before


@pytest.mark.parametrize("changes", [{"supported": False}, {"mode": "TOMO"}, {"domain": "TOMO"}])
def test_unexpected_analysis_state_never_passes_an_empty_reference_gate(tmp_path, changes):
    _write_case(tmp_path, required_version="geometry-v3", baseline_version="geometry-v3")
    case = replace(_load(tmp_path), expected_metrics={})
    report = _run(tmp_path, case, _result(metrics={}, **changes))
    assert report["summary"]["reference_exact_green"] is False
    assert report["summary"]["analysis_failures"] == 1
    assert report["cases"][0]["analysis_status"] == "fail"


def test_explicit_unsupported_reference_can_be_frozen_and_checked(tmp_path):
    path = _write_case(tmp_path, required_version="geometry-v3", expected_supported=False)
    path.write_text("{}")
    case = _load(tmp_path)
    assert case.expected_supported is False
    observed = _result(metrics={}, supported=False, reason="Unsupported synthetic example")
    with patch("tools.freeze_reference_outputs.analyze_validation_case", return_value=observed):
        freeze_case(case, source_root=tmp_path, allow_formula_version_change=True)
    report = _run(tmp_path, _load(tmp_path), observed)
    assert report["summary"]["reference_exact_green"] is True
    assert report["summary"]["analysis_failures"] == 0


def test_freezer_rejects_unexpected_unsupported_analysis(tmp_path):
    path = _write_case(tmp_path, baseline_version="geometry-v3")
    before = path.read_bytes()
    with patch("tools.freeze_reference_outputs.analyze_validation_case", return_value=_result(supported=False)):
        with pytest.raises(ValueError, match="supported.*mismatch|state.*mismatch"):
            freeze_case(_load(tmp_path), source_root=tmp_path)
    assert path.read_bytes() == before


def test_freezer_does_not_replace_scalars_if_provenance_cannot_be_written(tmp_path, monkeypatch):
    path = _write_case(tmp_path, required_version="geometry-v3")
    before = path.read_bytes()
    original_write = Path.write_bytes

    def fail_sidecar_write(target, data):
        if target.name == "expected_metrics_provenance.json":
            raise OSError("Synthetic sidecar write failure")
        return original_write(target, data)

    monkeypatch.setattr(Path, "write_bytes", fail_sidecar_write)
    with patch("tools.freeze_reference_outputs.analyze_validation_case", return_value=_result(metrics={"mcsv": 0.7})):
        with pytest.raises(OSError, match="Synthetic sidecar"):
            freeze_case(_load(tmp_path), source_root=tmp_path, allow_formula_version_change=True)
    assert path.read_bytes() == before


@pytest.mark.parametrize("observed_metrics,expected_status", [({}, "fail"), ({"mcsv": None}, "pass")])
def test_exact_null_baseline_requires_the_observed_metric_key(tmp_path, observed_metrics, expected_status):
    path = _write_case(tmp_path)
    path.write_text('{"mcsv": null}')
    report = _run(tmp_path, _load(tmp_path), _result(metrics=observed_metrics))
    row = report["metrics"][0]
    assert row["status"] == expected_status
    assert report["summary"]["reference_exact_green"] is (expected_status == "pass")
    if expected_status == "fail":
        assert "missing" in row["note"].lower()
