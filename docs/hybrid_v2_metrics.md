# VMAT/IMRT Hybrid-v2 Metric Contract

`hybrid-v2` is the default VMAT/IMRT formula set. Every supported VMAT/IMRT analysis records
`metric_formula_version: hybrid-v2` in structured metadata and exports it in CSV output. TOMO,
Aurora, and CyberKnife formulas and schemas are unchanged.

## Intentional formula changes

- `mad`: at each control point, average `abs((left + right) / 2)` over jaw-overlapping leaf pairs
  with a strictly positive gap; aggregate valid control points by MU and beams by beam MU.
- `alg` and `alg_sd`: first balance active gaps within each control point, then apply control-point
  MU and beam MU. A control point does not gain influence merely by having more active pairs.
- `sas_5mm`, `sas_10mm`, and `sas_20mm`: compute the active-gap fraction separately at each
  control point and MU weight the ratios. The denominator contains only jaw-overlapping, strictly
  positive gaps; the threshold comparison remains strict (`gap < threshold`).

Missing, misaligned, non-finite, negative, or non-positive weight vectors use uniform weights over
valid observations and emit a warning beginning `[METRIC_WEIGHT_FALLBACK]`. Results never expose
NaN or infinity through these formulas.

## Preserved and new outputs

- `mcsv`, `lsv`, `aav`, `pa`, and `ja` retain their existing formulas.
- `lt` retains the existing dose-weighted control-arc total leaf-travel definition.
- `lt_mean_leaf` sums raw geometric travel for every physical bank leaf and divides by the number
  of physical leaves with positive accumulated motion. Beam values are aggregated by beam MU.
- `nl_pairs` is the MU-weighted active leaf-pair count.
- `nl_leaves` is exactly `2 * nl_pairs`.
- `nl` remains as an output alias value equal to `nl_pairs`.

## Halcyon and Ethos representations

Layer-specific MLCX1 and MLCX2 results remain available. Aligned dual-layer plans add two scalar
families.

### Physical effective aperture (`*_effective`)

The effective opening is the intersection of aligned distal and proximal openings at each control
point. `mcsv_effective` and `pa_effective` are aliases of the existing `mcs5` and `pa5` values.
The family also includes AAV, LSV, MAD, ALG/ALG SD, SAS, both LT concepts, and both NL concepts.
`lt_mean_leaf_effective` is measured per moving synthesized 5 mm virtual leaf.

### Non-physical stacked diagnostics (`*_stacked`)

The stacked view concatenates jaw-evaluated MLCX1 slots followed by jaw-evaluated MLCX2 slots.
Every slot retains its original layer, slot index, leaf width, leaf positions, and source jaw state.
It does not fabricate an extended Y axis. LSV intentionally includes one artificial cross-layer
adjacency, and PA sums both layer areas, including overlapping regions twice by design.

These values are algorithm-comparison and dual-layer modulation descriptors. They are not a
physical transmission aperture and must not be used as one.

If any treatment beam has unequal layer control-point series, all `*_effective` and `*_stacked`
values are retained as unavailable (`None`, blank in fixed CSV) and the analysis emits a warning
beginning `[HALCYON_LAYER_ALIGNMENT]`. Layer-specific results remain available.

## RT Complexity Lens comparison boundary

The repository has no `RT_LENS` calculation mode, compatibility profile, or runtime dependency.
The stacked diagnostic idea is implemented internally without copying or vendoring the upstream
library. Reproduction studies should invoke `matteomaspero/rt-complexity-lens` independently and
compare its outputs against this repository's explicitly labeled result families.

## Migration note

Reference ranges created with earlier formulas must not be applied silently to `mad`, `alg`,
`alg_sd`, or `sas_*`. Recompute study cohorts or retain the earlier calculation environment and
label its formula provenance. Existing MCS/AAV/LSV/PA/JA and legacy `lt` series can be compared at
the repository's current rounding precision, subject to the usual plan-parser and machine checks.
