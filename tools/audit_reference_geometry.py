"""Independent, metric-only audit of the two checked-in VMAT reference cases.

Reads clinical RTPLANs locally without printing or exporting metadata or paths.
Native rectangles come directly from DICOM device boundaries and jaw positions.
Effective geometry is their physical intersection. A sweep over distinct X edges
computes union area and perimeter, without production aperture geometry helpers.
The old perimeter replay is explanatory only and is not an independent oracle.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
import pydicom

ROOT = Path(__file__).resolve().parents[1]
PRE_CHANGE_GEOMETRY_REVISION = "be93062484277b362948d959a2044c72c8543dcc"
COORDINATE_TOLERANCE_MM = 1e-9
sys.path.insert(0, str(ROOT))

from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from cyberknife_parser import parse_cyberknife_beams, resolve_referenced_xml_paths
from DicomParse.dicom_rt import RTPlan
from halcyon_dual_layer_metrics import _build_layer_control_points
from ucomx_service import analyze_plan_file
from validation.utils.loaders import load_reference_manifest, resolve_reference_source_path


def merge_intervals(intervals):
    result = []
    for low, high in sorted(intervals):
        if high <= low:
            continue
        # Repeated floating-point width additions in the XML parser can put
        # the two encodings of a shared edge a few ULPs apart. Coalesce only
        # sub-nanometre differences; do not count those as physical cracks.
        if result and low <= result[-1][1] + COORDINATE_TOLERANCE_MM:
            result[-1] = (result[-1][0], max(result[-1][1], high))
        else:
            result.append((low, high))
    return result


def interval_length(intervals):
    return sum(high - low for low, high in intervals)


def interval_intersection_length(first, second):
    return sum(max(0.0, min(hi, hj) - max(lo, lj))
               for lo, hi in first for lj, hj in second)


def union_geometry(rectangles):
    """X sweep: area, horizontal edge lengths, and vertical interface changes."""
    if not rectangles:
        return 0.0, 0.0
    xs = sorted({x for left, right, _, _ in rectangles for x in (left, right)})
    previous = []
    area = perimeter = 0.0
    for left, right in zip(xs[:-1], xs[1:]):
        midpoint = (left + right) / 2
        intervals = merge_intervals((low, high) for x1, x2, low, high in rectangles
                                    if x1 < midpoint < x2)
        height = interval_length(intervals)
        width = right - left
        area += width * height
        perimeter += 2 * len(intervals) * width
        perimeter += (interval_length(previous) + height
                      - 2 * interval_intersection_length(previous, intervals))
        previous = intervals
    perimeter += interval_length(previous)
    return float(area), float(perimeter)


def rectangles_from_device(boundaries, positions, jaw):
    n = len(boundaries) - 1
    if len(positions) != 2 * n:
        raise AssertionError("Unexpected leaf count in reference input.")
    x1, x2, y1, y2 = jaw
    result = []
    for index in range(n):
        left = max(x1, positions[index])
        right = min(x2, positions[index + n])
        low = max(y1, boundaries[index])
        high = min(y2, boundaries[index + 1])
        if right > left and high > low:
            result.append((left, right, low, high))
    return result


def intersect_rectangles(first, second):
    result = []
    for a, b, c, d in first:
        for e, f, g, h in second:
            left, right, low, high = max(a, e), min(b, f), max(c, g), min(d, h)
            if right > left and high > low:
                result.append((left, right, low, high))
    return result


def cp_weights(raw_beam, mu):
    weights = np.asarray([float(cp.CumulativeMetersetWeight)
                          for cp in raw_beam.ControlPointSequence])
    final = float(raw_beam.FinalCumulativeMetersetWeight)
    assert weights[0] == 0 and final > 0 and weights[-1] == final
    intervals = np.diff(weights) * mu / final
    assert np.all(intervals >= 0)
    centered = np.zeros(len(weights))
    centered[:-1] += intervals / 2
    centered[1:] += intervals / 2
    assert math.isclose(float(sum(centered)), mu)
    return centered


def raw_snapshots(raw_beam, *, dual):
    boundaries = {
        str(device.RTBeamLimitingDeviceType): np.asarray(device.LeafPositionBoundaries, dtype=float)
        for device in raw_beam.BeamLimitingDeviceSequence
        if str(device.RTBeamLimitingDeviceType).startswith("MLC")
    }
    state = {}
    output = []
    half = 140.0 if dual else 200.0
    for cp in raw_beam.ControlPointSequence:
        for item in getattr(cp, "BeamLimitingDevicePositionSequence", []):
            state[str(item.RTBeamLimitingDeviceType)] = np.asarray(item.LeafJawPositions, dtype=float)
        x1, x2 = state.get("ASYMX", state.get("X", [-half, half]))
        y1, y2 = state.get("ASYMY", state.get("Y", [-half, half]))
        jaw = (x1, x2, y1, y2)
        native = {kind: rectangles_from_device(bounds, state[kind], jaw)
                  for kind, bounds in boundaries.items()}
        row = {"native": native, "jaw": jaw}
        if dual:
            row["effective"] = intersect_rectangles(native["MLCX1"], native["MLCX2"])
        row["active_pairs"] = {}
        for kind, bounds in boundaries.items():
            positions = state[kind]
            n = len(bounds) - 1
            gaps, centers = [], []
            for index in range(n):
                # Hybrid v2 eligibility uses Y overlap and positive raw gap;
                # widths and X-jaw clipping do not weight individual pairs.
                gap = float(positions[index + n] - positions[index])
                if gap > 0 and min(y2, bounds[index + 1]) > max(y1, bounds[index]):
                    gaps.append(gap)
                    centers.append(abs(float(positions[index] + positions[index + n]) / 2))
            row["active_pairs"][kind] = {"gaps": np.asarray(gaps), "centers": np.asarray(centers)}
        output.append(row)
    return output


def old_aperture_class():
    content = subprocess.run(["git", "show", PRE_CHANGE_GEOMETRY_REVISION + ":ApertureMetric/aperture_geometry.py"],
                             cwd=ROOT, check=True, capture_output=True, text=True).stdout
    namespace = {}
    exec(compile(content.lstrip("\ufeff"), "<pre-change-aperture-geometry>", "exec"), namespace)
    return namespace["PyAperture"]


def replay_old_geometry(aperture, old_class):
    # Effective positions remain on the legacy centered 5 mm grid. Replaying
    # the prior boundary formula isolates its counting error from native shifts.
    positions = np.asarray([[p.left for p in aperture.leaf_pairs],
                            [p.right for p in aperture.leaf_pairs]])
    widths = np.asarray([p.width for p in aperture.leaf_pairs])
    jaw = [aperture.jaw.left, aperture.jaw.top, aperture.jaw.right, aperture.jaw.bottom]
    old = old_class(positions, widths, jaw, aperture.gantry_angle)
    horizontal = old.side_perimeter_horizontal()
    vertical = old.side_perimeter_vertical()
    positive_height = sum(p.open_leaf_width() for p in old.leaf_pairs if p.field_size() > 0)
    return float(horizontal), float(vertical), float(positive_height)


def audit_case(case, old_class):
    path = resolve_reference_source_path(case)
    raw = pydicom.dcmread(path)
    parsed = RTPlan(str(path)).to_plan_dict()
    result = analyze_plan_file(str(path))
    assert result.supported
    metrics = result.flattened_metrics
    references = {int(item.ReferencedBeamNumber): float(item.BeamMeterset)
                  for item in raw.FractionGroupSequence[0].ReferencedBeamSequence
                  if hasattr(item, "BeamMeterset")}
    dual = case.case_id == "vmat_halcyon_edge"
    checks = {"native": {"count": 0, "area_max_abs_error": 0., "perimeter_max_abs_error": 0.}}
    if dual:
        checks["effective"] = {"count": 0, "area_max_abs_error": 0., "perimeter_max_abs_error": 0.}
    beam_results = []
    for raw_beam in raw.BeamSequence:
        number = int(raw_beam.BeamNumber)
        if str(raw_beam.TreatmentDeliveryType) != "TREATMENT" or references.get(number, 0) <= 0:
            continue
        mu = references[number]
        w = cp_weights(raw_beam, mu)
        rows = raw_snapshots(raw_beam, dual=dual)
        production_beam = parsed["beams"][number]
        aps = AperturesFromBeamCreator().create(production_beam)
        snapshots = _build_layer_control_points(production_beam) if dual else None
        pi_values, old_pi, components = [], [], []
        lower_count = closed_count = 0
        for index, row in enumerate(rows):
            kinds = ["MLCX1", "MLCX2"] if dual else ["MLCX"]
            comparisons = [("native", row["native"][kind], aps[2 * index + layer] if dual else aps[index])
                           for layer, kind in enumerate(kinds)]
            if dual:
                comparisons.append(("effective", row["effective"], snapshots[index].effective_aperture))
            for kind, rectangles, aperture in comparisons:
                area, perimeter = union_geometry(rectangles)
                stats = checks[kind]
                stats["count"] += 1
                stats["area_max_abs_error"] = max(stats["area_max_abs_error"], abs(area - aperture.area()))
                stats["perimeter_max_abs_error"] = max(stats["perimeter_max_abs_error"], abs(perimeter - aperture.perimeter()))
                if kind == "effective":
                    h_old, v_old, height_open = replay_old_geometry(aperture, old_class)
                    h_new = perimeter - 2 * height_open
                    old_p = h_old + v_old
                    pi_values.append(perimeter**2 / (4 * math.pi * area) if area > 0 else 0.)
                    old_pi.append(old_p**2 / (4 * math.pi * area) if area > 0 else 0.)
                    components.append((h_old, v_old, h_new, 2 * height_open,
                                       v_old - height_open))
                    lower_count += int(perimeter < old_p - 1e-8)
                    closed_count += sum(p.field_size() == 0 and not p.is_outside_jaw()
                                        for p in aperture.leaf_pairs)
        info = {"mu": mu, "control_points": len(rows)}
        if dual:
            delta_pi = np.asarray(pi_values) - np.asarray(old_pi)
            info.update(pi5=float(np.average(pi_values, weights=w)),
                        old_pi5=float(np.average(old_pi, weights=w)),
                        negative_pi_change=float(sum(w * np.minimum(delta_pi, 0.)) / sum(w)),
                        positive_pi_change=float(sum(w * np.maximum(delta_pi, 0.)) / sum(w)),
                        components=np.average(components, axis=0, weights=w).tolist(),
                        perimeter_decreased_cp_count=lower_count,
                        closed_slots_inside_jaws=closed_count)
        info["layers"] = {}
        for kind in (["MLCX1", "MLCX2"] if dual else ["MLCX"]):
            observations = [row["active_pairs"][kind] for row in rows]
            valid = [i for i, row in enumerate(observations) if len(row["gaps"])]
            selected_w = w[valid] / sum(w[valid])
            first = float(sum(weight * np.mean(observations[i]["gaps"]) for weight, i in zip(selected_w, valid)))
            second = float(sum(weight * np.mean(observations[i]["gaps"]**2) for weight, i in zip(selected_w, valid)))
            mad = float(sum(weight * np.mean(observations[i]["centers"]) for weight, i in zip(selected_w, valid)))
            summary = dict(gap_first=first, gap_second=second, mad=mad,
                           active_cp_count=len(valid), active_pair_observations=sum(len(row["gaps"]) for row in observations))
            for threshold in (5, 10, 20):
                summary[f"sas_{threshold}mm"] = float(sum(weight * np.mean(observations[i]["gaps"] < threshold)
                                                        for weight, i in zip(selected_w, valid)))
            info["layers"][kind] = summary
        beam_results.append(info)
    mus = np.asarray([beam["mu"] for beam in beam_results])
    def avg(key):
        return float(np.average([beam[key] for beam in beam_results], weights=mus))
    for stats in checks.values():
        assert stats["area_max_abs_error"] < 1e-7 and stats["perimeter_max_abs_error"] < 1e-7
    output = {"case_id": case.case_id, "beam_count": len(beam_results),
              "control_point_count": sum(beam["control_points"] for beam in beam_results),
              "geometry_checks": checks}
    if dual:
        audited = {"pi5": avg("pi5")}
        components = np.average([beam["components"] for beam in beam_results], axis=0, weights=mus)
        output["perimeter_counterfactual"] = {
            "old_formula_replay_pi5": avg("old_pi5"),
            "new_independent_pi5": audited["pi5"],
            "negative_cp_pi_change_contribution": avg("negative_pi_change"),
            "positive_cp_pi_change_contribution": avg("positive_pi_change"),
            "weighted_old_horizontal_mm": float(components[0]),
            "weighted_old_one_bank_all_slots_mm": float(components[1]),
            "weighted_correct_horizontal_mm": float(components[2]),
            "weighted_correct_two_banks_positive_slots_mm": float(components[3]),
            "weighted_old_closed_slot_vertical_contribution_mm": float(components[4]),
            "perimeter_decreased_cp_count": sum(b["perimeter_decreased_cp_count"] for b in beam_results),
            "closed_slots_inside_jaws": int(sum(b["closed_slots_inside_jaws"] for b in beam_results)),
        }
    else:
        audited = {}
    for kind in (["MLCX1", "MLCX2"] if dual else ["MLCX"]):
        suffix = "_" + kind.lower() if dual else ""
        def layer_avg(key):
            return float(np.average([b["layers"][kind][key] for b in beam_results], weights=mus))
        first, second = layer_avg("gap_first"), layer_avg("gap_second")
        audited.update({"alg" + suffix: first, "alg_sd" + suffix: math.sqrt(max(second - first**2, 0.)),
                        "mad" + suffix: layer_avg("mad")})
        for threshold in (5, 10, 20):
            key = f"sas_{threshold}mm"
            audited[key + suffix] = layer_avg(key)
        output["positive_gap_observations" + suffix] = sum(b["layers"][kind]["active_pair_observations"] for b in beam_results)
    output["metric_checks"] = {
        key: {"independent_unrounded": value, "production": float(metrics[key]),
              "pre_migration_expected": case.expected_metrics.get(key),
              "abs_error_after_declared_rounding": abs(round(value, 6 if key == "pi5" else 2) - float(metrics[key]))}
        for key, value in audited.items()
    }
    assert all(check["abs_error_after_declared_rounding"] < 1e-8 for check in output["metric_checks"].values())
    return output


def audit_cyberknife_pi(case):
    """Reuse the existing XML parser; independently union its segment rectangles."""
    path = resolve_reference_source_path(case)
    plan = RTPlan(str(path)).to_plan_dict()
    xml_paths, missing = resolve_referenced_xml_paths(plan, str(path.parent))
    assert not missing
    beams = parse_cyberknife_beams(xml_paths, machine_name="CyberKnife MLC")
    values, weights = [], []
    area_error = perimeter_error = 0.
    for beam in beams:
        for segment in beam.segments:
            ap = segment.aperture
            rects = []
            for pair in ap.leaf_pairs:
                left, right = max(pair.left, ap.jaw.left), min(pair.right, ap.jaw.right)
                low, high = max(pair.bottom, ap.jaw.bottom), min(pair.top, ap.jaw.top)
                if right > left and high > low:
                    rects.append((left, right, low, high))
            area, perimeter = union_geometry(rects)
            area_error = max(area_error, abs(area - ap.area()))
            perimeter_error = max(perimeter_error, abs(perimeter - ap.perimeter()))
            values.append(perimeter**2 / (4 * math.pi * area) if area > 0 else 0.)
            weights.append(float(segment.mu))
    independent_pi = float(np.average(values, weights=weights))
    production_pi = float(analyze_plan_file(str(path)).flattened_metrics["pi"])
    assert area_error < 1e-7 and perimeter_error < 1e-7, (area_error, perimeter_error, independent_pi, production_pi)
    assert round(independent_pi, 2) == production_pi
    return {"case_id": case.case_id,
            "scope": "Existing DICOM/XML segment parser reused; X-sweep union boundary and segment-MU aggregation independently recomputed.",
            "segment_count": len(values), "independent_pi_unrounded": independent_pi,
            "production_pi": production_pi, "pre_migration_expected_pi": case.expected_metrics["pi"],
            "area_max_abs_error": float(area_error), "perimeter_max_abs_error": float(perimeter_error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    old_class = old_aperture_class()
    manifest = load_reference_manifest()
    cases = [case for case in manifest if case.domain == "VMAT_IMRT"]
    assert len(cases) == 2
    report = {"audit": "raw-dicom-sweep-geometry-v3", "pydicom_version": pydicom.__version__,
              "shared_edge_coordinate_tolerance_mm": COORDINATE_TOLERANCE_MM,
              "oracle": "Physical rectangles from raw IEC boundaries; X-sweep union area and perimeter; native-layer intersection for effective geometry.",
              "gap_formula": "Positive raw gap with positive Y-jaw overlap. Equal leaf-pair weighting within CP; adjacent half-interval MU weighting over nonempty CPs; beam-MU mixture of first and second moments. MAD uses absolute raw bank midpoint.",
              "counterfactual_limit": "Pinned prior aperture code is replayed only to explain the change; it is not the independent geometry oracle.",
              "counterfactual_geometry_revision": PRE_CHANGE_GEOMETRY_REVISION,
              "cases": [audit_case(case, old_class) for case in cases]}
    report["cyberknife_pi_check"] = audit_cyberknife_pi(next(
        case for case in manifest if case.case_id == "cyberknife_multiplan_canonical"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
