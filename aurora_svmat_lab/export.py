from __future__ import annotations

import csv
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

from .metrics import (
    FIRST_PASS_METRIC_ORDER,
    calculate_beam_metrics,
    calculate_observed_angle_deltas,
    calculate_plan_metrics,
)
from .models import AuroraControlPoint


def export_plan_rows(results: Iterable[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in results:
        metadata = _metadata_for_result(result)
        plan_metrics = _plan_metrics_for_result(result)
        row = {
            "source_path": getattr(result, "source_path", getattr(metadata, "source_path", "")),
            "plan_label": getattr(metadata, "plan_label", ""),
            "plan_name": getattr(metadata, "plan_name", ""),
            "manufacturer": getattr(metadata, "manufacturer", ""),
            "manufacturer_model_name": getattr(metadata, "manufacturer_model_name", ""),
            "supported": bool(getattr(result, "supported", False)),
            "reason": getattr(result, "reason", ""),
            "warning_count": len(getattr(result, "warnings", []) or []),
            "total_beams": len(getattr(result, "beams", []) or []),
        }
        row.update(_ordered_metric_values(plan_metrics))
        rows.append(row)
    return rows


def export_beam_rows(results: Iterable[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in results:
        metadata = _metadata_for_result(result)
        for beam in getattr(result, "beams", []) or []:
            row = {
                "source_path": getattr(result, "source_path", getattr(metadata, "source_path", "")),
                "plan_label": getattr(metadata, "plan_label", ""),
                "plan_name": getattr(metadata, "plan_name", ""),
                "beam_number": getattr(beam, "beam_number", ""),
                "beam_name": getattr(beam, "beam_name", ""),
                "supported": bool(getattr(result, "supported", False)),
                "reason": getattr(result, "reason", ""),
            }
            row.update(_ordered_metric_values(_beam_metrics_for_export(beam)))
            rows.append(row)
    return rows


def export_projection_rows(results: Iterable[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in results:
        metadata = _metadata_for_result(result)
        for beam in getattr(result, "beams", []) or []:
            rows.extend(_projection_rows_for_beam(result, metadata, beam))
    return rows


def export_trajectory_rows(results: Iterable[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in results:
        metadata = _metadata_for_result(result)
        for beam in getattr(result, "beams", []) or []:
            control_points = list(getattr(beam, "control_points", []) or [])
            observed_angle_deltas = calculate_observed_angle_deltas(control_points)
            for index, control_point in enumerate(control_points):
                previous_cp = control_points[index - 1] if index > 0 else None
                row = {
                    "source_path": getattr(result, "source_path", getattr(metadata, "source_path", "")),
                    "plan_label": getattr(metadata, "plan_label", ""),
                    "beam_number": getattr(beam, "beam_number", ""),
                    "beam_name": getattr(beam, "beam_name", ""),
                    "control_point_index": control_point.control_point_index,
                    "gantry_angle_deg": control_point.gantry_angle_deg,
                    "axial_position_mm": control_point.axial_position_mm,
                    "cumulative_meterset_weight": control_point.cumulative_meterset_weight,
                    "dose_rate_mu_per_min": control_point.dose_rate_mu_per_min,
                    "jaw_x1_mm": control_point.jaw_x[0] if len(control_point.jaw_x) >= 1 else None,
                    "jaw_x2_mm": control_point.jaw_x[1] if len(control_point.jaw_x) >= 2 else None,
                    "jaw_y1_mm": control_point.jaw_y[0] if len(control_point.jaw_y) >= 1 else None,
                    "jaw_y2_mm": control_point.jaw_y[1] if len(control_point.jaw_y) >= 2 else None,
                    "delta_gantry_deg": observed_angle_deltas[index - 1] if index > 0 else None,
                    "delta_axial_mm": (
                        control_point.axial_position_mm - previous_cp.axial_position_mm
                        if previous_cp is not None
                        else None
                    ),
                    "delta_cumulative_meterset_weight": (
                        control_point.cumulative_meterset_weight - previous_cp.cumulative_meterset_weight
                        if previous_cp is not None
                        else None
                    ),
                    "aperture_width_mm": _aperture_width_mm(control_point),
                }
                if previous_cp is not None:
                    row.update(
                        {
                            "projection_label": f"{previous_cp.control_point_index}\u2192{control_point.control_point_index}",
                            "projection_pitch": _projection_pitch(
                                row["delta_axial_mm"],
                                row["delta_gantry_deg"],
                            ),
                            "projection_mu_density_proxy": _projection_mu_density_proxy(
                                row["delta_cumulative_meterset_weight"],
                                row["delta_axial_mm"],
                            ),
                            "projection_aperture_change": _projection_aperture_change(previous_cp, control_point),
                            "projection_leaf_travel": _projection_leaf_travel(previous_cp, control_point),
                            "projection_leaf_travel_mlcx1": _projection_leaf_travel_for_layer(
                                previous_cp,
                                control_point,
                                "mlcx1",
                            ),
                            "projection_leaf_travel_mlcx2": _projection_leaf_travel_for_layer(
                                previous_cp,
                                control_point,
                                "mlcx2",
                            ),
                        }
                    )
                rows.append(row)
    return rows


def _metadata_for_result(result: Any) -> Any:
    return getattr(result, "metadata", None) or SimpleNamespace()


def _plan_metrics_for_result(result: Any) -> dict[str, Any]:
    explicit_plan_metrics = getattr(result, "plan_metrics", None)
    if isinstance(explicit_plan_metrics, dict) and explicit_plan_metrics:
        return explicit_plan_metrics

    explicit_metrics = getattr(result, "metrics", None)
    if isinstance(explicit_metrics, dict):
        return explicit_metrics
    if explicit_metrics:
        metric_map: dict[str, Any] = {}
        for metric in explicit_metrics:
            metric_name = getattr(metric, "metric_name", "")
            if metric_name:
                metric_map[metric_name] = getattr(metric, "value", None)
        if metric_map:
            return metric_map

    beams = getattr(result, "beams", []) or []
    return calculate_plan_metrics(beams)


def _beam_metrics_for_export(beam: Any) -> dict[str, Any]:
    explicit_metrics = getattr(beam, "metrics", None)
    if isinstance(explicit_metrics, dict) and explicit_metrics:
        return explicit_metrics
    return calculate_beam_metrics(beam)


def _ordered_metric_values(metrics: dict[str, Any]) -> dict[str, Any]:
    ordered_values = {metric_name: metrics.get(metric_name) for metric_name in FIRST_PASS_METRIC_ORDER}
    for metric_name, value in metrics.items():
        if metric_name not in ordered_values:
            ordered_values[metric_name] = value
    return ordered_values


def write_metric_rows_to_csv(path: str | Path, rows: list[dict[str, Any]]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames: list[str] = []
    for row in rows:
        for fieldname in row:
            if fieldname not in fieldnames:
                fieldnames.append(fieldname)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _aperture_width_mm(control_point: AuroraControlPoint) -> float:
    return sum(
        max(0.0, x2_mm - x1_mm)
        for x1_mm, x2_mm in zip(control_point.mlc_x1_positions_mm, control_point.mlc_x2_positions_mm)
    )


def _projection_rows_for_beam(result: Any, metadata: Any, beam: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    control_points = list(getattr(beam, "control_points", []) or [])
    observed_angle_deltas = calculate_observed_angle_deltas(control_points)
    for interval_index, (previous_cp, control_point) in enumerate(zip(control_points, control_points[1:]), start=1):
        delta_gantry_deg = observed_angle_deltas[interval_index - 1]
        delta_axial_mm = control_point.axial_position_mm - previous_cp.axial_position_mm
        delta_weight = control_point.cumulative_meterset_weight - previous_cp.cumulative_meterset_weight
        rows.append(
            {
                "source_path": getattr(result, "source_path", getattr(metadata, "source_path", "")),
                "plan_label": getattr(metadata, "plan_label", ""),
                "plan_name": getattr(metadata, "plan_name", ""),
                "beam_number": getattr(beam, "beam_number", ""),
                "beam_name": getattr(beam, "beam_name", ""),
                "start_control_point_index": previous_cp.control_point_index,
                "end_control_point_index": control_point.control_point_index,
                "projection_label": f"{previous_cp.control_point_index}\u2192{control_point.control_point_index}",
                "delta_gantry_deg": delta_gantry_deg,
                "delta_axial_mm": delta_axial_mm,
                "delta_cumulative_meterset_weight": delta_weight,
                "projection_pitch": _projection_pitch(delta_axial_mm, delta_gantry_deg),
                "projection_mu_density_proxy": _projection_mu_density_proxy(delta_weight, delta_axial_mm),
                "projection_aperture_change": _projection_aperture_change(previous_cp, control_point),
                "projection_leaf_travel": _projection_leaf_travel(previous_cp, control_point),
                "projection_leaf_travel_mlcx1": _projection_leaf_travel_for_layer(previous_cp, control_point, "mlcx1"),
                "projection_leaf_travel_mlcx2": _projection_leaf_travel_for_layer(previous_cp, control_point, "mlcx2"),
            }
        )
    return rows


def _projection_pitch(delta_axial_mm: float | None, delta_gantry_deg: float | None) -> float | None:
    if delta_axial_mm is None or delta_gantry_deg is None or delta_gantry_deg == 0.0:
        return None
    return abs(delta_axial_mm) / abs(delta_gantry_deg)


def _projection_mu_density_proxy(delta_weight: float | None, delta_axial_mm: float | None) -> float | None:
    if delta_weight is None or delta_axial_mm is None or delta_axial_mm == 0.0:
        return None
    return abs(delta_weight) / abs(delta_axial_mm)


def _projection_aperture_change(previous_cp: AuroraControlPoint, control_point: AuroraControlPoint) -> float | None:
    delta_axial_mm = control_point.axial_position_mm - previous_cp.axial_position_mm
    if delta_axial_mm == 0.0:
        return None
    return abs(_aperture_width_mm(control_point) - _aperture_width_mm(previous_cp)) / abs(delta_axial_mm)


def _projection_leaf_travel(previous_cp: AuroraControlPoint, control_point: AuroraControlPoint) -> float | None:
    x1_value = _projection_leaf_travel_for_layer(previous_cp, control_point, "mlcx1")
    x2_value = _projection_leaf_travel_for_layer(previous_cp, control_point, "mlcx2")
    if x1_value is None or x2_value is None:
        return None
    return x1_value + x2_value


def _projection_leaf_travel_for_layer(
    previous_cp: AuroraControlPoint,
    control_point: AuroraControlPoint,
    layer_name: str,
) -> float | None:
    delta_axial_mm = control_point.axial_position_mm - previous_cp.axial_position_mm
    if delta_axial_mm == 0.0:
        return None
    if layer_name == "mlcx1":
        travel_mm = _leaf_bank_travel_mm(previous_cp.mlc_x1_positions_mm, control_point.mlc_x1_positions_mm)
    elif layer_name == "mlcx2":
        travel_mm = _leaf_bank_travel_mm(previous_cp.mlc_x2_positions_mm, control_point.mlc_x2_positions_mm)
    else:
        raise ValueError(f"Unsupported Aurora MLC layer: {layer_name}")
    return travel_mm / abs(delta_axial_mm)


def _leaf_bank_travel_mm(previous_positions: tuple[float, ...], next_positions: tuple[float, ...]) -> float:
    return sum(abs(next_mm - previous_mm) for previous_mm, next_mm in zip(previous_positions, next_positions))
