import hashlib
import importlib
import json
from pathlib import Path
import zipfile

import pytest


def _api():
    return importlib.import_module("validation.external_benchmarks")


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(tmp_path):
    """Minimal OOXML fixture; no clinical files or external workbook edits."""
    paths = {key: tmp_path / name for key, name in {
        "input": "synthetic_plan.dcm", "workbook": "synthetic.xlsx",
        "config": "CONFIG.in", "metrics_config": "METRICS.in",
    }.items()}
    paths["input"].write_bytes(b"synthetic input identity")
    paths["config"].write_text("# Precision scale\n2\n")
    paths["metrics_config"].write_text("ComplexityMetrics:\n MUs\n")
    main = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    relation = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    with zipfile.ZipFile(paths["workbook"], "w") as z:
        z.writestr("xl/workbook.xml", f'<workbook xmlns="{main}" xmlns:r="{relation}"><sheets><sheet name="metrics" sheetId="2" r:id="rId2"/><sheet name="info" sheetId="4" r:id="rId4"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId2" Target="worksheets/sheet2.xml"/><Relationship Id="rId4" Target="worksheets/sheet4.xml"/></Relationships>')
        z.writestr("xl/worksheets/sheet2.xml", f'<worksheet xmlns="{main}"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>MUs</t></is></c></row><row r="2"><c r="A2"><v>123.5</v></c></row></sheetData></worksheet>')
        z.writestr("xl/worksheets/sheet4.xml", f'<worksheet xmlns="{main}"><sheetData><row r="1"><c r="B1" t="inlineStr"><is><t>Filename</t></is></c><c r="C1" t="inlineStr"><is><t>PatientName</t></is></c></row><row r="2"><c r="B2" t="inlineStr"><is><t>synthetic_plan.dcm</t></is></c><c r="C2" t="inlineStr"><is><t>synthetic_restricted_marker</t></is></c></row></sheetData></worksheet>')
    return paths, {key: _sha(path) for key, path in paths.items()}


def _capture(paths, hashes):
    return _api().capture_external_workbook(
        input_path=paths["input"], workbook_path=paths["workbook"],
        config_path=paths["config"], metrics_config_path=paths["metrics_config"],
        expected_hashes=hashes, case_id="synthetic", benchmark_id="synthetic-ucomx",
        metric_columns={"MUs": "A"},
    )


def test_capture_records_bound_numeric_cells_without_identifiers_or_local_paths(tmp_path):
    paths, hashes = _fixture(tmp_path)
    result = _capture(paths, hashes)
    assert result["samples"] == [{
        "external_metric": "MUs", "external_value": 123.5,
        "sheet": "metrics", "value_cell": "A2", "header_cell": "A1",
    }]
    assert result["provenance"]["input_sha256"] == hashes["input"]
    assert result["provenance"]["workbook_sha256"] == hashes["workbook"]
    assert result["provenance"]["identity_cell"] == "B2"
    assert result["provenance"]["input_identity_method"] == "filename_resolved_input_sha256"
    assert result["provenance"]["execution_binary_verified"] is False
    serialized = json.dumps(result)
    assert "synthetic_restricted_marker" not in serialized
    assert "synthetic_plan.dcm" not in serialized
    assert str(tmp_path) not in serialized


@pytest.mark.parametrize("artifact", ["input", "workbook", "config", "metrics_config"])
def test_capture_refuses_tampered_source_artifacts(tmp_path, artifact):
    paths, hashes = _fixture(tmp_path)
    paths[artifact].write_bytes(paths[artifact].read_bytes() + b"changed")
    with pytest.raises(ValueError, match="checksum"):
        _capture(paths, hashes)


@pytest.mark.parametrize("artifact", ["input", "workbook", "config", "metrics_config"])
def test_capture_requires_every_expected_source_hash(tmp_path, artifact):
    paths, hashes = _fixture(tmp_path)
    del hashes[artifact]
    with pytest.raises(ValueError, match="provenance|hash"):
        _capture(paths, hashes)


def test_capture_refuses_ambiguous_or_unmatched_input_row(tmp_path):
    paths, hashes = _fixture(tmp_path)
    renamed = paths["input"].with_name("different_synthetic.dcm")
    paths["input"].rename(renamed)
    paths["input"] = renamed
    with pytest.raises(ValueError, match="unique|identity"):
        _capture(paths, hashes)


def test_loaded_capture_requires_provenance_and_detects_content_tampering(tmp_path):
    path = tmp_path / "capture.json"
    path.write_text('{"samples": []}')
    with pytest.raises(ValueError, match="provenance|schema"):
        _api().load_external_capture(path)
    paths, hashes = _fixture(tmp_path)
    capture = _capture(paths, hashes)
    capture["provenance"]["workbook_sha256"] = "f" * 64
    path.write_text(json.dumps(capture))
    with pytest.raises(ValueError, match="integrity|checksum"):
        _api().load_external_capture(path)


def test_historical_pair_is_reported_without_promoting_numerical_agreement(tmp_path):
    paths, hashes = _fixture(tmp_path)
    capture = _capture(paths, hashes)
    rows = [{"case_id": "synthetic", "domain": "VMAT_IMRT", "metric_key": "mus", "observed": 124.0,
             "source_checksum": hashes["input"], "numeric_precision": "float64"}]
    report = _api().run_external_benchmarks(rows, captures=[capture], metric_mapping={
        "MUs": {"internal_metric": "mus", "definition_status": "definition_unverified"},
    })
    assert report["summary"]["actually_paired"] == 1
    assert report["summary"]["definition_eligible"] == 0
    assert report["summary"]["authenticated_external_runs"] == 0
    comparison = report["comparisons"][0]
    assert comparison["internal_value"] == 124.0
    assert comparison["external_value"] == 123.5
    assert comparison["abs_difference"] == 0.5
    assert comparison["status"] == "paired"
    assert comparison["exact_gate_eligible"] is False


def test_absent_metric_mapping_cannot_create_verified_evidence(tmp_path):
    paths, hashes = _fixture(tmp_path)
    capture = _capture(paths, hashes)
    report = _api().run_external_benchmarks([], captures=[capture], metric_mapping={})
    assert report["summary"]["actually_paired"] == 0
    assert report["summary"]["definition_eligible"] == 0
    assert report["comparisons"][0]["status"] == "unmapped"


def test_definition_verified_flag_requires_documented_definition_evidence(tmp_path):
    paths, hashes = _fixture(tmp_path)
    with pytest.raises(ValueError, match="definition evidence"):
        _api().run_external_benchmarks([], captures=[_capture(paths, hashes)], metric_mapping={
            "MUs": {"internal_metric": "mus", "definition_status": "definition_verified"},
        })


def test_missing_internal_value_is_unavailable_not_zero(tmp_path):
    paths, hashes = _fixture(tmp_path)
    report = _api().run_external_benchmarks([], captures=[_capture(paths, hashes)], metric_mapping={
        "MUs": {"internal_metric": "mus", "definition_status": "definition_unverified"},
    })
    assert report["comparisons"][0]["status"] == "internal_unavailable"
    assert report["comparisons"][0]["abs_difference"] is None
    assert report["summary"]["actually_paired"] == 0


def test_identity_join_handles_two_digit_row_numbers(tmp_path):
    paths, hashes = _fixture(tmp_path)
    with zipfile.ZipFile(paths["workbook"]) as z:
        parts = {name: z.read(name) for name in z.namelist()}
    with zipfile.ZipFile(paths["workbook"], "w") as z:
        for name, content in parts.items():
            z.writestr(name, content.replace(b'r="2"', b'r="10"').replace(b'A2', b'A10').replace(b'B2', b'B10').replace(b'C2', b'C10'))
    hashes["workbook"] = _sha(paths["workbook"])
    result = _capture(paths, hashes)
    assert result["provenance"]["identity_cell"] == "B10"
    assert result["samples"][0]["value_cell"] == "A10"


def test_local_tool_snapshot_is_context_and_does_not_authenticate_historical_execution(tmp_path):
    paths, hashes = _fixture(tmp_path)
    result = _api().capture_external_workbook(
        input_path=paths["input"], workbook_path=paths["workbook"],
        config_path=paths["config"], metrics_config_path=paths["metrics_config"],
        expected_hashes=hashes, case_id="synthetic", benchmark_id="synthetic-ucomx",
        metric_columns={"MUs": "A"}, local_tool_files={"vcomx/VCoMX.p": "b" * 64},
        local_gui_label="VCoMX v1.0",
    )
    assert result["provenance"]["local_tool_snapshot_at_capture"] == {"vcomx/VCoMX.p": "b" * 64}
    assert result["provenance"]["execution_binary_verified"] is False


@pytest.mark.parametrize("field,value", [
    ("source_checksum", None), ("source_checksum", "f" * 64),
    ("numeric_precision", None), ("numeric_precision", "float32"),
])
def test_internal_input_and_precision_provenance_are_required_for_pairing(tmp_path, field, value):
    paths, hashes = _fixture(tmp_path)
    row = {"case_id": "synthetic", "domain": "VMAT_IMRT", "metric_key": "mus", "observed": 123.5,
           "source_checksum": hashes["input"], "numeric_precision": "float64"}
    if value is None:
        del row[field]
    else:
        row[field] = value
    report = _api().run_external_benchmarks([row], captures=[_capture(paths, hashes)])
    assert report["summary"]["actually_paired"] == 0
    comparison = report["comparisons"][0]
    assert comparison["status"] == "internal_provenance_unverified"
    assert comparison["internal_value"] is None
    assert comparison["abs_difference"] is None


def test_import_cli_writes_redacted_capture_and_checks_reproducibility(tmp_path, monkeypatch, capsys):
    cli = importlib.import_module("tools.import_external_benchmark")
    paths, hashes = _fixture(tmp_path)
    capture = _capture(paths, hashes)
    monkeypatch.setattr(cli, "import_ucomx_halcyon_historical", lambda *args, **kwargs: capture)
    output = tmp_path / "captured.json"
    args = ["--source-root", str(tmp_path / "readonly_source"), "--output", str(output)]
    assert cli.main(args) == 0
    assert _api().load_external_capture(output)["capture_sha256"] == capture["capture_sha256"]
    assert cli.main(args + ["--check"]) == 0
    modified = json.loads(output.read_text())
    modified["samples"][0]["external_value"] = 999
    output.write_text(json.dumps(modified))
    assert cli.main(args + ["--check"]) == 1
    assert "synthetic_restricted_marker" not in capsys.readouterr().out


@pytest.mark.parametrize("mutation", ["case_alias", "cell_selector", "duplicate_metric", "tool_name"])
def test_capture_schema_limits_identifiers_and_requires_unambiguous_selectors(tmp_path, mutation):
    paths, hashes = _fixture(tmp_path)
    capture = _capture(paths, hashes)
    if mutation == "case_alias":
        capture["case_id"] = "private/path/patient"
    elif mutation == "cell_selector":
        capture["samples"][0]["value_cell"] = "A3"
    elif mutation == "duplicate_metric":
        capture["samples"].append(capture["samples"][0].copy())
    else:
        capture["provenance"]["tool_name"] = "unbounded private text"
    capture["capture_sha256"] = _api()._content_hash(capture)
    path = tmp_path / "capture.json"
    path.write_text(json.dumps(capture))
    with pytest.raises(ValueError):
        _api().load_external_capture(path)
