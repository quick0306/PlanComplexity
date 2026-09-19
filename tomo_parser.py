from typing import List, Optional, Sequence, Tuple

import numpy as np
import pydicom
from pydicom.dataset import Dataset

from formula_versions import TOMO_FORMULA_VERSION
from tomo_metrics import TomoPlan


_TOMO_PRIVATE_CREATOR = "TOMO_HA_01"
_PRIVATE_CREATOR_TAG = (0x300D, 0x0010)
_PRIVATE_SINOGRAM_TAG = (0x300D, 0x10A7)


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
    if sinogram.shape[0] > 1 and np.all(sinogram[-1] == 0):
        sinogram = sinogram[:-1]

    geometry, geometry_source = _infer_plan_geometry(beam, control_points, warnings)
    projections_per_rotation = _infer_projections_per_rotation(control_points)
    projection_time_s = _infer_projection_time_s(beam, control_points, projections_per_rotation)
    timing_known = projection_time_s > 0
    if projection_time_s <= 0:
        if not rows_are_fractional:
            raise ValueError("Projection time is required to normalize Tomo leaf open durations in seconds.")
        projection_time_s = 0.02
        warnings.append("Projection time is unavailable; 0.02 s is assumed for research timing metrics.")

    if not rows_are_fractional:
        sinogram = sinogram / projection_time_s
    if not np.all(np.isfinite(sinogram)) or np.any((sinogram < 0) | (sinogram > 1)):
        raise ValueError("Tomo leaf open fractions must be in [0, 1]; durations cannot exceed the projection interval.")

    field_width_mm = _infer_field_width_mm(beam, control_points)
    field_width_known = bool(np.isfinite(field_width_mm) and field_width_mm > 0)
    if not field_width_known:
        field_width_mm = 10.0
        warnings.append("Field width could not be inferred from the RT Plan; defaulted to 10 mm.")

    motion = _resolve_couch_motion(
        beam, control_points, nproj=sinogram.shape[0],
        projection_time_s=projection_time_s, timing_known=timing_known,
        projections_per_rotation=projections_per_rotation,
        field_width_mm=field_width_mm, field_width_known=field_width_known,
        geometry=geometry, warnings=warnings,
    )

    fraction_dose_cgy = _infer_fraction_dose_cgy(ds)
    if not np.isfinite(fraction_dose_cgy):
        warnings.append("Fraction dose is unavailable: prescription or fraction-group information is missing, invalid, or ambiguous.")
    metadata = {
        "metric_formula_version": TOMO_FORMULA_VERSION,
        "sinogram_input_units": "fraction" if rows_are_fractional else "seconds",
        "tomo_plan_geometry": geometry,
        "tomo_geometry_source": geometry_source,
        "field_width_source": "maximum_inherited_Y_jaw_opening" if field_width_known else "assumed:10_mm",
        **motion["metadata"],
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
            pitch=motion["pitch"],
            couch_translation_mm=motion["translation"],
            planned_couch_speed_mm_s=motion["speed"],
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
    """Read only documented source units, preserving closed private projections.

    Standard (3010,0099) is seconds (DICOM PS3.3 C.36.17). Private
    TOMO_HA_01 (300D,10A7) is 64 fractional opening times (Accuray DCS).
    See docs/tomo_input_contract.md for the evidence and supported scope.
    """
    sources = set()
    for cp in control_points:
        if "TomotherapeuticLeafOpenDurations" in cp:
            sources.add("seconds")
        if _PRIVATE_SINOGRAM_TAG in cp:
            sources.add("fraction")
            if _private_creator(cp) != _TOMO_PRIVATE_CREATOR:
                raise ValueError("Unsupported Tomo private sinogram creator; units cannot be established.")
    if len(sources) > 1:
        raise ValueError("Mixed standard and private Tomo sinogram sources are unsupported.")
    if not sources:
        if not any(_private_creator(cp) == _TOMO_PRIVATE_CREATOR for cp in control_points):
            return [], False
        sources.add("fraction")

    rows_are_fractional = "fraction" in sources
    rows: List[List[float]] = []
    leaf_count = 64 if rows_are_fractional else None
    for index, cp in enumerate(control_points):
        if rows_are_fractional and _private_creator(cp) not in (None, _TOMO_PRIVATE_CREATOR):
            raise ValueError("Unsupported Tomo private sinogram creator; units cannot be established.")
        values = _extract_row_values(cp)
        if values is None or len(values) == 0:
            if rows_are_fractional:
                # The vendor explicitly permits no value for an all-closed
                # projection and the final control point. Keep interior rows.
                values = [0.0] * 64
            elif index == len(control_points) - 1 and leaf_count is not None:
                # Keep a terminal placeholder so the parser removes exactly
                # one sentinel, even if the preceding projection is closed.
                values = [0.0] * leaf_count
            else:
                raise ValueError("Missing or empty standard Tomo duration row within the control-point sequence.")
        if leaf_count is None:
            leaf_count = len(values)
        if len(values) != leaf_count:
            raise ValueError("Inconsistent Tomo leaf count; private sinogram rows must contain 64 leaves.")
        array = np.asarray(values, dtype=float)
        if array.ndim != 1 or not np.all(np.isfinite(array)) or np.any(array < 0):
            raise ValueError("Tomo sinogram values must be finite, nonnegative numbers.")
        if rows_are_fractional and np.any(array > 1):
            raise ValueError("Private Tomo sinogram fractions must be in the range [0, 1].")
        rows.append(list(values))
    return rows, rows_are_fractional


def _private_creator(ds: Dataset) -> Optional[str]:
    element = ds.get(_PRIVATE_CREATOR_TAG)
    return str(element.value).strip() if element is not None else None


def _extract_row_values(cp: Dataset) -> Optional[Sequence[float]]:
    if "TomotherapeuticLeafOpenDurations" in cp:
        value = cp.TomotherapeuticLeafOpenDurations
    elif _PRIVATE_SINOGRAM_TAG in cp:
        value = cp[_PRIVATE_SINOGRAM_TAG].value
    else:
        return None
    if value is None:
        return None
    try:
        if isinstance(value, bytes):
            value = value.decode("ascii")
        if isinstance(value, str):
            value = value.strip(" \x00")
            if not value:
                return []
            value = value.split("\\")
        if np.isscalar(value):
            value = [value]
        return [float(item) for item in value]
    except (TypeError, ValueError, UnicodeError):
        raise ValueError("Tomo sinogram row contains invalid numeric data.") from None


def _to_float(value: object) -> Optional[float]:
    if value is None:
        return None
    try:
        result = float(value)
        return result if np.isfinite(result) else None
    except (TypeError, ValueError):
        return None


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
    # Accuray TOMO_HA_01 Tomo Gantry Period is a rotation duration in seconds.
    if _private_creator(beam) == _TOMO_PRIVATE_CREATOR and (0x300D, 0x1040) in beam and projections_per_rotation:
        value = _to_float(beam[0x300D, 0x1040].value)
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
    positive_diffs = [diff for diff in diffs if diff > 0]
    if not positive_diffs:
        raise ValueError("Tomo rotation geometry is unsupported: no nonzero gantry rotation was found.")
    median_diff = float(np.median(positive_diffs))
    if median_diff <= 0:
        return len(control_points)
    return max(int(round(360.0 / median_diff)), 1)


def _infer_field_width_mm(beam: Dataset, control_points: Sequence[Dataset]) -> float:
    """Nominal TOMO width is the maximum Y opening, including dynamic jaws."""
    width = None
    widths = []
    for index, obj in enumerate([beam, *control_points]):
        for item in getattr(obj, "BeamLimitingDevicePositionSequence", []):
            if getattr(item, "RTBeamLimitingDeviceType", "") not in ("Y", "ASYMY"):
                continue
            try:
                values = [_to_float(value) for value in item.LeafJawPositions]
            except (AttributeError, TypeError):
                return float("nan")
            if len(values) != 2 or any(value is None for value in values):
                return float("nan")
            width = abs(values[1] - values[0])
        if index:
            if width is None:
                return float("nan")
            widths.append(width)
    return max(widths) if widths else float("nan")


def _infer_plan_geometry(beam: Dataset, control_points: Sequence[Dataset], warnings: List[str]) -> Tuple[str, str]:
    """Read the vendor geometry enum without guessing from model names."""
    motion_tags = ((0x300D, 0x1080), (0x300D, 0x1060), (0x300D, 0x10A4))
    if _private_creator(beam) != _TOMO_PRIVATE_CREATOR:
        if any(tag in beam for tag in motion_tags):
            warnings.append("Unrecognized private creator: Tomo private motion fields are ignored.")
    elif (0x300D, 0x10A4) in beam:
        value = beam[0x300D, 0x10A4].value
        try:
            geometry = (value.decode("ascii") if isinstance(value, bytes) else str(value)).strip(" \x00").upper()
        except UnicodeError:
            geometry = "UNKNOWN"
        if geometry == "FIXED_ANGLE":
            raise ValueError("FIXED_ANGLE Tomo plans are unsupported: helical timing and motion assumptions do not apply.")
        if geometry == "HELICAL":
            return geometry, "TOMO_HA_01:(300D,10A4)"
    elif _private_creator(beam) == _TOMO_PRIVATE_CREATOR:
        # Older native exports omit the enum. The vendor documents private
        # pitch/period for helical plans only; corroborate with recorded motion.
        period_element = beam.get((0x300D, 0x1040))
        pitch_element = beam.get((0x300D, 0x1060))
        period = _to_float(period_element.value) if period_element is not None else None
        pitch = _to_float(pitch_element.value) if pitch_element is not None else None
        if period is not None and period > 0 and pitch is not None and pitch > 0 and _rotation_geometry_known(control_points):
            warnings.append("Helical geometry is inferred from native helical pitch, gantry period, and regular rotating control points; the explicit geometry field is absent.")
            return "HELICAL", "inferred:TOMO_HA_01_pitch_and_period_with_regular_gantry_rotation"
    warnings.append("Tomo plan geometry is unavailable; helical pitch and private motion extrapolation are disabled.")
    return "UNKNOWN", "unavailable"


def _private_motion_number(beam: Dataset, element: int, name: str, warnings: List[str]) -> float:
    if _private_creator(beam) != _TOMO_PRIVATE_CREATOR or (0x300D, element) not in beam:
        return float("nan")
    value = _to_float(beam[0x300D, element].value)
    if value is None or value < 0:
        warnings.append(f"Tomo {name} is invalid; a finite nonnegative value is required.")
        return float("nan")
    return value


def _longitudinal_translation(control_points: Sequence[Dataset], nproj: int, warnings: List[str]) -> float:
    """Use inherited standard positions over complete retained intervals."""
    positions = []
    position = None
    for cp in control_points:
        if "TableTopLongitudinalPosition" in cp:
            # An absent attribute inherits. An explicitly empty value is unknown.
            position = _to_float(cp.TableTopLongitudinalPosition)
        positions.append(position)
    if not any(value is not None for value in positions):
        return float("nan")
    if nproj >= len(positions) or any(value is None for value in positions[:nproj + 1]):
        warnings.append("Standard couch motion is unavailable: longitudinal positions do not cover every retained interval.")
        return float("nan")
    trajectory = np.asarray(positions[:nproj + 1], dtype=float)
    steps = np.diff(trajectory)
    if np.any(steps > 0) and np.any(steps < 0):
        warnings.append("Standard couch motion is unavailable: longitudinal positions are not monotonic.")
        return float("nan")
    return float(abs(trajectory[-1] - trajectory[0]))


def _rotation_geometry_known(control_points: Sequence[Dataset]) -> bool:
    angles = []
    angle = None
    for cp in control_points:
        for keyword in ("SourceRollAngle", "GantryAngle"):
            if keyword in cp:
                angle = _to_float(getattr(cp, keyword))
                break
        angles.append(angle)
    if len(angles) < 3 or any(angle is None for angle in angles):
        return False
    increments = np.diff(np.unwrap(np.radians(angles)))
    monotonic = np.all(increments > 0) or np.all(increments < 0)
    return bool(monotonic and np.allclose(increments, np.median(increments), rtol=1e-4, atol=1e-6))


def _resolve_couch_motion(
    beam: Dataset, control_points: Sequence[Dataset], *, nproj: int,
    projection_time_s: float, timing_known: bool, projections_per_rotation: int,
    field_width_mm: float, field_width_known: bool, geometry: str, warnings: List[str],
) -> dict:
    """Resolve planned motion from independent quantities with explicit sources.

    Accuray TOMO_HA_01 (300D,1080) is mm/s; (300D,1060) is advance
    per rotation divided by maximum Y opening. Missing quantities stay NaN.
    """
    helical = geometry == "HELICAL"
    rotation_known = _rotation_geometry_known(control_points)
    direct_projection_time_known = any(
        (_to_float(getattr(obj, keyword, None)) or 0) > 0
        for obj in (beam, control_points[0])
        for keyword in ("ProjectionTime", "TomotherapeuticProjectionTime")
    )
    # Rotation-period / guessed projection-count timing is insufficient for
    # physical motion even when the legacy timing metric remains available.
    timing_known = timing_known and (rotation_known or direct_projection_time_known)
    duration = nproj * projection_time_s if timing_known else float("nan")
    rotations = nproj / projections_per_rotation if rotation_known else float("nan")
    speed = _private_motion_number(beam, 0x1080, "couch speed", warnings)
    pitch = _private_motion_number(beam, 0x1060, "pitch", warnings) if helical else float("nan")
    standard_travel = _longitudinal_translation(control_points, nproj, warnings)
    sources = {"couch_speed_source": "TOMO_HA_01:(300D,1080)" if np.isfinite(speed) else "unavailable",
               "pitch_source": "TOMO_HA_01:(300D,1060)" if np.isfinite(pitch) else "unavailable",
               "couch_translation_source": "unavailable"}
    invalid_supplied = _private_creator(beam) == _TOMO_PRIVATE_CREATOR and (
        ((0x300D, 0x1080) in beam and not np.isfinite(speed))
        or (helical and (0x300D, 0x1060) in beam and not np.isfinite(pitch))
    )
    if invalid_supplied:
        warnings.append("Tomo motion is unavailable because a supplied private motion value is invalid; no replacement is inferred.")
        sources = {key: "unavailable:invalid_private_motion" for key in sources}
        sources["target_length_available"] = False
        sources["target_length_source"] = "unavailable:invalid_private_motion"
        return {"translation": float("nan"), "speed": float("nan"), "pitch": float("nan"), "metadata": sources}
    candidates = []
    if np.isfinite(standard_travel):
        candidates.append((standard_travel, "TableTopLongitudinalPosition:inherited_control_points"))
    if np.isfinite(speed) and timing_known and (helical or np.isfinite(standard_travel)):
        candidates.append((speed * duration, "private_couch_speed_times_retained_duration"))
    if helical and field_width_known and rotation_known and np.isfinite(pitch):
        candidates.append((pitch * field_width_mm * rotations, "private_pitch_times_field_width_times_retained_rotations"))
    if candidates and any(not np.isclose(value, candidates[0][0], rtol=1e-4, atol=1e-3) for value, _ in candidates[1:]):
        warnings.append("Tomo motion sources conflict; couch speed, translation, pitch, and target length are unavailable.")
        sources = {key: "unavailable:conflicting_motion_sources" for key in sources}
        sources["target_length_available"] = False
        sources["target_length_source"] = "unavailable:conflicting_motion_sources"
        return {"translation": float("nan"), "speed": float("nan"), "pitch": float("nan"), "metadata": sources}
    translation = candidates[0][0] if candidates else float("nan")
    if candidates:
        sources["couch_translation_source"] = candidates[0][1]
    if not np.isfinite(speed) and np.isfinite(translation) and timing_known:
        speed = translation / duration
        sources["couch_speed_source"] = "derived:translation_over_retained_duration"
    if not np.isfinite(pitch) and np.isfinite(translation) and helical and field_width_known and rotation_known:
        pitch = translation / (rotations * field_width_mm)
        sources["pitch_source"] = "derived:translation_over_rotations_and_field_width"
    if not np.isfinite(translation):
        warnings.append("Tomo couch motion is unavailable; no complete supported motion source was found.")
    if not np.isfinite(pitch):
        warnings.append("Tomo pitch is unavailable; required helical motion or field-width information is missing.")
    target_available = bool(helical and field_width_known and np.isfinite(translation) and translation >= field_width_mm)
    sources["target_length_available"] = target_available
    sources["target_length_source"] = "helical_translation_minus_field_width" if target_available else "unavailable"
    if not target_available:
        warnings.append("Tomo target length is unavailable; known helical travel must be at least the known field width.")
    return {"translation": translation, "speed": speed, "pitch": pitch, "metadata": sources}


def _infer_fraction_dose_cgy(ds: Dataset) -> float:
    """Return one unambiguous fraction dose in cGy, or NaN when unavailable.

    Course prescriptions require division by the sole fraction group's count.
    BeamDose is already in Gy per fraction (DICOM PS3.3 C.8.8.13).
    """
    groups = list(getattr(ds, "FractionGroupSequence", []))
    if len(groups) != 1:
        return float("nan")
    fg = groups[0]
    fractions = _to_float(getattr(fg, "NumberOfFractionsPlanned", None))
    if fractions is None or fractions <= 0 or not fractions.is_integer():
        return float("nan")

    prescriptions = []
    for item in getattr(ds, "DoseReferenceSequence", []):
        if getattr(item, "DoseReferenceType", "TARGET") != "TARGET":
            continue
        if hasattr(item, "TargetPrescriptionDose"):
            value = _to_float(item.TargetPrescriptionDose)
            if value is None or value <= 0:
                return float("nan")
            prescriptions.append(value)
    if prescriptions:
        if not np.allclose(prescriptions, prescriptions[0], rtol=1e-9, atol=0):
            return float("nan")
        return prescriptions[0] * 100.0 / fractions

    refs = list(getattr(fg, "ReferencedBeamSequence", []))
    if not refs:
        return float("nan")
    beam_doses = [_to_float(getattr(ref, "BeamDose", None)) for ref in refs]
    if any(value is None or value < 0 for value in beam_doses):
        return float("nan")
    total = sum(beam_doses)
    return total * 100.0 if total > 0 else float("nan")


def _infer_total_mu(ds: Dataset, beam: Dataset) -> float:
    fg_sequence = getattr(ds, "FractionGroupSequence", [])
    if fg_sequence:
        for ref_beam in getattr(fg_sequence[0], "ReferencedBeamSequence", []):
            if getattr(ref_beam, "ReferencedBeamNumber", None) == getattr(beam, "BeamNumber", None) and hasattr(ref_beam, "BeamMeterset"):
                value = _to_float(ref_beam.BeamMeterset)
                if value is not None:
                    return value
    return 0.0
