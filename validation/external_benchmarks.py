"""Traceable historical external captures, kept separate from exact validation.

No patient names, input filenames, UIDs, or source directory paths are retained.
Artifact integrity and current input identity do not authenticate a historical
execution or establish metric-definition equivalence.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import posixpath
import re
from typing import Any
import xml.etree.ElementTree as ET
import zipfile


CAPTURE_DIR = Path(__file__).with_name("external_benchmarks")
UCOMX_COLUMNS = {
    "MUs": "A", "LT": "F", "MCSv": "R", "AAV": "S", "LSV": "T",
    "PI": "Y", "PA": "AH", "EFS": "AM", "EM": "AR", "P": "AU",
}
HISTORICAL_HASHES = {
    "input": "9813382359503e91d2b1750b706ae98be811ca3bc064cc223f9aa80ddb02b854",
    "workbook": "fa1987065c2a758574b1804c8b397f750d50bafdeceea6e43fd2ca417ef97b10",
    "config": "5bc25903704c14b767f0c04c369100f0279e4a6297cf632e2ccf3650cfeb402e",
    "metrics_config": "993fe6d8fc244aaeff66f38b2bd804ab61e3e782c7f7cb59bf5c55f961241a55",
}
_DEFAULT_MAPPING = {
    "MUs": {"internal_metric": "mus", "definition_status": "definition_unverified"},
    **{
        name: {"internal_metric": metric, "definition_status": "variant_unverified"}
        for name, metric in {
            "LT": "lt_stacked", "MCSv": "mcsv_stacked", "AAV": "aav_stacked",
            "LSV": "lsv_stacked", "PA": "pa_stacked",
        }.items()
    },
}
_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_REL_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
_SHA = re.compile(r"^[0-9a-f]{64}$")
_TOOL_FILES = {"UCoMX.mlapp", "vcomx/VCoMX.p", "vcomx/VCoMX_GUI.mlapp"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _content_hash(payload: dict[str, Any]) -> str:
    value = {key: value for key, value in payload.items() if key != "capture_sha256"}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _workbook_sheets(path: Path) -> dict[str, dict[str, Any]]:
    """Read stored cell values without running formulas or refreshing links."""
    result = {}
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = {
            item.get("Id"): item.get("Target")
            for item in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        }
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = ["".join(item.itertext()) for item in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        for sheet in workbook.findall(f"{_MAIN}sheets/{_MAIN}sheet"):
            # The info sheet is used only for an in-memory identity join.
            if sheet.get("name") not in {"metrics", "info"}:
                continue
            target = relationships[sheet.get(_REL_ID)]
            target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            cells = {}
            for cell in ET.fromstring(archive.read(target)).iter(f"{_MAIN}c"):
                if cell.find(f"{_MAIN}f") is not None:
                    cells[cell.get("r")] = {"formula": True}
                    continue
                value = cell.find(f"{_MAIN}v")
                if cell.get("t") == "s":
                    decoded = shared[int(value.text)] if value is not None else None
                elif cell.get("t") == "inlineStr":
                    decoded = "".join(cell.find(f"{_MAIN}is").itertext())
                elif value is not None and value.text is not None:
                    decoded = float(value.text)
                else:
                    decoded = None
                cells[cell.get("r")] = decoded
            result[sheet.get("name")] = cells
    return result


def capture_external_workbook(
    *, input_path: Path | str, workbook_path: Path | str,
    config_path: Path | str, metrics_config_path: Path | str,
    expected_hashes: dict[str, str], case_id: str, benchmark_id: str,
    metric_columns: dict[str, str] | None = None,
    local_tool_files: dict[str, str] | None = None,
    local_gui_label: str = "not_inspected",
) -> dict[str, Any]:
    """Capture numeric cells only after every supplied source anchor matches."""
    paths = {
        "input": Path(input_path), "workbook": Path(workbook_path),
        "config": Path(config_path), "metrics_config": Path(metrics_config_path),
    }
    if set(expected_hashes) != set(paths) or any(not _SHA.fullmatch(str(v)) for v in expected_hashes.values()):
        raise ValueError("Complete expected source hash provenance is required.")
    for name, path in paths.items():
        if not path.is_file():
            raise ValueError(f"Required {name} source artifact is missing.")
        if _sha256(path) != expected_hashes[name]:
            raise ValueError(f"External {name} source checksum mismatch.")
    if not all(re.fullmatch(r"[a-z0-9_-]+", name) for name in (case_id, benchmark_id)):
        raise ValueError("Use neutral case and benchmark aliases.")
    sheets = _workbook_sheets(paths["workbook"])
    if not {"info", "metrics"}.issubset(sheets):
        raise ValueError("Required external workbook sheets are missing.")
    info, metrics = sheets["info"], sheets["metrics"]
    filename_columns = [cell[:-1] for cell, value in info.items() if re.fullmatch(r"[A-Z]+1", cell) and value == "Filename"]
    if len(filename_columns) != 1:
        raise ValueError("A unique filename identity column is required.")
    column = filename_columns[0]
    identity_cells = [
        cell for cell, value in info.items()
        if re.fullmatch(column + r"(?:[2-9]|[1-9][0-9]+)", cell)
        and isinstance(value, str)
        and Path(value.replace("\\", "/")).name == paths["input"].name
    ]
    if len(identity_cells) != 1:
        raise ValueError("A unique external input identity row is required.")
    row = re.search(r"\d+$", identity_cells[0]).group()
    samples = []
    for external_metric, column in (UCOMX_COLUMNS if metric_columns is None else metric_columns).items():
        if external_metric not in UCOMX_COLUMNS or not re.fullmatch(r"[A-Z]+", column):
            raise ValueError("Unknown external metric selector.")
        if metrics.get(column + "1") != external_metric:
            raise ValueError(f"External metric header mismatch for {external_metric}.")
        value = metrics.get(column + row)
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError(f"External metric {external_metric} is missing, nonfinite, or formula-derived.")
        samples.append({"external_metric": external_metric, "external_value": float(value),
                        "sheet": "metrics", "value_cell": column + row, "header_cell": column + "1"})
    result = {
        "schema_version": 1, "benchmark_id": benchmark_id, "case_id": case_id,
        "domain": "VMAT_IMRT", "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "provenance": {
            **{name + "_sha256": digest for name, digest in expected_hashes.items()},
            "tool_name": "UCoMX/VCoMX", "evidence_class": "historical_external_capture",
            "identity_sheet": "info", "identity_cell": identity_cells[0],
            "input_identity_method": "filename_resolved_input_sha256",
            "historical_input_hash_recorded": False, "execution_binary_verified": False,
            "historical_tool_version": "not_recorded", "local_gui_label": local_gui_label,
            "local_tool_snapshot_at_capture": dict(local_tool_files or {}),
            "row_alignment": "same_row_index_in_paired_export_sheets",
        },
        "samples": samples,
    }
    result["capture_sha256"] = _content_hash(result)
    _validate_capture(result)
    return result


def _validate_capture(payload: dict[str, Any]) -> None:
    required = {"schema_version", "benchmark_id", "case_id", "domain", "captured_at", "provenance", "samples", "capture_sha256"}
    if not isinstance(payload, dict) or set(payload) != required or payload.get("schema_version") != 1:
        raise ValueError("External capture schema/provenance is incomplete.")
    if (payload["domain"] != "VMAT_IMRT" or
            any(not isinstance(payload[name], str) or not re.fullmatch(r"[a-z0-9_-]+", payload[name]) for name in ("case_id", "benchmark_id"))):
        raise ValueError("External capture requires a supported domain and neutral aliases.")
    if not isinstance(payload["captured_at"], str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+00:00", payload["captured_at"]):
        raise ValueError("External capture requires a UTC capture timestamp.")
    p = payload["provenance"]
    fields = {"input_sha256", "workbook_sha256", "config_sha256", "metrics_config_sha256",
              "tool_name", "evidence_class", "identity_sheet", "identity_cell", "input_identity_method",
              "historical_input_hash_recorded", "execution_binary_verified", "historical_tool_version",
              "local_gui_label", "local_tool_snapshot_at_capture", "row_alignment"}
    if not isinstance(p, dict) or set(p) != fields:
        raise ValueError("External capture provenance is incomplete or contains unapproved fields.")
    if any(not _SHA.fullmatch(str(p[name + "_sha256"])) for name in HISTORICAL_HASHES):
        raise ValueError("Invalid external source checksum provenance.")
    if p["execution_binary_verified"] is not False or p["historical_input_hash_recorded"] is not False:
        raise ValueError("Historical captures cannot assert authenticated execution provenance.")
    if p["evidence_class"] != "historical_external_capture" or p["input_identity_method"] != "filename_resolved_input_sha256":
        raise ValueError("Unsupported external capture provenance class.")
    fixed_fields = {"tool_name": "UCoMX/VCoMX", "identity_sheet": "info", "historical_tool_version": "not_recorded",
                    "row_alignment": "same_row_index_in_paired_export_sheets"}
    if any(p[key] != value for key, value in fixed_fields.items()) or not re.fullmatch(r"[A-Z]+(?:[2-9]|[1-9][0-9]+)", str(p["identity_cell"])):
        raise ValueError("Invalid external identity or tool provenance.")
    snapshot = p["local_tool_snapshot_at_capture"]
    if not isinstance(snapshot, dict) or not set(snapshot).issubset(_TOOL_FILES) or any(not _SHA.fullmatch(str(v)) for v in snapshot.values()):
        raise ValueError("Invalid local tool snapshot provenance.")
    if p["local_gui_label"] != "not_inspected" and not re.fullmatch(r"VCoMX v[0-9]+\.[0-9]+", p["local_gui_label"]):
        raise ValueError("Invalid local GUI version label.")
    if not isinstance(payload["samples"], list) or not payload["samples"]:
        raise ValueError("External capture requires numeric samples.")
    seen_metrics = set()
    identity_row = re.search(r"\d+$", p["identity_cell"]).group()
    for sample in payload["samples"]:
        if set(sample) != {"external_metric", "external_value", "sheet", "value_cell", "header_cell"}:
            raise ValueError("Invalid external sample schema.")
        v = sample["external_value"]
        if sample["external_metric"] not in UCOMX_COLUMNS or isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError("Invalid external numeric sample.")
        if sample["external_metric"] in seen_metrics:
            raise ValueError("Duplicate external metric selector.")
        seen_metrics.add(sample["external_metric"])
        if sample["sheet"] != "metrics" or not re.fullmatch(r"[A-Z]+1", str(sample["header_cell"])) or sample["value_cell"] != sample["header_cell"][:-1] + identity_row:
            raise ValueError("External sample selectors must match the resolved identity row.")
    if payload["capture_sha256"] != _content_hash(payload):
        raise ValueError("External capture integrity checksum mismatch.")
    if payload["benchmark_id"] == "ucomx-halcyon-historical-20251229":
        if any(p[name + "_sha256"] != value for name, value in HISTORICAL_HASHES.items()):
            raise ValueError("Pinned historical external source checksum mismatch.")


def load_external_capture(path: Path | str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    _validate_capture(payload)
    return payload


def run_external_benchmarks(
    reference_rows: list[dict[str, Any]] | dict[str, Any], *,
    captures: list[dict[str, Any]] | None = None,
    metric_mapping: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Compare raw observed values; historical captures never enter an exact gate."""
    if captures is None:
        captures = [load_external_capture(path) for path in sorted(CAPTURE_DIR.glob("*.json"))]
    mapping = _DEFAULT_MAPPING if metric_mapping is None else metric_mapping
    for item in mapping.values():
        if item.get("definition_status") not in {"definition_unverified", "variant_unverified", "definition_verified"}:
            raise ValueError("An explicit metric definition status is required.")
        if item["definition_status"] == "definition_verified" and not item.get("definition_evidence", "").strip():
            raise ValueError("Verified mappings require documented definition evidence.")
    rows = reference_rows.get("metrics", []) if isinstance(reference_rows, dict) else reference_rows
    internal = {}
    for row in rows:
        key = (row.get("case_id"), row.get("domain"), row.get("metric_key"))
        if key in internal:
            raise ValueError("Ambiguous duplicate internal metric row.")
        internal[key] = row
    comparisons, samples, sources = [], [], []
    seen = set()
    for capture in captures:
        _validate_capture(capture)
        if capture["benchmark_id"] in seen:
            raise ValueError("Duplicate external capture would inflate evidence counts.")
        seen.add(capture["benchmark_id"])
        sources.append({"benchmark_id": capture["benchmark_id"], "case_id": capture["case_id"],
                        "capture_sha256": capture["capture_sha256"], **capture["provenance"]})
        for sample in capture["samples"]:
            samples.append({"benchmark_id": capture["benchmark_id"], "case_id": capture["case_id"], **sample})
            rule = mapping.get(sample["external_metric"], {})
            metric = rule.get("internal_metric")
            row = internal.get((capture["case_id"], capture["domain"], metric), {}) if metric else {}
            value = row.get("observed")
            provenance_ok = (row.get("source_checksum") == capture["provenance"]["input_sha256"]
                             and row.get("numeric_precision") == "float64")
            finite = provenance_ok and not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
            status = ("unmapped" if not metric else "internal_provenance_unverified" if row and not provenance_ok
                      else "paired" if finite else "internal_unavailable")
            comparisons.append({
                "benchmark_id": capture["benchmark_id"], "case_id": capture["case_id"],
                "domain": capture["domain"], "external_metric": sample["external_metric"],
                "internal_metric": metric, "internal_value": value if finite else None,
                "external_value": sample["external_value"], "status": status,
                "abs_difference": abs(value - sample["external_value"]) if finite else None,
                "definition_status": rule.get("definition_status", "unmapped"),
                "definition_evidence": rule.get("definition_evidence", ""),
                "exact_gate_eligible": False,
                "internal_source_checksum": row.get("source_checksum"),
                "internal_numeric_precision": row.get("numeric_precision"),
            })
    return {
        "summary": {"traceable_historical_captures": len(sources), "external_samples": len(samples),
                    "actually_paired": sum(c["status"] == "paired" for c in comparisons),
                    "definition_eligible": sum(c["status"] == "paired" and c["definition_status"] == "definition_verified" for c in comparisons),
                    "authenticated_external_runs": 0, "not_clinical_validation": True},
        "sources": sources, "samples": samples, "comparisons": comparisons,
    }


def import_ucomx_halcyon_historical(source_root: Path | str, reference_root: Path | str | None = None) -> dict[str, Any]:
    """Reproduce the pinned capture, locating raw inputs by hash instead of names."""
    from validation.utils.loaders import load_reference_manifest, verify_reference_source_checksum
    import pydicom

    root = Path(source_root)
    reference = next(c for c in load_reference_manifest() if c.case_id == "vmat_halcyon_edge")
    reference_path = verify_reference_source_checksum(reference, source_root=reference_root)
    if reference.checksum != HISTORICAL_HASHES["input"]:
        raise ValueError("The external capture is pinned to a different reference input checksum.")
    def find_by_hash(extension: str, expected: str) -> Path:
        matches = [p for p in root.rglob("*" + extension) if _sha256(p) == expected]
        if not matches:
            raise ValueError(f"Pinned external {extension} artifact was not found by checksum.")
        return sorted(matches)[0]
    source = find_by_hash(".dcm", HISTORICAL_HASHES["input"])
    workbook = find_by_hash(".xlsx", HISTORICAL_HASHES["workbook"])
    uid = lambda path: str(pydicom.dcmread(path, stop_before_pixels=True, specific_tags=["SOPInstanceUID"]).SOPInstanceUID)
    if uid(source) != uid(reference_path):
        raise ValueError("Reference and external local input SOP identity mismatch.")
    tool_files = {name: _sha256(root / name) for name in sorted(_TOOL_FILES) if (root / name).is_file()}
    label = "not_inspected"
    gui = root / "vcomx/VCoMX_GUI.mlapp"
    if gui.is_file():
        with zipfile.ZipFile(gui) as archive:
            code = "".join(ET.fromstring(archive.read("matlab/document.xml")).itertext())
        match = re.search(r"VCoMX v[0-9]+\.[0-9]+", code)
        if match:
            label = match.group()
    return capture_external_workbook(
        input_path=source, workbook_path=workbook,
        config_path=workbook.parent / "CONFIG.in", metrics_config_path=workbook.parent / "METRICS.in",
        expected_hashes=HISTORICAL_HASHES, case_id=reference.case_id,
        benchmark_id="ucomx-halcyon-historical-20251229",
        local_tool_files=tool_files, local_gui_label=label,
    )
