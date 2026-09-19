"""Audit TOMO reference migration from raw, allowlisted DICOM fields.

This bounded, read-only audit covers the two checked-in TOMO reference cases.
The independent calculations do not call parser or metric helpers. Production
entrypoints are imported only when comparing against the independent values.
Output contains case aliases and numerical evidence, never source filenames or
patient metadata. This is a migration audit, not a clinical validation claim.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sys

import numpy as np
import pydicom

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


CASES = ("tomo_canonical", "tomo_default_inference_edge")
TIMING_METRICS = {
    "projection_time_s", "gantry_period_s", "treatment_time_s", "couch_speed_mm_s",
    "mlot", "sdlot", "mdlot", "molot", "maxlot", "minlot",
    *(f"clns_{n}ms" for n in (10, 20, 30, 50)),
    *(f"clns_pt_{n}ms" for n in (10, 20, 30, 50)),
}
PROJECTION_METRICS = {
    "nproj", "nrot", "ta", "ncc", "fdisc", "cls", "lotv", "elotv_1",
    "elotv_5", "pstv", "epstv_1_1", "epstv_1_0", "epstv_0_1", "mi", "noc",
    "msi", "mdsi", "sdsi",
}
INVARIANT_METRICS = {"mf", "klot", "slot", "msa"}


def _equal(left, right):
    if left is None or right is None:
        return left is None and right is None
    return math.isclose(float(left), float(right), rel_tol=1e-11, abs_tol=1e-12)


def _clean(value):
    if isinstance(value, dict):
        return {key: _clean(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clean(item) for item in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, (np.integer, np.bool_)):
        return value.item()
    return value


def _raw_inputs(path):
    if path.stat().st_size > 20 * 1024 * 1024:
        raise ValueError("Reference exceeds the bounded DICOM inspection limit.")
    ds = pydicom.dcmread(path, stop_before_pixels=True, specific_tags=[
        "BeamSequence", "FractionGroupSequence", "DoseReferenceSequence",
    ])
    beams = [beam for beam in ds.BeamSequence if beam.get("TreatmentDeliveryType", "") != "SETUP"]
    if len(beams) != 1:
        raise ValueError("Audit requires one treatment beam.")
    beam = beams[0]
    if str(beam[0x300D, 0x0010].value).strip() != "TOMO_HA_01":
        raise ValueError("Audit requires documented TOMO_HA_01 semantics.")
    cps = list(beam.ControlPointSequence)
    rows, present = [], []
    for cp in cps:
        element = cp.get((0x300D, 0x10A7))
        value = None if element is None else element.value
        if value is None or value == b"" or value == "":
            rows.append(np.zeros(64))
            present.append(False)
            continue
        if str(cp[0x300D, 0x0010].value).strip() != "TOMO_HA_01":
            raise ValueError("Audit encountered unsupported sinogram ownership.")
        if isinstance(value, bytes):
            value = value.decode("ascii").strip(" \x00").split("\\")
        row = np.array([float(item) for item in value])
        if row.shape != (64,) or not np.isfinite(row).all() or np.any((row < 0) | (row > 1)):
            raise ValueError("Audit encountered an invalid private fractional row.")
        rows.append(row)
        present.append(True)
    if np.any(rows[-1]):
        raise ValueError("Audit requires the vendor terminal closed control point.")
    sinogram = np.array(rows[:-1])
    legacy_sinogram = np.array([row for row, exists in zip(rows, present) if exists])
    if len(legacy_sinogram) > 1 and not np.any(legacy_sinogram[-1]):
        legacy_sinogram = legacy_sinogram[:-1]

    # Unwrap the complete gantry path, then verify uniform angular intervals.
    angles = np.unwrap(np.radians([float(cp.GantryAngle) for cp in cps]))
    steps = np.abs(np.degrees(np.diff(angles)))
    step = float(np.median(steps))
    if step <= 0 or not np.allclose(steps, step, atol=1e-3, rtol=1e-4):
        raise ValueError("Independent audit requires a regular helical gantry path.")
    ppr = round(360 / step)
    period_s = float(beam[0x300D, 0x1040].value)
    if not math.isfinite(period_s) or period_s <= 0:
        raise ValueError("Private gantry period is invalid.")
    groups = list(ds.get("FractionGroupSequence", []))
    beam_doses = [float(item.BeamDose) if "BeamDose" in item else None
                  for group in groups for item in group.get("ReferencedBeamSequence", [])]
    dose_unavailable = not ds.get("DoseReferenceSequence") and all(
        dose is None or dose == 0 for dose in beam_doses
    )
    if not dose_unavailable:
        raise ValueError("Reference dose availability differs from the audited zero/missing case.")
    return sinogram, legacy_sinogram, ppr, period_s, {
        "control_points": len(cps),
        "projection_count_from_intervals": len(cps) - 1,
        "legacy_projection_count_from_nonempty_rows": len(legacy_sinogram),
        "restored_closed_projections": len(sinogram) - len(legacy_sinogram),
        "positive_fraction_count": int(np.count_nonzero(sinogram)),
        "all_closed_projection_count": int(np.count_nonzero(~np.any(sinogram, axis=1))),
        "projections_per_rotation_from_angles": ppr,
        "maximum_angular_step_residual_degrees": float(np.max(np.abs(steps - 360 / ppr))),
        "private_gantry_period_seconds": period_s,
        "fraction_groups": len(groups),
        "target_prescription_count": len(ds.get("DoseReferenceSequence", [])),
        "missing_beam_dose_count": sum(dose is None for dose in beam_doses),
        "zero_beam_dose_count": sum(dose == 0 for dose in beam_doses),
        "fraction_dose_unavailable": dose_unavailable,
    }


def _independent_metrics(sinogram, ppr, projection_s, couch_translation):
    """Independent equations for every metric that can change in this migration."""
    nproj, nleaves = sinogram.shape
    fractions = sinogram[sinogram > 0]
    lots = fractions * (projection_s * 1000)
    n = len(lots)
    mean = math.fsum(map(float, lots)) / n
    # Compute standardized moments on dimensionless fractions: changing time
    # units cannot materially alter their values.
    fm = math.fsum(map(float, fractions)) / n
    m2 = math.fsum(float(x - fm) ** 2 for x in fractions) / n
    m3 = math.fsum(float(x - fm) ** 3 for x in fractions) / n
    m4 = math.fsum(float(x - fm) ** 4 for x in fractions) / n
    g2 = m4 / m2 ** 2 - 3
    moments = {
        "mf": fm / float(max(fractions)),
        "klot": (n - 1) * ((n + 1) * g2 + 6) / ((n - 2) * (n - 3)),
        "slot": math.sqrt(n * (n - 1)) / (n - 2) * m3 / m2 ** 1.5,
    }
    result = {
        **moments, "nproj_rot": float(ppr), "nproj": float(nproj),
        "nrot": nproj / ppr, "projection_time_s": projection_s,
        "gantry_period_s": projection_s * ppr,
        "treatment_time_s": projection_s * nproj,
        "couch_speed_mm_s": couch_translation / (projection_s * nproj),
        "ttdf_s_cgy": None, "mlot": mean,
        "sdlot": math.sqrt(math.fsum(float(x - mean) ** 2 for x in lots) / (n - 1)),
        "mdlot": float(np.quantile(lots, 0.5)),
        "molot": float(Counter(np.round(lots, 6)).most_common(1)[0][0]),
        "maxlot": float(max(lots)), "minlot": float(min(lots)),
    }
    for threshold in (10, 20, 30, 50):
        result[f"clns_{threshold}ms"] = int((lots < threshold).sum()) / n
        result[f"clns_pt_{threshold}ms"] = int((lots > projection_s * 1000 - threshold).sum()) / n

    opened = sinogram > 0
    transitions = np.diff(np.pad(opened.astype(int), ((0, 0), (1, 1))), axis=1)
    components = (transitions == 1).sum(axis=1)
    nonempty = opened.any(axis=1)
    spans = np.zeros(nproj)
    spans[nonempty] = (nleaves - np.argmax(opened[nonempty, ::-1], axis=1)
                       - np.argmax(opened[nonempty], axis=1))
    result.update({"ta": float(spans.mean()), "ncc": float(components.mean()),
                   "fdisc": float((components > 1).mean()), "cls": 1 - float(opened.mean())})
    maxima = sinogram.max(axis=0)
    maxima[maxima == 0] = np.inf
    for delta in (1, 5):
        variation = np.abs(sinogram[delta:] - sinogram[:-delta]).mean(axis=0) / maxima
        result[f"elotv_{delta}"] = float(variation.mean())
    result["lotv"] = 1 - result["elotv_1"]
    result["epstv_1_0"] = float(np.abs(np.diff(sinogram, axis=0)).mean())
    result["epstv_0_1"] = float(np.abs(np.diff(sinogram, axis=1)).mean())
    result["epstv_1_1"] = float((np.abs(sinogram[1:, :-1] - sinogram[:-1, :-1])
                                + np.abs(sinogram[:-1, 1:] - sinogram[:-1, :-1])).mean())
    result["pstv"] = result["epstv_1_1"]
    # Integrate empirical survival functions using sorted differences and
    # explicit trapezoid weights, independent of the production grid loop.
    sigma = math.sqrt(m2 * n / (n - 1))
    thresholds = np.arange(201) * 0.01 * sigma
    direction_integrals = []
    for difference in (np.diff(sinogram, axis=0), np.diff(sinogram, axis=1),
                       sinogram[1:, 1:] - sinogram[:-1, :-1],
                       sinogram[1:, :-1] - sinogram[:-1, 1:]):
        sorted_values = np.sort(np.abs(difference).ravel())
        survival = 1 - np.searchsorted(sorted_values, thresholds, side="right") / len(sorted_values)
        integral = 0.01 * (float(survival[1:-1].sum()) + 0.5 * float(survival[0] + survival[-1]))
        direction_integrals.append(integral)
    result["mi"] = sum(direction_integrals) / 4
    # With fractions <= 1, centered intervals merge exactly when neighboring
    # projections both equal 1. Count intervals algebraically instead of merging.
    merged_pairs = ((sinogram[1:] == 1) & (sinogram[:-1] == 1)).sum()
    result["noc"] = 2 * (int(opened.sum()) - int(merged_pairs)) / (nproj * nleaves)
    column_totals = sinogram.sum(axis=0)
    intensities = column_totals / nproj
    positions = np.arange(nleaves) - (nleaves - 1) / 2
    result.update({"msa": float(column_totals @ positions / column_totals.sum()),
                   "msi": float(sinogram.mean()), "mdsi": float(np.quantile(intensities, 0.5)),
                   "sdsi": float(np.std(intensities, ddof=1))})
    return result


def audit(snapshot_dir):
    from validation.utils.loaders import load_reference_manifest, verify_reference_source_checksum
    from tomo_parser import parse_tomo_rtplan
    from tomo_metrics import calculate_tomo_metrics

    before = json.loads((snapshot_dir / "before.json").read_text(encoding="utf-8"))
    after = json.loads((snapshot_dir / "after.json").read_text(encoding="utf-8"))
    cases = {case.case_id: case for case in load_reference_manifest() if case.case_id in CASES}
    report = {"audit": "tomo-v2-reference-migration", "tolerance": {"relative": 1e-11, "absolute": 1e-12},
              "method": "Raw private fractions and gantry timing; independent numerical equations; no parser helpers in oracle.",
              "cases": {}, "unexplained_changes": [], "failures": []}
    for alias in CASES:
        path = verify_reference_source_checksum(cases[alias])
        sinogram, legacy, ppr, period_s, raw = _raw_inputs(path)
        plan, _ = parse_tomo_rtplan(str(path))
        live = _clean(calculate_tomo_metrics(plan))
        old = before[alias]["old_observed"]
        new = after[alias]["metrics"]
        independent = _independent_metrics(sinogram, ppr, period_s / ppr, new["couch_translation_mm"])
        legacy_independent = _independent_metrics(legacy, ppr, old["projection_time_s"], old["couch_translation_mm"])
        legacy_independent["ttdf_s_cgy"] = 0.0  # explicitly reproduce the superseded missing-dose sentinel
        if plan.sinogram.shape != sinogram.shape or not np.array_equal(plan.sinogram, sinogram):
            report["failures"].append(f"{alias}: parser sinogram differs from raw interval reconstruction")
        if not _equal(plan.projection_time_s, period_s / ppr) or not math.isnan(plan.fraction_dose_cgy):
            report["failures"].append(f"{alias}: parser timing or dose availability mismatch")
        for metric in new:
            if not _equal(live[metric], new[metric]):
                report["failures"].append(f"{alias}/{metric}: after snapshot differs from current implementation")
        for metric, value in independent.items():
            if not _equal(value, new[metric]):
                report["failures"].append(f"{alias}/{metric}: current value differs from independent calculation")
            if not _equal(legacy_independent[metric], old[metric]):
                report["failures"].append(f"{alias}/{metric}: before value differs from independent legacy reconstruction")
        changes, counts = [], Counter()
        for metric, old_value in old.items():
            value = new[metric]
            if old_value == value:
                continue
            if metric == "ttdf_s_cgy":
                category, reason = "unavailable_dose", "Zero/missing dose now propagates unavailable instead of zero."
            elif metric in INVARIANT_METRICS and _equal(old_value, value):
                category, reason = "floating_point_roundoff", "Dimensionless invariant agrees with independent fraction-based calculation."
            elif metric in TIMING_METRICS:
                category, reason = "documented_timing", "Private gantry period / angular projections per rotation replaces the 0.02-second assumption."
                if metric in ("treatment_time_s", "couch_speed_mm_s") and raw["restored_closed_projections"]:
                    reason += " Restored closed projections also change total duration."
            elif metric in PROJECTION_METRICS and raw["restored_closed_projections"]:
                category, reason = "restored_closed_projections", "Empty intervals are restored; per-projection denominators and temporal neighbors change."
            else:
                category, reason = "unexplained", "No approved primitive explains this change."
                report["unexplained_changes"].append(f"{alias}/{metric}")
            counts[category] += 1
            changes.append({"metric": metric, "before_observed": old_value, "after": value,
                            "before_expected": before[alias]["old_expected"][metric],
                            "independent_before": legacy_independent.get(metric),
                            "independent_after": independent.get(metric),
                            "category": category, "reason": reason,
                            "independent_agreement": metric in independent and _equal(value, independent[metric])})
        report["cases"][alias] = {"raw_metric_evidence": raw,
                                   "timing_scale_factor": period_s / ppr / old["projection_time_s"],
                                   "independent_metric_checks": len(independent),
                                   "live_snapshot_metric_checks": len(new),
                                   "changed_metric_count": len(changes), "change_categories": dict(counts),
                                   "changes": changes}
    report["passed"] = not report["failures"] and not report["unexplained_changes"]
    return _clean(report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-dir", required=True, type=Path)
    args = parser.parse_args()
    report = audit(args.snapshot_dir.resolve())
    (args.snapshot_dir / "tomo_audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"],
                      "cases": {alias: {"changed": case["changed_metric_count"], "categories": case["change_categories"]}
                                for alias, case in report["cases"].items()},
                      "failures": report["failures"], "unexplained_changes": report["unexplained_changes"]}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
