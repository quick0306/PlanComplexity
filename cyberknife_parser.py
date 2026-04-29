from __future__ import annotations

from dataclasses import dataclass
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import numpy as np
from pydicom.dataset import Dataset

from ApertureMetric.aperture_geometry import PyAperture


@dataclass(frozen=True)
class CyberKnifeSegment:
    segment_id: str
    aperture: PyAperture
    mu: float


@dataclass(frozen=True)
class CyberKnifeBeam:
    beam_id: str
    latitude_deg: float
    longitude_deg: float
    polar_deg: float
    azimuth_deg: float
    interval_key: Tuple[int, int]
    segments: Tuple[CyberKnifeSegment, ...]

    @property
    def mu(self) -> float:
        return float(sum(segment.mu for segment in self.segments))


def extract_referenced_xml_names(plan_dict: Dict[str, Any]) -> List[str]:
    """Extract referenced CyberKnife beam-path XML names from beam descriptions."""
    xml_names: List[str] = []
    for beam in plan_dict.get("beams", {}).values():
        description = str(beam.get("BeamDescription", "") or "")
        for match in re.findall(r'([^\s<>"\']+\.xml)', description, flags=re.IGNORECASE):
            xml_names.append(os.path.basename(match))
    return xml_names


def resolve_referenced_xml_paths(plan_dict: Dict[str, Any], plan_dir: str) -> Tuple[List[str], List[str]]:
    """Resolve referenced XML names against files present next to the RT Plan."""
    referenced_names = extract_referenced_xml_names(plan_dict)
    available_paths = sorted(Path(plan_dir).glob("*.xml"))
    available_by_name = {path.name.lower(): str(path) for path in available_paths}

    resolved: List[str] = []
    missing: List[str] = []
    seen = set()

    for name in referenced_names:
        key = name.lower()
        resolved_path = available_by_name.get(key)
        if resolved_path is None:
            suffix_matches = [str(path) for path in available_paths if path.name.lower().endswith(key)]
            if len(suffix_matches) == 1:
                resolved_path = suffix_matches[0]

        if resolved_path is None:
            missing.append(name)
            continue

        if resolved_path not in seen:
            resolved.append(resolved_path)
            seen.add(resolved_path)

    return resolved, missing


def build_cyberknife_plan_dict(
    base_plan_dict: Dict[str, Any],
    xml_paths: Sequence[str],
    *,
    machine_name: str,
) -> Dict[str, Any]:
    """Build a synthetic plan dict backed by CyberKnife beam-path XML geometry."""
    synthetic_plan = dict(base_plan_dict)
    beams: Dict[int, Dict[str, Any]] = {}
    total_mu = 0.0

    for beam_number, beam in enumerate(parse_cyberknife_beams(xml_paths, machine_name=machine_name), start=1):
        segment_mus = np.asarray([segment.mu for segment in beam.segments], dtype=float)
        apertures = [segment.aperture for segment in beam.segments]
        control_points = []
        for meterset in segment_mus:
            cp = Dataset()
            cp.GantryAngle = 0.0
            cp.CumulativeMetersetWeight = float(meterset)
            control_points.append(cp)

        plan_beam = {
            "TreatmentMachineName": machine_name,
            "TreatmentDeliveryType": "TREATMENT",
            "BeamDescription": beam.beam_id,
            "BeamType": "STATIC",
            "PrimaryDosimeterUnit": "MU",
            "MU": float(segment_mus.sum()),
            "GantryAngle": 0.0,
            "BeamLimitingDeviceSequence": [],
            "ControlPointSequence": control_points,
            "_cached_apertures": apertures,
            "_cached_cp_metersets": segment_mus,
            "_cached_cumulative_metersets": _build_pairwise_cumulative_weights(segment_mus),
        }
        plan_beam["CyberKnifePolarAngle"] = beam.polar_deg
        plan_beam["CyberKnifeAzimuthAngle"] = beam.azimuth_deg
        plan_beam["CyberKnifeIntervalKey"] = beam.interval_key
        plan_beam["CyberKnifeLatitude"] = beam.latitude_deg
        plan_beam["CyberKnifeLongitude"] = beam.longitude_deg

        beam = plan_beam
        beams[beam_number] = beam
        total_mu += float(beam["MU"])

    if not beams:
        raise ValueError("No usable CyberKnife beam-path XML files were found.")

    synthetic_plan["beams"] = beams
    synthetic_plan["machine_id"] = machine_name
    synthetic_plan["beam_number"] = len(beams)
    synthetic_plan["beam_type"] = "STATIC"
    synthetic_plan["Plan_MU"] = round(total_mu, 2)
    return synthetic_plan


def parse_cyberknife_beams(xml_paths: Sequence[str], *, machine_name: str) -> List[CyberKnifeBeam]:
    beams: List[CyberKnifeBeam] = []
    for xml_path in xml_paths:
        root = ET.parse(xml_path).getroot()
        collimator = root.find("./Header/PlanInfo/Collimator")
        if collimator is None:
            raise ValueError(f"Missing Collimator section in {Path(xml_path).name}.")

        leaf_widths, jaw = _extract_collimator_geometry(collimator)
        beams.extend(_extract_beams(root, leaf_widths, jaw, xml_name=Path(xml_path).name))

    if not beams:
        raise ValueError("No usable CyberKnife beam-path XML files were found.")
    return beams


def _extract_collimator_geometry(collimator: ET.Element) -> Tuple[np.ndarray, List[float]]:
    number_of_leaves = int(collimator.findtext("NumberOfLeaves", default="0"))
    leaf_pairs = max(number_of_leaves // 2, 0)
    if leaf_pairs == 0:
        raise ValueError("CyberKnife beam-path XML does not define any MLC leaf pairs.")

    field_width = float(collimator.findtext("FieldSizeWidth", default="0"))
    x1_closed = float(collimator.findtext("X1DefaultLeafClosedPosition", default="-68.5"))
    x2_closed = float(collimator.findtext("X2DefaultLeafClosedPosition", default="68.5"))

    # The XML provides the full projected MLC span at SAD. We model the CyberKnife MLC
    # as equally spaced leaf pairs across that span so the existing aperture engine can
    # reuse its geometry/perimeter/area logic without a parallel implementation.
    leaf_widths = np.full(leaf_pairs, field_width / leaf_pairs, dtype=float)
    jaw = [x1_closed, field_width / 2.0, x2_closed, -field_width / 2.0]
    return leaf_widths, jaw


def _extract_beams(
    root: ET.Element,
    leaf_widths: np.ndarray,
    jaw: List[float],
    *,
    xml_name: str,
) -> List[CyberKnifeBeam]:
    beams: List[CyberKnifeBeam] = []
    for node in root.findall("./Body/Node"):
        latitude_deg = float(node.findtext("Latitude", default="0"))
        longitude_deg = float(node.findtext("Longitude", default="0"))
        polar_deg, azimuth_deg = _compute_polar_azimuth(node)
        interval_key = _compute_interval_key(polar_deg, azimuth_deg)
        grouped_segments: Dict[str, List[CyberKnifeSegment]] = {}
        for beam in node.findall("./Beam"):
            segment = beam.find("./CollimatorDescription/Segment")
            if segment is None:
                continue
            leaf_positions = _extract_leaf_positions(beam, leaf_pair_count=len(leaf_widths))
            aperture = PyAperture(leaf_positions, leaf_widths, jaw, 0.0)
            dose_mu = float(beam.findtext("Dose_MU", default="0"))
            segment_id = beam.findtext("SegmentDisplayID", default=beam.findtext("BeamNumber", default="0"))
            beam_display_id = beam.findtext("BeamDisplayID", default=beam.findtext("PlanBeamID", default=beam.findtext("BeamNumber", default="0")))
            grouped_segments.setdefault(str(beam_display_id), []).append(
                CyberKnifeSegment(segment_id=str(segment_id), aperture=aperture, mu=dose_mu)
            )

        for beam_display_id, segments in grouped_segments.items():
            beams.append(
                CyberKnifeBeam(
                    beam_id=f"{xml_name}#{beam_display_id}",
                    latitude_deg=latitude_deg,
                    longitude_deg=longitude_deg,
                    polar_deg=polar_deg,
                    azimuth_deg=azimuth_deg,
                    interval_key=interval_key,
                    segments=tuple(segments),
                )
            )
    return beams


def _extract_leaf_positions(beam: ET.Element, *, leaf_pair_count: int) -> np.ndarray:
    segment = beam.find("./CollimatorDescription/Segment")
    if segment is None:
        raise ValueError("Beam segment is missing CollimatorDescription/Segment.")

    banks: Dict[int, Dict[int, float]] = {0: {}, 1: {}}
    for leaf in segment.findall("./Leaf"):
        bank_index = int(leaf.attrib["bankIndex"])
        leaf_index = int(leaf.attrib["leafIndex"])
        banks[bank_index][leaf_index] = float(leaf.text)

    positions = []
    for bank_index in (0, 1):
        bank = banks[bank_index]
        ordered_values = [bank[index] for index in range(leaf_pair_count)]
        positions.append(ordered_values)
    return np.asarray(positions, dtype=float)


def _compute_polar_azimuth(node: ET.Element) -> Tuple[float, float]:
    x = float(node.findtext("x", default="0"))
    y = float(node.findtext("y", default="0"))
    z = float(node.findtext("z", default="0"))
    radius = float(np.sqrt(x ** 2 + y ** 2 + z ** 2))
    if radius == 0.0:
        return 0.0, 0.0

    polar_deg = float(np.degrees(np.arccos(np.clip(y / radius, -1.0, 1.0))))
    azimuth_deg = float((np.degrees(np.arctan2(z, x)) + 360.0) % 180.0)
    return polar_deg, azimuth_deg


def _compute_interval_key(polar_deg: float, azimuth_deg: float) -> Tuple[int, int]:
    polar_bin = min(int(max(polar_deg, 0.0) // 30.0), 3)
    # The supplement states that CK beams were grouped with a 30-degree polar step and
    # a mixed 45/90-degree azimuth step, resulting in 14 intervals. The paper does not
    # enumerate the bins explicitly, so we use the coarsest anterior polar band (0-30 deg)
    # with 90-degree azimuth bins and split the remaining polar bands with 45-degree bins.
    azimuth_step = 90.0 if polar_bin == 0 else 45.0
    azimuth_bin = min(int(max(azimuth_deg, 0.0) // azimuth_step), int(180.0 / azimuth_step) - 1)
    return polar_bin, azimuth_bin


def _build_pairwise_cumulative_weights(segment_mus: np.ndarray) -> np.ndarray:
    if len(segment_mus) == 0:
        return np.array([], dtype=float)
    if len(segment_mus) == 1:
        return np.array([0.0], dtype=float)

    # VMAT-oriented MCS/PM code expects per-aperture MU weights and a second cumulative
    # series for adjacent aperture pairs. For static CK segments, we approximate each
    # adjacent pair with the mean MU of the two segments so the existing pairwise
    # aggregation logic can run without distorting the segment ordering.
    pair_weights = 0.5 * (segment_mus[:-1] + segment_mus[1:])
    cumulative = np.zeros(len(segment_mus), dtype=float)
    cumulative[1:] = np.cumsum(pair_weights)
    return cumulative
