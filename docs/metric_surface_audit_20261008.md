# Metric surface audit — 2026-10-08

This records the restoration-stage audit against pre-restoration commit `4652b74`. The current V4 version is `aurora-v4-physical-aperture-open-only`; its closed-endpoint rule supersedes the initial rule described below. See [current definitions](aurora_aperture_metrics.md) and [documentation synchronization](documentation_sync_20261008.md).

This audit compares calculation output keys, flattening, export ordering, labels and
descriptions, formula contracts, definition exports, and validation specifications.
It uses repository source and constructed synthetic inputs; no clinical plan files
were opened for this audit. Counts include container keys and layer variants, not
independently validated scientific quantities.

## Confirmed discrepancies

| Finding | Evidence | Resolution in this working change |
| --- | --- | --- |
| Seven Aurora V4 metrics absent from main and the compatibility branch | `git show 4652b74:aurora_svmat_lab/metrics.py` and `git show codex/aurora-wisdomtech-compatibility:aurora_svmat_lab/metrics.py` have no V4 order; full stash `b8419fd` (`stash@{0}`) contains V4 calculation, GUI, documentation and tests; its untracked-files parent `79a8fb9` contains the design/plan | Restore the public keys using the separately documented physical geometry version; add catalog, GUI, export, contract and validation coverage |
| Native Halcyon MCSv layer values disappear during aggregation | `analysis_helpers.calculate_core_metrics_with_warnings` constructs a native MCSv tuple, then updates it with Halcyon paper metrics; `halcyon_dual_layer_metrics._calculate_beam_paper_metrics` includes scalar `mcsv=effective_mcs`; flattening therefore cannot produce the catalog's `mcsv_mlcx1` and `mcsv_mlcx2` | Preserve native values under explicit layer keys before the scalar compatibility override |
| Three Varian dual-layer metrics missing from generated definitions | At audit start, `metric_registry.py` and validation specifications contain `ethos_sas10`, `ethos_one_minus_mcs`, `ethos_penumbra_ratio`, but `docs/metric_definitions_all.md`, `docs/metric_definitions_vmat_imrt.md`, and the local definition CSV omit them | Regenerate definitions; add exact generated-document comparisons |
| 32 flattened motion keys lack GUI descriptions | `metric_descriptions_with_aliases()` omits four speed/acceleration summaries and fourteen bins/summaries for each native MLC layer; all their GUI labels and formula definitions already exist | Add descriptions including native layer identity; specify nonzero means and sample standard deviations consistently with `MLCAttributes` |
| Historical migration document misstates current versions | `docs/hybrid_v2_metrics.md` opening still describes geometry-v3 and tomo-v2 as current while `formula_versions.py` and README use geometry-v4 and tomo-v3 | Correct the current-version pointers and retain the document's historical scope |

The local CSV is ignored and untracked (`git ls-files output/metric_definitions_all.csv`
returns no entry). It is a generated local artifact, whereas the Markdown definitions
are checked in. Regression checks therefore compare a fresh temporary CSV against
every catalog field and compare checked-in Markdown against fresh generation.

## Aurora history and formula boundary

The stash is **not design-only**: its `aurora_svmat_lab/metrics.py` contains
`V4_METRIC_ORDER`, `calculate_v4_beam_metrics`, `_summarize_v4_aperture_records`, and
`_effective_aperture_row_intervals`, together with GUI/export/documentation tests.
Its reconstruction explicitly uses unit-height rows and zips MLCX1 against MLCX2
entries as if they were opposing banks. Restoring those formulas verbatim would
preserve a surrogate rather than reconstruct the physical intersection of two
independent MLC layers.

The new `aurora-v4-physical-aperture` contract is a conscious formula correction.
Seven familiar key names do not imply numerical equivalence with the stashed
surrogate. Physical leaf boundaries, bank ordering, jaws, positive delivered
intervals and weight provenance are required. Undefined BI/CA on a closed aperture
remain unavailable with a warning; an unavailable value is not an omitted key.
The adapted gap-based MCS remains a research variant rather than a claim of exact
McNiven or vendor equivalence. See [the migration contract](aurora_v4_migration.md).

## Coverage and intentional subsets

- At audit start, the catalog had 427 records: 286 VMAT/IMRT, 65 TOMO, 6 CyberKnife
  MLC and 70 Aurora. After the seven V4 additions, the inventory is 434 with 77
  Aurora records. There were no duplicate platform/key identities.
- Runtime TOMO keys from a constructed sinogram match all 65 catalog entries.
  CyberKnife empty and nonempty synthetic calculations match its six entries.
  Six CyberKnife MLC entries are the intentionally supported MLC subset, not an
  assertion that every CyberKnife delivery technique is implemented.
- Constructed single-layer and Halcyon calculations plus flattened outputs cover
  the VMAT catalog, subject to the native-MCSv preservation fix above. Native,
  effective and stacked outputs are conditional representations; expecting all
  variants from a conventional single-layer plan would be incorrect.
- Aurora beam, plan and declared export order are checked against the catalog,
  including missing-geometry cases. Metric availability depends on inputs;
  undefined values must retain their public keys.
- Every catalog record is checked for a GUI label, description, exact formula
  contract and unit. Validation specifications, logical groups and the research
  profile are checked against the expanded catalog, including the new V4 group.
- V3's anatomy-linked, delivery-log deviation and explicit mode-switch metrics
  are explicitly outside its design scope. Imported UCoMX comparator planning
  documents are labeled future work; their prospective workflow is not evidence
  of missing implemented public metrics.

Durable checks are in `tests/test_metric_surface_consistency.py` and the existing
`tests/test_metric_formula_contracts.py` and `tests/validation/test_metric_specs.py`.
The new checks compare keys and formulas, rather than accepting approximate counts
or checking only a few representative metric names.

Verification on this working change: `python -m pytest
tests/test_metric_surface_consistency.py tests/validation/test_metric_specs.py
tests/test_aurora_v4.py -q` completed with **27 passed**. The VMAT synthetic case
also distinguishes native layer MCS from the effective scalar and checks that all
three values survive aggregation. This targeted result is separate from the full
repository verification performed for the overall change.

## Limits

This is a surface and provenance audit, not independent physical or clinical
validation of every formula. It inspects the current checkout, all currently listed
branch refs relevant to Aurora, and the one listed stash; it cannot establish what
was present in deleted, unreachable or external repositories. GUI label/description
coverage is verified structurally; visual rendering is covered separately by GUI
tests. Existing reference baselines and their recorded provenance are preserved;
adding V4 specifications does not turn historical baselines into V4 evidence.
