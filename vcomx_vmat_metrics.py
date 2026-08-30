from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

import numpy as np

from ApertureMetric.aperture_geometry import PyAperture
from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.meterset_creator import MetersetsFromMetersetWeightsCreator
from ApertureMetric.mlc_attributes import MLCAttributes
from ComplexityMetric.aperture_series_metrics import active_leaf_pairs, mean_leaf_travel
from DicomParse.utilities import divide_or_default


TIME_DEPENDENT_KEYS = ("mdrv", "mgsv", "dr", "gs", "ls", "dt")
MLC_DEPENDENT_KEYS = (
    "lt",
    "lt_mean_leaf",
    "ltmu",
    "ltnlmu",
    "nl",
    "nl_pairs",
    "nl_leaves",
    "ltnl",
    "lna",
    "ltal",
    "aav",
    "lsv",
    "tg",
    "pa",
    "ja",
    "efs",
    "psmall",
    "perimeter",
    "md",
)


@dataclass
class BeamLayerSummary:
    metrics: Dict[str, float]


def calculate_vcomx_supplemental_metrics(plan_dict: Dict[str, object]) -> Dict[str, object]:
    metrics, _ = calculate_vcomx_supplemental_metrics_with_warnings(plan_dict)
    return metrics


def calculate_vcomx_supplemental_metrics_with_warnings(
    plan_dict: Dict[str, object],
) -> tuple[Dict[str, object], list[str]]:
    beams = [
        beam
        for beam in plan_dict.get("beams", {}).values()
        if beam.get("TreatmentDeliveryType") == "TREATMENT" and float(beam.get("MU", 0.0)) > 0.0
    ]
    if not beams:
        return {}, []

    warnings = _supplemental_weight_warnings(beams)

    total_mu = float(plan_dict.get("Plan_MU", 0.0) or sum(float(beam.get("MU", 0.0)) for beam in beams))
    fractions = float(plan_dict.get("fractions", 0.0) or 0.0)
    prescribed_dose_cgy = float(plan_dict.get("rxdose", 0.0) or 0.0)
    fraction_dose_cgy = divide_or_default(prescribed_dose_cgy, fractions) if fractions > 0 else prescribed_dose_cgy
    fraction_dose_gy = fraction_dose_cgy / 100.0

    total_control_arcs = sum(max(len(beam.get("ControlPointSequence", [])) - 1, 0) for beam in beams)
    total_gantry_travel = sum(abs(float(beam.get("GantryRotationAngle", 0.0) or 0.0)) for beam in beams)
    beam_weights = [float(beam.get("MU", 0.0)) for beam in beams]
    dual_layer = any(token in str(plan_dict.get("machine_id", "")).lower() for token in ("halcyon", "ethos"))

    metrics: Dict[str, object] = {
        "mus": total_mu,
        "pmu": divide_or_default(total_mu * 2.0, fraction_dose_gy),
        "muca": divide_or_default(total_mu, total_control_arcs),
        "fractions_count": fractions,
        "fraction_dose_gy": fraction_dose_gy,
        "mucgy": divide_or_default(total_mu, fraction_dose_cgy),
        "narcs": float(len(beams)),
        "al": divide_or_default(total_gantry_travel, len(beams)),
        "cal": divide_or_default(total_gantry_travel, total_control_arcs),
        "gt": total_gantry_travel,
        "mudeg": divide_or_default(total_mu, total_gantry_travel),
    }

    if dual_layer:
        beam_summaries = [_summarize_dual_layer_beam(beam) for beam in beams]
        for key in MLC_DEPENDENT_KEYS:
            mlcx1 = _weighted_mean([summary[0].metrics.get(key, 0.0) for summary in beam_summaries], beam_weights)
            mlcx2 = _weighted_mean([summary[1].metrics.get(key, 0.0) for summary in beam_summaries], beam_weights)
            metrics[key] = (_round_metric(mlcx1), _round_metric(mlcx2))

        for key in TIME_DEPENDENT_KEYS:
            mlcx1 = _weighted_mean([summary[0].metrics.get(key, 0.0) for summary in beam_summaries], beam_weights)
            mlcx2 = _weighted_mean([summary[1].metrics.get(key, 0.0) for summary in beam_summaries], beam_weights)
            metrics[key] = (_round_metric(mlcx1), _round_metric(mlcx2))
        metrics["nl"] = metrics["nl_pairs"]
    else:
        beam_summaries = [_summarize_single_layer_beam(beam) for beam in beams]
        for key in MLC_DEPENDENT_KEYS + TIME_DEPENDENT_KEYS:
            metrics[key] = _round_metric(
                _weighted_mean([summary.metrics.get(key, 0.0) for summary in beam_summaries], beam_weights)
            )
        metrics["nl"] = metrics["nl_pairs"]

    return metrics, list(dict.fromkeys(warnings))


def supplemental_metric_weight_warnings(plan_dict: Dict[str, object]) -> list[str]:
    beams = [
        beam
        for beam in plan_dict.get("beams", {}).values()
        if beam.get("TreatmentDeliveryType") == "TREATMENT" and float(beam.get("MU", 0.0)) > 0.0
    ]
    return _supplemental_weight_warnings(beams)


def _supplemental_weight_warnings(beams: Sequence[Dict[str, object]]) -> list[str]:
    warnings = []
    for beam_number, beam in enumerate(beams, start=1):
        _, cp_fallback = _cp_weights_with_fallback(beam)
        _, ca_fallback = _ca_weights_with_fallback(beam)
        if cp_fallback:
            warnings.append(
                "[METRIC_WEIGHT_FALLBACK] Supplemental control-point metrics used uniform "
                f"weights for treatment beam {beam_number} because MU increments were missing, "
                "misaligned, or invalid."
            )
        if ca_fallback:
            warnings.append(
                "[METRIC_WEIGHT_FALLBACK] Supplemental control-arc metrics used uniform "
                f"weights for treatment beam {beam_number} because MU increments were missing, "
                "misaligned, or invalid."
            )

    return list(dict.fromkeys(warnings))


def _summarize_dual_layer_beam(beam: Dict[str, object]) -> tuple[BeamLayerSummary, BeamLayerSummary]:
    apertures = AperturesFromBeamCreator().create(beam)
    cumulative_mu = MetersetsFromMetersetWeightsCreator().get_cumulative_metersets(beam)
    return (
        BeamLayerSummary(_summarize_aperture_series(apertures[0::2], beam, cumulative_mu)),
        BeamLayerSummary(_summarize_aperture_series(apertures[1::2], beam, cumulative_mu)),
    )


def _summarize_single_layer_beam(beam: Dict[str, object]) -> BeamLayerSummary:
    apertures = AperturesFromBeamCreator().create(beam)
    cumulative_mu = MetersetsFromMetersetWeightsCreator().get_cumulative_metersets(beam)
    return BeamLayerSummary(_summarize_aperture_series(apertures, beam, cumulative_mu))


def _summarize_aperture_series(
    apertures: Sequence[PyAperture],
    beam: Dict[str, object],
    cumulative_mu: np.ndarray | None,
) -> Dict[str, float]:
    if not apertures:
        return {key: 0.0 for key in MLC_DEPENDENT_KEYS + TIME_DEPENDENT_KEYS}

    cp_weights = _cp_weights(beam)
    ca_weights = _ca_weights(beam)
    aav_normalization = _aav_normalization(apertures)
    cp_areas = np.array([aperture.area() for aperture in apertures], dtype=float)
    cp_leaf_counts = np.array([_active_leaf_count(aperture) for aperture in apertures], dtype=float)
    cp_perimeters = np.array([_aperture_perimeter(aperture) for aperture in apertures], dtype=float)
    cp_jaw_areas = np.array([_jaw_area(aperture) for aperture in apertures], dtype=float)
    cp_efs = np.array([divide_or_default(4.0 * area, perimeter) for area, perimeter in zip(cp_areas, cp_perimeters)], dtype=float)
    cp_tg = np.array([_tongue_and_groove(aperture) for aperture in apertures], dtype=float)
    cp_aav = np.array([_cp_aav(aperture, aav_normalization) for aperture in apertures], dtype=float)
    cp_lsv = np.array([_cp_lsv(aperture) for aperture in apertures], dtype=float)

    gantry_diffs = _gantry_diffs(apertures)
    ca_lt = np.array([_leaf_travel(first, second) for first, second in zip(apertures[:-1], apertures[1:])], dtype=float)
    ca_nl = np.array([(cp_leaf_counts[i] + cp_leaf_counts[i + 1]) / 2.0 for i in range(len(cp_leaf_counts) - 1)], dtype=float)
    ca_aav = np.array([(cp_aav[i] + cp_aav[i + 1]) / 2.0 for i in range(len(cp_aav) - 1)], dtype=float)
    ca_lsv = np.array([(cp_lsv[i] + cp_lsv[i + 1]) / 2.0 for i in range(len(cp_lsv) - 1)], dtype=float)

    plan_modulation = _modulation_degree(cp_areas, cp_weights, apertures)

    metrics = {
        "lt": _weighted_mean(ca_lt, ca_weights),
        "lt_mean_leaf": mean_leaf_travel(apertures),
        "ltmu": divide_or_default(float(np.sum(ca_lt)), float(beam.get("MU", 0.0) or 0.0)),
        "ltnlmu": divide_or_default(float(np.sum(_safe_divide(ca_lt, ca_nl))), float(beam.get("MU", 0.0) or 0.0)),
        "nl": _weighted_mean(cp_leaf_counts, cp_weights),
        "nl_pairs": _weighted_mean(cp_leaf_counts, cp_weights),
        "nl_leaves": 2.0 * _weighted_mean(cp_leaf_counts, cp_weights),
        "ltnl": _weighted_mean(_safe_divide(ca_lt, ca_nl), ca_weights),
        "lna": _weighted_mean(_safe_divide(ca_lt, ca_nl * gantry_diffs), ca_weights),
        "ltal": _weighted_mean(_safe_divide(ca_lt, gantry_diffs), ca_weights),
        "aav": _weighted_mean(ca_aav, ca_weights),
        "lsv": _weighted_mean(ca_lsv, ca_weights),
        "tg": _weighted_mean(cp_tg, cp_weights),
        "pa": _weighted_mean(cp_areas, cp_weights),
        "ja": _weighted_mean(cp_jaw_areas, cp_weights),
        "efs": _weighted_mean(cp_efs, cp_weights),
        "psmall": _weighted_fraction(cp_efs < 30.0, cp_weights),
        "perimeter": _weighted_mean(cp_perimeters, cp_weights),
        "md": plan_modulation,
    }
    metrics.update(_timing_metrics(apertures, cumulative_mu, beam))
    return metrics


def _timing_metrics(apertures: Sequence[PyAperture], cumulative_mu: np.ndarray | None, beam: Dict[str, object]) -> Dict[str, float]:
    if cumulative_mu is None:
        return {key: 0.0 for key in TIME_DEPENDENT_KEYS}

    try:
        attrs = MLCAttributes(
            list(apertures),
            cumulative_mu,
            beam["TreatmentMachineName"],
            beam["DoseRateSet"],
            beam["GantryRotationAngle"],
        )
    except Exception:
        return {key: 0.0 for key in TIME_DEPENDENT_KEYS}

    delta_gantry = np.asarray(attrs.gantry["delta_gantry"].fillna(0.0).values, dtype=float)
    delta_gantry_speed = np.asarray(attrs.gantry["delta_gantry_speed"].fillna(0.0).values, dtype=float)
    delta_dose_rate = np.asarray(attrs.dose_rate["delta_dose_rate"].fillna(0.0).values, dtype=float)

    return {
        "mdrv": _finite_mean(_safe_divide(delta_dose_rate, delta_gantry)),
        "mgsv": _finite_mean(_safe_divide(delta_gantry_speed, delta_gantry)),
        "dr": _finite_mean(np.asarray(attrs.dose_rate["DR"].values, dtype=float)),
        "gs": _finite_mean(np.asarray(attrs.gantry["gantry_speed"].values, dtype=float)),
        "ls": _finite_value(attrs.get_mlc_speed_avg()),
        "dt": _finite_mean(np.asarray(attrs.delta_mu_time["time"].values, dtype=float)) * len(apertures),
    }


def _cp_weights(beam: Dict[str, object]) -> np.ndarray:
    return _cp_weights_with_fallback(beam)[0]


def _cp_weights_with_fallback(beam: Dict[str, object]) -> tuple[np.ndarray, bool]:
    expected_count = len(beam.get("ControlPointSequence", []))
    values = MetersetsFromMetersetWeightsCreator().create(beam)
    return _validated_weights(values, expected_count)


def _ca_weights(beam: Dict[str, object]) -> np.ndarray:
    return _ca_weights_with_fallback(beam)[0]


def _ca_weights_with_fallback(beam: Dict[str, object]) -> tuple[np.ndarray, bool]:
    expected_count = max(len(beam.get("ControlPointSequence", [])) - 1, 0)
    cumulative = MetersetsFromMetersetWeightsCreator().get_cumulative_metersets(beam)
    values = None if cumulative is None else np.diff(np.asarray(cumulative, dtype=float))
    return _validated_weights(values, expected_count)


def _validated_weights(
    values: Sequence[float] | None, expected_count: int
) -> tuple[np.ndarray, bool]:
    if values is not None:
        weights = np.asarray(values, dtype=float)
        valid = (
            weights.size == expected_count
            and np.all(np.isfinite(weights))
            and np.all(weights >= 0.0)
            and (expected_count == 0 or float(np.sum(weights)) > 0.0)
        )
        if valid:
            return weights, False
    return np.ones(expected_count, dtype=float), True


def _weighted_mean(values: Iterable[float], weights: Sequence[float]) -> float:
    values_arr = np.asarray(list(values), dtype=float)
    if values_arr.size == 0:
        return 0.0
    weights_arr = np.asarray(weights, dtype=float)
    if (
        weights_arr.size != values_arr.size
        or not np.all(np.isfinite(weights_arr))
        or np.any(weights_arr < 0.0)
        or float(np.sum(weights_arr)) <= 0.0
    ):
        weights_arr = np.ones(values_arr.size, dtype=float)
    valid = np.isfinite(values_arr)
    if not np.any(valid):
        return 0.0
    values_arr = values_arr[valid]
    weights_arr = weights_arr[valid]
    total = float(np.sum(weights_arr))
    if total <= 0.0:
        return float(np.mean(values_arr))
    return float(np.sum(values_arr * weights_arr) / total)


def _weighted_fraction(mask: np.ndarray, weights: Sequence[float]) -> float:
    mask_arr = np.asarray(mask, dtype=float)
    if mask_arr.size == 0:
        return 0.0
    return _weighted_mean(mask_arr, weights)


def _active_leaf_count(aperture: PyAperture) -> int:
    return len(active_leaf_pairs(aperture))


def _aperture_perimeter(aperture: PyAperture) -> float:
    return float(aperture.side_perimeter_horizontal() + aperture.side_perimeter_vertical())


def _jaw_area(aperture: PyAperture) -> float:
    return max(aperture.jaw.right - aperture.jaw.left, 0.0) * max(aperture.jaw.top - aperture.jaw.bottom, 0.0)


def _tongue_and_groove(aperture: PyAperture) -> float:
    left_offsets = []
    right_offsets = []
    active = [lp for lp in aperture.leaf_pairs if not lp.is_outside_jaw()]
    for first, second in zip(active[:-1], active[1:]):
        left_offsets.append(abs(first.left - second.left))
        right_offsets.append(abs(first.right - second.right))
    values = np.asarray(left_offsets + right_offsets, dtype=float)
    return _finite_mean(values)


def _aav_normalization(arc_apertures: Sequence[PyAperture]) -> float:
    # The normalization term only depends on the full arc, so compute it once
    # and reuse it for every control point instead of rescanning the arc each time.
    left_min: Dict[int, float] = {}
    right_max: Dict[int, float] = {}
    widths: Dict[int, float] = {}

    for candidate in arc_apertures:
        for idx, lp in enumerate(candidate.leaf_pairs):
            if lp.is_outside_jaw():
                continue
            left_min[idx] = min(left_min.get(idx, lp.left), lp.left)
            right_max[idx] = max(right_max.get(idx, lp.right), lp.right)
            widths[idx] = lp.open_leaf_width()

    normalization = 0.0
    for idx in left_min:
        normalization += max(right_max[idx] - left_min[idx], 0.0) * widths.get(idx, 0.0)
    return normalization


def _cp_aav(aperture: PyAperture, normalization: float) -> float:
    return divide_or_default(aperture.area(), normalization)


def _cp_lsv(aperture: PyAperture) -> float:
    active_leaf_pairs = [lp for lp in aperture.leaf_pairs if not lp.is_outside_jaw() and lp.field_size() > 0]
    if len(active_leaf_pairs) < 2:
        return 1.0 if active_leaf_pairs else 0.0

    left_positions = [lp.left for lp in active_leaf_pairs]
    right_positions = [lp.right for lp in active_leaf_pairs]
    return _bank_lsv(left_positions) * _bank_lsv(right_positions)


def _bank_lsv(positions: List[float]) -> float:
    if len(positions) < 2:
        return 1.0
    span = max(positions) - min(positions)
    if span <= 0:
        return 1.0
    variation_sum = sum(span - abs(curr - nxt) for curr, nxt in zip(positions[:-1], positions[1:]))
    return variation_sum / ((len(positions) - 1) * span)


def _leaf_travel(first: PyAperture, second: PyAperture) -> float:
    total = 0.0
    for first_lp, second_lp in zip(first.leaf_pairs, second.leaf_pairs):
        if first_lp.is_outside_jaw() and second_lp.is_outside_jaw():
            continue
        total += abs(first_lp.left - second_lp.left) + abs(first_lp.right - second_lp.right)
    return total


def _gantry_diffs(apertures: Sequence[PyAperture]) -> np.ndarray:
    diffs: List[float] = []
    for first, second in zip(apertures[:-1], apertures[1:]):
        phi = abs(second.gantry_angle - first.gantry_angle) % 360.0
        diffs.append(360.0 - phi if phi > 180.0 else phi)
    return np.asarray(diffs, dtype=float)


def _modulation_degree(cp_areas: np.ndarray, cp_weights: np.ndarray, apertures: Sequence[PyAperture]) -> float:
    if cp_areas.size == 0 or cp_weights.size == 0:
        return 0.0
    union_area = _union_area(apertures)
    weighted_area = _weighted_mean(cp_areas, cp_weights)
    return divide_or_default(union_area, weighted_area)


def _union_area(apertures: Sequence[PyAperture]) -> float:
    area_max: Dict[int, float] = {}
    for aperture in apertures:
        for idx, lp in enumerate(aperture.leaf_pairs):
            if lp.is_outside_jaw():
                continue
            area_max[idx] = max(lp.field_area(), area_max.get(idx, 0.0))
    return float(sum(area_max.values()))


def _safe_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    numerator_arr = np.asarray(numerator, dtype=float)
    denominator_arr = np.asarray(denominator, dtype=float)
    result = np.zeros_like(numerator_arr, dtype=float)
    np.divide(numerator_arr, denominator_arr, out=result, where=denominator_arr != 0)
    return result


def _finite_mean(values: np.ndarray) -> float:
    values_arr = np.asarray(values, dtype=float)
    values_arr = values_arr[np.isfinite(values_arr)]
    if values_arr.size == 0:
        return 0.0
    return float(np.mean(values_arr))


def _finite_value(value: float) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(numeric):
        return 0.0
    return numeric


def _round_metric(value: float) -> float:
    return round(_finite_value(value), 2)



