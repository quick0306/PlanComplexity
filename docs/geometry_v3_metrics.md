# Geometry-v3 and TOMO-v2 migration

This document preserves the preceding `geometry-v3` / `tomo-v2` migration and its
audits. The active versions are now `geometry-v4` / `tomo-v3`; see the
[precision and motion migration](precision_motion_validation.md). The geometry
definitions below remain applicable. Historical audit outputs are preserved.

## Physical aperture geometry

All DICOM coordinates and lengths below are in millimetres. Each native MLC
device supplies its own increasing `LeafPositionBoundaries` with N+1 entries
for N pairs. Position arrays must contain both banks with exactly N entries.
The implementation reflects IEC Y into its internal Y axis without reversing
the DICOM leaf-slot order. It preserves absolute offsets and unequal widths.
Symmetric `X`/`Y` and asymmetric `ASYMX`/`ASYMY` jaws clip identically, with
control-point positions taking precedence over inherited positions. If a later
control point omits one jaw axis, it inherits that axis from the latest control
point; beam defaults are used only before a control-point value exists.

Halcyon native distal/proximal representations retain all 28/29 leaf pairs and
their separate boundaries. The outer proximal half-leaf is clipped by the
fixed 280 mm field. The effective 5 mm representation remains the intersection
of the two layers. Stacked diagnostics still sum both native layers and retain
their artificial cross-layer adjacency; they are not a transmission aperture.
The widths-only constructor remains available for legacy/synthetic callers;
DICOM paths supply absolute boundaries rather than reconstructing a centre.

For each transmitted row, let g be the X-jaw-clipped positive gap and h the
Y-jaw-clipped height. Closed, crossed, or zero-height openings contribute no
physical area or perimeter. Area is `A = sum(g_i * h_i)`. Full perimeter is the
sum of both vertical sides (`2 * sum(h_i)` over open rows), the first/last
horizontal edges, and the non-overlapping horizontal edges between adjacent
rows. Equivalently, an internal interface contributes
`g_i + g_(i+1) - 2 * overlap(i, i+1)`.

The common full perimeter supplies `PI = P^2 / (4*pi*A)`, `EFS = 4*A/P`, and
the small-field quantities derived from EFS. A 10 by 10 mm square has A=100,
P=40, PI=4/pi, and EFS=10. The previous one-bank perimeter gave P=30.
Horizontal interfaces also correctly account for closed or disconnected
rows. Therefore the correction need not increase P for every old aperture.
The existing one-sided edge metric and edge-area helper retain their own
definitions; they are not replaced by the full perimeter.

## Dynamic-jaw normalization and shared implementation

For each slot i, maximum-aperture normalization takes the minimum raw left
position, maximum raw right position, and maximum exposed height over all
control points where that slot overlaps the jaws:

`A_max = sum_i(max(R_max,i - L_min,i, 0) * max_cp(h_i,cp))`.

This preserves the established raw-bank X convention. It is a per-slot
envelope, not the exact geometric union of delivered rectangles. The prior
implementation overwrote height with the last control point. The corrected
denominator is invariant to reversing the control-point sequence: equal-MU
100 and 20 mm2 rectangular apertures yield MCSv=0.6 in either order.

`ComplexityMetric/aperture_shape_metrics.py` now owns AAV normalization and
leaf-sequence variability. VMAT, Halcyon, and CyberKnife wrappers share it;
family-specific MU/interval aggregation remains separate. Full perimeter is
owned by the aperture object. Previously duplicated TOMO service branches now
share the same parsing/error handling and formula-version metadata.

## TOMO units

See the [TOMO input contract](tomo_input_contract.md) for authoritative unit
definitions and supported sources. Standard leaf durations use seconds;
documented `TOMO_HA_01` private rows use fractions. Units do not depend on
numeric magnitude. Interior closed projections remain in the sinogram.
The private gantry period replaces the old default where present. Course
prescription is divided by fraction count: 60 Gy / 30 gives 200 cGy per fraction.
Missing or ambiguous dose produces an unavailable dose-normalized metric
(`null` in validation JSON), not a numerical zero.

## Baseline migration evidence

Original scalar baselines were unversioned and also predated parts of the
hybrid-v2 output schema. Their exact bytes and hashes are retained under
`validation/reference_cases/history/pre-geometry-v3/`, anchored to source
commit `be93062484277b362948d959a2044c72c8543dcc`. Do not interpret that archive
as a uniformly hybrid-v2 baseline.

The migration separates changes from the old checked-in expectations and
changes from the runtime immediately before this fix. The machine-readable
audit is `validation/reference_cases/migrations/geometry-v3_tomo-v2.json`.
It records every changed/added metric, old expectation, preceding runtime
value, new value, and reason. Existing tolerances are unchanged. The 37 added
keys were already emitted by hybrid-v2; this migration brings them into the
versioned reference pack.

Independent hand cases cover square/disconnected/closed apertures, symmetric
jaws, absolute and odd-layer offsets, reversed jaw motion, duration units,
and fractional dose. Additional raw-reference audits reconstruct geometry
from DICOM rectangles and TOMO metrics from private rows; those scripts use
production calculations only on the comparison side. Their metric-only
results accompany the migration. Versioned baseline agreement is a regression
check; it does not establish clinical accuracy or external-tool equivalence.

The raw geometry audit covers 1,417 apertures/segments (356 TrueBeam, 664 native
and 332 effective Halcyon, 65 CyberKnife). Maximum area/perimeter residuals are
below 1e-12 mm2/mm. CyberKnife reuses the XML segment parser but independently
calculates rectangle boundaries and MU weighting. Raw native gap moments and
SAS were checked over 19,514 positive-gap observations. Halcyon PI5 changes
from 11.374771 to 10.457651: 79 control points lose false closed-row boundary;
their negative PI contribution dominates the positive contribution elsewhere.

The TOMO audit explains all 60 changed values: 34 timing-dependent values,
17 changes from restoring closed projections, two unavailable-dose values,
and seven floating-point roundoff differences. The edge case retains 697
projections rather than 594. Projection durations are 11.8/51 and 30.2/51 seconds per
projection for the canonical and edge cases respectively.

Together the six migrated cases contain 106 changed scalar values and 37
previously unfrozen hybrid-v2 outputs. Reproduce the independent audits locally
with the manifest data available (geometry replay also requires the archived
source Git commit):

```bash
python tools/audit_reference_geometry.py --output /path/to/geometry_audit.json
python tools/audit_reference_tomo.py --snapshot-dir validation/reference_cases/migrations/tomo-v2
```

The TOMO command writes a fresh `tomo_audit.json` into its snapshot directory;
the archived audit at the migration root remains the migration evidence.

The rebuilt research reference gate contains 8 cases and 517 metric rows, with
269 exact-equivalent comparisons passing and zero formula-provenance or
analysis-state failures. The actual CLI was also observed returning 1 before
provenance migration and 0 afterwards. Report rendering refreshes existing
JSON/CSV files before computing hashes; absent metrics fail even when an
explicitly unavailable (`null`) value was expected. Twelve independent formula
oracles pass. External comparator inputs and all existing tolerances are unchanged.
