"""Versioned Aurora aperture research descriptors using physical dual-layer strips.

These seven metrics preserve historical names, not the old unit-width surrogate.
MCS is a gap-variability adaptation, not the classic bank-based McNiven MCS.
"""
from bisect import bisect_right
import math

V4_METRIC_ORDER = ('mean_ba', 'mean_bi', 'mean_ca', 'mean_sas5', 'mean_sas10',
                   'mean_mcs_aurora', 'mcs_complexity_aurora')


def _finite(values):
    result = tuple(float(x) for x in values)
    if not all(math.isfinite(x) for x in result):
        raise ValueError('Nonfinite aperture geometry or weights.')
    return result


def _bounds(beam, attr):
    edges = _finite(getattr(beam, attr, ()))
    if len(edges) < 2 or any(b <= a for a, b in zip(edges, edges[1:])):
        raise ValueError('Missing or invalid physical leaf boundaries.')
    return edges


def _jaw(values):
    pair = _finite(values)
    if len(pair) != 2 or pair[0] >= pair[1]:
        raise ValueError('Missing or invalid physical jaws.')
    return pair


def _aperture(cp, e1, e2, grid):
    x, y = _jaw(cp.jaw_x), _jaw(cp.jaw_y)
    layers = []
    for positions, edges in ((cp.mlc_x1_positions_mm, e1), (cp.mlc_x2_positions_mm, e2)):
        positions = _finite(positions)
        n = len(edges) - 1
        if len(positions) != 2 * n:
            raise ValueError('Leaf-position count does not match declared boundaries.')
        layers.append((positions[:n], positions[n:], edges))
    strips = []
    for low, high in zip(grid, grid[1:]):
        bottom, top = max(low, y[0]), min(high, y[1])
        if bottom >= top:
            strips.append((0., 0., 0.))
            continue
        left, right = x
        for bank_a, bank_b, edges in layers:
            idx = bisect_right(edges, (low + high) / 2) - 1
            left, right = max(left, bank_a[idx]), min(right, bank_b[idx])
        strips.append((top - bottom, left, max(left, right)))
    return strips


def _area_perimeter(strips):
    area = sum(h * (r - l) for h, l, r in strips)
    perimeter, previous = 0., None
    for h, left, right in strips:
        current = (left, right) if h > 0 and right > left else None
        perimeter += 2 * h if current else 0
        previous_width = previous[1] - previous[0] if previous else 0
        current_width = right - left if current else 0
        overlap = max(0., min(previous[1], right) - max(previous[0], left)) if previous and current else 0
        perimeter += previous_width + current_width - 2 * overlap
        previous = current
    if previous:
        perimeter += previous[1] - previous[0]
    return area, perimeter


def _samples(beam):
    mu = getattr(beam, 'beam_meterset_mu', None)
    if mu is not None and (not math.isfinite(mu) or mu < 0):
        raise ValueError('Invalid BeamMeterset MU.')
    if mu == 0:
        return [], False
    cps = list(beam.control_points)
    if len(cps) < 2:
        raise ValueError('At least two control points are required.')
    weights = _finite(cp.cumulative_meterset_weight for cp in cps)
    deltas = [b - a for a, b in zip(weights, weights[1:])]
    if weights[0] != 0 or any(d < 0 for d in deltas) or weights[-1] <= 0:
        raise ValueError('Invalid cumulative meterset weights.')
    e1 = _bounds(beam, 'leaf_boundaries_mlcx1')
    e2 = _bounds(beam, 'leaf_boundaries_mlcx2')
    low, high = max(e1[0], e2[0]), min(e1[-1], e2[-1])
    if low >= high:
        raise ValueError('MLC layers have no common physical coverage.')
    grid = sorted({low, high} | {e for e in e1 + e2 if low < e < high})
    apertures = [(_aperture(cp, e1, e2, grid), dw / weights[-1])
                 for cp, dw in zip(cps[1:], deltas) if dw > 0]
    # Per-strip maximum clipped area over positive-weight interval endpoints.
    envelope = sum(max(s[i][0] * (s[i][2] - s[i][1]) for s, _ in apertures)
                   for i in range(len(grid) - 1))
    samples = []
    for strips, relative_weight in apertures:
        area, perimeter = _area_perimeter(strips)
        gaps = [r - l for h, l, r in strips if h > 0 and r > l]
        lsv = (1 - sum(abs(b - a) for a, b in zip(gaps, gaps[1:])) /
               ((len(gaps) - 1) * max(gaps))) if len(gaps) > 1 else 1.
        mcs = area / envelope * max(0., min(1., lsv)) if envelope > 0 else 0.
        samples.append((relative_weight * (mu if mu is not None else 1.), {
            'mean_ba': area,
            'mean_bi': perimeter ** 2 / (4 * math.pi * area) if area > 0 else None,
            'mean_ca': perimeter / area if area > 0 else None,
            'mean_sas5': sum(g < 5 for g in gaps) / len(gaps) if gaps else 0.,
            'mean_sas10': sum(g < 10 for g in gaps) / len(gaps) if gaps else 0.,
            'mean_mcs_aurora': mcs,
            'mcs_complexity_aurora': 1 - mcs,
        }))
    return samples, mu is None


def calculate_v4_metrics_with_warnings(beams):
    missing = dict.fromkeys(V4_METRIC_ORDER)
    samples, relative = [], False
    beams = list(beams)
    # Never mix MU and relative units: when any nonzero beam lacks MU, normalize
    # every contributing beam to unit total weight and disclose the fallback.
    fallback = any(getattr(b, 'beam_meterset_mu', None) is None for b in beams)
    try:
        for beam in beams:
            current, used_relative = _samples(beam)
            if fallback and current:
                total = sum(w for w, _ in current)
                current = [(w / total, values) for w, values in current]
            samples.extend(current)
            relative |= used_relative
    except (ValueError, TypeError, AttributeError, OverflowError) as exc:
        return missing, [f'[AURORA_V4_UNAVAILABLE] {exc}']
    total = sum(w for w, _ in samples)
    if total <= 0:
        return missing, ['[AURORA_V4_UNAVAILABLE] No positive delivered interval weight.']
    result = {key: (sum(w * v[key] for w, v in samples) / total
                    if all(v[key] is not None for _, v in samples) else None)
              for key in V4_METRIC_ORDER}
    messages = ['[AURORA_V4_RELATIVE_WEIGHTS] Missing BeamMeterset; all beams use unit-normalized relative weights.'] if relative else []
    if any(value is None for value in result.values()):
        messages.append('[AURORA_V4_UNDEFINED_SHAPE] Positive-weight closed aperture makes BI and CA undefined.')
    return result, messages
