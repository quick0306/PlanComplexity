# Hybrid VMAT/IMRT Complexity Metrics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved `hybrid-v2` VMAT/IMRT metric definitions, add Halcyon effective and stacked diagnostic outputs, preserve specified legacy values, and synchronize all living repository documentation with the shipped behavior.

**Architecture:** Add one focused aperture-series calculation module that owns valid-observation filtering, weight fallback, gap moments, MAD, SAS, active counts, and traditional mean leaf travel. Existing public metric classes and `vcomx_vmat_metrics.py` consume those helpers. `halcyon_dual_layer_metrics.py` reuses the same formulas for effective virtual apertures and a layer-aware stacked view without introducing an RT Lens mode or dependency.

**Tech Stack:** Python 3, NumPy, pydicom, unittest/pytest, existing `PyAperture` geometry and metric registry/export framework.

**Spec:** `docs/superpowers/specs/2026-08-30-hybrid-complexity-metrics-design.md`

---

## Execution constraints

- The current `main` worktree contains pre-existing user edits, including tracked and untracked files this feature may also touch. Record status, hashes, tracked diffs, and complete untracked contents for every planned path before editing, and preserve that baseline exactly.
- Do not use reset, checkout, broad staging, `git add .`, or `git add -A`.
- Commit only files that were clean at the start or newly created by this feature. Leave every overlapping pre-existing dirty or untracked file unstaged unless an exact patch containing only this feature's hunks can be proven safe. Never commit a pre-existing untracked file merely because this feature added lines to it.
- Historical files under `docs/superpowers/specs/` and `docs/superpowers/plans/` are archival records; audit them for context but do not rewrite older decisions.
- Do not add an RT Lens calculation mode, source copy, package dependency, CLI option, or GUI setting.

## Task 0: Create a feature branch without moving the dirty working tree

**Files:**
- No file changes.

- [ ] **Step 1: Create the feature branch in place**

Because relevant uncommitted user edits must remain available, do not create a clean secondary worktree that would omit them. Preserve the current working tree and run:

```powershell
git switch -c codex/hybrid-complexity-metrics
```

Expected: the branch changes while all tracked and untracked working-tree changes remain present.

- [ ] **Step 2: Verify branch and dirty-state preservation**

```powershell
git branch --show-current
git status --short
```

Expected branch: `codex/hybrid-complexity-metrics`. Compare status with the pre-branch snapshot and stop if any user change disappeared.

## File map

### Create

- `ComplexityMetric/aperture_series_metrics.py` — shared hybrid-v2 aperture-series formulas and weight diagnostics.
- `ApertureMetric/stacked_aperture.py` — layer-aware stacked leaf-pair/aperture views that retain original jaw state and width.
- `tests/test_hybrid_metric_formulas.py` — hand-calculated formula tests.
- `tests/test_hybrid_metric_integration.py` — plan/service/export integration and backward-compatibility tests.
- `validation/hybrid_v2_formula_oracles.py` — standalone hybrid-v2 hand-calculated validation oracles.
- `tests/validation/test_hybrid_v2_formula_oracles.py` — oracle regression tests without altering pre-existing untracked oracle work.
- `docs/hybrid_v2_migration.md` — user-facing formula migration and output-key guide.

### Modify

- `ComplexityMetric/mean_asymmetry_distance.py` — corrected aperture-center MAD and valid CP weighting.
- `ComplexityMetric/leaf_gap.py` — per-CP MU-weighted ALG and balanced weighted SD.
- `ComplexityMetric/small_aperture_score.py` — per-CP active-gap ratio and MU weighting.
- `vcomx_vmat_metrics.py` — add `lt_mean_leaf`, `nl_pairs`, `nl_leaves`, retain legacy `lt` and `nl`.
- `halcyon_dual_layer_metrics.py` — add hybrid effective aliases/metrics and stacked diagnostics.
- `analysis_helpers.py` — metrics-plus-warnings service path with metrics-only compatibility wrapper.
- `ucomx_service.py` — merge metric warnings, add `metric_formula_version`, export provenance.
- `metric_registry.py` — register new default/effective/stacked outputs and descriptions.
- `metric_definition_catalog.py` — formulas, units, applicability, non-physical stacked warning.
- `analysis_exports.py` — expose formula version and new registry-driven columns.
- `tests/test_metric_formulas.py` — replace old MAD/LG/SAS expectations with hybrid-v2 expectations.
- `tests/test_halcyon_dual_layer_paper_metrics.py` — three-representation coverage.
- `tests/test_analysis_helpers.py` — registry/flatten/export/provenance coverage.
- `.github/workflows/validation.yml` — include new focused tests only if current discovery would otherwise miss them.
- `README.md`, living files under `docs/`, and generated metric definition outputs — post-implementation documentation synchronization.

## Task 1: Freeze legacy baselines and write failing core formula tests

**Files:**
- Create: `tests/test_hybrid_metric_formulas.py`
- Create: `tests/test_hybrid_metric_integration.py`
- Inspect only: `run_reports/real_rtplan_metrics_all.csv`
- Inspect only: `tests/test_metric_formulas.py`

- [ ] **Step 1: Record the starting state of overlapping dirty files**

Run:

```powershell
$plannedPaths = @(
  '.github/workflows/validation.yml',
  'ApertureMetric/aperture_creator.py',
  'ApertureMetric/stacked_aperture.py',
  'ComplexityMetric/aperture_series_metrics.py',
  'ComplexityMetric/mean_asymmetry_distance.py',
  'ComplexityMetric/leaf_gap.py',
  'ComplexityMetric/small_aperture_score.py',
  'vcomx_vmat_metrics.py',
  'halcyon_dual_layer_metrics.py',
  'analysis_helpers.py',
  'ucomx_service.py',
  'analysis_exports.py',
  'metric_registry.py',
  'metric_definition_catalog.py',
  'validation/formula_oracles.py',
  'validation/hybrid_v2_formula_oracles.py',
  'tests/test_metric_formulas.py',
  'tests/test_motion_metrics.py',
  'tests/test_halcyon_dual_layer_paper_metrics.py',
  'tests/test_analysis_helpers.py',
  'tests/validation/test_formula_oracles.py',
  'tests/validation/test_hybrid_v2_formula_oracles.py',
  'README.md',
  'docs/clinical_implementation_sop.md',
  'docs/reference_pack_v1.md',
  'docs/metric_definitions_all.md',
  'docs/metric_definitions_vmat_imrt.md',
  'docs/hybrid_v2_migration.md',
  'output/metric_definitions_all.csv',
  'run_reports/validation/validation_summary.md'
)

git status --porcelain=v1 --untracked-files=all
foreach ($path in $plannedPaths) {
  if (-not (Test-Path -LiteralPath $path)) { continue }
  Write-Output "BASELINE_PATH $path"
  Get-FileHash -Algorithm SHA256 -LiteralPath $path | Select-Object Path, Hash
  git ls-files --error-unmatch -- $path 2>$null
  if ($LASTEXITCODE -eq 0) {
    git diff --binary -- $path
  } else {
    Write-Output "BASELINE_UNTRACKED_CONTENT_BEGIN $path"
    Get-Content -Raw -LiteralPath $path
    Write-Output "BASELINE_UNTRACKED_CONTENT_END $path"
  }
}
```

Retain the complete output in the execution transcript. This read-only snapshot covers every planned overlapping path, including the current untracked formula-oracle, clinical, and reference-pack files. Expected: user edits are visible and no feature edits exist yet.

- [ ] **Step 1b: Classify staging eligibility before editing**

From the status snapshot, produce two lists in the execution transcript:

- `FEATURE_STAGEABLE`: clean-at-start files and files newly created by this feature.
- `PRESERVE_UNSTAGED`: every dirty-at-start or pre-existing untracked path.

Use these lists for every later commit. Recompute status before staging and stop if a path's classification is unclear.

- [ ] **Step 2: Create the integration test file and capture representative preserved values**

Create `tests/test_hybrid_metric_integration.py`. Select one available conventional VMAT plan and calculate the current `mcsv`, `aav`, `lsv`, `pa`, `ja`, `lt`, and `nl`. Store expected values in a regression test in that file; skip with an explicit reason when the local real-plan fixture is unavailable. Do not alter the plan or existing result CSV.

- [ ] **Step 3: Write failing pure-formula tests**

Add tests for the wished-for API:

```python
from ComplexityMetric.aperture_series_metrics import (
    active_pair_count,
    mean_asymmetry_distance,
    mean_leaf_travel,
    small_aperture_score,
    weighted_gap_moments,
)

def test_mad_uses_opening_center_and_excludes_closed_and_outside_jaw(): ...
def test_gap_moments_balance_each_control_point_before_mu_weighting(): ...
def test_sas_is_per_control_point_then_mu_weighted(): ...
def test_sas_keeps_strict_threshold_boundary(): ...
def test_mean_leaf_travel_uses_raw_trajectory_and_moving_physical_leaves(): ...
def test_mean_leaf_travel_counts_interval_when_pair_is_inside_jaw_at_either_endpoint(): ...
def test_active_pair_count_includes_zero_as_valid_observation(): ...
def test_invalid_weights_use_uniform_fallback_and_report_it(): ...
```

Use the approved numeric examples: MAD from aperture centers, gap weights `[0.5, 0.5, 3]`, and leaf trajectories totaling 4 mm and 6 mm.

- [ ] **Step 4: Verify RED**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_hybrid_metric_formulas.py -q
```

Expected: collection fails because `ComplexityMetric.aperture_series_metrics` does not exist.

## Task 2: Implement the shared aperture-series formula core

**Files:**
- Create: `ComplexityMetric/aperture_series_metrics.py`
- Test: `tests/test_hybrid_metric_formulas.py`

- [ ] **Step 1: Add narrow result types and observation helpers**

Implement:

```python
@dataclass(frozen=True)
class MetricValue:
    value: float
    used_uniform_weights: bool = False

@dataclass(frozen=True)
class GapMoments:
    mean: float
    standard_deviation: float
    used_uniform_weights: bool = False
```

Add helpers that select leaf pairs with `not pair.is_outside_jaw()` and `pair.field_size() > 0`, normalize only valid finite non-negative weights, and return finite zero values for an entirely empty series.

- [ ] **Step 2: Implement MAD, gap moments, SAS, NL, and mean leaf travel**

Required signatures:

```python
def mean_asymmetry_distance(apertures, cp_weights) -> MetricValue: ...
def weighted_gap_moments(apertures, cp_weights) -> GapMoments: ...
def small_aperture_score(apertures, cp_weights, threshold_mm) -> MetricValue: ...
def active_pair_count(apertures, cp_weights) -> MetricValue: ...
def mean_leaf_travel(apertures) -> float: ...
```

MAD/LG/SAS exclude CPs with no active pairs and renormalize. NL includes zero-count CPs. Mean leaf travel performs no interval-MU weighting, counts left/right leaves separately only when accumulated travel is positive, and includes an interval whenever the source pair overlaps the jaw at either endpoint.

- [ ] **Step 3: Verify GREEN and refactor**

Run the focused test file. Expected: all tests pass with no warnings. Refactor only duplication found by the tests.

- [ ] **Step 4: Commit clean new files only**

```powershell
git add -- ComplexityMetric/aperture_series_metrics.py tests/test_hybrid_metric_formulas.py
git commit -m "feat: add hybrid aperture series formulas"
```

## Task 3: Correct MAD, LG, and SAS through their public metric classes

**Files:**
- Modify: `ComplexityMetric/mean_asymmetry_distance.py`
- Modify: `ComplexityMetric/leaf_gap.py`
- Modify: `ComplexityMetric/small_aperture_score.py`
- Modify: `tests/test_metric_formulas.py`
- Modify: `tests/test_hybrid_metric_integration.py`

- [ ] **Step 1: Write failing public-class tests**

Construct two-control-point beams with unequal centered MU weights and assert:

```python
assert MeanAsymmetryDistance().calculate_for_plan(plan) == expected_mad
assert LeafGap().calculate_for_plan(plan) == (expected_alg, expected_sd)
assert SmallApertureScore().calculate_for_plan(plan, x=5) == expected_sas
```

Cover single-layer and dual-layer return shapes. Verify old global-pooling expectations fail for the intended reason.

- [ ] **Step 2: Verify RED**

Run the two focused test files. Expected: MAD/LG/SAS values differ from hybrid-v2 expectations.

- [ ] **Step 3: Integrate the shared formulas**

Keep current class names and public method signatures. Each corrected class adds `calculate_for_plan_with_warnings(plan) -> tuple[value, list[str]]`; existing `calculate_for_plan(plan)` remains a wrapper returning only `value`. Add explicit beam-MU aggregation and preserve tuple results for Halcyon/Ethos layer-specific metrics. Do not change CyberKnife's dedicated `cyberknife_metrics.py` path.

- [ ] **Step 4: Verify GREEN**

Run focused formula and integration tests plus `tests/test_cyberknife_metrics.py` to prove the CyberKnife subset is unchanged.

- [ ] **Step 5: Commit only clean feature files/hunks**

Do not stage any pre-existing unrelated changes.

## Task 4: Add traditional mean leaf travel and explicit NL outputs

**Files:**
- Modify: `vcomx_vmat_metrics.py`
- Modify: `tests/test_hybrid_metric_integration.py`
- Modify: `tests/test_motion_metrics.py`

- [ ] **Step 1: Write failing supplemental-output tests**

Assert that a synthetic beam returns:

```python
metrics["lt"] == legacy_expected_lt
metrics["lt_mean_leaf"] == traditional_expected_lt
metrics["nl"] == metrics["nl_pairs"]
metrics["nl_leaves"] == 2 * metrics["nl_pairs"]
```

Also assert the stored representative plan retains its baseline MCS/AAV/LSV/PA/JA/LT values.

- [ ] **Step 2: Verify RED**

Expected: new keys are missing while legacy assertions pass.

- [ ] **Step 3: Implement new outputs without changing legacy calculations**

Add `lt_mean_leaf`, `nl_pairs`, and `nl_leaves` to `MLC_DEPENDENT_KEYS`. Set `nl` from the exact `nl_pairs` result after aggregation so the alias cannot drift. Use the shared raw-trajectory helper for `lt_mean_leaf`; leave existing `ca_lt`/`lt` logic untouched.

- [ ] **Step 4: Verify GREEN and legacy baselines**

Run focused tests and recompute the representative real plan. Expected: new keys appear and preserved metrics match the recorded baseline exactly at current rounding precision.

## Task 5: Propagate formula provenance and calculation warnings

**Files:**
- Modify: `analysis_helpers.py`
- Modify: `ucomx_service.py`
- Modify: `analysis_exports.py`
- Test: `tests/test_hybrid_metric_integration.py`
- Test: `tests/test_analysis_helpers.py`

- [ ] **Step 1: Write failing API/export tests**

Test that VMAT/IMRT results include:

```python
result.metadata["metric_formula_version"] == "hybrid-v2"
```

Test export records include `metric_formula_version`, invalid weights append a warning beginning `[METRIC_WEIGHT_FALLBACK]`, and existing `calculate_core_metrics(plan_dict)` still returns a plain metrics mapping.

- [ ] **Step 2: Verify RED**

Expected: provenance and warning-path assertions fail.

- [ ] **Step 3: Add the metrics-plus-warnings path**

Implement `calculate_core_metrics_with_warnings(plan_dict) -> tuple[dict, list[str]]`; call the warning-aware MAD/LG/SAS methods and the warning-aware Halcyon helper, deduplicate warning strings, and retain `calculate_core_metrics(plan_dict)` as a wrapper returning only the first tuple item. Make `ucomx_service.analyze_plan_file` use the warning-aware function only for VMAT/IMRT and merge its warnings with existing mode warnings.

- [ ] **Step 4: Add provenance to structured and CSV exports**

Add the metadata key only for VMAT/IMRT. Include it in `build_export_record`, metadata rows, and fixed CSV base metadata without changing TOMO/Aurora/CyberKnife formula metadata.

- [ ] **Step 5: Verify GREEN**

Run API, export, VMAT, TOMO, Aurora, and CyberKnife service tests.

## Task 6: Add a jaw-aware stacked Halcyon aperture view

**Files:**
- Create: `ApertureMetric/stacked_aperture.py`
- Modify: `tests/test_hybrid_metric_formulas.py`

- [ ] **Step 1: Write failing stacked-view tests**

Build two layers whose leaf-width coordinates would be clipped if naively concatenated along Y. Assert:

```python
stacked.active_pair_count == layer1.active_pair_count + layer2.active_pair_count
stacked.area() == layer1.area() + layer2.area()
stacked.leaf_pairs[-1_of_layer1].next_is_first_of_layer2
```

Test that original width, left/right position, jaw state, layer ID, and slot ID are retained.

- [ ] **Step 2: Verify RED**

Expected: stacked view module is missing.

- [ ] **Step 3: Implement the view**

Create immutable leaf-pair views exposing the methods needed by shared and MCS helpers: `field_size`, `field_area`, `open_leaf_width`, and `is_outside_jaw`. Create an aperture view exposing ordered `leaf_pairs`, `gantry_angle`, and `area`. Order all MLCX1 slots first, then MLCX2 slots. Evaluate jaw state from each source aperture before concatenation.

- [ ] **Step 4: Verify GREEN**

Run stacked-view tests and confirm the artificial cross-layer adjacency is present exactly once when both layers contain slots.

- [ ] **Step 5: Commit the clean new module and its isolated tests**

```powershell
git add -- ApertureMetric/stacked_aperture.py tests/test_hybrid_metric_formulas.py
git commit -m "feat: add stacked dual-layer aperture view"
```

## Task 7: Add Halcyon effective and stacked hybrid metric families

**Files:**
- Modify: `halcyon_dual_layer_metrics.py`
- Modify: `tests/test_halcyon_dual_layer_paper_metrics.py`
- Modify: `tests/test_hybrid_metric_integration.py`

- [ ] **Step 1: Write failing synthetic Halcyon tests**

Use aligned layer control points with intentionally offset openings. Assert the complete key families from the spec, including aliases:

```python
assert metrics["mcsv_effective"] == metrics["mcs5"]
assert metrics["pa_effective"] == metrics["pa5"]
assert flattened["nl_pairs_stacked"] == flattened["nl_pairs_mlcx1"] + flattened["nl_pairs_mlcx2"]
assert metrics["mcsv_effective"] != metrics["mcsv_stacked"]
```

Also test `lt_effective` versus `lt_mean_leaf_effective` units/aggregation and `None` families for mismatched layer CP counts.

- [ ] **Step 2: Verify RED**

Expected: effective aliases and stacked keys are missing.

- [ ] **Step 3: Extend `LayerControlPoint` and beam aggregation**

Store a stacked aperture view beside distal, proximal, and effective apertures. Reuse shared formulas for MAD/LG/SAS/LT/NL. Reuse existing MCS/AAV/LSV helpers while applying the defined artificial boundary and per-slot AAV normalization. Keep all current Tamura/Quintero values unchanged.

- [ ] **Step 4: Implement alignment failure policy**

Add `calculate_halcyon_dual_layer_metrics_with_warnings(plan_dict) -> tuple[dict, list[str]]` and keep the existing metrics-only function as a compatibility wrapper. Detect unequal paired CP series before metric aggregation. Return all effective/stacked keys with `None` and warning `[HALCYON_LAYER_ALIGNMENT]`; never truncate or aggregate only valid beams. Keep layer-specific metrics.

- [ ] **Step 5: Verify GREEN with synthetic and real fixtures**

Run the Halcyon test file. If `data/Halcyon` exists, analyze at least one real plan and assert finite layer/effective/stacked outputs and explicit non-physical stacked descriptions.

## Task 8: Register, flatten, export, and validate every new output

**Files:**
- Modify: `metric_registry.py`
- Modify: `metric_definition_catalog.py`
- Modify: `analysis_exports.py`
- Create: `validation/hybrid_v2_formula_oracles.py`
- Modify: `tests/test_metric_definition_exports.py`
- Modify: `tests/test_analysis_helpers.py`
- Create: `tests/validation/test_hybrid_v2_formula_oracles.py`

- [ ] **Step 1: Write failing registry/export tests**

Assert every new base/effective/stacked key has a unique registry entry, display label, description, unit/formula catalog entry, flattened value, and CSV column. Assert stacked descriptions contain “non-physical” or equivalent unambiguous wording. Assert `None` exports as a blank CSV cell.

- [ ] **Step 2: Verify RED**

Expected: registry and catalog completeness tests report missing keys.

- [ ] **Step 3: Add registry and catalog records**

Register `lt_mean_leaf`, `nl_pairs`, `nl_leaves`, all `*_effective`, and all `*_stacked` keys. Keep `nl` and its label. Mark only layer-specific tuple metrics as `dual_mlc`; effective and stacked outputs are plan scalars.

- [ ] **Step 4: Extend formula oracles**

Add the hand-calculated oracles for corrected MAD, weighted LG/SAS, mean-leaf LT, NL aliases, and stacked/effective divergence in the new standalone `hybrid_v2_formula_oracles.py` module. Leave the pre-existing untracked `validation/formula_oracles.py` and `tests/validation/test_formula_oracles.py` files untouched and unstaged.

- [ ] **Step 5: Verify GREEN**

Run registry, catalog, export, and validation-oracle tests.

## Task 9: Run focused and full code verification

**Files:**
- Modify only if tests expose an in-scope defect.

- [ ] **Step 1: Run focused formula and integration tests**

```powershell
.venv\Scripts\python.exe -m pytest tests/test_hybrid_metric_formulas.py tests/test_hybrid_metric_integration.py tests/test_metric_formulas.py tests/test_halcyon_dual_layer_paper_metrics.py -q
```

- [ ] **Step 2: Run cross-mode regression tests**

```powershell
.venv\Scripts\python.exe -m pytest tests/test_tomo_metrics.py tests/test_cyberknife_metrics.py tests/test_aurora_metrics.py tests/test_analysis_helpers.py -q
```

- [ ] **Step 3: Run the full suite**

```powershell
.venv\Scripts\python.exe -m pytest -q
```

Record pass/fail/skip counts and investigate every new failure before proceeding.

- [ ] **Step 4: Recalculate representative real plans**

Run one conventional single-layer plan and one Halcyon plan when fixtures exist. Compare preserved values against Task 1 and inspect all new outputs for finiteness, units, and expected relationships.

- [ ] **Step 5: Inspect the feature diff against the recorded dirty baseline**

Confirm no pre-existing user change was removed, rewritten, or accidentally staged.

## Task 10: Synchronize all living repository documentation

**Required sub-skill:** Use `document-release` after code verification.

**Files:**
- Create: `docs/hybrid_v2_migration.md`
- Modify as warranted: `README.md`
- Regenerate: `docs/metric_definitions_all.md`
- Regenerate: `docs/metric_definitions_vmat_imrt.md`
- Regenerate: `output/metric_definitions_all.csv`
- Audit/update as warranted: every non-archival Markdown file listed by `rg --files -g "*.md"`

- [ ] **Step 1: Inventory and classify every document**

Read every Markdown file. Classify it as living user documentation, living research/validation documentation, generated metric reference, run artifact, or archival spec/plan. Historical specs/plans are “Current/archival” unless their links are broken; do not rewrite their historical content.

- [ ] **Step 2: Update the primary user documentation**

Update README feature lists, output keys, Halcyon three-representation explanation, warning behavior, and test commands. Add a discoverable link to `docs/hybrid_v2_migration.md`.

- [ ] **Step 3: Write the migration guide**

Document intentional changes to MAD/ALG/ALG SD/SAS, preserved MCS/AAV/LSV/PA/JA/LT, the `nl` alias, new units, formula version, effective versus stacked meaning, and guidance for directly calling `rtplan-complexity` in an independent comparison workflow.

- [ ] **Step 4: Regenerate formula documentation from the catalog**

Run:

```powershell
.venv\Scripts\python.exe tools/export_metric_definitions.py
```

Inspect generated diffs and ensure TOMO, Aurora, and CyberKnife sections did not change unintentionally.

- [ ] **Step 5: Cross-reference research, validation, and clinical documents**

Update only factual statements contradicted by the implementation. In particular audit `docs/research/README.md`, `project_design_summary.md`, `analysis_plan.md`, `shared_code_extraction.md`, `research_guardrails.md`, `docs/reference_pack_v1.md`, and `docs/clinical_implementation_sop.md`. Preserve research-only/clinical-readiness limitations.

- [ ] **Step 6: Audit run-report documentation and discoverability**

Check `run_reports/validation/validation_summary.md` for formula-version claims. Do not rewrite generated validation results without rebuilding them. Ensure every living document is reachable from README or `docs/research/README.md`.

- [ ] **Step 7: Verify documentation consistency**

Run metric-definition export tests, repository-hygiene tests, Markdown link/path checks available in the repo, and `git diff --check`. Report every audited file as Updated, Current, Generated, or Archival.

## Task 11: Final review and handoff

**Required sub-skill:** Use `superpowers:requesting-code-review`.

- [ ] **Step 1: Request independent code review**

Provide the approved spec, this plan, starting SHA, ending SHA, exact changed files, test evidence, and the recorded pre-existing dirty-file baseline. Ask specifically for formula correctness, warning propagation, Halcyon stacked non-physical labeling, and accidental user-change loss.

- [ ] **Step 2: Fix Critical and Important findings using TDD**

For every valid issue, write or tighten a failing regression test before editing production code, then rerun focused and full verification.

- [ ] **Step 3: Run fresh completion verification**

Run the full test suite, representative real-plan calculations, formula export generation/checks, and `git diff --check` in the final state. Read all output before making completion claims.

- [ ] **Step 4: Report documentation health and concerns**

List code changes, intentional metric changes, preserved metrics, new keys, Halcyon representations, test counts, real-plan evidence, every documentation file status, and any unavailable fixture or pre-existing unrelated failure.
