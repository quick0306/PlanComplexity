# Hybrid VMAT/IMRT Complexity Metrics Design

**Date:** 2026-08-30

**Status:** Approved for implementation planning

## Objective

Update the repository's default VMAT/IMRT metric set to use a literature-oriented hybrid calculation model while preserving the existing MCS, LSV, AAV, PA, JA, dose-weighted leaf-travel, and legacy output keys. Add explicit traditional mean leaf travel and leaf-count outputs, correct MAD, make LG and SAS control-point/MU weighted, and expose two additional Halcyon dual-layer representations: a physical effective aperture and an RT Complexity Lens-style stacked diagnostic geometry.

## Scope

This change applies only to the repository's VMAT/IMRT calculation path. It includes metric calculation, metric registration, flattened results, CSV export, formula documentation, migration notes, and automated tests.

TOMO, Aurora, and CyberKnife calculations are outside this change. Their current formulas and result schemas must remain unchanged.

## Non-goals

- Do not add an `RT_LENS` calculation profile, compatibility mode, command-line option, or runtime dependency.
- Do not copy or vendor the `matteomaspero/rt-complexity-lens` implementation.
- Do not change the existing MCS, LSV, AAV, PA, or JA formulas.
- Do not silently translate thresholds or reference ranges between conventional single-layer MLC, Halcyon/Ethos dual-layer MLC, TOMO, Aurora, or CyberKnife.
- Do not claim that stacked dual-layer geometry is the physical transmitted aperture.

External comparison with `rt-complexity-lens` remains an independent validation workflow that may call the installed upstream library directly.

## Public Result Contract

The existing VMAT/IMRT result interface remains the primary API. No calculation-profile parameter is added.

### Backward-compatible keys

- `mcsv`, `aav`, `lsv`, `pa`, and `ja` retain their existing formulas and meanings.
- `lt` retains the current dose-weighted control-arc total leaf-travel definition.
- `nl` remains present and is an alias of `nl_pairs`.
- `alg` and `alg_sd` remain present, but their formulas intentionally change to the MU-weighted definitions below.
- Existing SAS and MAD keys remain present, but their formulas intentionally change to the corrected definitions below.

### New keys

- `lt_mean_leaf`: traditional mean travel per participating physical leaf.
- `nl_pairs`: MU-weighted number of active leaf pairs.
- `nl_leaves`: MU-weighted number of active physical leaves and exactly `2 * nl_pairs`.

For Halcyon/Ethos results, flattened exports add the suffix families described under “Halcyon dual-layer representations.”

### Formula provenance

VMAT/IMRT results expose a non-metric metadata field identifying the formula set, initially `hybrid-v2`. This field is available in structured results and documentation. It does not replace individual metric DOI/reference metadata.

## Default Hybrid Metric Definitions

### Preserved MCS family and area metrics

The current implementations of MCSv, AAV, LSV, PA, and JA remain unchanged, including their current control-point/control-arc and beam-level aggregation behavior. Regression tests must demonstrate unchanged values on fixed synthetic cases and available real-plan fixtures.

### Mean asymmetry distance

For control point `c`, let `G_c` contain leaf pairs that:

1. overlap the Y-jaw opening; and
2. have a strictly positive leaf gap.

For each active pair `l`, define the aperture center on the MLC motion axis as:

`center(c,l) = (left(c,l) + right(c,l)) / 2`.

The control-point MAD is:

`MAD_c = mean_l in G_c (abs(center(c,l)))`.

The beam value is the weighted mean of valid `MAD_c` values using control-point MU weights. The plan value is the beam-MU-weighted mean. A control point with no active pairs is excluded from the weighted numerator and denominator. If no valid control point exists, the result is `0.0`.

The reference axis is the DICOM beam central axis at leaf coordinate zero, not the jaw center.

### Average leaf gap and weighted standard deviation

For each valid control point, collect strictly positive gaps from leaf pairs that overlap the Y-jaw opening.

`LG_c = mean(active_gaps_c)`.

The exported `alg` value is the control-point-MU-weighted mean of `LG_c`, followed by beam-MU-weighted plan aggregation.

The exported `alg_sd` is the weighted population standard deviation of active gaps around the plan/layer weighted mean. Each valid control point receives its control-point MU weight as a whole; that weight is divided equally among its active gaps. Consequently, a control point does not gain additional influence merely because it contains more active leaf pairs. Beam MU participates in the plan-level sample weights. Empty control points are excluded. If no active gap exists, both `alg` and `alg_sd` are `0.0`.

### Small aperture score

For threshold `x` and valid control point `c`:

`SAS_x,c = count(0 < gap < x and inside jaw) / count(0 < gap and inside jaw)`.

The beam result is the control-point-MU-weighted mean of valid control-point ratios. The plan result is the beam-MU-weighted mean. Empty control points are excluded and the remaining weights are renormalized. If the whole plan/layer has no valid control point, return `0.0`.

Threshold comparison remains strict (`gap < x`) to preserve the current boundary convention.

### Leaf travel outputs

`lt` is unchanged. It remains the current MU-weighted mean of total physical leaf travel over adjacent control-point intervals.

`lt_mean_leaf` is calculated per beam:

1. For every physical leaf in both banks, sum absolute travel across adjacent control points whenever that leaf's pair overlaps the jaw in at least one endpoint of the interval.
2. A physical leaf participates in the denominator only when its accumulated travel is strictly positive.
3. Divide total accumulated travel by the number of participating physical leaves.
4. Aggregate beam values to the plan using beam MU.

If no physical leaf moves, return `0.0`. The unit is millimetres per participating physical leaf.

### Active leaf counts

At each control point, an active pair overlaps the Y-jaw opening and has a strictly positive gap.

- `nl_pairs` is the control-point-MU-weighted active-pair count, then beam-MU-weighted at plan level.
- `nl_leaves = 2 * nl_pairs`.
- `nl` is assigned the same result as `nl_pairs` for backward compatibility.

## Control-point and Plan Weighting

Control-point metrics use the repository's existing centered per-control-point MU weights. Control-arc metrics continue to use interval MU derived from adjacent cumulative meterset weights.

Only valid observations participate in metric-specific weighted denominators. When a required weight vector is missing, misaligned, non-finite, or has a non-positive total, the calculation uses uniform weights over valid observations and emits a structured warning. Metric functions must never emit `NaN` or infinity.

Beam-level VMAT/IMRT plan aggregation uses beam MU. Non-treatment beams and beams with non-positive MU remain excluded.

## Halcyon Dual-layer Representations

Halcyon/Ethos results expose three representations. All three use the same default hybrid formulas where those formulas are defined.

### Layer-specific

The existing `MLCX1` and `MLCX2` calculations remain available and preserve current flattened key behavior.

### Physical effective aperture

The existing effective 5 mm aperture construction is reused. At each control point, the open interval for a matched effective leaf pair is the intersection of the distal and proximal layer openings after the repository's existing center alignment/cropping rules. Closed or inverted intersections become zero-width openings.

The effective aperture series produces:

- `mcsv_effective`, `aav_effective`, `lsv_effective`, and `pa_effective`;
- `mad_effective`, `alg_effective`, and `alg_sd_effective`;
- `sas_5mm_effective`, `sas_10mm_effective`, and `sas_20mm_effective`;
- `lt_effective` and `lt_mean_leaf_effective`;
- `nl_pairs_effective` and `nl_leaves_effective`.

`mcsv_effective` and `pa_effective` are explicit aliases of the equivalent existing `mcs5` and `pa5` values. Existing Tamura and Quintero keys remain unchanged. JA is jaw-defined and is not duplicated as an effective-aperture metric.

### Stacked diagnostic geometry

The stacked representation is inspired by the RT Complexity Lens dual-layer parser behavior but is implemented as an internal diagnostic representation, not as an RT Lens compatibility mode.

For each control point, the MLCX1 and MLCX2 leaf-pair collections are concatenated into one metric input. Each source pair retains:

- its original layer identity;
- its original leaf width;
- its own jaw-overlap state; and
- its original left/right positions.

The implementation must not place the two layers consecutively along a fabricated extended Y axis. Jaw inclusion is evaluated before concatenation, or through an equivalent layer-aware abstraction.

The stacked series produces:

- `mcsv_stacked`, `aav_stacked`, `lsv_stacked`, and `pa_stacked`;
- `mad_stacked`, `alg_stacked`, and `alg_sd_stacked`;
- `sas_5mm_stacked`, `sas_10mm_stacked`, and `sas_20mm_stacked`;
- `lt_stacked` and `lt_mean_leaf_stacked`;
- `nl_pairs_stacked` and `nl_leaves_stacked`.

JA is not duplicated. Documentation and result descriptions must state that stacked geometry is an algorithm-comparison and dual-layer modulation descriptor, not a physical transmission aperture.

### Dual-layer alignment failures

Layer-specific metrics remain calculable when a layer has valid data. Effective and stacked series require paired control points for both layers. If layer control-point counts do not match, effective and stacked outputs are unavailable and a structured warning explains the mismatch. The implementation must not silently truncate to the shorter layer.

## Architecture

The implementation uses focused reusable helpers rather than calculation-profile branches.

- Existing metric classes remain the public calculation interface.
- Shared helpers implement active-pair selection, valid weighted aggregation, weighted gap moments, physical-leaf trajectory accumulation, and explicit leaf-pair counts.
- `vcomx_vmat_metrics.py` consumes the shared helpers for supplemental `lt`, `lt_mean_leaf`, `nl`, `nl_pairs`, and `nl_leaves` outputs while preserving its current MCS/LSV/AAV/PA/JA path.
- MAD, LG, and SAS classes use the shared control-point aggregation behavior.
- `halcyon_dual_layer_metrics.py` remains responsible for constructing layer-specific snapshots and the physical effective aperture, and gains a layer-aware stacked metric series.
- The metric registry, definition catalog, flattened-output logic, CSV exports, and user documentation are updated together.

No new external dependency is introduced.

## Error Handling

- Inherited DICOM machine parameters continue to use the repository's existing prior-control-point behavior.
- Empty active-pair sets are excluded from metric-specific weighted denominators.
- Missing or invalid weights use uniform fallback with a warning.
- Dual-layer count mismatches disable only effective and stacked calculations; layer-specific calculations remain available.
- Metric results are finite. Invalid intermediate arithmetic resolves to a documented zero or unavailable output, never `NaN`/infinity.
- Unsupported non-VMAT calculation paths are unaffected.

## Migration and Documentation

The formula version changes to `hybrid-v2` for VMAT/IMRT results.

Migration notes explicitly identify intentional result changes for:

- `mad`;
- `alg` and `alg_sd`;
- `sas_5mm`, `sas_10mm`, and `sas_20mm`.

They also identify the new `lt_mean_leaf`, `nl_pairs`, `nl_leaves`, effective, and stacked outputs. Existing `lt` and `nl` keys remain available as described above.

Generated formula documentation and CSV headers must reflect the new keys and units. Stacked results must carry a visible non-physical-geometry warning in metric descriptions.

## Verification Strategy

### Formula unit tests

Use small hand-constructed apertures and meterset weights to verify:

- MAD uses aperture centers rather than mean absolute leaf-end positions;
- jaw-excluded and closed pairs do not enter MAD, LG, SAS, or NL;
- LG and SAS are calculated per control point and MU weighted;
- `alg_sd` follows the specified control-point-balanced weighted population variance;
- strict SAS threshold behavior;
- `lt_mean_leaf` counts physical leaves, excludes stationary leaves, and handles jaw transitions;
- `nl_pairs`, `nl_leaves`, and legacy `nl` relationships;
- empty valid sets and invalid-weight fallbacks.

### Regression tests

Fixed cases must prove no value change for MCS, LSV, AAV, PA, JA, and legacy `lt`. Existing VMAT/IMRT, motion, registry, export, and validation tests must remain green except where expected values intentionally change under `hybrid-v2`.

### Halcyon tests

Synthetic dual-layer apertures must verify all three representations. At least one offset-layer case must prove that physical effective and stacked results differ. Tests must verify that stacked pair counts equal the sum of layer-specific pair counts and that stacked geometry does not lose a layer through fabricated Y-axis jaw clipping.

Available real Halcyon plans provide integration smoke coverage for layer-specific, effective, stacked, flattened, registry, and CSV outputs. Tests skip explicitly when the local real-plan fixtures are unavailable.

### Full verification

Run the focused formula and Halcyon tests first, followed by the full repository test suite and a representative real-plan calculation. Inspect the final diff to confirm unrelated working-tree changes were not overwritten.

## Acceptance Criteria

1. Default VMAT/IMRT results preserve MCS, LSV, AAV, PA, JA, `lt`, and legacy `nl` compatibility as specified.
2. Corrected MAD and MU-weighted LG/SAS match hand-calculated fixtures.
3. `lt_mean_leaf`, `nl_pairs`, and `nl_leaves` are exported and documented.
4. Halcyon/Ethos exposes layer-specific, effective, and stacked result families with clear physical interpretation labels.
5. No RT Lens mode, formula copy, or runtime dependency is added.
6. TOMO, Aurora, and CyberKnife behavior remains unchanged.
7. Focused and full automated verification passes, or any unrelated pre-existing failures are reported with evidence.
