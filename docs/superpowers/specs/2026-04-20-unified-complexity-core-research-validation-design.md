# Unified Complexity Core Research Validation Design

## Goal

Build a unified research-grade validation framework for the current PlanComplexity project that:

- standardizes complexity metric definitions across supported modalities and devices
- validates formula correctness and reference-case reproducibility
- harmonizes comparisons against existing tools and literature where appropriate
- produces publication-ready and open-source-reproducible evidence artifacts

This first phase is explicitly `research/publication-ready`, not clinical deployment ready.

## Why This Phase Comes First

The current repository already has strong metric-calculation foundations, real multi-platform RTPLAN datasets, targeted formula tests, and diagnostic scripts. What is still missing is a single validation layer that turns those scattered assets into a reproducible evidence package.

Without that layer, later PSQA/SPC and clinical endpoint work would be built on metric definitions that are not yet fully normalized across platforms, comparator sources, and validation semantics.

## Phase 1 Scope

Phase 1 will implement `Unified Complexity Core for Research Validation`.

### In Scope

- canonical metric specification for all user-facing complexity metrics
- cross-platform reference-case validation
- exact, derived-equivalent, and association-only comparison semantics
- comparator mapping to external tools and literature
- reproducible validation runners and report artifacts
- inclusion of Aurora within the same validation framework
- support for the currently analyzed domains:
  - VMAT/IMRT
  - TOMO
  - CyberKnife MLC
  - Aurora SVMAT Lab

### Out Of Scope

- patient-level clinical endpoint modeling
- machine-level SPC threshold policy or alerting logic
- internal clinical deployment SOPs
- claims of clinical validation completion
- claims that the software is ready for clinical use

## Design Principles

### 1. Validation is separate from computation

The existing runtime analysis code should remain responsible for parsing and metric calculation. The new validation framework should consume standardized outputs from that runtime layer rather than reimplement formulas inside the validation code.

### 2. One canonical metric definition per metric

Each metric must have one canonical record describing what it means, how it is aggregated, how it may be compared, and what level of validation is expected.

### 3. Comparability must be explicit

Metrics that share a name but differ in units, normalization, aggregation, or scope must not be treated as exact equivalents. The framework must encode those differences directly.

### 4. Research transparency over hidden convenience

Skipped comparisons, unsupported cases, missing evidence, and known non-comparability must appear in the final artifacts rather than being silently dropped.

## High-Level Architecture

The first phase adds a standalone validation architecture that sits beside the current application modules.

```text
validation/
  specs/
    metric_specs.yaml
    metric_groups.yaml
    comparator_mapping.yaml
    validation_profiles.yaml
  reference_cases/
    manifest.yaml
    cases/
      <case_id>/
        expected_metrics.json
        provenance.json
        notes.md
  schemas/
    metric_spec.schema.json
    reference_case.schema.json
    comparator_mapping.schema.json
    validation_report.schema.json
  reports/
    templates/
      validation_summary.md.j2
      comparison_table.csv.j2
  utils/
    tolerances.py
    statistics.py
    comparators.py
    loaders.py
    serializers.py
```

Additional execution and bridge modules:

```text
tools/
  run_reference_suite.py
  run_tool_comparison.py
  build_validation_report.py
  freeze_reference_outputs.py

validation_models.py
validation_runtime.py
```

## Module Responsibilities

### `validation/specs/metric_specs.yaml`

Single source of truth for research validation semantics per metric.

Each metric record should include at least:

- `key`
- `label`
- `mode`
- `unit`
- `aggregation_scope`
- `normalization_basis`
- `validation_level`
- `comparison_class`
- `default_tolerance_abs`
- `default_tolerance_rel`
- `expected_range`
- `clinical_readiness`
- `known_noncomparability`
- `comparable_to`
- `assumptions`
- `exclusions`

### `validation/specs/metric_groups.yaml`

Defines logical families for reporting and supplement tables, such as:

- aperture geometry
- modulation
- motion and trajectory
- sinogram
- Aurora coupled-motion metrics

### `validation/specs/comparator_mapping.yaml`

Defines how internal metrics relate to:

- UCoMX/VCoMX/TCoMX outputs
- literature tables or supplementary material
- vendor or prior-tool exports when available

Each mapping must explicitly state whether the relationship is:

- `exact-equivalent`
- `derived-equivalent`
- `association-only`
- `not-comparable`

### `validation/specs/validation_profiles.yaml`

Defines reusable tolerance and gating profiles, such as:

- `strict`
- `research`
- `paper-supplement`

Phase 1 will use `research` as the default reporting profile.

### `validation/reference_cases/manifest.yaml`

Declares the reference-case suite with metadata for each case:

- `case_id`
- `source_path`
- `domain`
- `device_or_tps`
- `expected_mode`
- `case_class` (`canonical` or `edge`)
- `expected_metrics_source`
- `tolerance_overrides`
- `checksum`
- `provenance`
- `notes`

### `validation/reference_cases/cases/<case_id>/expected_metrics.json`

Stores frozen expected values for exact-comparison metrics and any case-specific tolerances or skip rules.

### `validation/utils/statistics.py`

Implements shared statistics used by all comparison scripts, including:

- bias
- MAE
- RMSE
- correlation
- Bland-Altman summary
- CCC or ICC where appropriate

### `validation_runtime.py`

Provides the bridge from runtime analysis outputs into canonical validation records. It should:

- call the existing analysis layer
- normalize metric keys and metadata
- attach device, mode, and source provenance
- hand back comparison-ready metric payloads

## Relationship To Existing Code

### Runtime analysis remains in current modules

The validation framework should reuse the current runtime path centered on:

- `ucomx_service.py`
- `metric_registry.py`
- `aurora_svmat_lab/service.py`
- `aurora_svmat_lab/export.py`

### `metric_registry.py` becomes the programmatic registry entry point

The current registry already contains labels, aliases, descriptions, and DOI metadata. Phase 1 should evolve it toward the canonical in-code representation of the same concepts that are serialized in `validation/specs/metric_specs.yaml`.

GUI, CSV export, and validation should all derive from the same definition source rather than drifting independently.

### Existing scripts become seeds for the validation runners

The current scripts:

- `tools/diagnose_rtplans.py`
- `tools/export_real_dataset_csv.py`

already prove that the repository can scan the real dataset corpus and export summary artifacts. Phase 1 should absorb their useful behavior into the new validation runner structure instead of keeping one-off report scripts as the long-term interface.

## Validation Semantics

Not all metrics should be validated the same way. Phase 1 uses four evidence classes.

### 1. `Formula-exact`

For metrics with deterministic synthetic or hand-computable test cases.

Examples:

- MAD
- Leaf Gap
- SAS-style gap thresholds

These comparisons should pass only when the implementation agrees exactly or within negligible floating-point tolerance.

### 2. `Reference-case exact`

For real DICOM golden cases where the project and comparator share the same definition, units, and aggregation semantics.

These comparisons should use explicit absolute and/or relative tolerances defined in the metric spec or case manifest.

### 3. `Derived-equivalent`

For metrics whose scientific intent aligns but whose normalization, aggregation, or reported scope differs.

These should not be treated as simple pass/fail equalities. Instead, the framework must report:

- mapping basis
- transform rationale
- bias
- MAE
- RMSE
- Bland-Altman summary
- agreement coefficient where appropriate

### 4. `Association-only`

For literature or endpoint contexts where only directional or statistical association can be assessed rather than exact numeric equivalence.

These provide research evidence but do not contribute to the core exactness gate.

## Aurora Integration

Aurora should be included in Phase 1 within the same validation framework rather than deferred into a separate later annex.

However, Aurora should still keep its own evidence semantics because it is a newer research-facing subsystem with a different comparator landscape.

### Aurora in Phase 1 should include

- canonical metric specifications for current Aurora user-facing metrics
- Aurora-specific synthetic and reference-case validation where exact definitions are available
- Aurora-specific provenance and assumptions
- Aurora-specific comparison mappings when literature or companion exports exist
- Aurora report sections in the same artifact pipeline as the other domains

### Aurora should not be forced into false equivalence

If an Aurora metric has no exact external comparator, it should remain:

- `Formula-exact` when synthetic or internally frozen reference validation is possible
- `Association-only` or `not-comparable` when only conceptual alignment exists

This keeps Aurora unified at the framework level without pretending that its evidence maturity matches every legacy metric family.

## Data Sources Available For Phase 1

The current repository already contains the main ingredients for the first reference suite:

- multi-platform RTPLAN samples under `data/`
- UCoMX manual text under `reference_text/`
- real-dataset summary artifacts under `run_reports/`
- formula-oriented tests in `tests/`
- Aurora-specific formula PDF generation and tests

These existing assets should be formalized into versioned reference inputs rather than treated as ad hoc local experiments.

## Data Flow

Phase 1 validation runs should follow this sequence:

1. Load `metric_specs`, `metric_groups`, `comparator_mapping`, `reference_cases`, and the chosen `validation_profile`.
2. Validate all config files against their schemas.
3. Execute runtime analysis using the existing project analyzers.
4. Normalize outputs into canonical validation records.
5. Route each metric comparison according to its `comparison_class`.
6. Aggregate results at:
   - case level
   - metric level
   - domain level
   - device or TPS level
7. Build JSON, CSV, and Markdown artifacts for publication support and repository release evidence.

## Error Handling Semantics

### Schema or manifest errors

These are definition-layer failures and should fail fast.

### Unsupported parser or runtime cases

These must be recorded as `unsupported`, not misreported as formula failures.

### Missing comparator evidence

These must be recorded as `incomplete evidence`, not code failures.

### Known non-comparability

These must be surfaced as skipped results with explicit rationale.

### Exact-comparison mismatches

Every mismatch must preserve detailed payload fields such as:

- `expected`
- `observed`
- `abs_diff`
- `rel_diff`
- `tolerance_abs`
- `tolerance_rel`
- `tolerance_source`

## Output Artifacts

Phase 1 should generate a versionable evidence bundle under:

```text
run_reports/validation/
  reference_case_results.json
  reference_case_results.csv
  comparator_statistics.csv
  validation_summary.md
  supplement_tables/
  manifest_lock.json
```

The outputs should be suitable for:

- repository release artifacts
- paper methods support
- supplement table generation
- regression detection between commits

## First-Phase Acceptance Criteria

Phase 1 is complete when all of the following are true:

1. Every currently user-facing metric across VMAT/IMRT, TOMO, CyberKnife MLC, and Aurora has a canonical validation definition.
2. Each current analysis domain has at least one canonical case and one edge case in the reference suite.
3. All `Formula-exact` and `Reference-case exact` checks pass under the `research` profile.
4. All `Derived-equivalent` comparisons produce interpretable agreement statistics rather than simple correlation-only outputs.
5. A single command path can rebuild the main validation artifacts from repository state.
6. CI gates at minimum cover:
   - schema validation
   - reference-suite execution
   - validation-report build
7. All outward-facing text for Phase 1 remains explicitly research-oriented and avoids claims of clinical readiness.

## Deferred Roadmap

Once Phase 1 is stable, later work can extend the same framework into:

### Phase 2

- PSQA-oriented complexity harmonization
- SPC-oriented operational endpoint support
- device and workflow reproducibility studies

### Phase 3

- patient-level endpoint association
- internal or external cohort modeling
- deployment-specific governance and SOP packaging

## Success Definition

The practical success condition for Phase 1 is not merely that the code computes metrics. It is that the repository can prove, in a reproducible and reviewable way, what each metric means, where it agrees with known references, where it does not, and why.
