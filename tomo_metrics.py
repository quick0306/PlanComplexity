from dataclasses import dataclass, field
from statistics import StatisticsError, mode
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
from scipy import stats


@dataclass
class TomoPlan:
    source_path: str
    sinogram: np.ndarray
    projection_time_s: float
    projections_per_rotation: int
    field_width_mm: float
    pitch: float
    couch_translation_mm: float
    fraction_dose_cgy: float
    metadata: Dict[str, object] = field(default_factory=dict)

    @property
    def mask(self) -> np.ndarray:
        return (self.sinogram > 0).astype(int)

    @property
    def lot_ms(self) -> np.ndarray:
        return self.sinogram[self.sinogram > 0] * self.projection_time_s * 1000.0

    @property
    def flot(self) -> np.ndarray:
        return self.sinogram[self.sinogram > 0]

    @property
    def nproj(self) -> int:
        return int(self.sinogram.shape[0])

    @property
    def nleaves(self) -> int:
        return int(self.sinogram.shape[1])

    @property
    def nrot(self) -> float:
        if not self.projections_per_rotation:
            return 0.0
        return self.nproj / self.projections_per_rotation

    @property
    def gantry_period_s(self) -> float:
        return self.projection_time_s * self.projections_per_rotation

    @property
    def treatment_time_s(self) -> float:
        return self.projection_time_s * self.nproj

    @property
    def couch_speed_mm_s(self) -> float:
        return self.couch_translation_mm / self.treatment_time_s if self.treatment_time_s else 0.0

    @property
    def target_length_mm(self) -> float:
        return self.couch_translation_mm - self.field_width_mm

    @property
    def leaf_positions(self) -> np.ndarray:
        center = (self.nleaves - 1) / 2.0
        return np.arange(self.nleaves, dtype=float) - center


def calculate_tomo_metrics(plan: TomoPlan) -> Dict[str, float]:
    metrics: Dict[str, float] = {}
    metrics.update(_delivery_metrics(plan))
    metrics.update(_lot_statistics(plan))
    metrics.update(_flot_statistics(plan))
    metrics.update(_geometry_metrics(plan))
    metrics.update(_modulation_metrics(plan))
    return metrics


def _delivery_metrics(plan: TomoPlan) -> Dict[str, float]:
    mf = _safe_divide(_nonzero_mean(plan.lot_ms), _safe_max(plan.lot_ms))
    ttdf = _safe_divide(plan.treatment_time_s, plan.fraction_dose_cgy)
    return {
        "mf": mf,
        "nproj_rot": float(plan.projections_per_rotation),
        "nproj": float(plan.nproj),
        "nrot": float(plan.nrot),
        "projection_time_s": float(plan.projection_time_s),
        "gantry_period_s": float(plan.gantry_period_s),
        "treatment_time_s": float(plan.treatment_time_s),
        "field_width_mm": float(plan.field_width_mm),
        "pitch": float(plan.pitch),
        "couch_translation_mm": float(plan.couch_translation_mm),
        "couch_speed_mm_s": float(plan.couch_speed_mm_s),
        "target_length_mm": float(plan.target_length_mm),
        "ttdf_s_cgy": float(ttdf),
    }


def _lot_statistics(plan: TomoPlan) -> Dict[str, float]:
    values = plan.lot_ms
    result = {
        "mlot": _nonzero_mean(values),
        "sdlot": _nonzero_std(values),
        "mdlot": _nonzero_median(values),
        "molot": _nonzero_mode(values),
        "maxlot": _safe_max(values),
        "minlot": _safe_min(values),
        "klot": _safe_stat(lambda x: stats.kurtosis(x, bias=False), values),
        "slot": _safe_stat(lambda x: stats.skew(x, bias=False), values),
    }
    for threshold in (10, 20, 30, 50):
        result[f"clns_{threshold}ms"] = _fraction(values < threshold, values.size)
        result[f"clns_pt_{threshold}ms"] = _fraction(values > (plan.projection_time_s * 1000.0 - threshold), values.size)
    return result


def _flot_statistics(plan: TomoPlan) -> Dict[str, float]:
    values = plan.flot
    result = {
        "mflot": _nonzero_mean(values),
        "sdflot": _nonzero_std(values),
        "mdflot": _nonzero_median(values),
        "moflot": _nonzero_mode(values),
        "maxflot": _safe_max(values),
        "minflot": _safe_min(values),
    }
    for threshold in (0.1, 0.25, 0.5, 0.75):
        key = str(threshold).replace(".", "_")
        result[f"cfns_{key}"] = _fraction(values < threshold, values.size)
    return result


def _geometry_metrics(plan: TomoPlan) -> Dict[str, float]:
    mask = plan.mask
    ncc_values = np.array([len(_connected_components(row)) for row in mask], dtype=float)
    ta_values = np.array([_treatment_area(row) for row in mask], dtype=float)
    result = {
        "ta": float(np.mean(ta_values)) if ta_values.size else 0.0,
        "ncc": float(np.mean(ncc_values)) if ncc_values.size else 0.0,
        "lengthcc": _average_component_length(mask),
        "fdisc": _fraction(ncc_values > 1, len(ncc_values)),
        "cls": float(np.mean((plan.nleaves - np.sum(mask, axis=1)) / plan.nleaves)) if plan.nproj else 0.0,
        "clsin": _cls_in(mask, normalize_by_area=False, discontinuous_only=False),
        "clsinarea": _cls_in(mask, normalize_by_area=True, discontinuous_only=False),
        "clsindisc": _cls_in(mask, normalize_by_area=False, discontinuous_only=True),
        "clsinareadisc": _cls_in(mask, normalize_by_area=True, discontinuous_only=True),
        "centroid": _centroid(mask, plan.leaf_positions),
    }
    for neighbours in (0, 1, 2):
        result[f"l{neighbours}ns"] = _lnns(mask, neighbours)
    return result


def _modulation_metrics(plan: TomoPlan) -> Dict[str, float]:
    sinogram = plan.sinogram
    result = {
        "lotv": _lotv(sinogram),
        "elotv_1": _elotv(sinogram, 1),
        "elotv_5": _elotv(sinogram, 5),
        "pstv": _epstv(sinogram, 1, 1),
        "epstv_1_1": _epstv(sinogram, 1, 1),
        "epstv_1_0": _epstv(sinogram, 1, 0),
        "epstv_0_1": _epstv(sinogram, 0, 1),
        "mi": _tomo_mi(sinogram),
        "noc": _number_of_openings_and_closures(sinogram),
        "msa": _mean_sinogram_asymmetry(sinogram, plan.leaf_positions),
    }
    lps = np.sum(sinogram, axis=0) / plan.nproj if plan.nproj else np.zeros(plan.nleaves)
    result["msi"] = float(np.mean(lps)) if lps.size else 0.0
    result["mdsi"] = float(np.median(lps)) if lps.size else 0.0
    result["sdsi"] = float(np.std(lps, ddof=1)) if lps.size > 1 else 0.0
    return result


def _connected_components(row: Sequence[int]) -> List[Tuple[int, int]]:
    components: List[Tuple[int, int]] = []
    start = None
    for idx, value in enumerate(row):
        if value and start is None:
            start = idx
        if not value and start is not None:
            components.append((start, idx - 1))
            start = None
    if start is not None:
        components.append((start, len(row) - 1))
    return components


def _treatment_area(row: Sequence[int]) -> float:
    open_idx = np.where(np.asarray(row) > 0)[0]
    if open_idx.size == 0:
        return 0.0
    return float((open_idx[-1] - open_idx[0]) + 1)


def _average_component_length(mask: np.ndarray) -> float:
    lengths = []
    for row in mask:
        for left, right in _connected_components(row):
            lengths.append((right - left) + 1)
    return float(np.mean(lengths)) if lengths else 0.0


def _cls_in(mask: np.ndarray, *, normalize_by_area: bool, discontinuous_only: bool) -> float:
    values = []
    for row in mask:
        area = _treatment_area(row)
        if area == 0:
            continue
        components = _connected_components(row)
        if discontinuous_only and len(components) <= 1:
            continue
        closed_inside = area - np.sum(row)
        denominator = area if normalize_by_area else len(row)
        values.append(closed_inside / denominator if denominator else 0.0)
    return float(np.mean(values)) if values else 0.0


def _centroid(mask: np.ndarray, positions: np.ndarray) -> float:
    centroids = []
    for row in mask:
        open_count = np.sum(row)
        if open_count == 0:
            continue
        centroids.append(float(np.sum(row * positions) / open_count))
    return float(np.mean(centroids)) if centroids else 0.0


def _lnns(mask: np.ndarray, neighbours: int) -> float:
    values = []
    for row in mask:
        open_indices = np.where(row > 0)[0]
        if open_indices.size == 0:
            continue
        count = 0
        for idx in open_indices:
            left = 1 if idx > 0 and row[idx - 1] > 0 else 0
            right = 1 if idx < len(row) - 1 and row[idx + 1] > 0 else 0
            if left + right == neighbours:
                count += 1
        values.append(count / open_indices.size)
    return float(np.mean(values)) if values else 0.0


def _lotv(sinogram: np.ndarray) -> float:
    values = []
    for column in sinogram.T:
        maximum = np.max(column)
        if maximum <= 0:
            values.append(1.0)
            continue
        diffs = np.abs(np.diff(column))
        values.append(float(np.sum(maximum - diffs) / ((len(column) - 1) * maximum)))
    return float(np.mean(values)) if values else 0.0


def _elotv(sinogram: np.ndarray, delta_p: int) -> float:
    if sinogram.shape[0] <= delta_p:
        return 0.0
    values = []
    for column in sinogram.T:
        maximum = np.max(column)
        if maximum <= 0:
            values.append(0.0)
            continue
        diffs = np.abs(column[:-delta_p] - column[delta_p:])
        values.append(float(np.sum(diffs) / ((len(column) - delta_p) * maximum)))
    return float(np.mean(values)) if values else 0.0


def _epstv(sinogram: np.ndarray, delta_p: int, delta_l: int) -> float:
    if sinogram.size == 0:
        return 0.0
    values = []
    max_i = sinogram.shape[0] - delta_p
    max_j = sinogram.shape[1] - delta_l
    if max_i <= 0 or max_j <= 0:
        return 0.0
    for i in range(max_i):
        for j in range(max_j):
            value = 0.0
            if delta_p > 0:
                value += abs(float(sinogram[i + delta_p, j] - sinogram[i, j]))
            if delta_l > 0:
                value += abs(float(sinogram[i, j + delta_l] - sinogram[i, j]))
            values.append(value)
    return float(np.mean(values)) if values else 0.0


def _tomo_mi(sinogram: np.ndarray) -> float:
    sdflot = float(np.std(sinogram[sinogram > 0], ddof=1)) if np.count_nonzero(sinogram) > 1 else 0.0
    if sdflot == 0:
        return 0.0

    diffs = {
        "x": np.abs(np.diff(sinogram, axis=1)),
        "y": np.abs(np.diff(sinogram, axis=0)),
        "xy": np.abs(sinogram[1:, 1:] - sinogram[:-1, :-1]),
        "yx": np.abs(sinogram[1:, :-1] - sinogram[:-1, 1:]),
    }
    grid = np.linspace(0.0, 2.0, 201)
    z_values = []
    for f in grid:
        threshold = f * sdflot
        directional = []
        for values in diffs.values():
            if values.size == 0:
                directional.append(0.0)
            else:
                directional.append(float(np.count_nonzero(values > threshold) / values.size))
        z_values.append(float(np.mean(directional)))
    return float(np.trapezoid(z_values, grid))


def _number_of_openings_and_closures(sinogram: np.ndarray) -> float:
    if sinogram.size == 0:
        return 0.0
    events_per_leaf = []
    centers = np.arange(sinogram.shape[0], dtype=float) + 0.5
    for column in sinogram.T:
        intervals = []
        for center, value in zip(centers, column):
            if value <= 0:
                continue
            half = value / 2.0
            intervals.append((center - half, center + half))
        if not intervals:
            events_per_leaf.append(0.0)
            continue
        merged = []
        start, end = intervals[0]
        for next_start, next_end in intervals[1:]:
            if next_start <= end:
                end = max(end, next_end)
            else:
                merged.append((start, end))
                start, end = next_start, next_end
        merged.append((start, end))
        events_per_leaf.append((2 * len(merged)) / sinogram.shape[0])
    return float(np.mean(events_per_leaf)) if events_per_leaf else 0.0


def _mean_sinogram_asymmetry(sinogram: np.ndarray, positions: np.ndarray) -> float:
    lps = np.sum(sinogram, axis=0) / sinogram.shape[0] if sinogram.shape[0] else np.zeros(sinogram.shape[1])
    denominator = np.sum(lps)
    if denominator == 0:
        return 0.0
    return float(np.sum(positions * lps) / denominator)


def _nonzero_mean(values: np.ndarray) -> float:
    return float(np.mean(values)) if values.size else 0.0


def _nonzero_std(values: np.ndarray) -> float:
    return float(np.std(values, ddof=1)) if values.size > 1 else 0.0


def _nonzero_median(values: np.ndarray) -> float:
    return float(np.median(values)) if values.size else 0.0


def _nonzero_mode(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    try:
        return float(mode(np.round(values, 6)))
    except StatisticsError:
        return float(np.round(values[0], 6))


def _safe_stat(func, values: np.ndarray) -> float:
    if values.size < 2:
        return 0.0
    result = func(values)
    if np.isnan(result):
        return 0.0
    return float(result)


def _safe_max(values: np.ndarray) -> float:
    return float(np.max(values)) if values.size else 0.0


def _safe_min(values: np.ndarray) -> float:
    return float(np.min(values)) if values.size else 0.0


def _safe_divide(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _fraction(mask_or_values: Iterable[bool], denominator: int) -> float:
    return float(np.count_nonzero(mask_or_values) / denominator) if denominator else 0.0
