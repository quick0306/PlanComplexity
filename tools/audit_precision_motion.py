"""Read-only, PHI-free audit before the geometry-v4/tomo-v3 baseline migration.

Reuses the earlier independent geometry audit's unrounded answers (with its
hash and original input hashes), and recomputes TOMO couch motion directly from
allowlisted raw DICOM fields. This is regression/migration evidence, not an
external tool comparison.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import pydicom

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.audit_reference_tomo import _raw_inputs
from ucomx_service import analyze_plan_file
from validation.utils.loaders import load_reference_manifest, verify_reference_source_checksum
from validation_runtime import _normalize_core_result


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_audit(output: Path):
    archive = ROOT / "validation/reference_cases/history/pre-geometry-v4-tomo-v3"
    geometry_path = ROOT / "validation/reference_cases/migrations/geometry_audit.json"
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    answers = {case["case_id"]: {key: value["independent_unrounded"]
                               for key, value in case["metric_checks"].items()}
               for case in geometry["cases"]}
    ck = geometry["cyberknife_pi_check"]
    answers[ck["case_id"]] = {"pi": ck["independent_pi_unrounded"]}
    cases = []
    for case in load_reference_manifest():
        if case.domain == "AURORA":
            continue
        path = verify_reference_source_checksum(case)
        archived_provenance = json.loads((archive / case.case_id / "expected_metrics_provenance.json").read_text())
        if archived_provenance["source_checksum"] != case.checksum:
            raise ValueError("Independent audit input identity changed.")
        result = analyze_plan_file(str(path), full_precision=True)
        normalized = _normalize_core_result(result, domain=case.domain)
        checks = dict(answers.get(case.case_id, {}))
        raw_motion = None
        if case.domain == "TOMO":
            sinogram, _, ppr, period, _ = _raw_inputs(path)
            ds = pydicom.dcmread(path, stop_before_pixels=True, specific_tags=["BeamSequence"])
            beam = next(b for b in ds.BeamSequence if b.get("TreatmentDeliveryType", "") != "SETUP")
            speed = float(beam[0x300D, 0x1080].value)
            pitch = float(beam[0x300D, 0x1060].value)
            duration = len(sinogram) * (period / ppr)
            distance = speed * duration
            # Independently read nominal opening; these two fixtures have 25.1 mm Y jaws.
            y = next(item for item in beam.ControlPointSequence[0].BeamLimitingDevicePositionSequence
                     if str(item.RTBeamLimitingDeviceType) in {"Y", "ASYMY"})
            width = abs(float(y.LeafJawPositions[1]) - float(y.LeafJawPositions[0]))
            assert math.isclose(speed * period / pitch, width, abs_tol=2e-5)
            checks.update(couch_speed_mm_s=speed, pitch=pitch, couch_translation_mm=distance,
                          target_length_mm=distance - width, treatment_time_s=duration)
            raw_motion = {"speed_mm_s": speed, "pitch": pitch, "period_s": period,
                          "nproj": len(sinogram), "projections_per_rotation": ppr,
                          "width_mm": width, "equation": "D = speed * nproj * period / projections_per_rotation; L = D - width"}
        checked = {}
        for key, expected in checks.items():
            observed = normalized.metrics[key]
            error = abs(observed - expected)
            checked[key] = {"independent": expected, "observed": observed, "abs_error": error}
            if not math.isclose(observed, expected, rel_tol=1e-11, abs_tol=1e-10):
                raise AssertionError(f"Independent audit failed: {case.case_id}/{key}")
        previous = json.loads((archive / case.case_id / "expected_metrics.json").read_text())
        current = normalized.metrics
        changed = {key: {"before": previous[key], "after": current[key]}
                   for key in sorted(previous.keys() & current.keys()) if previous[key] != current[key]}
        cases.append({"case_id": case.case_id, "source_sha256": case.checksum,
                      "formula_version": result.metadata.get("metric_formula_version"),
                      "supported": result.supported, "independent_checks": checked,
                      "raw_motion": raw_motion, "changed_metrics": changed,
                      "added_metrics": sorted(current.keys() - previous.keys()),
                      "removed_metrics": sorted(previous.keys() - current.keys()),
                      "full_precision_metrics": current})
    report = {"audit": "geometry-v4_tomo-v3", "numeric_precision": "unrounded float64",
              "prior_geometry_audit": {"path": str(geometry_path.relative_to(ROOT)), "sha256": _sha(geometry_path)},
              "scope": "20 previously independently audited geometry values plus 10 raw-DICOM motion values; other values are regression snapshots, not independent truth.",
              "cases": cases}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run_audit(args.output)
    print(json.dumps({"cases": len(report["cases"]),
                      "independent_checks": sum(len(c["independent_checks"]) for c in report["cases"]),
                      "changed": sum(len(c["changed_metrics"]) for c in report["cases"]),
                      "added": sum(len(c["added_metrics"]) for c in report["cases"])}))
