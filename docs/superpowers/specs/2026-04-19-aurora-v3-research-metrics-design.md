# Aurora V3 Research Metrics Design

## Goal

Extend the standalone Aurora SVMAT Lab with additional research-grade complexity metrics that can be computed directly from the currently available Aurora RTPLAN control-point data. The new metrics should remain interpretable, exportable, and consistent with the existing v2 paper-style physics metrics.

## Scope

This increment adds only the metrics that are immediately supportable from the present Aurora parser output:

1. Reversal and bidirectional symmetry metrics
2. Small-opening and narrow-gap burden metrics
3. Local peak interval metrics
4. Axial regional metrics
5. Dual-layer coordination metrics

Out of scope for this increment:

- Explicit mode classification or mode-switch metrics
- Anatomy-linked metrics that require RTSS or CT
- Planned-versus-delivered deviation metrics that require delivery logs

## Available Inputs

Aurora RTPLAN parsing already exposes:

- beam-level control-point sequences
- gantry angle
- axial position from `IsocenterPosition[2]`
- cumulative meterset weight
- dose rate
- `MLCX1` and `MLCX2` leaf positions
- jaw positions
- WisdomTech private axial audit values for consistency checks

## Metric Families

### 1. Reversal and bidirectional symmetry

These metrics quantify how similarly forward-moving and backward-moving beams share the modulation burden within one plan.

- `reversal_symmetry_index`
- `forward_backward_metric_difference`
- `beam_pair_balance_index`

The burden basis will be the currently implemented Aurora engineering modulation summary, so the new metrics remain tied to actual delivery modulation rather than beam count alone.

### 2. Small-opening burden

These metrics summarize how often the effective surrogate opening is narrow, because small openings are more likely to challenge delivery.

- `small_opening_fraction`
- `near_closed_fraction`
- `effective_small_gap_burden`

Thresholds for this increment:

- small opening: `0 < gap < 10 mm`
- near closed: `0 < gap < 2 mm`

The implementation will use the current Aurora effective opening surrogate already implied by the existing aperture-width calculations.

### 3. Local peak interval metrics

These metrics capture whether a plan contains a few very difficult intervals even when global averages look moderate.

For each interval-series family, expose:

- `p95`
- `max`
- `top3_mean`

Series families in scope:

- projection pitch
- projection meterset-weight density proxy
- projection aperture-change rate
- projection leaf-travel rate

### 4. Axial regional metrics

These metrics measure whether complexity concentrates in one longitudinal subregion.

The covered z-span will be partitioned into:

- `head`
- `mid`
- `tail`

using interval midpoint position over the global z-range. For each region, compute mean and coefficient of variation for:

- MU-density proxy
- aperture-change rate
- leaf-travel rate

### 5. Dual-layer coordination metrics

These metrics emphasize Aurora’s distinguishing dual-layer behavior.

- `layer_imbalance_index`
- `layer_correlation_index`
- `x1_x2_aperture_disparity`
- `x1_x2_leaf_travel_ratio`

`x1_x2_aperture_disparity` will be documented as a surrogate based on asymmetric side opening magnitude, not as a direct physical aperture-overlap reconstruction.

## Integration Points

The increment should update:

- `aurora_svmat_lab/metrics.py`
- `aurora_svmat_lab/notes.py`
- `aurora_svmat_lab/export.py`
- `tests/test_aurora_metrics.py`
- `tests/test_aurora_export.py`

Existing GUI and CSV exports should pick up the new metrics through the existing export ordering machinery without needing a separate Aurora UI redesign.

## Verification

Verification should cover:

- deterministic synthetic unit tests for each new metric family
- export-path tests that ensure new metric names appear in plan or beam rows
- regression coverage for the previously implemented Aurora metrics
