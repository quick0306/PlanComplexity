"""Shared, versioned physical dual-layer geometry for all Aurora aperture metrics.

The one millimeter closure convention is an analysis mask, not a statement
about measured transmission. Geometry is never inferred from zipped layers.
"""
from __future__ import annotations

from bisect import bisect_right
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
import math

CLOSURE_MM = 1.0
GEOMETRY_TOL_MM = 1e-8
SMALL_OPENING_MM = 10.0
NEAR_CLOSED_MM = 2.0
_ERROR_TYPES = (ValueError, TypeError, AttributeError, OverflowError, IndexError)
_cache = ContextVar("aurora_geometry_cache", default=None)


def geometry_scope(function):
    """Reuse geometry only within a calculation, never across mutable inputs."""
    @wraps(function)
    def wrapped(*args, **kwargs):
        if _cache.get() is not None:
            return function(*args, **kwargs)
        token = _cache.set({})
        try:
            return function(*args, **kwargs)
        finally:
            _cache.reset(token)
    return wrapped


def _finite(values):
    result = tuple(float(value) for value in values)
    if not all(math.isfinite(value) for value in result):
        raise ValueError("Nonfinite aperture geometry or weights.")
    return result


def _bounds(beam, attr):
    edges = _finite(getattr(beam, attr, ()))
    if len(edges) < 2 or any(b <= a for a, b in zip(edges, edges[1:])):
        raise ValueError("Missing or invalid physical leaf boundaries.")
    return edges


def _jaw(values):
    pair = _finite(values)
    if len(pair) != 2 or pair[0] >= pair[1]:
        raise ValueError("Missing or invalid physical jaws.")
    return pair


def _layer_intervals(cp, e1, e2):
    layers = []
    for positions, edges in ((cp.mlc_x1_positions_mm, e1),
                             (cp.mlc_x2_positions_mm, e2)):
        positions = _finite(positions)
        n = len(edges) - 1
        if len(positions) != 2 * n:
            raise ValueError("Leaf-position count does not match declared boundaries.")
        layers.append((positions[:n], positions[n:], edges))
    return layers


def _aperture(cp, e1, e2, grid, *, closure_mm=0.0, layer=None):
    """Reconstruct strips. The default unmasked helper supports polygon oracles.

    Production callers explicitly pass CLOSURE_MM for effective and native
    apertures on the same common Y coverage. Each strip retains its actual height.
    """
    x, y = _jaw(cp.jaw_x), _jaw(cp.jaw_y)
    layers = _layer_intervals(cp, e1, e2)
    if layer is not None:
        layers = [layers[layer]]
    strips = []
    for low, high in zip(grid, grid[1:]):
        bottom, top = max(low, y[0]), min(high, y[1])
        if bottom >= top:
            strips.append((0.0, 0.0, 0.0))
            continue
        left, right = x
        for bank_a, bank_b, edges in layers:
            index = bisect_right(edges, (low + high) / 2) - 1
            if not 0 <= index < len(bank_a):
                raise ValueError("Strip lies outside physical layer coverage.")
            left, right = max(left, bank_a[index]), min(right, bank_b[index])
        tolerance = GEOMETRY_TOL_MM if closure_mm > 0 else 0.0
        if right - left <= closure_mm + tolerance:
            right = left
        strips.append((top - bottom, left, right))
    return tuple(strips)


def _area_perimeter(strips):
    """Exact rectangle-union area and exposed boundary, including islands."""
    area = sum(h * (right - left) for h, left, right in strips)
    perimeter, previous = 0.0, None
    for height, left, right in strips:
        current = (left, right) if height > 0 and right > left else None
        perimeter += 2 * height if current else 0
        previous_width = previous[1] - previous[0] if previous else 0
        current_width = right - left if current else 0
        overlap = (max(0.0, min(previous[1], right) - max(previous[0], left))
                   if previous and current else 0.0)
        perimeter += previous_width + current_width - 2 * overlap
        previous = current
    if previous:
        perimeter += previous[1] - previous[0]
    return area, perimeter


@dataclass(frozen=True)
class BeamGeometry:
    control_points: tuple
    strips: tuple
    areas: tuple
    perimeters: tuple
    native_areas: tuple
    relative_weights: tuple
    beam_mu: float | None
    envelope_area: float


def _build_geometry(beam):
    mu = getattr(beam, "beam_meterset_mu", None)
    if mu is None:
        mu = getattr(beam, "total_mu", None)
    if mu is not None:
        mu = float(mu)
        if not math.isfinite(mu) or mu < 0:
            raise ValueError("Invalid BeamMeterset MU.")
    if mu == 0:
        return BeamGeometry((), (), (), (), (), (), mu, 0.0)
    cps = tuple(beam.control_points)
    if len(cps) < 2:
        raise ValueError("At least two control points are required.")
    cmw = _finite(cp.cumulative_meterset_weight for cp in cps)
    deltas = tuple(b - a for a, b in zip(cmw, cmw[1:]))
    if cmw[0] != 0 or any(d < 0 for d in deltas) or cmw[-1] <= 0:
        raise ValueError("Invalid cumulative meterset weights.")
    e1 = _bounds(beam, "leaf_boundaries_mlcx1")
    e2 = _bounds(beam, "leaf_boundaries_mlcx2")
    low, high = max(e1[0], e2[0]), min(e1[-1], e2[-1])
    if low >= high:
        raise ValueError("MLC layers have no common physical coverage.")
    grid = sorted({low, high} | {edge for edge in e1 + e2 if low < edge < high})
    # Include CP0 for area changes; only positive delivered endpoints enter means.
    strips = tuple(_aperture(cp, e1, e2, grid, closure_mm=CLOSURE_MM) for cp in cps)
    area_perimeter = tuple(_area_perimeter(value) for value in strips)
    native = tuple(tuple(sum(h * (r - l) for h, l, r in
                                 _aperture(cp, e1, e2, grid,
                                           closure_mm=CLOSURE_MM, layer=layer))
                         for layer in (0, 1)) for cp in cps)
    delivered = [strips[i + 1] for i, weight in enumerate(deltas) if weight > 0]
    envelope = sum(max(s[j][0] * (s[j][2] - s[j][1]) for s in delivered)
                   for j in range(len(grid) - 1))
    return BeamGeometry(cps, strips, tuple(a for a, _ in area_perimeter),
                        tuple(p for _, p in area_perimeter), native,
                        tuple(d / cmw[-1] for d in deltas), mu, envelope)


def beam_geometry(beam):
    cache = _cache.get()
    key = id(beam)
    if cache is not None and key in cache:
        value = cache[key]
        if isinstance(value, Exception):
            raise ValueError(str(value))
        return value
    try:
        value = _build_geometry(beam)
    except _ERROR_TYPES as exc:
        if cache is not None:
            cache[key] = exc
        raise ValueError(str(exc)) from exc
    if cache is not None:
        cache[key] = value
    return value


def try_beam_geometry(beam):
    try:
        return beam_geometry(beam)
    except ValueError:
        return None


def aperture_area_values(beam):
    geometry = try_beam_geometry(beam)
    return geometry.areas if geometry is not None else None


def aperture_change_values(beam):
    geometry = try_beam_geometry(beam)
    if geometry is None:
        return None
    values = []
    for i, (previous, current) in enumerate(zip(geometry.control_points,
                                              geometry.control_points[1:])):
        distance = abs(current.axial_position_mm - previous.axial_position_mm)
        if distance > 0:
            values.append(abs(geometry.areas[i + 1] - geometry.areas[i]) / distance)
    return values


def _endpoint_metrics(geometry, index):
    strips = geometry.strips[index]
    area, perimeter = geometry.areas[index], geometry.perimeters[index]
    gaps = [r - l for h, l, r in strips if h > 0 and r > l]
    n = len(gaps)
    lsv = (1.0 - sum(abs(b - a) for a, b in zip(gaps, gaps[1:])) /
           ((n - 1) * max(gaps))) if n > 1 else 1.0
    mcs = area / geometry.envelope_area * min(1.0, max(0.0, lsv))
    a1, a2 = geometry.native_areas[index]
    return {
        "mean_ba": area,
        "mean_bi": perimeter ** 2 / (4 * math.pi * area),
        "mean_ca": perimeter / area,
        "mean_sas5": sum(g < 5.0 for g in gaps) / n,
        "mean_sas10": sum(g < SMALL_OPENING_MM for g in gaps) / n,
        "mean_mcs_aurora": mcs,
        "near_closed_fraction": sum(g < NEAR_CLOSED_MM for g in gaps) / n,
        "effective_small_gap_burden": sum(max(0.0, 1.0 - g / SMALL_OPENING_MM)
                                          for g in gaps) / n,
        "x1_x2_aperture_disparity": abs(a1 - a2) / (a1 + a2),
    }


APERTURE_MEAN_KEYS = (
    "mean_ba", "mean_bi", "mean_ca", "mean_sas5", "mean_sas10",
    "mean_mcs_aurora", "mcs_complexity_aurora", "small_opening_fraction",
    "near_closed_fraction", "effective_small_gap_burden", "x1_x2_aperture_disparity",
)


@geometry_scope
def summarize_apertures(beams):
    """All aperture means share the same open mask, endpoints and delivery weights."""
    missing = dict.fromkeys(APERTURE_MEAN_KEYS)
    try:
        geometries = [beam_geometry(beam) for beam in beams]
    except ValueError as exc:
        return missing, [f"[AURORA_V5_UNAVAILABLE] {exc}"]
    fallback = any(g.beam_mu is None for g in geometries)
    samples, closed_count, excluded_weight, total_weight = [], 0, 0.0, 0.0
    for geometry in geometries:
        scale = 1.0 if fallback else geometry.beam_mu
        for i, relative_weight in enumerate(geometry.relative_weights, 1):
            if relative_weight <= 0:
                continue
            weight = relative_weight * scale
            total_weight += weight
            if geometry.areas[i] <= 0:
                closed_count += 1
                excluded_weight += weight
                continue
            samples.append((weight, _endpoint_metrics(geometry, i)))
    warnings = (["[AURORA_V5_RELATIVE_WEIGHTS] Missing BeamMeterset; all beams use "
                 "unit-normalized relative weights."] if fallback else [])
    if closed_count:
        warnings.append("[AURORA_V5_CLOSED_SAMPLES_EXCLUDED] "
                        f"{closed_count} closed endpoint samples excluded from aperture means; "
                        f"excluded weight fraction={excluded_weight / total_weight:.12g}. "
                        "Weights renormalized over open apertures only.")
    if not samples:
        return missing, warnings + ["[AURORA_V5_NO_OPEN_APERTURE] No positive-weight open endpoint aperture."]
    total = sum(w for w, _ in samples)
    result = {key: sum(w * values[key] for w, values in samples) / total
              for key in samples[0][1]}
    result["mcs_complexity_aurora"] = 1.0 - result["mean_mcs_aurora"]
    result["small_opening_fraction"] = result["mean_sas10"]
    return result, warnings
