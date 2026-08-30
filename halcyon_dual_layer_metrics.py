from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Sequence

import numpy as np

from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.aperture_geometry import PyAperture
from ApertureMetric.meterset_creator import MetersetsFromMetersetWeightsCreator
from ApertureMetric.stacked_aperture import StackedAperture, stack_dual_layer_apertures
from ComplexityMetric.aperture_series_metrics import (
    active_pair_count,
    mean_asymmetry_distance,
    mean_leaf_travel,
    small_aperture_score,
    weighted_gap_moments,
)
from DicomParse.utilities import divide_or_default


DISTAL_DEVICE = "MLCX1"
PROXIMAL_DEVICE = "MLCX2"
EDGE_TIE_ABS_TOL = 1e-6
EDGES_PER_LEAF_PAIR = 2.0


@dataclass(frozen=True)
class LayerControlPoint:
    distal_aperture: PyAperture
    proximal_aperture: PyAperture
    effective_aperture: PyAperture
    stacked_aperture: StackedAperture
    distal_weight: float
    proximal_weight: float
    distal_uncovered: float
    proximal_uncovered: float
    distal_positions: np.ndarray
    proximal_positions: np.ndarray


@dataclass(frozen=True)
class BeamPaperMetrics:
    values: Dict[str, float]
    mu: float
    warnings: tuple[str, ...] = ()


def calculate_halcyon_dual_layer_paper_metrics(plan_dict: Dict[str, Any]) -> Dict[str, float]:
    """Return Tamura 2020 and Quintero 2021 metrics for Halcyon/Ethos dual-layer MLC plans."""
    metrics, _ = calculate_halcyon_dual_layer_metrics_with_warnings(plan_dict)
    return metrics


def calculate_halcyon_dual_layer_metrics_with_warnings(
    plan_dict: Dict[str, Any]
) -> tuple[Dict[str, float], list[str]]:
    if not _is_dual_layer_plan(plan_dict):
        return {}, []

    beams = list(_treatment_beams(plan_dict))
    alignment_failed = any(not _dual_layer_alignment_ok(beam) for beam in beams)
    beam_results = [
        _calculate_beam_paper_metrics(beam)
        for beam in beams
    ]
    beam_results = [result for result in beam_results if result is not None and result.mu > 0.0]
    if not beam_results:
        if alignment_failed:
            return {key: None for key in HYBRID_REPRESENTATION_KEYS}, [
                "[HALCYON_LAYER_ALIGNMENT] Effective and stacked metrics are unavailable because "
                "the dual-layer control-point series are not aligned."
            ]
        return {}, []

    total_mu = sum(result.mu for result in beam_results)
    metric_keys = list(beam_results[0].values.keys())
    metrics: Dict[str, float] = {}
    for key in metric_keys:
        metrics[key] = _round_metric(
            sum(result.values.get(key, 0.0) * result.mu for result in beam_results) / total_mu
        )
    warnings = list(dict.fromkeys(warning for result in beam_results for warning in result.warnings))
    if alignment_failed:
        for key in HYBRID_REPRESENTATION_KEYS:
            metrics[key] = None
        warnings.append(
            "[HALCYON_LAYER_ALIGNMENT] Effective and stacked metrics are unavailable because "
            "the dual-layer control-point series are not aligned."
        )
    return metrics, warnings


HYBRID_REPRESENTATION_KEYS = tuple(
    f"{metric}_{representation}"
    for representation in ("effective", "stacked")
    for metric in (
        "mcsv", "aav", "lsv", "pa", "mad", "alg", "alg_sd", "sas_5mm",
        "sas_10mm", "sas_20mm", "lt", "lt_mean_leaf", "nl_pairs", "nl_leaves",
    )
)


def _is_dual_layer_plan(plan_dict: Dict[str, Any]) -> bool:
    machine_id = str(plan_dict.get("machine_id", "")).lower()
    if not any(token in machine_id for token in ("halcyon", "ethos")):
        return False
    return any(_has_dual_layer_devices(beam) for beam in _treatment_beams(plan_dict))


def _treatment_beams(plan_dict: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    for beam in plan_dict.get("beams", {}).values():
        if beam.get("TreatmentDeliveryType") == "TREATMENT" and float(beam.get("MU", 0.0) or 0.0) > 0.0:
            yield beam


def _has_dual_layer_devices(beam: Dict[str, Any]) -> bool:
    device_types = {
        str(getattr(device, "RTBeamLimitingDeviceType", "")).upper()
        for device in beam.get("BeamLimitingDeviceSequence", [])
    }
    return DISTAL_DEVICE in device_types and PROXIMAL_DEVICE in device_types


def _dual_layer_alignment_ok(beam: Dict[str, Any]) -> bool:
    creator = AperturesFromBeamCreator()
    distal_count = 0
    proximal_count = 0
    for control_point in beam.get("ControlPointSequence", []):
        has_distal = creator.get_halcyon_leaf_positions(control_point, DISTAL_DEVICE) is not None
        has_proximal = creator.get_halcyon_leaf_positions(control_point, PROXIMAL_DEVICE) is not None
        distal_count += int(has_distal)
        proximal_count += int(has_proximal)
        if has_distal != has_proximal:
            return False
    return distal_count == proximal_count


def _calculate_beam_paper_metrics(beam: Dict[str, Any]) -> BeamPaperMetrics | None:
    snapshots = _build_layer_control_points(beam)
    if len(snapshots) < 2:
        return None

    cumulative_mu = MetersetsFromMetersetWeightsCreator().get_cumulative_metersets(beam)
    if cumulative_mu is None or len(cumulative_mu) != len(snapshots):
        return None

    cp_mu = MetersetsFromMetersetWeightsCreator().create(beam)
    if cp_mu is None or len(cp_mu) != len(snapshots):
        cp_mu = _centered_control_point_mu(cumulative_mu)
    interval_mu = np.diff(cumulative_mu)
    beam_mu = float(cumulative_mu[-1] - cumulative_mu[0])
    if beam_mu <= 0.0:
        beam_mu = float(beam.get("MU", 0.0) or 0.0)
    if beam_mu <= 0.0:
        return None

    distal_apertures = [snapshot.distal_aperture for snapshot in snapshots]
    proximal_apertures = [snapshot.proximal_aperture for snapshot in snapshots]
    effective_apertures = [snapshot.effective_aperture for snapshot in snapshots]
    stacked_apertures = [snapshot.stacked_aperture for snapshot in snapshots]
    distal_weights = np.array([snapshot.distal_weight for snapshot in snapshots], dtype=float)
    proximal_weights = np.array([snapshot.proximal_weight for snapshot in snapshots], dtype=float)
    distal_uncovered = np.array([snapshot.distal_uncovered for snapshot in snapshots], dtype=float)
    proximal_uncovered = np.array([snapshot.proximal_uncovered for snapshot in snapshots], dtype=float)

    distal_mcs = _beam_mcs(distal_apertures, interval_mu)
    proximal_mcs = _beam_mcs(proximal_apertures, interval_mu)
    effective_mcs = _beam_mcs(effective_apertures, interval_mu)

    distal_pa = _weighted_cp_mean([aperture.area() for aperture in distal_apertures], cp_mu)
    proximal_pa = _weighted_cp_mean([aperture.area() for aperture in proximal_apertures], cp_mu)
    effective_pa = _weighted_cp_mean([aperture.area() for aperture in effective_apertures], cp_mu)

    distal_pi = _weighted_cp_mean([_aperture_irregularity(aperture) for aperture in distal_apertures], cp_mu)
    proximal_pi = _weighted_cp_mean([_aperture_irregularity(aperture) for aperture in proximal_apertures], cp_mu)
    effective_pi = _weighted_cp_mean([_aperture_irregularity(aperture) for aperture in effective_apertures], cp_mu)

    distal_pm = _beam_pm(distal_apertures, cp_mu)
    proximal_pm = _beam_pm(proximal_apertures, cp_mu)
    effective_pm = _beam_pm(effective_apertures, cp_mu)

    mcsw, proximal_mcsw, distal_mcsw = _weighted_mcs(
        proximal_apertures,
        distal_apertures,
        interval_mu,
        proximal_weights,
        distal_weights,
    )
    paw, proximal_paw, distal_paw = _weighted_cp_metric(
        [aperture.area() for aperture in proximal_apertures],
        [aperture.area() for aperture in distal_apertures],
        cp_mu,
        proximal_weights,
        distal_weights,
    )
    piw, proximal_piw, distal_piw = _weighted_cp_metric(
        [_aperture_irregularity(aperture) for aperture in proximal_apertures],
        [_aperture_irregularity(aperture) for aperture in distal_apertures],
        cp_mu,
        proximal_weights,
        distal_weights,
    )
    pmw, proximal_pmw, distal_pmw = _weighted_pm(
        proximal_apertures,
        distal_apertures,
        cp_mu,
        proximal_weights,
        distal_weights,
    )
    mcsul, proximal_mcsul, distal_mcsul = _mcs_with_uncovered_layer(
        proximal_apertures,
        distal_apertures,
        interval_mu,
        proximal_weights,
        distal_weights,
        proximal_uncovered,
        distal_uncovered,
    )

    values = {
        "mcsv": effective_mcs,
        "mcs5": effective_mcs,
        "pa5": effective_pa,
        "pi5": effective_pi,
        "pm5": effective_pm,
        "eds": _weighted_cp_mean(distal_weights, cp_mu),
        "mcsw": mcsw,
        "paw": paw,
        "piw": piw,
        "pmw": pmw,
        "proximal_mcs": proximal_mcs,
        "distal_mcs": distal_mcs,
        "proximal_pa": proximal_pa,
        "distal_pa": distal_pa,
        "proximal_pi": proximal_pi,
        "distal_pi": distal_pi,
        "proximal_pm": proximal_pm,
        "distal_pm": distal_pm,
        "proximal_mcsw": proximal_mcsw,
        "distal_mcsw": distal_mcsw,
        "proximal_paw": proximal_paw,
        "distal_paw": distal_paw,
        "proximal_piw": proximal_piw,
        "distal_piw": distal_piw,
        "proximal_pmw": proximal_pmw,
        "distal_pmw": distal_pmw,
        "ul": _weighted_cp_mean(proximal_uncovered + distal_uncovered, cp_mu),
        "proximal_ul": _weighted_cp_mean(proximal_uncovered, cp_mu),
        "distal_ul": _weighted_cp_mean(distal_uncovered, cp_mu),
        "mcsul": mcsul,
        "proximal_mcsul": proximal_mcsul,
        "distal_mcsul": distal_mcsul,
        "np": _number_of_peaks_score(snapshots),
        "mucp": _mean_interval_mu_fraction(interval_mu, beam_mu),
        "proximal_weight_mean": _weighted_cp_mean(proximal_weights, cp_mu),
        "distal_weight_mean": _weighted_cp_mean(distal_weights, cp_mu),
    }
    effective_values, effective_warnings = _hybrid_representation_values(
        effective_apertures, cp_mu, interval_mu, "effective"
    )
    stacked_values, stacked_warnings = _hybrid_representation_values(
        stacked_apertures, cp_mu, interval_mu, "stacked"
    )
    values.update(effective_values)
    values.update(stacked_values)
    values["mcsv_effective"] = values["mcs5"]
    values["pa_effective"] = values["pa5"]
    return BeamPaperMetrics(
        values=values,
        mu=float(beam.get("MU", beam_mu) or beam_mu),
        warnings=tuple(dict.fromkeys(effective_warnings + stacked_warnings)),
    )


def _hybrid_representation_values(
    apertures: Sequence[Any],
    cp_mu: Sequence[float],
    interval_mu: Sequence[float],
    suffix: str,
) -> tuple[Dict[str, float], list[str]]:
    gap_moments = weighted_gap_moments(apertures, cp_mu)
    mad = mean_asymmetry_distance(apertures, cp_mu)
    sas_values = {
        threshold: small_aperture_score(apertures, cp_mu, float(threshold))
        for threshold in (5, 10, 20)
    }
    pair_count = active_pair_count(apertures, cp_mu)
    aav, lsv = _beam_aav_lsv(apertures, interval_mu)
    travel_terms = [
        _leaf_travel_total(first, second)
        for first, second in zip(apertures[:-1], apertures[1:])
    ]
    values = {
        f"mcsv_{suffix}": _beam_mcs(apertures, interval_mu),
        f"aav_{suffix}": aav,
        f"lsv_{suffix}": lsv,
        f"pa_{suffix}": _weighted_cp_mean([aperture.area() for aperture in apertures], cp_mu),
        f"mad_{suffix}": mad.value,
        f"alg_{suffix}": gap_moments.mean,
        f"alg_sd_{suffix}": gap_moments.standard_deviation,
        f"sas_5mm_{suffix}": sas_values[5].value,
        f"sas_10mm_{suffix}": sas_values[10].value,
        f"sas_20mm_{suffix}": sas_values[20].value,
        f"lt_{suffix}": _weighted_interval_mean(travel_terms, interval_mu),
        f"lt_mean_leaf_{suffix}": mean_leaf_travel(apertures),
        f"nl_pairs_{suffix}": pair_count.value,
        f"nl_leaves_{suffix}": 2.0 * pair_count.value,
    }
    fallback = gap_moments.used_uniform_weights or mad.used_uniform_weights or pair_count.used_uniform_weights
    fallback = fallback or any(result.used_uniform_weights for result in sas_values.values())
    warnings = []
    if fallback:
        warnings.append(
            f"[METRIC_WEIGHT_FALLBACK] Halcyon {suffix} metrics used uniform control-point "
            "weights because MU increments were missing or invalid."
        )
    return values, warnings


def _beam_aav_lsv(
    apertures: Sequence[Any], interval_mu: Sequence[float]
) -> tuple[float, float]:
    if len(apertures) < 2:
        return 0.0, 0.0
    normalization = _arc_aav_normalization(apertures)
    aav_cp = np.asarray(
        [divide_or_default(aperture.area(), normalization) for aperture in apertures],
        dtype=float,
    )
    lsv_cp = np.asarray([_leaf_sequence_variability(aperture) for aperture in apertures])
    return (
        _weighted_interval_mean(_adjacent_mean(aav_cp), interval_mu),
        _weighted_interval_mean(_adjacent_mean(lsv_cp), interval_mu),
    )


def _leaf_travel_total(first: Any, second: Any) -> float:
    total = 0.0
    for first_pair, second_pair in zip(first.leaf_pairs, second.leaf_pairs):
        if first_pair.is_outside_jaw() and second_pair.is_outside_jaw():
            continue
        total += abs(float(first_pair.left) - float(second_pair.left))
        total += abs(float(first_pair.right) - float(second_pair.right))
    return total


def _build_layer_control_points(beam: Dict[str, Any]) -> list[LayerControlPoint]:
    distal_widths = _device_widths(beam, DISTAL_DEVICE)
    proximal_widths = _device_widths(beam, PROXIMAL_DEVICE)
    if len(distal_widths) == 0 or len(proximal_widths) == 0:
        return []

    snapshots: list[LayerControlPoint] = []
    creator = AperturesFromBeamCreator()
    for control_point in beam.get("ControlPointSequence", []):
        distal_positions = creator.get_halcyon_leaf_positions(control_point, DISTAL_DEVICE)
        proximal_positions = creator.get_halcyon_leaf_positions(control_point, PROXIMAL_DEVICE)
        if distal_positions is None or proximal_positions is None:
            continue

        gantry_angle = float(control_point.GantryAngle) if "GantryAngle" in control_point else float(beam.get("GantryAngle", 0.0))
        jaw = creator.get_halcyon_jaw_positions(beam, control_point)
        distal_aperture = PyAperture(distal_positions, distal_widths, jaw, gantry_angle)
        proximal_aperture = PyAperture(proximal_positions, proximal_widths, jaw, gantry_angle)

        effective_positions, aligned_distal, aligned_proximal = _effective_positions(distal_positions, proximal_positions)
        effective_widths = _effective_widths(distal_widths, len(effective_positions[0]))
        effective_aperture = PyAperture(effective_positions, effective_widths, jaw, gantry_angle)
        stacked_aperture = stack_dual_layer_apertures(distal_aperture, proximal_aperture)
        distal_weight, proximal_weight, distal_uncovered, proximal_uncovered = _layer_contributions(
            effective_aperture,
            aligned_distal,
            aligned_proximal,
        )
        snapshots.append(
            LayerControlPoint(
                distal_aperture=distal_aperture,
                proximal_aperture=proximal_aperture,
                effective_aperture=effective_aperture,
                stacked_aperture=stacked_aperture,
                distal_weight=distal_weight,
                proximal_weight=proximal_weight,
                distal_uncovered=distal_uncovered,
                proximal_uncovered=proximal_uncovered,
                distal_positions=distal_positions,
                proximal_positions=proximal_positions,
            )
        )
    return snapshots


def _device_widths(beam: Dict[str, Any], device_type: str) -> np.ndarray:
    for device in beam.get("BeamLimitingDeviceSequence", []):
        if str(getattr(device, "RTBeamLimitingDeviceType", "")).upper() == device_type:
            boundaries = np.array(getattr(device, "LeafPositionBoundaries", []), dtype=float)
            if len(boundaries) >= 2:
                return np.diff(boundaries)
    return np.array([])


def _effective_positions(distal_positions: np.ndarray, proximal_positions: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    distal = np.repeat(np.asarray(distal_positions, dtype=float), 2, axis=1)
    proximal = np.repeat(np.asarray(proximal_positions, dtype=float), 2, axis=1)
    if proximal.shape[1] == distal.shape[1] + 2:
        proximal = proximal[:, 1:-1]
    elif distal.shape[1] == proximal.shape[1] + 2:
        distal = distal[:, 1:-1]

    columns = min(distal.shape[1], proximal.shape[1])
    distal = _center_crop_columns(distal, columns)
    proximal = _center_crop_columns(proximal, columns)

    effective = np.vstack((np.maximum(distal[0], proximal[0]), np.minimum(distal[1], proximal[1])))
    closed = effective[1] - effective[0] < 0.0
    effective[:, closed] = 0.0
    return effective, distal, proximal


def _center_crop_columns(values: np.ndarray, columns: int) -> np.ndarray:
    if values.shape[1] == columns:
        return values
    start = max((values.shape[1] - columns) // 2, 0)
    return values[:, start:start + columns]


def _effective_widths(distal_widths: np.ndarray, count: int) -> np.ndarray:
    if len(distal_widths) == 0:
        return np.ones(count, dtype=float)
    width = float(np.median(np.abs(distal_widths))) / 2.0
    return np.full(count, width if width > 0.0 else 5.0, dtype=float)


def _layer_contributions(
    effective_aperture: PyAperture,
    distal_positions: np.ndarray,
    proximal_positions: np.ndarray,
) -> tuple[float, float, float, float]:
    distal_edge_score = 0.0
    proximal_edge_score = 0.0
    distal_uncovered_edge_score = 0.0
    proximal_uncovered_edge_score = 0.0
    active_pairs = 0

    for index, leaf_pair in enumerate(effective_aperture.leaf_pairs):
        if leaf_pair.is_outside_jaw() or leaf_pair.field_size() <= 0.0:
            continue
        active_pairs += 1
        distal_left = distal_positions[0, index]
        proximal_left = proximal_positions[0, index]
        distal_right = distal_positions[1, index]
        proximal_right = proximal_positions[1, index]

        left_distal, left_proximal = _limiting_left_edge(distal_left, proximal_left)
        right_distal, right_proximal = _limiting_right_edge(distal_right, proximal_right)
        distal_edge_score += left_distal + right_distal
        proximal_edge_score += left_proximal + right_proximal
        # Tied layer edges share effective-aperture weight but do not create uncovered exposure.
        if not _edges_tied(distal_left, proximal_left):
            distal_uncovered_edge_score += left_distal
            proximal_uncovered_edge_score += left_proximal
        if not _edges_tied(distal_right, proximal_right):
            distal_uncovered_edge_score += right_distal
            proximal_uncovered_edge_score += right_proximal

    if active_pairs == 0:
        return 0.5, 0.5, 0.0, 0.0

    normalization = EDGES_PER_LEAF_PAIR * active_pairs
    distal_weight = distal_edge_score / normalization
    proximal_weight = proximal_edge_score / normalization
    total = distal_weight + proximal_weight
    if total <= 0.0:
        distal_weight = proximal_weight = 0.5
    else:
        distal_weight /= total
        proximal_weight /= total

    return (
        distal_weight,
        proximal_weight,
        distal_uncovered_edge_score / normalization,
        proximal_uncovered_edge_score / normalization,
    )


def _limiting_left_edge(distal_left: float, proximal_left: float) -> tuple[float, float]:
    if _edges_tied(distal_left, proximal_left):
        return 0.5, 0.5
    return (1.0, 0.0) if distal_left > proximal_left else (0.0, 1.0)


def _limiting_right_edge(distal_right: float, proximal_right: float) -> tuple[float, float]:
    if _edges_tied(distal_right, proximal_right):
        return 0.5, 0.5
    return (1.0, 0.0) if distal_right < proximal_right else (0.0, 1.0)


def _edges_tied(first: float, second: float) -> bool:
    return math.isclose(first, second, abs_tol=EDGE_TIE_ABS_TOL)


def _beam_mcs(apertures: Sequence[PyAperture], interval_mu: Sequence[float]) -> float:
    terms = _mcs_interval_terms(apertures)
    return _weighted_interval_mean(terms, interval_mu)


def _weighted_mcs(
    proximal_apertures: Sequence[PyAperture],
    distal_apertures: Sequence[PyAperture],
    interval_mu: Sequence[float],
    proximal_weights: Sequence[float],
    distal_weights: Sequence[float],
) -> tuple[float, float, float]:
    proximal_terms = _mcs_interval_terms(proximal_apertures)
    distal_terms = _mcs_interval_terms(distal_apertures)
    proximal_interval_weights = _adjacent_mean(proximal_weights)
    distal_interval_weights = _adjacent_mean(distal_weights)
    proximal = _weighted_interval_sum(proximal_terms, interval_mu, proximal_interval_weights)
    distal = _weighted_interval_sum(distal_terms, interval_mu, distal_interval_weights)
    return proximal + distal, proximal, distal


def _mcs_with_uncovered_layer(
    proximal_apertures: Sequence[PyAperture],
    distal_apertures: Sequence[PyAperture],
    interval_mu: Sequence[float],
    proximal_weights: Sequence[float],
    distal_weights: Sequence[float],
    proximal_uncovered: Sequence[float],
    distal_uncovered: Sequence[float],
) -> tuple[float, float, float]:
    proximal_terms = _mcs_interval_terms(proximal_apertures)
    distal_terms = _mcs_interval_terms(distal_apertures)
    proximal_component_weights = _adjacent_mean(proximal_weights) * _adjacent_mean(proximal_uncovered)
    distal_component_weights = _adjacent_mean(distal_weights) * _adjacent_mean(distal_uncovered)
    proximal = _weighted_interval_sum(proximal_terms, interval_mu, proximal_component_weights)
    distal = _weighted_interval_sum(distal_terms, interval_mu, distal_component_weights)
    return proximal + distal, proximal, distal


def _mcs_interval_terms(apertures: Sequence[PyAperture]) -> np.ndarray:
    if len(apertures) < 2:
        return np.array([], dtype=float)
    normalization = _arc_aav_normalization(apertures)
    aav = np.array([divide_or_default(aperture.area(), normalization) for aperture in apertures], dtype=float)
    lsv = np.array([_leaf_sequence_variability(aperture) for aperture in apertures], dtype=float)
    return ((aav[:-1] + aav[1:]) / 2.0) * ((lsv[:-1] + lsv[1:]) / 2.0)


def _arc_aav_normalization(apertures: Sequence[PyAperture]) -> float:
    left_min: dict[int, float] = {}
    right_max: dict[int, float] = {}
    widths: dict[int, float] = {}
    for aperture in apertures:
        for index, leaf_pair in enumerate(aperture.leaf_pairs):
            if leaf_pair.is_outside_jaw():
                continue
            left_min[index] = min(left_min.get(index, leaf_pair.left), leaf_pair.left)
            right_max[index] = max(right_max.get(index, leaf_pair.right), leaf_pair.right)
            widths[index] = leaf_pair.open_leaf_width()
    return sum(max(right_max[index] - left_min[index], 0.0) * widths.get(index, 0.0) for index in left_min)


def _leaf_sequence_variability(aperture: PyAperture) -> float:
    active_leaf_pairs = [leaf_pair for leaf_pair in aperture.leaf_pairs if not leaf_pair.is_outside_jaw() and leaf_pair.field_size() > 0.0]
    if len(active_leaf_pairs) < 2:
        return 1.0 if active_leaf_pairs else 0.0
    left_positions = [leaf_pair.left for leaf_pair in active_leaf_pairs]
    right_positions = [leaf_pair.right for leaf_pair in active_leaf_pairs]
    return _bank_lsv(left_positions) * _bank_lsv(right_positions)


def _bank_lsv(positions: Sequence[float]) -> float:
    if len(positions) < 2:
        return 1.0
    position_range = max(positions) - min(positions)
    if position_range == 0.0:
        return 1.0
    variation_sum = sum(position_range - abs(current - next_position) for current, next_position in zip(positions[:-1], positions[1:]))
    return variation_sum / ((len(positions) - 1) * position_range)


def _aperture_irregularity(aperture: PyAperture) -> float:
    area = aperture.area()
    perimeter = aperture.side_perimeter_horizontal() + aperture.side_perimeter_vertical()
    return divide_or_default(perimeter ** 2, 4.0 * math.pi * area)


def _beam_pm(apertures: Sequence[PyAperture], cp_mu: Sequence[float]) -> float:
    union_area = _union_area(apertures)
    if union_area <= 0.0:
        return 0.0
    numerator = sum(aperture.area() * weight for aperture, weight in zip(apertures, cp_mu))
    denominator = sum(cp_mu) * union_area
    return max(0.0, min(1.0, 1.0 - divide_or_default(numerator, denominator)))


def _weighted_pm(
    proximal_apertures: Sequence[PyAperture],
    distal_apertures: Sequence[PyAperture],
    cp_mu: Sequence[float],
    proximal_weights: Sequence[float],
    distal_weights: Sequence[float],
) -> tuple[float, float, float]:
    proximal_union = _union_area(proximal_apertures)
    distal_union = _union_area(distal_apertures)
    cp_mu_array = np.asarray(cp_mu, dtype=float)
    normalized_mu = _normalize_weights(cp_mu_array)
    proximal = 0.0
    distal = 0.0
    if proximal_union > 0.0:
        proximal = float(np.sum((1.0 - np.array([a.area() / proximal_union for a in proximal_apertures])) * normalized_mu * np.asarray(proximal_weights, dtype=float)))
    if distal_union > 0.0:
        distal = float(np.sum((1.0 - np.array([a.area() / distal_union for a in distal_apertures])) * normalized_mu * np.asarray(distal_weights, dtype=float)))
    return max(0.0, min(1.0, proximal + distal)), max(0.0, proximal), max(0.0, distal)


def _union_area(apertures: Sequence[PyAperture]) -> float:
    area_max: dict[int, float] = {}
    for aperture in apertures:
        for index, leaf_pair in enumerate(aperture.leaf_pairs):
            if leaf_pair.is_outside_jaw():
                continue
            area_max[index] = max(leaf_pair.field_area(), area_max.get(index, 0.0))
    return sum(area_max.values())


def _weighted_cp_metric(
    proximal_values: Sequence[float],
    distal_values: Sequence[float],
    cp_mu: Sequence[float],
    proximal_weights: Sequence[float],
    distal_weights: Sequence[float],
) -> tuple[float, float, float]:
    normalized_mu = _normalize_weights(np.asarray(cp_mu, dtype=float))
    proximal = float(np.sum(np.asarray(proximal_values, dtype=float) * normalized_mu * np.asarray(proximal_weights, dtype=float)))
    distal = float(np.sum(np.asarray(distal_values, dtype=float) * normalized_mu * np.asarray(distal_weights, dtype=float)))
    return proximal + distal, proximal, distal


def _weighted_cp_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    return float(np.sum(np.asarray(values, dtype=float) * _normalize_weights(np.asarray(weights, dtype=float))))


def _weighted_interval_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    values_array = np.asarray(values, dtype=float)
    weights_array = _normalize_weights(np.asarray(weights, dtype=float)[: len(values_array)])
    return float(np.sum(values_array * weights_array))


def _weighted_interval_sum(values: Sequence[float], interval_mu: Sequence[float], component_weights: Sequence[float]) -> float:
    values_array = np.asarray(values, dtype=float)
    interval_weights = _normalize_weights(np.asarray(interval_mu, dtype=float)[: len(values_array)])
    component_array = np.asarray(component_weights, dtype=float)[: len(values_array)]
    return float(np.sum(values_array * interval_weights * component_array))


def _normalize_weights(weights: np.ndarray) -> np.ndarray:
    total = float(np.sum(weights))
    if total <= 0.0:
        return np.zeros_like(weights, dtype=float)
    return weights / total


def _adjacent_mean(values: Sequence[float]) -> np.ndarray:
    values_array = np.asarray(values, dtype=float)
    if len(values_array) < 2:
        return np.array([], dtype=float)
    return (values_array[:-1] + values_array[1:]) / 2.0


def _centered_control_point_mu(cumulative_mu: Sequence[float]) -> np.ndarray:
    cumulative = np.asarray(cumulative_mu, dtype=float)
    values = np.zeros(len(cumulative), dtype=float)
    if len(cumulative) < 2:
        return values
    deltas = np.diff(cumulative)
    values[0] = deltas[0] / 2.0
    values[-1] = deltas[-1] / 2.0
    if len(cumulative) > 2:
        values[1:-1] = (deltas[:-1] + deltas[1:]) / 2.0
    return values


def _mean_interval_mu_fraction(interval_mu: Sequence[float], beam_mu: float) -> float:
    if beam_mu <= 0.0 or len(interval_mu) == 0:
        return 0.0
    return float(np.mean(np.asarray(interval_mu, dtype=float) / beam_mu) * 100.0)


def _number_of_peaks_score(snapshots: Sequence[LayerControlPoint]) -> float:
    trajectories = _leaf_trajectories(snapshots)
    peak_counts = []
    for trajectory in trajectories:
        if max(trajectory) - min(trajectory) <= 1e-6:
            continue
        peak_counts.append(float(len(_find_peaks(trajectory))))
    if not peak_counts:
        return 0.0
    return float(np.mean(peak_counts))


def _leaf_trajectories(snapshots: Sequence[LayerControlPoint]) -> list[list[float]]:
    arrays = []
    for layer_name in ("distal_positions", "proximal_positions"):
        first_positions = getattr(snapshots[0], layer_name)
        for bank_index in range(first_positions.shape[0]):
            for leaf_index in range(first_positions.shape[1]):
                arrays.append([
                    float(getattr(snapshot, layer_name)[bank_index, leaf_index])
                    for snapshot in snapshots
                    if leaf_index < getattr(snapshot, layer_name).shape[1]
                ])
    return arrays


def _find_peaks(values: Sequence[float]) -> list[int]:
    try:
        from scipy.signal import find_peaks

        return list(find_peaks(np.asarray(values, dtype=float))[0])
    except Exception:
        peaks = []
        for index in range(1, len(values) - 1):
            if values[index] > values[index - 1] and values[index] > values[index + 1]:
                peaks.append(index)
        return peaks


def _round_metric(value: float) -> float:
    if isinstance(value, float) and math.isnan(value):
        return 0.0
    return round(float(value), 6)
