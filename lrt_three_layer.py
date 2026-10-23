"""Strict, versioned three-layer geometry path alongside unchanged legacy outputs.

All layers share reconstruction, CP weights and metric kernels. The bounded PR
extension uses actual 5/10 mm strip heights; it is a geometric descriptor, not
a measurement of layer-specific dosimetric penumbra. See docs/lrt_three_layer.md.
"""
from __future__ import annotations

import math
import numpy as np

from ethos_report_metrics import CLOSURE_MM, GEOMETRY_TOL_MM, TIP_MM, SIDE_MM, supported_beam_layout
from halcyon_dual_layer_metrics import (
    _build_layer_control_points, _hybrid_representation_values, _beam_pm,
    _aperture_irregularity, _is_dual_layer_plan,
)
from lrt_metric_schema import BASE_METRICS, GEOMETRY_KEYS, EXPORT_KEYS


def centered_weights(cumulative):
    """Validate raw CMW before any normalization; do not use mutable MU caches."""
    mu = np.asarray(cumulative, dtype=float)
    if (mu.ndim != 1 or len(mu) < 2 or not np.all(np.isfinite(mu)) or
            mu[0] != 0 or np.any(np.diff(mu) < 0) or mu[-1] <= 0):
        raise ValueError('Finite nondecreasing CMW starting at zero and ending positive is required')
    delta = np.diff(mu)
    return (np.r_[0., delta] + np.r_[delta, 0.]) / 2, delta


def finite_strip_pr(aperture):
    """CP aperture fraction in finite tip/side strips; None for unsupported rows.

    For row j (height h_j), K_j=[l_j+t,r_j-t] if nonempty. Protected core:
      C=sum_j (h_j-2s)|K_j| + s|K_j intersect O_(j-1)|
                                  + s|K_j intersect O_(j+1)|.
    O_j is empty for gaps <=0.5 mm. Missing/non-touching neighbors protect no
    side. This is the original 5 mm formula generalized to h_j >= 2s.
    Jaw-clipped partial rows below 2s are rejected, never approximated.
    """
    rows = []
    for p in aperture.leaf_pairs:
        h = float(p.open_leaf_width())
        if h <= 0:
            continue
        l, r = max(float(p.left), p.jaw.left), min(float(p.right), p.jaw.right)
        bottom, top = max(p.bottom, p.jaw.bottom), min(p.top, p.jaw.top)
        if not np.all(np.isfinite([h, l, r, bottom, top])) or h < 2 * SIDE_MM - GEOMETRY_TOL_MM:
            return None
        if r-l <= CLOSURE_MM + GEOMETRY_TOL_MM:
            r = l
        rows.append((l, r, h, bottom, top))
    area = sum((r-l)*h for l, r, h, _, _ in rows)
    if area <= 0:
        return 0.0
    core = 0.0
    for j, (l, r, h, bottom, top) in enumerate(rows):
        if r-l <= 2*TIP_MM:
            continue
        core += (h-2*SIDE_MM)*(r-l-2*TIP_MM)
        for k in (j-1, j+1):
            if not 0 <= k < len(rows):
                continue
            nl, nr, _, nb, nt = rows[k]
            if abs(top-nb) <= GEOMETRY_TOL_MM or abs(bottom-nt) <= GEOMETRY_TOL_MM:
                core += SIDE_MM * max(0., min(r-TIP_MM, nr)-max(l+TIP_MM, nl))
    return float(np.clip(1-core/area, 0., 1.))


def _validate_beam(beam):
    if beam.get('TreatmentDeliveryType') != 'TREATMENT':
        raise ValueError('Only treatment beams are eligible')
    mu = float(beam['MU'])
    if not math.isfinite(mu) or mu <= 0 or beam.get('PrimaryDosimeterUnit') != 'MU':
        raise ValueError('Positive finite treatment MU is required')
    if not supported_beam_layout(beam):
        raise ValueError('Only established standard 28/29 pair, 5 mm staggered layout is supported')
    cps = beam['ControlPointSequence']
    indices = [getattr(cp, 'ControlPointIndex', None) for cp in cps]
    if any(x is not None for x in indices) and indices != list(range(len(cps))):
        raise ValueError('ControlPointIndex must be complete and ordered 0..N-1; input is not silently sorted')
    return centered_weights([getattr(cp, 'CumulativeMetersetWeight', np.nan) for cp in cps])


def calculate_lrt_beam_metrics(beam, *, pr_system=None):
    """Return 51 fields and warnings. System value is only explicitly supplied.

    No single-layer averaging and no automatic System-to-Eff replacement occur.
    Invalid geometry/weights invalidate all canonical fields, with a reason.
    """
    empty = dict.fromkeys(EXPORT_KEYS)
    try:
        cp_mu, interval_mu = _validate_beam(beam)
        snapshots = _build_layer_control_points(beam)
        if len(snapshots) != len(cp_mu):
            raise ValueError('Incomplete inherited leaf-position series')
        values, warnings = {}, []
        for suffix, attr in [('Eff', 'effective_aperture'), ('D', 'distal_aperture'), ('P', 'proximal_aperture')]:
            aps = [getattr(s, attr) for s in snapshots]
            # The same existing kernel is used at all three levels.
            base, messages = _hybrid_representation_values(aps, cp_mu, interval_mu, 'lrt')
            warnings.extend(messages)
            values.update({f'{name}_{suffix}': base[f'{old}_lrt'] for name, old in BASE_METRICS.items()})
            values[f'PI_{suffix}'] = float(np.average([_aperture_irregularity(a) for a in aps], weights=cp_mu))
            values[f'PM_{suffix}'] = _beam_pm(aps, cp_mu)
            pr = [finite_strip_pr(a) for a in aps]
            # Entirely closed beams follow the bounded report convention.
            has_report_opening = any(
                min(p.right, p.jaw.right)-max(p.left, p.jaw.left) > CLOSURE_MM + GEOMETRY_TOL_MM
                and p.open_leaf_width() > 0 for a in aps for p in a.leaf_pairs
            )
            if any(x is None for x in pr) or not has_report_opening:
                values[f'PR_{suffix}'] = None
                warnings.append(f'[LRT_PR_UNAVAILABLE] {suffix}: closed beam or row height below 4.6 mm')
            else:
                values[f'PR_{suffix}'] = float(np.average(pr, weights=cp_mu))
        values['MU'] = float(beam['MU'])
        values['MU_per_CP'] = float(beam['MU'])/len(cp_mu)
        values['PR_System'] = pr_system
        return values, list(dict.fromkeys(warnings))
    except (ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        return empty, [f'[LRT_UNAVAILABLE] {exc}']


def calculate_lrt_plan_metrics(plan, *, pr_system=None, full_precision=True):
    """Strict common beam eligibility and MU aggregation; no partial plan mean."""
    if not _is_dual_layer_plan(plan):
        return {}, []
    results, warnings = [], []
    for beam in plan.get('beams', {}).values():
        if beam.get('TreatmentDeliveryType') != 'TREATMENT':
            continue
        try:
            if float(beam.get('MU', np.nan)) == 0:
                continue
        except (TypeError, ValueError):
            pass
        values, messages = calculate_lrt_beam_metrics(beam)
        results.append(values)
        warnings.extend(messages)
    if not results or any(r['MU'] is None for r in results):
        return dict.fromkeys(EXPORT_KEYS), warnings or ['[LRT_UNAVAILABLE] No valid treatment beams']
    mu = np.array([r['MU'] for r in results])
    values = {}
    for key in GEOMETRY_KEYS:
        observations = [r[key] for r in results]
        values[key] = None if any(x is None for x in observations) else float(np.average(observations, weights=mu))
    values['MU'] = float(mu.sum())
    values['MU_per_CP'] = values['MU']/sum(r['MU']/r['MU_per_CP'] for r in results)
    values['PR_System'] = pr_system
    if not full_precision:
        values = {k: None if v is None else round(v, 6) for k, v in values.items()}
    return values, list(dict.fromkeys(warnings))
