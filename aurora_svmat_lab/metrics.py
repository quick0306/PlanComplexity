from __future__ import annotations

import math
from statistics import fmean, pstdev
from typing import Any, Iterable, Sequence

from .models import AuroraBeam, AuroraControlPoint


SMALL_OPENING_THRESHOLD_MM = 10.0
NEAR_CLOSED_THRESHOLD_MM = 2.0
TOP_K_INTERVALS = 3
AXIAL_REGIONS: tuple[str, ...] = ("head", "mid", "tail")

V2_METRIC_ORDER: tuple[str, ...] = (
    "longitudinal_travel_mm",
    "total_rotation_deg",
    "rotations",
    "travel_per_rotation_mm",
    "projection_pitch_mean",
    "projection_pitch_cv",
    "projection_mu_density_mean_proxy",
    "projection_mu_density_cv_proxy",
    "projection_aperture_change_mean",
    "projection_aperture_change_cv",
    "projection_leaf_travel_mean",
    "projection_leaf_travel_cv",
    "projection_leaf_travel_mean_mlcx1",
    "projection_leaf_travel_cv_mlcx1",
    "projection_leaf_travel_mean_mlcx2",
    "projection_leaf_travel_cv_mlcx2",
    "theta_z_coupling_cv",
    "mu_z_coupling_cv_proxy",
    "mlc_z_coupling_cv",
    "mlcx1_z_coupling_cv",
    "mlcx2_z_coupling_cv",
)

REVERSAL_METRIC_ORDER: tuple[str, ...] = (
    "reversal_symmetry_index",
    "forward_backward_metric_difference",
    "beam_pair_balance_index",
)

SMALL_OPENING_METRIC_ORDER: tuple[str, ...] = (
    "small_opening_fraction",
    "near_closed_fraction",
    "effective_small_gap_burden",
)

PEAK_METRIC_ORDER: tuple[str, ...] = (
    "projection_pitch_p95",
    "projection_pitch_max",
    "projection_pitch_top3_mean",
    "projection_mu_density_p95_proxy",
    "projection_mu_density_max_proxy",
    "projection_mu_density_top3_mean_proxy",
    "projection_aperture_change_p95",
    "projection_aperture_change_max",
    "projection_aperture_change_top3_mean",
    "projection_leaf_travel_p95",
    "projection_leaf_travel_max",
    "projection_leaf_travel_top3_mean",
)

REGIONAL_METRIC_ORDER: tuple[str, ...] = tuple(
    f"{region}_{suffix}"
    for region in AXIAL_REGIONS
    for suffix in (
        "mu_density_mean_proxy",
        "mu_density_cv_proxy",
        "aperture_change_mean",
        "aperture_change_cv",
        "leaf_travel_mean",
        "leaf_travel_cv",
    )
)

LAYER_METRIC_ORDER: tuple[str, ...] = (
    "layer_imbalance_index",
    "layer_correlation_index",
    "x1_x2_aperture_disparity",
    "x1_x2_leaf_travel_ratio",
)

V3_METRIC_ORDER: tuple[str, ...] = (
    REVERSAL_METRIC_ORDER
    + SMALL_OPENING_METRIC_ORDER
    + PEAK_METRIC_ORDER
    + REGIONAL_METRIC_ORDER
    + LAYER_METRIC_ORDER
)

LEGACY_METRIC_ORDER: tuple[str, ...] = (
    "axial_travel_mm",
    "gantry_rotation_deg",
    "mm_per_deg",
    "mm_per_rotation",
    "pitch_consistency",
    "mu_per_mm",
    "aperture_change_per_mm",
    "leaf_travel_per_mm",
    "coupled_modulation_index",
)

FIRST_PASS_METRIC_ORDER: tuple[str, ...] = V2_METRIC_ORDER + V3_METRIC_ORDER + LEGACY_METRIC_ORDER


def calculate_observed_angle_deltas(
    beam_or_control_points: AuroraBeam | Sequence[AuroraControlPoint] | Any,
) -> list[float]:
    control_points = _control_points(beam_or_control_points)
    deltas: list[float] = []
    for current_cp, next_cp in _iter_control_point_pairs(control_points):
        delta = next_cp.gantry_angle_deg - current_cp.gantry_angle_deg
        if delta > 180.0:
            delta -= 360.0
        if delta < -180.0:
            delta += 360.0
        deltas.append(delta)
    return deltas


def calculate_axial_travel_mm(beam: AuroraBeam | Any) -> float:
    control_points = _control_points(beam)
    return sum(
        abs(next_cp.axial_position_mm - current_cp.axial_position_mm)
        for current_cp, next_cp in _iter_control_point_pairs(control_points)
    )


def calculate_gantry_rotation_deg(beam: AuroraBeam | Any) -> float:
    return sum(abs(delta_deg) for delta_deg in calculate_observed_angle_deltas(beam))


def calculate_mm_per_deg(beam: AuroraBeam | Any) -> float | None:
    axial_travel_mm = calculate_axial_travel_mm(beam)
    gantry_rotation_deg = calculate_gantry_rotation_deg(beam)
    if gantry_rotation_deg <= 0.0:
        return None
    return axial_travel_mm / gantry_rotation_deg


def calculate_mm_per_rotation(beam: AuroraBeam | Any) -> float | None:
    gantry_rotation_deg = calculate_gantry_rotation_deg(beam)
    if gantry_rotation_deg <= 0.0:
        return None
    return calculate_axial_travel_mm(beam) / (gantry_rotation_deg / 360.0)


def calculate_pitch_consistency(beam: AuroraBeam | Any) -> float | None:
    # First-pass Aurora pitch = |delta axial| / |delta gantry|.
    # We summarize consistency as the coefficient of variation of interval pitch.
    # Lower values mean the axial advance per gantry degree is steadier.
    return _coefficient_of_variation(_interval_pitch_values(beam))


def calculate_mu_per_mm(beam: AuroraBeam | Any) -> float | None:
    axial_travel_mm = calculate_axial_travel_mm(beam)
    if axial_travel_mm <= 0.0:
        return None

    total_mu = _total_mu_for_beam(beam)
    if total_mu is None:
        return None
    return total_mu / axial_travel_mm


def calculate_aperture_change_per_mm(beam: AuroraBeam | Any) -> float | None:
    # Aperture is approximated as the summed open leaf-pair widths.
    # We measure how much that open width changes between adjacent control points,
    # then normalize by axial travel to keep the value tied to couch motion.
    total_axial_travel_mm = 0.0
    total_aperture_change_mm = 0.0
    for current_cp, next_cp in _iter_control_point_pairs(_control_points(beam)):
        delta_axial_mm = abs(next_cp.axial_position_mm - current_cp.axial_position_mm)
        if delta_axial_mm <= 0.0:
            continue
        total_axial_travel_mm += delta_axial_mm
        total_aperture_change_mm += abs(_aperture_width_mm(next_cp) - _aperture_width_mm(current_cp))

    if total_axial_travel_mm <= 0.0:
        return None
    return total_aperture_change_mm / total_axial_travel_mm


def calculate_leaf_travel_per_mm(beam: AuroraBeam | Any) -> float | None:
    # Leaf travel is the summed absolute motion across both banks between
    # adjacent control points, normalized by axial travel over the same intervals.
    total_axial_travel_mm = 0.0
    total_leaf_travel_mm = 0.0
    for current_cp, next_cp in _iter_control_point_pairs(_control_points(beam)):
        delta_axial_mm = abs(next_cp.axial_position_mm - current_cp.axial_position_mm)
        if delta_axial_mm <= 0.0:
            continue
        total_axial_travel_mm += delta_axial_mm
        total_leaf_travel_mm += _leaf_bank_travel_mm(
            current_cp.mlc_x1_positions_mm,
            next_cp.mlc_x1_positions_mm,
        )
        total_leaf_travel_mm += _leaf_bank_travel_mm(
            current_cp.mlc_x2_positions_mm,
            next_cp.mlc_x2_positions_mm,
        )

    if total_axial_travel_mm <= 0.0:
        return None
    return total_leaf_travel_mm / total_axial_travel_mm


def calculate_coupled_modulation_index(beam: AuroraBeam | Any) -> float | None:
    # Transparent first-pass aggregate:
    # 1. aperture change per mm
    # 2. leaf travel per mm
    # 3. interval MU-density variability
    # 4. pitch variability
    #
    # The raw terms live on different scales, so each is normalized with x / (1 + x),
    # then averaged with equal weight. This keeps the aggregate monotonic and readable.
    return _combine_modulation_components(
        aperture_change_per_mm=calculate_aperture_change_per_mm(beam),
        leaf_travel_per_mm=calculate_leaf_travel_per_mm(beam),
        mu_density_variability=_calculate_mu_density_variability(beam),
        pitch_consistency=calculate_pitch_consistency(beam),
    )


def calculate_v2_beam_metrics(beam: AuroraBeam | Any) -> dict[str, float | None]:
    total_rotation_deg = calculate_gantry_rotation_deg(beam)
    longitudinal_travel_mm = calculate_axial_travel_mm(beam)
    rotations = (total_rotation_deg / 360.0) if total_rotation_deg > 0.0 else None

    projection_pitch_values = _interval_pitch_values(beam)
    projection_mu_density_values = _interval_weight_density_values(beam)
    projection_aperture_change_values = _interval_aperture_change_values(beam)
    projection_leaf_travel_values = _interval_leaf_travel_values(beam)
    projection_leaf_travel_values_mlcx1 = _interval_leaf_travel_values_for_layer(beam, "mlcx1")
    projection_leaf_travel_values_mlcx2 = _interval_leaf_travel_values_for_layer(beam, "mlcx2")

    projection_pitch_cv = _coefficient_of_variation(projection_pitch_values)
    projection_mu_density_cv_proxy = _coefficient_of_variation(projection_mu_density_values)
    projection_leaf_travel_cv = _coefficient_of_variation(projection_leaf_travel_values)
    projection_leaf_travel_cv_mlcx1 = _coefficient_of_variation(projection_leaf_travel_values_mlcx1)
    projection_leaf_travel_cv_mlcx2 = _coefficient_of_variation(projection_leaf_travel_values_mlcx2)

    return {
        "longitudinal_travel_mm": longitudinal_travel_mm,
        "total_rotation_deg": total_rotation_deg,
        "rotations": rotations,
        "travel_per_rotation_mm": (longitudinal_travel_mm / rotations) if rotations and rotations > 0.0 else None,
        "projection_pitch_mean": _mean_or_none(projection_pitch_values),
        "projection_pitch_cv": projection_pitch_cv,
        "projection_mu_density_mean_proxy": _mean_or_none(projection_mu_density_values),
        "projection_mu_density_cv_proxy": projection_mu_density_cv_proxy,
        "projection_aperture_change_mean": _mean_or_none(projection_aperture_change_values),
        "projection_aperture_change_cv": _coefficient_of_variation(projection_aperture_change_values),
        "projection_leaf_travel_mean": _mean_or_none(projection_leaf_travel_values),
        "projection_leaf_travel_cv": projection_leaf_travel_cv,
        "projection_leaf_travel_mean_mlcx1": _mean_or_none(projection_leaf_travel_values_mlcx1),
        "projection_leaf_travel_cv_mlcx1": projection_leaf_travel_cv_mlcx1,
        "projection_leaf_travel_mean_mlcx2": _mean_or_none(projection_leaf_travel_values_mlcx2),
        "projection_leaf_travel_cv_mlcx2": projection_leaf_travel_cv_mlcx2,
        "theta_z_coupling_cv": projection_pitch_cv,
        "mu_z_coupling_cv_proxy": projection_mu_density_cv_proxy,
        "mlc_z_coupling_cv": projection_leaf_travel_cv,
        "mlcx1_z_coupling_cv": projection_leaf_travel_cv_mlcx1,
        "mlcx2_z_coupling_cv": projection_leaf_travel_cv_mlcx2,
    }


def calculate_v3_beam_metrics(beam: AuroraBeam | Any) -> dict[str, float | None]:
    interval_records = _interval_records_for_beam(beam)
    projection_pitch_values = [record["projection_pitch"] for record in interval_records if record["projection_pitch"] is not None]
    projection_mu_density_values = [
        record["projection_mu_density_proxy"]
        for record in interval_records
        if record["projection_mu_density_proxy"] is not None
    ]
    projection_aperture_change_values = [
        record["projection_aperture_change"]
        for record in interval_records
        if record["projection_aperture_change"] is not None
    ]
    projection_leaf_travel_values = [
        record["projection_leaf_travel"]
        for record in interval_records
        if record["projection_leaf_travel"] is not None
    ]
    metrics = {
        **_peak_metrics_for_series("projection_pitch", projection_pitch_values),
        **_peak_metrics_for_series("projection_mu_density_proxy", projection_mu_density_values),
        **_peak_metrics_for_series("projection_aperture_change", projection_aperture_change_values),
        **_peak_metrics_for_series("projection_leaf_travel", projection_leaf_travel_values),
        **_small_opening_metrics(_effective_gap_samples_for_beam(beam)),
        **_regional_interval_metrics(interval_records),
        **_dual_layer_synergy_metrics(
            control_points=_control_points(beam),
            x1_leaf_travel_values=_interval_leaf_travel_values_for_layer(beam, "mlcx1"),
            x2_leaf_travel_values=_interval_leaf_travel_values_for_layer(beam, "mlcx2"),
        ),
    }
    metrics.update({metric_name: None for metric_name in REVERSAL_METRIC_ORDER})
    return metrics


def calculate_beam_metrics(beam: AuroraBeam | Any) -> dict[str, float | None]:
    legacy_metrics = {
        "axial_travel_mm": calculate_axial_travel_mm(beam),
        "gantry_rotation_deg": calculate_gantry_rotation_deg(beam),
        "mm_per_deg": calculate_mm_per_deg(beam),
        "mm_per_rotation": calculate_mm_per_rotation(beam),
        "pitch_consistency": calculate_pitch_consistency(beam),
        "mu_per_mm": calculate_mu_per_mm(beam),
        "aperture_change_per_mm": calculate_aperture_change_per_mm(beam),
        "leaf_travel_per_mm": calculate_leaf_travel_per_mm(beam),
        "coupled_modulation_index": calculate_coupled_modulation_index(beam),
    }
    return {**calculate_v2_beam_metrics(beam), **calculate_v3_beam_metrics(beam), **legacy_metrics}


def calculate_plan_metrics(beams: Iterable[AuroraBeam | Any]) -> dict[str, float | None]:
    beam_list = list(beams)
    axial_travel_mm = sum(calculate_axial_travel_mm(beam) for beam in beam_list)
    gantry_rotation_deg = sum(calculate_gantry_rotation_deg(beam) for beam in beam_list)

    mu_per_mm = None
    total_mu = _calculate_plan_total_mu(beam_list)
    if total_mu is not None and axial_travel_mm > 0.0:
        mu_per_mm = total_mu / axial_travel_mm

    aperture_change_per_mm = _calculate_plan_aperture_change_per_mm(beam_list)
    leaf_travel_per_mm = _calculate_plan_leaf_travel_per_mm(beam_list)
    pitch_consistency = _calculate_plan_pitch_consistency(beam_list)
    mu_density_variability = _calculate_plan_mu_density_variability(beam_list)
    rotations = (gantry_rotation_deg / 360.0) if gantry_rotation_deg > 0.0 else None
    projection_pitch_values = _plan_interval_pitch_values(beam_list)
    projection_mu_density_values = _plan_interval_weight_density_values(beam_list)
    projection_aperture_change_values = _plan_interval_aperture_change_values(beam_list)
    projection_leaf_travel_values = _plan_interval_leaf_travel_values(beam_list)
    projection_leaf_travel_values_mlcx1 = _plan_interval_leaf_travel_values_for_layer(beam_list, "mlcx1")
    projection_leaf_travel_values_mlcx2 = _plan_interval_leaf_travel_values_for_layer(beam_list, "mlcx2")

    v2_metrics = {
        "longitudinal_travel_mm": axial_travel_mm,
        "total_rotation_deg": gantry_rotation_deg,
        "rotations": rotations,
        "travel_per_rotation_mm": (axial_travel_mm / rotations) if rotations and rotations > 0.0 else None,
        "projection_pitch_mean": _mean_or_none(projection_pitch_values),
        "projection_pitch_cv": _coefficient_of_variation(projection_pitch_values),
        "projection_mu_density_mean_proxy": _mean_or_none(projection_mu_density_values),
        "projection_mu_density_cv_proxy": _coefficient_of_variation(projection_mu_density_values),
        "projection_aperture_change_mean": _mean_or_none(projection_aperture_change_values),
        "projection_aperture_change_cv": _coefficient_of_variation(projection_aperture_change_values),
        "projection_leaf_travel_mean": _mean_or_none(projection_leaf_travel_values),
        "projection_leaf_travel_cv": _coefficient_of_variation(projection_leaf_travel_values),
        "projection_leaf_travel_mean_mlcx1": _mean_or_none(projection_leaf_travel_values_mlcx1),
        "projection_leaf_travel_cv_mlcx1": _coefficient_of_variation(projection_leaf_travel_values_mlcx1),
        "projection_leaf_travel_mean_mlcx2": _mean_or_none(projection_leaf_travel_values_mlcx2),
        "projection_leaf_travel_cv_mlcx2": _coefficient_of_variation(projection_leaf_travel_values_mlcx2),
        "theta_z_coupling_cv": _coefficient_of_variation(projection_pitch_values),
        "mu_z_coupling_cv_proxy": _coefficient_of_variation(projection_mu_density_values),
        "mlc_z_coupling_cv": _coefficient_of_variation(projection_leaf_travel_values),
        "mlcx1_z_coupling_cv": _coefficient_of_variation(projection_leaf_travel_values_mlcx1),
        "mlcx2_z_coupling_cv": _coefficient_of_variation(projection_leaf_travel_values_mlcx2),
    }

    legacy_metrics = {
        "axial_travel_mm": axial_travel_mm,
        "gantry_rotation_deg": gantry_rotation_deg,
        "mm_per_deg": (axial_travel_mm / gantry_rotation_deg) if gantry_rotation_deg > 0.0 else None,
        "mm_per_rotation": (axial_travel_mm / (gantry_rotation_deg / 360.0)) if gantry_rotation_deg > 0.0 else None,
        "pitch_consistency": pitch_consistency,
        "mu_per_mm": mu_per_mm,
        "aperture_change_per_mm": aperture_change_per_mm,
        "leaf_travel_per_mm": leaf_travel_per_mm,
        "coupled_modulation_index": _combine_modulation_components(
            aperture_change_per_mm=aperture_change_per_mm,
            leaf_travel_per_mm=leaf_travel_per_mm,
            mu_density_variability=mu_density_variability,
            pitch_consistency=pitch_consistency,
        ),
    }
    v3_metrics = _calculate_plan_v3_metrics(beam_list)
    return {**v2_metrics, **v3_metrics, **legacy_metrics}


def _calculate_plan_v3_metrics(beams: Sequence[AuroraBeam | Any]) -> dict[str, float | None]:
    interval_records = _plan_interval_records(beams)
    projection_pitch_values = [record["projection_pitch"] for record in interval_records if record["projection_pitch"] is not None]
    projection_mu_density_values = [
        record["projection_mu_density_proxy"]
        for record in interval_records
        if record["projection_mu_density_proxy"] is not None
    ]
    projection_aperture_change_values = [
        record["projection_aperture_change"]
        for record in interval_records
        if record["projection_aperture_change"] is not None
    ]
    projection_leaf_travel_values = [
        record["projection_leaf_travel"]
        for record in interval_records
        if record["projection_leaf_travel"] is not None
    ]
    x1_leaf_travel_values = _plan_interval_leaf_travel_values_for_layer(beams, "mlcx1")
    x2_leaf_travel_values = _plan_interval_leaf_travel_values_for_layer(beams, "mlcx2")
    control_points = [control_point for beam in beams for control_point in _control_points(beam)]
    metrics = {
        **_reversal_metrics(beams),
        **_small_opening_metrics(_effective_gap_samples_for_beams(beams)),
        **_peak_metrics_for_series("projection_pitch", projection_pitch_values),
        **_peak_metrics_for_series("projection_mu_density_proxy", projection_mu_density_values),
        **_peak_metrics_for_series("projection_aperture_change", projection_aperture_change_values),
        **_peak_metrics_for_series("projection_leaf_travel", projection_leaf_travel_values),
        **_regional_interval_metrics(interval_records),
        **_dual_layer_synergy_metrics(
            control_points=control_points,
            x1_leaf_travel_values=x1_leaf_travel_values,
            x2_leaf_travel_values=x2_leaf_travel_values,
        ),
    }
    return metrics


def _interval_records_for_beam(beam: AuroraBeam | Any) -> list[dict[str, float | None]]:
    control_points = _control_points(beam)
    observed_angle_deltas = calculate_observed_angle_deltas(control_points)
    records: list[dict[str, float | None]] = []
    for (current_cp, next_cp), delta_gantry_deg in zip(_iter_control_point_pairs(control_points), observed_angle_deltas):
        delta_axial_mm = next_cp.axial_position_mm - current_cp.axial_position_mm
        delta_axial_abs = abs(delta_axial_mm)
        leaf_travel_x1 = _leaf_travel_for_interval(current_cp, next_cp, "mlcx1")
        leaf_travel_x2 = _leaf_travel_for_interval(current_cp, next_cp, "mlcx2")
        records.append(
            {
                "midpoint_z_mm": (current_cp.axial_position_mm + next_cp.axial_position_mm) / 2.0,
                "projection_pitch": (delta_axial_abs / abs(delta_gantry_deg)) if abs(delta_gantry_deg) > 0.0 else None,
                "projection_mu_density_proxy": (
                    abs(next_cp.cumulative_meterset_weight - current_cp.cumulative_meterset_weight) / delta_axial_abs
                    if delta_axial_abs > 0.0
                    else None
                ),
                "projection_aperture_change": (
                    abs(_aperture_width_mm(next_cp) - _aperture_width_mm(current_cp)) / delta_axial_abs
                    if delta_axial_abs > 0.0
                    else None
                ),
                "projection_leaf_travel": (
                    (leaf_travel_x1 + leaf_travel_x2) / delta_axial_abs
                    if delta_axial_abs > 0.0
                    else None
                ),
                "projection_leaf_travel_mlcx1": (leaf_travel_x1 / delta_axial_abs) if delta_axial_abs > 0.0 else None,
                "projection_leaf_travel_mlcx2": (leaf_travel_x2 / delta_axial_abs) if delta_axial_abs > 0.0 else None,
            }
        )
    return records


def _plan_interval_records(beams: Sequence[AuroraBeam | Any]) -> list[dict[str, float | None]]:
    records: list[dict[str, float | None]] = []
    for beam in beams:
        records.extend(_interval_records_for_beam(beam))
    return records


def _peak_metrics_for_series(metric_prefix: str, values: Sequence[float]) -> dict[str, float | None]:
    if metric_prefix == "projection_mu_density_proxy":
        return {
            "projection_mu_density_p95_proxy": _nearest_rank_percentile(values, 95),
            "projection_mu_density_max_proxy": _max_or_none(values),
            "projection_mu_density_top3_mean_proxy": _top_k_mean(values, TOP_K_INTERVALS),
        }
    return {
        f"{metric_prefix}_p95": _nearest_rank_percentile(values, 95),
        f"{metric_prefix}_max": _max_or_none(values),
        f"{metric_prefix}_top3_mean": _top_k_mean(values, TOP_K_INTERVALS),
    }


def _small_opening_metrics(samples: Sequence[tuple[float, float]]) -> dict[str, float]:
    open_samples = [(gap_mm, weight) for gap_mm, weight in samples if gap_mm > 0.0 and weight > 0.0]
    denominator = sum(weight for _gap_mm, weight in open_samples)
    if denominator <= 0.0:
        return {
            "small_opening_fraction": 0.0,
            "near_closed_fraction": 0.0,
            "effective_small_gap_burden": 0.0,
        }

    small_opening_weight = sum(
        weight for gap_mm, weight in open_samples if gap_mm < SMALL_OPENING_THRESHOLD_MM
    )
    near_closed_weight = sum(
        weight for gap_mm, weight in open_samples if gap_mm < NEAR_CLOSED_THRESHOLD_MM
    )
    burden = sum(
        weight * max(0.0, 1.0 - (gap_mm / SMALL_OPENING_THRESHOLD_MM))
        for gap_mm, weight in open_samples
    )
    return {
        "small_opening_fraction": small_opening_weight / denominator,
        "near_closed_fraction": near_closed_weight / denominator,
        "effective_small_gap_burden": burden / denominator,
    }


def _effective_gap_samples_for_beam(beam: AuroraBeam | Any) -> list[tuple[float, float]]:
    control_points = _control_points(beam)
    samples: list[tuple[float, float]] = []
    for current_cp, next_cp in _iter_control_point_pairs(control_points):
        interval_weight = abs(next_cp.cumulative_meterset_weight - current_cp.cumulative_meterset_weight)
        sample_weight = interval_weight if interval_weight > 0.0 else 1.0
        for x1_mm, x2_mm in zip(next_cp.mlc_x1_positions_mm, next_cp.mlc_x2_positions_mm):
            samples.append((max(0.0, x2_mm - x1_mm), sample_weight))
    return samples


def _effective_gap_samples_for_beams(beams: Sequence[AuroraBeam | Any]) -> list[tuple[float, float]]:
    samples: list[tuple[float, float]] = []
    for beam in beams:
        samples.extend(_effective_gap_samples_for_beam(beam))
    return samples


def _regional_interval_metrics(interval_records: Sequence[dict[str, float | None]]) -> dict[str, float | None]:
    region_map = _partition_interval_records_by_region(interval_records)
    metrics: dict[str, float | None] = {}
    for region in AXIAL_REGIONS:
        mu_density_values = [
            record["projection_mu_density_proxy"]
            for record in region_map[region]
            if record["projection_mu_density_proxy"] is not None
        ]
        aperture_change_values = [
            record["projection_aperture_change"]
            for record in region_map[region]
            if record["projection_aperture_change"] is not None
        ]
        leaf_travel_values = [
            record["projection_leaf_travel"]
            for record in region_map[region]
            if record["projection_leaf_travel"] is not None
        ]
        metrics[f"{region}_mu_density_mean_proxy"] = _mean_or_none(mu_density_values)
        metrics[f"{region}_mu_density_cv_proxy"] = _coefficient_of_variation(mu_density_values)
        metrics[f"{region}_aperture_change_mean"] = _mean_or_none(aperture_change_values)
        metrics[f"{region}_aperture_change_cv"] = _coefficient_of_variation(aperture_change_values)
        metrics[f"{region}_leaf_travel_mean"] = _mean_or_none(leaf_travel_values)
        metrics[f"{region}_leaf_travel_cv"] = _coefficient_of_variation(leaf_travel_values)
    return metrics


def _partition_interval_records_by_region(
    interval_records: Sequence[dict[str, float | None]],
) -> dict[str, list[dict[str, float | None]]]:
    region_map: dict[str, list[dict[str, float | None]]] = {region: [] for region in AXIAL_REGIONS}
    midpoint_values = [record["midpoint_z_mm"] for record in interval_records if record["midpoint_z_mm"] is not None]
    if not midpoint_values:
        return region_map
    min_z = min(midpoint_values)
    max_z = max(midpoint_values)
    span = max_z - min_z
    for record in interval_records:
        midpoint = record["midpoint_z_mm"]
        if midpoint is None:
            continue
        if span <= 0.0:
            region = "mid"
        else:
            normalized = (midpoint - min_z) / span
            if normalized < (1.0 / 3.0):
                region = "head"
            elif normalized < (2.0 / 3.0):
                region = "mid"
            else:
                region = "tail"
        region_map[region].append(record)
    return region_map


def _dual_layer_synergy_metrics(
    *,
    control_points: Sequence[AuroraControlPoint],
    x1_leaf_travel_values: Sequence[float],
    x2_leaf_travel_values: Sequence[float],
) -> dict[str, float | None]:
    mean_x1 = _mean_or_none(x1_leaf_travel_values)
    mean_x2 = _mean_or_none(x2_leaf_travel_values)
    denominator = (abs(mean_x1) if mean_x1 is not None else 0.0) + (abs(mean_x2) if mean_x2 is not None else 0.0)
    aperture_disparity_values = []
    for control_point in control_points:
        x1_magnitude = sum(abs(position_mm) for position_mm in control_point.mlc_x1_positions_mm)
        x2_magnitude = sum(abs(position_mm) for position_mm in control_point.mlc_x2_positions_mm)
        total_magnitude = x1_magnitude + x2_magnitude
        if total_magnitude <= 0.0:
            continue
        aperture_disparity_values.append(abs(x1_magnitude - x2_magnitude) / total_magnitude)

    return {
        "layer_imbalance_index": (abs(mean_x1 - mean_x2) / denominator) if denominator > 0.0 and mean_x1 is not None and mean_x2 is not None else None,
        "layer_correlation_index": _correlation_or_none(x1_leaf_travel_values, x2_leaf_travel_values),
        "x1_x2_aperture_disparity": _mean_or_none(aperture_disparity_values),
        "x1_x2_leaf_travel_ratio": (mean_x1 / mean_x2) if mean_x1 is not None and mean_x2 not in (None, 0.0) else None,
    }


def _reversal_metrics(beams: Sequence[AuroraBeam | Any]) -> dict[str, float | None]:
    forward_metrics: list[dict[str, float | None]] = []
    backward_metrics: list[dict[str, float | None]] = []
    for beam in beams:
        direction = _beam_direction(beam)
        if direction == 0:
            continue
        metrics = calculate_beam_metrics(beam)
        if direction > 0:
            forward_metrics.append(metrics)
        else:
            backward_metrics.append(metrics)

    if not forward_metrics or not backward_metrics:
        return {metric_name: None for metric_name in REVERSAL_METRIC_ORDER}

    forward_loads = [metric["coupled_modulation_index"] for metric in forward_metrics if metric.get("coupled_modulation_index") is not None]
    backward_loads = [metric["coupled_modulation_index"] for metric in backward_metrics if metric.get("coupled_modulation_index") is not None]
    forward_mean_load = _mean_or_none(forward_loads)
    backward_mean_load = _mean_or_none(backward_loads)
    forward_total_load = sum(forward_loads)
    backward_total_load = sum(backward_loads)
    load_denominator = forward_total_load + backward_total_load

    symmetry_components: list[float] = []
    for metric_name in (
        "projection_mu_density_mean_proxy",
        "projection_aperture_change_mean",
        "projection_leaf_travel_mean",
        "projection_pitch_mean",
    ):
        forward_value = _mean_or_none(
            [metric[metric_name] for metric in forward_metrics if metric.get(metric_name) is not None]
        )
        backward_value = _mean_or_none(
            [metric[metric_name] for metric in backward_metrics if metric.get(metric_name) is not None]
        )
        component = _relative_symmetry(forward_value, backward_value)
        if component is not None:
            symmetry_components.append(component)

    return {
        "reversal_symmetry_index": _mean_or_none(symmetry_components),
        "forward_backward_metric_difference": (
            abs(forward_mean_load - backward_mean_load)
            if forward_mean_load is not None and backward_mean_load is not None
            else None
        ),
        "beam_pair_balance_index": (
            1.0 - (abs(forward_total_load - backward_total_load) / load_denominator)
            if load_denominator > 0.0
            else None
        ),
    }


def _beam_direction(beam: AuroraBeam | Any) -> int:
    control_points = _control_points(beam)
    if len(control_points) < 2:
        return 0
    net_axial_delta = control_points[-1].axial_position_mm - control_points[0].axial_position_mm
    if math.isclose(net_axial_delta, 0.0, abs_tol=1e-9):
        return 0
    return 1 if net_axial_delta > 0.0 else -1


def _control_points(beam_or_control_points: AuroraBeam | Sequence[AuroraControlPoint] | Any) -> list[AuroraControlPoint]:
    if isinstance(beam_or_control_points, Sequence) and not hasattr(beam_or_control_points, "control_points"):
        return list(beam_or_control_points)
    return list(getattr(beam_or_control_points, "control_points", []))


def _iter_control_point_pairs(
    control_points: Sequence[AuroraControlPoint],
) -> Iterable[tuple[AuroraControlPoint, AuroraControlPoint]]:
    return zip(control_points, control_points[1:])


def _iter_interval_motion(
    beam: AuroraBeam | Any,
) -> Iterable[tuple[float, float, float]]:
    control_points = _control_points(beam)
    observed_angle_deltas = calculate_observed_angle_deltas(control_points)
    total_mu = _total_mu_for_beam(beam)
    weight_span = _cumulative_weight_span(control_points)

    for (current_cp, next_cp), delta_gantry_deg in zip(
        _iter_control_point_pairs(control_points),
        observed_angle_deltas,
    ):
        delta_axial_mm = next_cp.axial_position_mm - current_cp.axial_position_mm
        delta_weight = next_cp.cumulative_meterset_weight - current_cp.cumulative_meterset_weight
        if total_mu is not None and weight_span > 0.0:
            delta_mu = abs(delta_weight) / weight_span * total_mu
        elif total_mu is not None and weight_span == 0.0:
            delta_mu = 0.0
        else:
            delta_mu = abs(delta_weight)
        yield delta_axial_mm, delta_gantry_deg, delta_mu


def _iter_plan_interval_motion(
    beams: Sequence[AuroraBeam | Any],
) -> Iterable[tuple[float, float, float]]:
    for beam in beams:
        yield from _iter_interval_motion(beam)


def _total_mu_for_beam(beam: AuroraBeam | Any) -> float | None:
    explicit_total_mu = getattr(beam, "total_mu", None)
    if explicit_total_mu is not None:
        return float(explicit_total_mu)

    control_points = _control_points(beam)
    if len(control_points) < 2:
        return None
    return _cumulative_weight_span(control_points)


def _calculate_plan_total_mu(beams: Sequence[AuroraBeam | Any]) -> float | None:
    beam_totals = [value for value in (_total_mu_for_beam(beam) for beam in beams) if value is not None]
    if not beam_totals:
        return None
    return sum(beam_totals)


def _cumulative_weight_span(control_points: Sequence[AuroraControlPoint]) -> float:
    if len(control_points) < 2:
        return 0.0
    return abs(control_points[-1].cumulative_meterset_weight - control_points[0].cumulative_meterset_weight)


def _aperture_width_mm(control_point: AuroraControlPoint) -> float:
    return sum(
        max(0.0, x2_mm - x1_mm)
        for x1_mm, x2_mm in zip(control_point.mlc_x1_positions_mm, control_point.mlc_x2_positions_mm)
    )


def _leaf_bank_travel_mm(previous_positions: Sequence[float], next_positions: Sequence[float]) -> float:
    return sum(abs(next_mm - previous_mm) for previous_mm, next_mm in zip(previous_positions, next_positions))


def _interval_pitch_values(beam: AuroraBeam | Any) -> list[float]:
    return [
        abs(delta_axial_mm) / abs(delta_gantry_deg)
        for delta_axial_mm, delta_gantry_deg, _delta_mu in _iter_interval_motion(beam)
        if abs(delta_gantry_deg) > 0.0
    ]


def _plan_interval_pitch_values(beams: Sequence[AuroraBeam | Any]) -> list[float]:
    values: list[float] = []
    for beam in beams:
        values.extend(_interval_pitch_values(beam))
    return values


def _interval_weight_density_values(beam: AuroraBeam | Any) -> list[float]:
    control_points = _control_points(beam)
    return [
        abs(next_cp.cumulative_meterset_weight - current_cp.cumulative_meterset_weight) / abs(next_cp.axial_position_mm - current_cp.axial_position_mm)
        for current_cp, next_cp in _iter_control_point_pairs(control_points)
        if abs(next_cp.axial_position_mm - current_cp.axial_position_mm) > 0.0
    ]


def _plan_interval_weight_density_values(beams: Sequence[AuroraBeam | Any]) -> list[float]:
    values: list[float] = []
    for beam in beams:
        values.extend(_interval_weight_density_values(beam))
    return values


def _interval_aperture_change_values(beam: AuroraBeam | Any) -> list[float]:
    control_points = _control_points(beam)
    return [
        abs(_aperture_width_mm(next_cp) - _aperture_width_mm(current_cp)) / abs(next_cp.axial_position_mm - current_cp.axial_position_mm)
        for current_cp, next_cp in _iter_control_point_pairs(control_points)
        if abs(next_cp.axial_position_mm - current_cp.axial_position_mm) > 0.0
    ]


def _plan_interval_aperture_change_values(beams: Sequence[AuroraBeam | Any]) -> list[float]:
    values: list[float] = []
    for beam in beams:
        values.extend(_interval_aperture_change_values(beam))
    return values


def _interval_leaf_travel_values(beam: AuroraBeam | Any) -> list[float]:
    control_points = _control_points(beam)
    values: list[float] = []
    for current_cp, next_cp in _iter_control_point_pairs(control_points):
        delta_axial_mm = abs(next_cp.axial_position_mm - current_cp.axial_position_mm)
        if delta_axial_mm <= 0.0:
            continue
        interval_leaf_travel_mm = _leaf_travel_for_interval(current_cp, next_cp, "mlcx1") + _leaf_travel_for_interval(
            current_cp,
            next_cp,
            "mlcx2",
        )
        values.append(interval_leaf_travel_mm / delta_axial_mm)
    return values


def _plan_interval_leaf_travel_values(beams: Sequence[AuroraBeam | Any]) -> list[float]:
    values: list[float] = []
    for beam in beams:
        values.extend(_interval_leaf_travel_values(beam))
    return values


def _interval_leaf_travel_values_for_layer(beam: AuroraBeam | Any, layer_name: str) -> list[float]:
    control_points = _control_points(beam)
    values: list[float] = []
    for current_cp, next_cp in _iter_control_point_pairs(control_points):
        delta_axial_mm = abs(next_cp.axial_position_mm - current_cp.axial_position_mm)
        if delta_axial_mm <= 0.0:
            continue
        values.append(_leaf_travel_for_interval(current_cp, next_cp, layer_name) / delta_axial_mm)
    return values


def _plan_interval_leaf_travel_values_for_layer(
    beams: Sequence[AuroraBeam | Any],
    layer_name: str,
) -> list[float]:
    values: list[float] = []
    for beam in beams:
        values.extend(_interval_leaf_travel_values_for_layer(beam, layer_name))
    return values


def _calculate_mu_density_variability(beam: AuroraBeam | Any) -> float | None:
    interval_mu_density = [
        delta_mu / abs(delta_axial_mm)
        for delta_axial_mm, _delta_gantry_deg, delta_mu in _iter_interval_motion(beam)
        if abs(delta_axial_mm) > 0.0
    ]
    return _coefficient_of_variation(interval_mu_density)


def _calculate_plan_pitch_consistency(beams: Sequence[AuroraBeam | Any]) -> float | None:
    interval_pitch_values: list[float] = []
    for beam in beams:
        interval_pitch_values.extend(_interval_pitch_values(beam))
    return _coefficient_of_variation(interval_pitch_values)


def _calculate_plan_mu_density_variability(beams: Sequence[AuroraBeam | Any]) -> float | None:
    interval_mu_density = [
        delta_mu / abs(delta_axial_mm)
        for delta_axial_mm, _delta_gantry_deg, delta_mu in _iter_plan_interval_motion(beams)
        if abs(delta_axial_mm) > 0.0
    ]
    return _coefficient_of_variation(interval_mu_density)


def _calculate_plan_aperture_change_per_mm(beams: Sequence[AuroraBeam | Any]) -> float | None:
    total_axial_travel_mm = 0.0
    total_aperture_change_mm = 0.0
    for beam in beams:
        for current_cp, next_cp in _iter_control_point_pairs(_control_points(beam)):
            delta_axial_mm = abs(next_cp.axial_position_mm - current_cp.axial_position_mm)
            if delta_axial_mm <= 0.0:
                continue
            total_axial_travel_mm += delta_axial_mm
            total_aperture_change_mm += abs(_aperture_width_mm(next_cp) - _aperture_width_mm(current_cp))
    if total_axial_travel_mm <= 0.0:
        return None
    return total_aperture_change_mm / total_axial_travel_mm


def _calculate_plan_leaf_travel_per_mm(beams: Sequence[AuroraBeam | Any]) -> float | None:
    total_axial_travel_mm = 0.0
    total_leaf_travel_mm = 0.0
    for beam in beams:
        for current_cp, next_cp in _iter_control_point_pairs(_control_points(beam)):
            delta_axial_mm = abs(next_cp.axial_position_mm - current_cp.axial_position_mm)
            if delta_axial_mm <= 0.0:
                continue
            total_axial_travel_mm += delta_axial_mm
            total_leaf_travel_mm += _leaf_bank_travel_mm(
                current_cp.mlc_x1_positions_mm,
                next_cp.mlc_x1_positions_mm,
            )
            total_leaf_travel_mm += _leaf_bank_travel_mm(
                current_cp.mlc_x2_positions_mm,
                next_cp.mlc_x2_positions_mm,
            )
    if total_axial_travel_mm <= 0.0:
        return None
    return total_leaf_travel_mm / total_axial_travel_mm


def _combine_modulation_components(
    *,
    aperture_change_per_mm: float | None,
    leaf_travel_per_mm: float | None,
    mu_density_variability: float | None,
    pitch_consistency: float | None,
) -> float | None:
    normalized_components = [
        _saturating_normalize(value)
        for value in (
            aperture_change_per_mm,
            leaf_travel_per_mm,
            mu_density_variability,
            pitch_consistency,
        )
        if value is not None
    ]
    if not normalized_components:
        return None
    return fmean(normalized_components)


def _coefficient_of_variation(values: Sequence[float]) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return 0.0

    mean_value = fmean(values)
    if math.isclose(mean_value, 0.0, abs_tol=1e-12):
        return 0.0 if all(math.isclose(value, 0.0, abs_tol=1e-12) for value in values) else None
    return pstdev(values) / abs(mean_value)


def _saturating_normalize(value: float) -> float:
    return value / (1.0 + value)


def _mean_or_none(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return fmean(values)


def _max_or_none(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return max(values)


def _nearest_rank_percentile(values: Sequence[float], percentile: int) -> float | None:
    if not values:
        return None
    sorted_values = sorted(values)
    rank = max(1, math.ceil((percentile / 100.0) * len(sorted_values)))
    return sorted_values[rank - 1]


def _top_k_mean(values: Sequence[float], top_k: int) -> float | None:
    if not values:
        return None
    sorted_values = sorted(values, reverse=True)
    return fmean(sorted_values[: min(top_k, len(sorted_values))])


def _correlation_or_none(x_values: Sequence[float], y_values: Sequence[float]) -> float | None:
    if not x_values or not y_values or len(x_values) != len(y_values):
        return None
    if len(x_values) == 1:
        return 1.0 if math.isclose(x_values[0], y_values[0], abs_tol=1e-12) else 0.0

    mean_x = fmean(x_values)
    mean_y = fmean(y_values)
    std_x = pstdev(x_values)
    std_y = pstdev(y_values)
    if math.isclose(std_x, 0.0, abs_tol=1e-12) or math.isclose(std_y, 0.0, abs_tol=1e-12):
        pairs_match = all(
            math.isclose(x_value, y_value, abs_tol=1e-12)
            for x_value, y_value in zip(x_values, y_values)
        )
        return 1.0 if pairs_match else 0.0

    covariance = fmean(
        (x_value - mean_x) * (y_value - mean_y)
        for x_value, y_value in zip(x_values, y_values)
    )
    return covariance / (std_x * std_y)


def _relative_symmetry(forward_value: float | None, backward_value: float | None) -> float | None:
    if forward_value is None or backward_value is None:
        return None
    denominator = abs(forward_value) + abs(backward_value)
    if math.isclose(denominator, 0.0, abs_tol=1e-12):
        return 1.0
    return 1.0 - (abs(forward_value - backward_value) / denominator)


def _leaf_travel_for_interval(
    current_cp: AuroraControlPoint,
    next_cp: AuroraControlPoint,
    layer_name: str,
) -> float:
    if layer_name == "mlcx1":
        return _leaf_bank_travel_mm(current_cp.mlc_x1_positions_mm, next_cp.mlc_x1_positions_mm)
    if layer_name == "mlcx2":
        return _leaf_bank_travel_mm(current_cp.mlc_x2_positions_mm, next_cp.mlc_x2_positions_mm)
    raise ValueError(f"Unsupported Aurora MLC layer: {layer_name}")
