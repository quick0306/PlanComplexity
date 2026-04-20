from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pydicom
from pydicom.dataset import Dataset

from .models import AuroraAnalysisResult, AuroraBeam, AuroraControlPoint, AuroraPlanMetadata


WISTECH_PRIVATE_TRACK_TAG = (0x4001, 0x1004)
WISTECH_PRIVATE_START_TAG = (0x4001, 0x1005)


def wrap_angle_delta(current_deg: float, next_deg: float) -> float:
    delta = next_deg - current_deg
    if delta > 180.0:
        delta -= 360.0
    if delta < -180.0:
        delta += 360.0
    return delta


def reconstruct_observed_angle_deltas(beam: AuroraBeam | Iterable[AuroraControlPoint]) -> list[float]:
    control_points = beam.control_points if isinstance(beam, AuroraBeam) else list(beam)
    deltas: list[float] = []
    for current, nxt in zip(control_points, control_points[1:]):
        deltas.append(wrap_angle_delta(current.gantry_angle_deg, nxt.gantry_angle_deg))
    return deltas


def is_aurora_rtplan(source: str | Path | Dataset) -> bool:
    dataset = _load_dataset(source)
    if not _manufacturer_model_hints_compatible(dataset):
        return False
    beams = _get_treatment_beams(dataset)
    if not beams:
        return False
    return all(_beam_is_aurora_candidate(beam) for beam in beams)


def parse_aurora_rtplan(source: str | Path | Dataset) -> AuroraAnalysisResult:
    dataset = _load_dataset(source)
    if not _manufacturer_model_hints_compatible(dataset):
        raise ValueError("Aurora RTPLAN detection failed: manufacturer/model hints are incompatible with Aurora/DeepPlan.")
    beams = _get_treatment_beams(dataset)
    if not beams or not all(_beam_is_aurora_candidate(beam) for beam in beams):
        raise ValueError("Aurora RTPLAN detection failed: expected dynamic dual-layer MLCX1/MLCX2 treatment beams.")

    parsed_beams = [_parse_beam(beam) for beam in beams]
    first_beam = parsed_beams[0] if parsed_beams else AuroraBeam()
    metadata = AuroraPlanMetadata(
        source_path=str(source) if isinstance(source, (str, Path)) else "",
        plan_label=str(getattr(dataset, "RTPlanLabel", "")),
        plan_name=str(getattr(dataset, "RTPlanName", getattr(dataset, "RTPlanLabel", ""))),
        manufacturer=str(getattr(dataset, "Manufacturer", "")),
        manufacturer_model_name=str(getattr(dataset, "ManufacturerModelName", "")),
        treatment_machine_name=first_beam.treatment_machine_name,
        patient_id=str(getattr(dataset, "PatientID", "")),
        study_instance_uid=str(getattr(dataset, "StudyInstanceUID", "")),
        series_instance_uid=str(getattr(dataset, "SeriesInstanceUID", "")),
        sop_instance_uid=str(getattr(dataset, "SOPInstanceUID", "")),
        beam_count=len(parsed_beams),
        notes=_build_detection_notes(dataset),
    )
    return AuroraAnalysisResult(
        source_path=metadata.source_path,
        metadata=metadata,
        beams=parsed_beams,
        warnings=[],
        supported=True,
    )


def _load_dataset(source: str | Path | Dataset) -> Dataset:
    if isinstance(source, Dataset):
        return source
    return pydicom.dcmread(str(source), force=True)


def _get_treatment_beams(dataset: Dataset) -> list[Dataset]:
    beams = list(getattr(dataset, "BeamSequence", []))
    if not beams:
        return []

    return [
        beam
        for beam in beams
        if str(getattr(beam, "TreatmentDeliveryType", "")).upper() != "SETUP"
    ]


def _beam_is_aurora_candidate(beam: Dataset) -> bool:
    control_points = list(getattr(beam, "ControlPointSequence", []))
    if len(control_points) < 2:
        return False
    if not _has_dual_layer_mlc(control_points):
        return False
    return _has_dynamic_control_points(beam, control_points)


def _has_dual_layer_mlc(control_points: list[Dataset]) -> bool:
    for control_point in control_points:
        device_types = {
            str(getattr(item, "RTBeamLimitingDeviceType", "")).upper()
            for item in getattr(control_point, "BeamLimitingDevicePositionSequence", [])
        }
        if "MLCX1" in device_types and "MLCX2" in device_types:
            return True
    return False


def _has_dynamic_control_points(beam: Dataset, control_points: list[Dataset]) -> bool:
    previous_angle: float | None = None
    previous_meterset: float | None = None
    previous_axial: float | None = None
    for control_point in control_points:
        angle = _read_float_attr(control_point, "GantryAngle")
        meterset = _read_float_attr(control_point, "CumulativeMetersetWeight")
        isocenter = _read_float_triplet_attr(control_point, "IsocenterPosition")
        axial = isocenter[2] if isocenter is not None else None
        if previous_angle is not None and angle is not None and wrap_angle_delta(previous_angle, angle) != 0.0:
            return True
        if previous_meterset is not None and meterset is not None and meterset != previous_meterset:
            return True
        if previous_axial is not None and axial is not None and axial != previous_axial:
            return True
        if angle is not None:
            previous_angle = angle
        if meterset is not None:
            previous_meterset = meterset
        if axial is not None:
            previous_axial = axial
    return False


def _manufacturer_model_hints_compatible(dataset: Dataset) -> bool:
    manufacturer = str(getattr(dataset, "Manufacturer", "")).strip().lower()
    model = str(getattr(dataset, "ManufacturerModelName", "")).strip().lower()
    known_manufacturers = {"wisdomtech medical systems", "wisdomtech", "neurt"}
    known_models = {"deepplan", "aurora", "aurora svmat"}

    manufacturer_present = bool(manufacturer)
    model_present = bool(model)

    manufacturer_ok = not manufacturer_present or any(hint in manufacturer for hint in known_manufacturers)
    model_ok = not model_present or model in known_models
    return manufacturer_ok and model_ok


def _build_detection_notes(dataset: Dataset) -> list[str]:
    notes: list[str] = []
    manufacturer = str(getattr(dataset, "Manufacturer", ""))
    model = str(getattr(dataset, "ManufacturerModelName", ""))
    if "wisdomtech" in manufacturer.lower():
        notes.append("Manufacturer hint matches WisdomTech.")
    if model.lower() in {"deepplan", "aurora", "aurora svmat"}:
        notes.append(f"Model hint matches {model}.")
    return notes


def _parse_beam(beam: Dataset) -> AuroraBeam:
    control_points = list(getattr(beam, "ControlPointSequence", []))
    previous_state: dict[str, Any] = {}
    parsed_control_points = [_parse_control_point(control_point, previous_state) for control_point in control_points]
    return AuroraBeam(
        beam_number=int(_read_float_attr(beam, "BeamNumber", default=0.0) or 0),
        beam_name=str(getattr(beam, "BeamName", "")),
        treatment_machine_name=str(getattr(beam, "TreatmentMachineName", "")),
        delivery_type=str(getattr(beam, "TreatmentDeliveryType", "")),
        control_points=parsed_control_points,
    )


def _parse_control_point(control_point: Dataset, previous_state: dict[str, Any]) -> AuroraControlPoint:
    device_positions = _extract_device_positions(control_point, previous_state)
    isocenter_position = _read_float_triplet_attr(control_point, "IsocenterPosition")
    if isocenter_position is None:
        isocenter_position = previous_state.get("isocenter_position_mm", (0.0, 0.0, 0.0))

    private_1004 = _extract_private_scalar(control_point, WISTECH_PRIVATE_TRACK_TAG)
    if private_1004:
        previous_state["private_wistech_4001_1004"] = private_1004
    else:
        private_1004 = previous_state.get("private_wistech_4001_1004", {})

    private_1005 = _extract_private_vector(control_point, WISTECH_PRIVATE_START_TAG)
    if private_1005:
        previous_state["private_wistech_4001_1005"] = private_1005
    else:
        private_1005 = previous_state.get("private_wistech_4001_1005", {})

    aurora_control_point = AuroraControlPoint(
        control_point_index=int(_read_float_attr(control_point, "ControlPointIndex", default=0.0) or 0),
        gantry_angle_deg=_read_float_attr(
            control_point,
            "GantryAngle",
            default=previous_state.get("gantry_angle_deg", 0.0),
        )
        or 0.0,
        dose_rate_mu_per_min=_read_float_attr(
            control_point,
            "DoseRateSet",
            default=previous_state.get("dose_rate_mu_per_min", 0.0),
        )
        or 0.0,
        cumulative_meterset_weight=_read_float_attr(
            control_point,
            "CumulativeMetersetWeight",
            default=previous_state.get("cumulative_meterset_weight", 0.0),
        )
        or 0.0,
        isocenter_position_mm=isocenter_position,
        axial_position_mm=isocenter_position[2],
        jaw_x=device_positions["jaw_x"],
        jaw_y=device_positions["jaw_y"],
        mlc_x1_positions_mm=device_positions["mlc_x1_positions_mm"],
        mlc_x2_positions_mm=device_positions["mlc_x2_positions_mm"],
        private_wistech_4001_1004=private_1004,
        private_wistech_4001_1005=private_1005,
    )

    previous_state.update(
        {
            "gantry_angle_deg": aurora_control_point.gantry_angle_deg,
            "dose_rate_mu_per_min": aurora_control_point.dose_rate_mu_per_min,
            "cumulative_meterset_weight": aurora_control_point.cumulative_meterset_weight,
            "isocenter_position_mm": aurora_control_point.isocenter_position_mm,
        }
    )
    return aurora_control_point


def _extract_device_positions(control_point: Dataset, previous_state: dict[str, Any]) -> dict[str, tuple[float, ...]]:
    positions = {
        "jaw_x": previous_state.get("jaw_x", (0.0, 0.0)),
        "jaw_y": previous_state.get("jaw_y", (0.0, 0.0)),
        "mlc_x1_positions_mm": previous_state.get("mlc_x1_positions_mm", ()),
        "mlc_x2_positions_mm": previous_state.get("mlc_x2_positions_mm", ()),
    }
    for item in getattr(control_point, "BeamLimitingDevicePositionSequence", []):
        device_type = str(getattr(item, "RTBeamLimitingDeviceType", "")).upper()
        values = _to_float_tuple(getattr(item, "LeafJawPositions", []))
        if device_type == "ASYMX" and len(values) >= 2:
            positions["jaw_x"] = values[:2]
        elif device_type == "ASYMY" and len(values) >= 2:
            positions["jaw_y"] = values[:2]
        elif device_type == "MLCX1":
            positions["mlc_x1_positions_mm"] = values
        elif device_type == "MLCX2":
            positions["mlc_x2_positions_mm"] = values
    previous_state.update(positions)
    return positions


def _extract_private_scalar(control_point: Dataset, tag: tuple[int, int]) -> dict[str, Any]:
    if tag not in control_point:
        return {}
    raw_value = control_point[tag].value
    return {
        "tag": f"({tag[0]:04X},{tag[1]:04X})",
        "value": _to_float(raw_value),
        "raw": str(raw_value),
    }


def _extract_private_vector(control_point: Dataset, tag: tuple[int, int]) -> dict[str, Any]:
    if tag not in control_point:
        return {}
    raw_value = control_point[tag].value
    values = _to_float_tuple(raw_value)
    return {
        "tag": f"({tag[0]:04X},{tag[1]:04X})",
        "values": values,
        "raw": tuple(str(value) for value in raw_value) if isinstance(raw_value, Iterable) and not isinstance(raw_value, (str, bytes)) else (str(raw_value),),
    }


def _read_float_attr(dataset: Dataset, attribute: str, default: float | None = None) -> float | None:
    if not hasattr(dataset, attribute):
        return default
    return _to_float(getattr(dataset, attribute))


def _read_float_triplet_attr(dataset: Dataset, attribute: str) -> tuple[float, float, float] | None:
    if not hasattr(dataset, attribute):
        return None
    values = _to_float_tuple(getattr(dataset, attribute))
    if len(values) < 3:
        return None
    return values[:3]


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_float_tuple(values: Any) -> tuple[float, ...]:
    if values is None:
        return ()
    if isinstance(values, (str, bytes)):
        parts = str(values).split("\\")
        try:
            return tuple(float(part) for part in parts if part != "")
        except ValueError:
            return ()
    try:
        return tuple(float(value) for value in values)
    except (TypeError, ValueError):
        scalar = _to_float(values)
        return () if scalar is None else (scalar,)
