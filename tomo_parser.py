from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pydicom
from pydicom.dataset import Dataset

from tomo_metrics import TomoPlan


@dataclass
class TomoExtractionWarning:
    message: str


def parse_tomo_rtplan(source_path: str) -> Tuple[TomoPlan, List[str]]:
    ds = pydicom.dcmread(source_path, force=True)
    beam = _get_treatment_beam(ds)
    warnings: List[str] = []

    control_points = list(getattr(beam, "ControlPointSequence", []))
    if not control_points:
        raise ValueError("No ControlPointSequence found for Tomo RT Plan.")

    sinogram_rows, rows_are_fractional = _extract_sinogram_rows(control_points)
    if not sinogram_rows:
        raise ValueError("Unable to extract Tomo sinogram rows from the RT Plan.")

    sinogram = np.asarray(sinogram_rows, dtype=float)
    if sinogram.shape[0] > 1 and np.allclose(sinogram[-1], 0):
        sinogram = sinogram[:-1]

    projections_per_rotation = _infer_projections_per_rotation(control_points)
    projection_time_s = _infer_projection_time_s(beam, control_points, projections_per_rotation)
    if projection_time_s <= 0:
        projection_time_s = 0.02
        warnings.append("Projection time could not be inferred from the RT Plan; defaulted to 0.02 s.")

    if not rows_are_fractional:
        sinogram = np.clip(sinogram / projection_time_s, 0.0, 1.0)

    field_width_mm = _infer_field_width_mm(beam, control_points)
    if field_width_mm <= 0:
        field_width_mm = 10.0
        warnings.append("Field width could not be inferred from the RT Plan; defaulted to 10 mm.")

    couch_translation_mm = _infer_couch_translation_mm(control_points, beam, field_width_mm, projections_per_rotation)
    pitch = _infer_pitch(beam, control_points, field_width_mm, couch_translation_mm, projections_per_rotation)
    if pitch <= 0:
        pitch = 0.287
        warnings.append("Pitch could not be inferred from the RT Plan; defaulted to 0.287.")

    fraction_dose_cgy = _infer_fraction_dose_cgy(ds)
    metadata = {
        "patient_id": getattr(ds, "PatientID", ""),
        "patient_name": str(getattr(ds, "PatientName", "")),
        "plan_name": getattr(ds, "RTPlanName", getattr(ds, "RTPlanLabel", "")),
        "plan_label": getattr(ds, "RTPlanLabel", ""),
        "machine_id": getattr(beam, "TreatmentMachineName", ""),
        "beam_type": getattr(beam, "BeamType", ""),
        "beam_number": 1,
        "rotation_direction": getattr(control_points[0], "GantryRotationDirection", ""),
        "prescribed_dose": fraction_dose_cgy,
        "mu": _infer_total_mu(ds, beam),
        "tomo_warning_count": len(warnings),
    }

    return (
        TomoPlan(
            source_path=source_path,
            sinogram=sinogram,
            projection_time_s=projection_time_s,
            projections_per_rotation=projections_per_rotation,
            field_width_mm=field_width_mm,
            pitch=pitch,
            couch_translation_mm=couch_translation_mm,
            fraction_dose_cgy=fraction_dose_cgy,
            metadata=metadata,
        ),
        warnings,
    )


def _get_treatment_beam(ds: Dataset) -> Dataset:
    for beam in getattr(ds, "BeamSequence", []):
        if getattr(beam, "TreatmentDeliveryType", "").upper() != "SETUP":
            return beam
    raise ValueError("No treatment beam found in RT Plan.")


def _extract_sinogram_rows(control_points: Sequence[Dataset]) -> Tuple[List[List[float]], bool]:
    rows = []
    rows_are_fractional = False
    for cp in control_points:
        values = _extract_row_values(cp)
        if values is None:
            continue
        if _looks_fractional(values):
            rows_are_fractional = True
        rows.append(list(values))
    return rows, rows_are_fractional


def _extract_row_values(cp: Dataset) -> Optional[Sequence[float]]:
    for keyword in ("TomotherapeuticLeafOpenDurations",):
        if hasattr(cp, keyword):
            values = getattr(cp, keyword)
            if values is None:
                return None
            return [float(value) for value in values]
    for tag in ((0x300D, 0x10A7),):
        if tag in cp:
            value = cp[tag].value
            if value is None:
                return None
            if isinstance(value, bytes):
                text = value.decode("ascii", errors="ignore").strip("\\ \x00")
                if not text:
                    return []
                return [float(item) for item in text.split("\\") if item != ""]
            return [float(item) for item in value]
    return None


def _to_float(value: object) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _looks_fractional(values: Sequence[float]) -> bool:
    return len(values) > 0 and max(values) <= 1.0 and min(values) >= 0.0


def _infer_projection_time_s(beam: Dataset, control_points: Sequence[Dataset], projections_per_rotation: int) -> float:
    for obj in (beam, control_points[0]):
        for keyword in ("ProjectionTime", "TomotherapeuticProjectionTime"):
            if hasattr(obj, keyword):
                value = _to_float(getattr(obj, keyword))
                if value is not None:
                    return value
    for obj in (beam, control_points[0]):
        for keyword in ("GantryRotationTime", "RevolutionTime"):
            if hasattr(obj, keyword) and projections_per_rotation:
                value = _to_float(getattr(obj, keyword))
                if value is not None:
                    return value / projections_per_rotation
    return 0.0


def _infer_projections_per_rotation(control_points: Sequence[Dataset]) -> int:
    angles = []
    for cp in control_points:
        for keyword in ("SourceRollAngle", "GantryAngle"):
            if hasattr(cp, keyword):
                value = _to_float(getattr(cp, keyword))
                if value is not None:
                    angles.append(value)
                    break
    if len(angles) < 3:
        return len(control_points)
    diffs = []
    for prev, curr in zip(angles, angles[1:]):
        phi = abs(curr - prev) % 360.0
        diffs.append(360.0 - phi if phi > 180.0 else phi)
    median_diff = float(np.median([diff for diff in diffs if diff > 0])) if diffs else 0.0
    if median_diff <= 0:
        return len(control_points)
    return max(int(round(360.0 / median_diff)), 1)


def _infer_field_width_mm(beam: Dataset, control_points: Sequence[Dataset]) -> float:
    for cp in control_points[:1]:
        positions = getattr(cp, "BeamLimitingDevicePositionSequence", [])
        for item in positions:
            if getattr(item, "RTBeamLimitingDeviceType", "") in ("Y", "ASYMY"):
                values = [float(v) for v in item.LeafJawPositions]
                return abs(values[1] - values[0])
    for item in getattr(beam, "BeamLimitingDevicePositionSequence", []):
        if getattr(item, "RTBeamLimitingDeviceType", "") in ("Y", "ASYMY"):
            values = [float(v) for v in item.LeafJawPositions]
            return abs(values[1] - values[0])
    return 0.0


def _infer_couch_translation_mm(control_points: Sequence[Dataset], beam: Dataset, field_width_mm: float, projections_per_rotation: int) -> float:
    positions = []
    for cp in control_points:
        if hasattr(cp, "TableTopLongitudinalPosition"):
            value = _to_float(cp.TableTopLongitudinalPosition)
            if value is not None:
                positions.append(value)
    if len(positions) >= 2:
        return abs(positions[-1] - positions[0])
    pitch = _infer_pitch(beam, control_points, field_width_mm, 0.0, projections_per_rotation)
    if pitch > 0 and projections_per_rotation > 0:
        nrot = max(len(control_points) - 1, 1) / projections_per_rotation
        return nrot * field_width_mm * pitch
    return 0.0


def _infer_pitch(beam: Dataset, control_points: Sequence[Dataset], field_width_mm: float, couch_translation_mm: float, projections_per_rotation: int) -> float:
    for obj in (beam, control_points[0]):
        for keyword in ("Pitch", "HelicalPitchFactor"):
            if hasattr(obj, keyword):
                value = _to_float(getattr(obj, keyword))
                if value is not None:
                    return value
    if field_width_mm > 0 and couch_translation_mm > 0:
        nrot = max(len(control_points) - 1, 1) / projections_per_rotation if projections_per_rotation else 0.0
        delta = couch_translation_mm / nrot if nrot else 0.0
        if delta > 0:
            return delta / field_width_mm
    return 0.0


def _infer_fraction_dose_cgy(ds: Dataset) -> float:
    dose_cgy = 0.0
    for item in getattr(ds, "DoseReferenceSequence", []):
        if hasattr(item, "TargetPrescriptionDose"):
            value = _to_float(item.TargetPrescriptionDose)
            if value is not None:
                dose_cgy = max(dose_cgy, value * 100.0)
    if dose_cgy > 0:
        return dose_cgy

    fg_sequence = getattr(ds, "FractionGroupSequence", [])
    if fg_sequence:
        fg = fg_sequence[0]
        fractions = _to_float(getattr(fg, "NumberOfFractionsPlanned", 0) or 0) or 0.0
        if fractions > 0:
            total = 0.0
            for beam in getattr(fg, "ReferencedBeamSequence", []):
                if hasattr(beam, "BeamDose"):
                    value = _to_float(beam.BeamDose)
                    if value is not None:
                        total += value * 100.0 * fractions
            if total > 0:
                return total / fractions
    return 0.0


def _infer_total_mu(ds: Dataset, beam: Dataset) -> float:
    fg_sequence = getattr(ds, "FractionGroupSequence", [])
    if fg_sequence:
        for ref_beam in getattr(fg_sequence[0], "ReferencedBeamSequence", []):
            if getattr(ref_beam, "ReferencedBeamNumber", None) == getattr(beam, "BeamNumber", None) and hasattr(ref_beam, "BeamMeterset"):
                value = _to_float(ref_beam.BeamMeterset)
                if value is not None:
                    return value
    return 0.0
