from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pydicom
from pydicom.dataset import Dataset

from .metrics import calculate_beam_metrics, calculate_plan_metrics
from .models import AuroraAnalysisResult, AuroraBeam, AuroraMetricValue, AuroraPlanMetadata
from .notes import get_metric_notes
from .parser import parse_aurora_rtplan


def analyze_dataset(dataset: Dataset, *, source_path: str = "") -> AuroraAnalysisResult:
    base_metadata = _metadata_from_dataset(dataset, source_path=source_path)
    try:
        result = parse_aurora_rtplan(dataset)
    except ValueError as exc:
        message = str(exc)
        return AuroraAnalysisResult(
            source_path=source_path or base_metadata.source_path,
            metadata=base_metadata,
            supported=False,
            reason=_reason_from_parse_error(message),
            warnings=[message],
        )

    result.source_path = source_path or result.source_path or base_metadata.source_path
    if result.metadata.source_path == "":
        result.metadata.source_path = result.source_path

    if not _has_axial_track(result.beams):
        result.supported = False
        result.reason = "Missing axial trajectory"
        result.warnings.append("Neither standard axial motion nor usable private axial audit values were found.")
        return result

    result.warnings = _collect_result_warnings(result.beams)
    result.beams = [_decorate_beam(beam) for beam in result.beams]
    result.plan_metrics = calculate_plan_metrics(result.beams)
    result.metrics = _metric_records_from_map(result.plan_metrics)
    result.supported = True
    result.reason = ""
    return result


def analyze_plan_file(path: str | Path) -> AuroraAnalysisResult:
    dataset = pydicom.dcmread(str(path), force=True)
    return analyze_dataset(dataset, source_path=str(path))


def analyze_directory(path: str | Path) -> list[AuroraAnalysisResult]:
    directory = Path(path)
    file_paths = sorted(directory.rglob("*.dcm"))
    return [analyze_plan_file(file_path) for file_path in file_paths]


def iter_supported_results(results: Iterable[AuroraAnalysisResult]) -> Iterable[AuroraAnalysisResult]:
    for result in results:
        if result.supported:
            yield result


def _metadata_from_dataset(dataset: Dataset, *, source_path: str) -> AuroraPlanMetadata:
    beams = [
        beam
        for beam in getattr(dataset, "BeamSequence", [])
        if str(getattr(beam, "TreatmentDeliveryType", "")).upper() != "SETUP"
    ]
    first_beam = beams[0] if beams else None
    return AuroraPlanMetadata(
        source_path=source_path,
        plan_label=str(getattr(dataset, "RTPlanLabel", "")),
        plan_name=str(getattr(dataset, "RTPlanName", getattr(dataset, "RTPlanLabel", ""))),
        manufacturer=str(getattr(dataset, "Manufacturer", "")),
        manufacturer_model_name=str(getattr(dataset, "ManufacturerModelName", "")),
        treatment_machine_name=str(getattr(first_beam, "TreatmentMachineName", "")) if first_beam else "",
        patient_id=str(getattr(dataset, "PatientID", "")),
        study_instance_uid=str(getattr(dataset, "StudyInstanceUID", "")),
        series_instance_uid=str(getattr(dataset, "SeriesInstanceUID", "")),
        sop_instance_uid=str(getattr(dataset, "SOPInstanceUID", "")),
        beam_count=len(beams),
    )


def _has_axial_track(beams: list[AuroraBeam]) -> bool:
    for beam in beams:
        axial_values = [round(control_point.axial_position_mm, 6) for control_point in beam.control_points]
        private_values = [
            round(float(control_point.private_wistech_4001_1004.get("value")), 6)
            for control_point in beam.control_points
            if control_point.private_wistech_4001_1004.get("value") is not None
        ]
        if len(set(axial_values)) > 1:
            return True
        if len(set(private_values)) > 1:
            return True
    return False


def _collect_result_warnings(beams: list[AuroraBeam]) -> list[str]:
    warnings: list[str] = []
    for beam in beams:
        warnings.extend(_beam_private_offset_warnings(beam))
    return warnings


def _beam_private_offset_warnings(beam: AuroraBeam) -> list[str]:
    paired_values = [
        control_point.axial_position_mm + float(control_point.private_wistech_4001_1004["value"])
        for control_point in beam.control_points
        if control_point.private_wistech_4001_1004.get("value") is not None
    ]
    if len(paired_values) < 2:
        return []

    offset_range_mm = max(paired_values) - min(paired_values)
    if offset_range_mm > 0.5:
        return [
            f"Beam {beam.beam_name or beam.beam_number}: private axial audit differs from standard isocenter z by up to {offset_range_mm:.3f} mm."
        ]
    return []


def _decorate_beam(beam: AuroraBeam) -> AuroraBeam:
    beam.metrics = calculate_beam_metrics(beam)
    beam.trajectory_summary = {
        "longitudinal_travel_mm": beam.metrics.get("longitudinal_travel_mm"),
        "total_rotation_deg": beam.metrics.get("total_rotation_deg"),
        "travel_per_rotation_mm": beam.metrics.get("travel_per_rotation_mm"),
        "projection_pitch_cv": beam.metrics.get("projection_pitch_cv"),
    }
    beam.warnings = _beam_private_offset_warnings(beam)
    return beam


def _metric_records_from_map(metric_values: dict[str, float | None]) -> list[AuroraMetricValue]:
    notes = get_metric_notes(tuple(metric_values.keys()))
    return [
        AuroraMetricValue(
            metric_name=metric_name,
            value=value,
            description=notes.get(metric_name, ""),
        )
        for metric_name, value in metric_values.items()
    ]


def _reason_from_parse_error(message: str) -> str:
    if "manufacturer/model hints" in message.lower():
        return "Incompatible manufacturer/model hints"
    if "dynamic dual-layer" in message.lower():
        return "Unsupported plan geometry"
    return "Unsupported input"
