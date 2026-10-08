# Aurora 77-metric restoration and formula migration

## Origin of the omission

The April 2026 `codex/unified-validation-phase1` stash (`b8419fd`, stash@{0}) contains the seven V4 aperture metrics, their tests and documentation. The main branch shipped 21 V2 + 40 V3 + 9 legacy keys (70), omitting V4. A search limited to the stash untracked-files parent found only the design and incorrectly suggested no implementation existed. Inspecting the complete stash corrected that finding.

## Compatibility boundary

The seven names are restored across calculation, service/GUI registry, beam/plan CSV, column descriptions, catalog, formula contracts, validation YAML and PDF. The existing 70 computations are unchanged. Real user plans were compared against the previous main source for all 70 values.

The archived V4 implementation paired `MLCX1` and `MLCX2` coordinate arrays with `zip`, assumed unit-height rows and pooled relative meterset changes. This is a surrogate rather than a physically valid intersection of the two banks in two layers. It also incorrectly assumed the RTPLAN could not provide physical leaf heights. The supplied plans contain `LeafPositionBoundaries` for both layers.

Restored V4 therefore records a new formula version, `aurora-v4-physical-aperture`. It does **not** claim to reproduce the archived seven values numerically. Both layers are split into their A/B banks, intersected on the union of their physical Y boundaries, and clipped to the jaws. Area is mm^2 and perimeter is mm. Sampling uses the endpoint of each positive delivered interval. Absolute interval MU weights are used when unambiguous BeamMeterset is available; otherwise every beam uses normalized relative weights and a warning discloses the fallback. Missing/invalid physical geometry yields seven unavailable values with an explicit warning rather than inventing leaf widths.

- `mean_ba`: weighted area.
- `mean_bi`: weighted P^2/(4*pi*A).
- `mean_ca`: weighted P/A, in 1/mm; not circularity.
- `mean_sas5`, `mean_sas10`: weighted fraction of open physical sub-strips with gaps strictly below the respective threshold. Sub-strips are defined by the union of both layers' leaf boundaries, not original single-layer leaf-pair counts.
- `mean_mcs_aurora`: weighted product of a beam-specific clipped-strip-area envelope ratio and gap-sequence variability. It is an Aurora adaptation, not the classic McNiven bank-based MCS.
- `mcs_complexity_aurora`: 1 - mean_mcs_aurora.

A positive-weight fully closed aperture contributes zero area/SAS/MCS, but BI and P/A are undefined. An aggregate with such an undefined shape value remains unavailable and carries a warning; no interval is silently dropped. The supplied UCC017 case exercises this boundary. Zero-MU intervals do not affect the V4 envelope or weighted averages.

## Prevention and verification

`tests/test_metric_surface_consistency.py` checks runtime keys, GUI labels/descriptions, catalog, formula contracts and regenerated definition documents. Validation YAML/catalog checks also include the new V4 group. `tests/test_aurora_v4.py` covers hand-calculated rectangle values, MU weighting, missing metadata, strict thresholds, closed apertures, zero MU, and an independent Shapely polygon-intersection/perimeter oracle. CSV integration asserts all seven columns and recorded formula version. Formula PDF tests inspect inequality text to prevent markup from swallowing less-than signs.

The older 70 Aurora metrics retain their existing research/proxy definitions; this restoration does not relabel those proxies as physical aperture metrics or independently validate all scientific interpretations.

Final validation on 2026-10-08: 393 tests passed, 1 skipped and 99 subtests passed. The build environment passed 29 focused tests. All three supplied Aurora plans export 77 keys in automatic and explicit Aurora modes; their prior 70 values remain identical. Additionally, 126 sampled real control-point apertures matched independent polygon intersection area and perimeter calculations. These are numerical/technical checks, not clinical validation.
