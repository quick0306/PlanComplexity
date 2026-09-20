"""Bounded Ethos report profile; see docs/ethos_report_profile.md for evidence.

Distinct from generic MCSv/SAS. Inputs are physical effective apertures in mm.
"""
from __future__ import annotations

import numpy as np

ETHOS_REPORT_KEYS = ('ethos_sas10', 'ethos_one_minus_mcs', 'ethos_penumbra_ratio')
ETHOS_REPORT_VERSION = 'ethos-report-v1'
CLOSURE_MM = .5
GEOMETRY_TOL_MM = 1e-8
TIP_MM = 2.8
SIDE_MM = 2.3
SLOT_MM = 5.


def unavailable(reason):
    return dict.fromkeys(ETHOS_REPORT_KEYS), [f'[ETHOS_REPORT_UNAVAILABLE] {reason}']


def supported_beam_layout(beam):
    """Only the standard staggered 28/29-pair geometry is established here."""
    devices = {str(d.RTBeamLimitingDeviceType).upper(): d
               for d in beam.get('BeamLimitingDeviceSequence', [])}
    for name, expected in [('MLCX1', np.arange(-140., 141., 10.)),
                           ('MLCX2', np.arange(-145., 146., 10.))]:
        device = devices.get(name)
        boundaries = np.asarray(getattr(device, 'LeafPositionBoundaries', []), dtype=float)
        if boundaries.shape != expected.shape or not np.allclose(boundaries, expected, rtol=0, atol=GEOMETRY_TOL_MM):
            return False
        if int(getattr(device, 'NumberOfLeafJawPairs', 0)) != len(expected) - 1:
            return False
    return True


def calculate_ethos_beam_metrics(apertures, cumulative_mu):
    """Return fractions and warnings; reject unsupported inputs rather than guess."""
    mu = np.asarray(cumulative_mu, dtype=float)
    if (len(apertures) < 2 or mu.shape != (len(apertures),) or
            not np.all(np.isfinite(mu)) or mu[0] != 0 or np.any(np.diff(mu) < 0) or mu[-1] <= mu[0]):
        return unavailable('A complete series with finite nondecreasing cumulative MU is required.')
    rows = []
    previous_geometry = None
    for aperture in apertures:
        pairs = aperture.leaf_pairs
        if not pairs:
            return unavailable('Effective leaf slots are missing.')
        geometry = np.asarray([(p.bottom, p.top) for p in pairs])
        lr = np.asarray([(p.left, p.right) for p in pairs])
        jaw = aperture.jaw
        if (not np.all(np.isfinite(lr)) or not np.all(np.isfinite(geometry)) or
                not np.all(np.isfinite([jaw.left, jaw.right, jaw.bottom, jaw.top])) or
                not all(abs(p.width-SLOT_MM) <= GEOMETRY_TOL_MM and
                        abs(p.open_leaf_width()-SLOT_MM) <= GEOMETRY_TOL_MM for p in pairs) or
                np.any(lr[:, 0] < jaw.left-GEOMETRY_TOL_MM) or
                np.any(lr[:, 1] > jaw.right+GEOMETRY_TOL_MM)):
            return unavailable('This profile requires finite, un-clipped 5 mm effective slots.')
        # PyAperture orders rows top to bottom. Do not bridge a missing row.
        if len(pairs) > 1 and not np.allclose(geometry[:-1, 0], geometry[1:, 1], rtol=0, atol=GEOMETRY_TOL_MM):
            return unavailable('Effective slots must be contiguous and ordered.')
        if previous_geometry is not None and (geometry.shape != previous_geometry.shape or
                not np.allclose(geometry, previous_geometry, rtol=0, atol=GEOMETRY_TOL_MM)):
            return unavailable('Effective slot geometry changes between control points.')
        previous_geometry = geometry
        rows.append(lr)
    positions = np.asarray(rows)
    gaps = positions[:, :, 1] - positions[:, :, 0]
    opened = gaps > CLOSURE_MM + GEOMETRY_TOL_MM
    if not np.any(opened):
        return unavailable('The beam has no gap above the closure threshold.')
    areas = np.where(opened, gaps, 0).sum(axis=1) * SLOT_MM
    low = np.min(np.where(opened, positions[:, :, 0], np.inf), axis=0)
    high = np.max(np.where(opened, positions[:, :, 1], -np.inf), axis=0)
    envelope = np.maximum(high-low, 0).sum() * SLOT_MM
    lsv = np.zeros(len(apertures))
    penumbra = np.zeros(len(apertures))
    for i, (lr, active) in enumerate(zip(positions, opened)):
        if not np.any(active):
            continue
        adjacent = active[:-1] & active[1:]
        span = np.ptp(lr[active], axis=0)
        denominator = adjacent.sum() * span
        variation = np.abs(np.diff(lr, axis=0))[adjacent].sum(axis=0)
        banks = 1 - np.divide(variation, denominator, out=np.zeros(2), where=denominator > 0)
        lsv[i] = np.prod(banks)
        left = lr[:, 0]
        right = np.where(active, lr[:, 1], left)
        core = (SLOT_MM-2*SIDE_MM) * np.maximum(right-left-2*TIP_MM, 0).sum()
        # Finite side strips: neighboring openings protect only their actual
        # x interval, without extending its tip distance around concave corners.
        core += SIDE_MM * np.maximum(0, np.minimum(right[1:]-TIP_MM, right[:-1]) -
                                    np.maximum(left[1:]+TIP_MM, left[:-1])).sum()
        core += SIDE_MM * np.maximum(0, np.minimum(right[:-1]-TIP_MM, right[1:]) -
                                    np.maximum(left[:-1]+TIP_MM, left[1:])).sum()
        penumbra[i] = 1 - core / areas[i]
    increments = np.diff(mu)
    weights = (np.r_[0., increments] + np.r_[increments, 0.]) / 2
    return {
        'ethos_sas10': float(np.count_nonzero(opened & (gaps <= 10. + GEOMETRY_TOL_MM)) / opened.sum()),
        'ethos_one_minus_mcs': float(1 - np.average(areas / envelope * lsv, weights=weights)),
        'ethos_penumbra_ratio': float(np.average(penumbra, weights=weights)),
    }, []
