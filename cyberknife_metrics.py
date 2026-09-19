from __future__ import annotations

from ComplexityMetric.aperture_shape_metrics import (
    maximum_aperture_area, leaf_sequence_variability,
)

from collections import defaultdict
from typing import Dict, Iterable, List, Sequence, Tuple

from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.edge_metric import EdgeMetric
from ComplexityMetric.plan_irregularity import PlanIrregularity


def calculate_cyberknife_metrics(cyberknife_beams: Sequence[object], *, full_precision: bool = False) -> Dict[str, float]:
    """Calculate the six CyberKnife MLC metrics following Masi et al. (2021)."""
    segments = list(_iter_segments(cyberknife_beams))
    plan_mu = sum(segment.mu for segment in segments)
    if plan_mu <= 0.0:
        return {"mcs": 0.0, "em": 0.0, "pi": 0.0, "pm": 0.0, "lg": 0.0, "sas10": 0.0}

    interval_apertures = _build_interval_apertures(cyberknife_beams)
    interval_union_areas = {
        interval_key: _build_union_area(apertures)
        for interval_key, apertures in interval_apertures.items()
    }

    edge_metric = EdgeMetric()
    irregularity_metric = PlanIrregularity()

    mcs = 0.0
    em = 0.0
    pi = 0.0
    pm = 0.0
    lg = 0.0
    total_small_pairs = 0
    total_open_pairs = 0

    for beam in cyberknife_beams:
        union_area = interval_union_areas.get(beam.interval_key, 0.0)
        weighted_beam_area = 0.0
        for segment in beam.segments:
            aperture = segment.aperture
            segment_mu_weight = segment.mu / plan_mu
            segment_area = aperture.area()

            mcs += segment_mu_weight * _calculate_aav(aperture, union_area) * _calculate_lsv(aperture)
            em += segment_mu_weight * edge_metric.calculate_aperture_edge_metric(aperture)
            pi += segment_mu_weight * irregularity_metric.calculate_aperture_irregularity(aperture)
            lg += segment_mu_weight * _calculate_segment_mean_leaf_gap(aperture)
            weighted_beam_area += segment.mu * segment_area

            small_count, open_count = _count_small_open_leaf_pairs(aperture, threshold_mm=10.0)
            total_small_pairs += small_count
            total_open_pairs += open_count

        beam_mu = beam.mu
        if beam_mu > 0.0 and union_area > 0.0:
            beam_modulation = 1.0 - (weighted_beam_area / (beam_mu * union_area))
            pm += (beam_mu / plan_mu) * beam_modulation

    sas10 = (total_small_pairs / total_open_pairs) if total_open_pairs else 0.0
    return {
        "mcs": float(mcs) if full_precision else round(float(mcs), 2),
        "em": float(em) if full_precision else round(float(em), 2),
        "pi": float(pi) if full_precision else round(float(pi), 2),
        "pm": float(pm) if full_precision else round(float(pm), 2),
        "lg": float(lg) if full_precision else round(float(lg), 2),
        "sas10": float(sas10) if full_precision else round(float(sas10), 2),
    }


def _iter_segments(cyberknife_beams: Sequence[object]) -> Iterable[object]:
    for beam in cyberknife_beams:
        for segment in beam.segments:
            yield segment


def _build_interval_apertures(cyberknife_beams: Sequence[object]) -> Dict[Tuple[int, int], List[PyAperture]]:
    grouped: Dict[Tuple[int, int], List[PyAperture]] = defaultdict(list)
    for beam in cyberknife_beams:
        grouped[beam.interval_key].extend(segment.aperture for segment in beam.segments)
    return grouped


def _build_union_area(apertures: Sequence[PyAperture]) -> float:
    return maximum_aperture_area(apertures)


def _calculate_aav(aperture: PyAperture, union_area: float) -> float:
    if union_area <= 0.0:
        return 0.0
    return aperture.area() / union_area


def _calculate_lsv(aperture: PyAperture) -> float:
    return leaf_sequence_variability(aperture)


def _calculate_segment_mean_leaf_gap(aperture: PyAperture) -> float:
    gaps = [
        leaf_pair.field_size()
        for leaf_pair in aperture.leaf_pairs
        if not leaf_pair.is_outside_jaw() and leaf_pair.field_size() > 0.0
    ]
    if not gaps:
        return 0.0
    return sum(gaps) / len(gaps)


def _count_small_open_leaf_pairs(aperture: PyAperture, *, threshold_mm: float) -> Tuple[int, int]:
    small_count = 0
    open_count = 0
    for leaf_pair in aperture.leaf_pairs:
        if leaf_pair.is_outside_jaw():
            continue
        gap = leaf_pair.field_size()
        if gap <= 0.0:
            continue
        open_count += 1
        if gap < threshold_mm:
            small_count += 1
    return small_count, open_count
