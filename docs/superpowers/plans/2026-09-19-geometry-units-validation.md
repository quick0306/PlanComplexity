# Geometry, Units, and Reference Validation Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development for bounded tasks and independent review. The user approved the preceding code-review recommendations and implementation order on 2026-09-19.

**Goal:** Fix verified geometry/unit defects, prove them with independent hand cases, make reference failures actionable, and migrate audited baselines with formula provenance.

**Architecture:** Preserve the existing public analysis entrypoints. Carry each MLC device's absolute boundaries into aperture construction; centralize perimeter and aperture-series normalization/LSV helpers. Interpret TOMO row units from documented source semantics, validate normalized ranges, and keep ambiguous inputs explicitly unavailable. Record formula versions separately from scalar metric values.

**Tech Stack:** Python, NumPy, pydicom, pytest/unittest, existing YAML/JSON validation infrastructure.

## 1. Geometry and units

- [x] Add failing hand cases in `tests/test_geometry_regressions.py`: 10 mm square perimeter 40 mm, PI 4/pi, EFS 10 mm; closed/disconnected rows; symmetric X/Y jaw area 100 mm2; 28/29-layer preservation; native proximal edge area 100 mm2; jaw-closing/reversed MCSv 0.6.
- [x] Fix `ApertureMetric/aperture_geometry.py`, `aperture_creator.py`, and `halcyon_dual_layer_metrics.py`: per-device boundaries and shape validation; complete perimeter; no native-layer cropping. Maintain declared effective/stacked representation meanings.
- [x] Add failing TOMO unit and dose cases in `tests/test_tomo_parser.py`; fix `tomo_parser.py` without guessing undocumented units. Validate all rows, reject mixed/unknown sources, handle terminal zero rows consistently, and convert course dose to fraction dose using a valid fraction group.
- [x] Run focused tests after each change and investigate affected existing expectations rather than automatically rewriting them.

## 2. Independent formula tests

- [x] Extend `validation/formula_oracles.py` with geometry, dynamic-jaw normalization, layer-offset, and unit/dose checks based on explicit mathematical answers.
- [x] Run `python -m pytest tests/test_geometry_regressions.py tests/test_tomo_parser.py tests/validation/test_formula_oracles.py -q` and the formula oracle CLI.

## 3. Validation failure propagation

- [x] Test then fix `tools/run_reference_suite.py` CLI to return nonzero for failed strict reference validation.
- [x] Ensure CI runs new numerical regression tests, including pytest function tests omitted by the old unittest-only selection.

## 4. Versioned, audited reference migration

- [x] Capture existing reference artifacts before replacement. Assign explicit new VMAT/IMRT and TOMO formula versions; preserve unrelated domains and external comparator samples.
- [x] Extend reference loading/freezing/evaluation to retain and check formula provenance with backwards-compatible handling of legacy test fixtures.
- [x] Compute current reference results, enumerate every changed metric, and check changes against the corrected primitives or independent recomputation. Update only justified expected values; document exceptions and unavailable results.
- [x] Rebuild validation outputs without patient identifiers and record version, baseline migration, and exact-gate outcomes.

## 5. Shared implementation and completion

- [x] Consolidate duplicated AAV/LSV and perimeter calculations behind tested helpers; retain wrappers when callers rely on them.
- [x] Update metric documentation and migration notes for changed formulas and TOMO input semantics.
- [x] Run focused then full tests and reference suite; independently review the diff; preserve unrelated untracked `output/software_copyright/` files.

No source DICOM files are modified. No external comparator values are regenerated from this implementation. Baseline agreement is regression evidence, not an independent validation claim.

## Execution evidence

- Geometry and unit regressions were observed failing before their fixes; additional closed-Y-jaw and omitted-axis inheritance cases were added during review.
- The independent raw-reference audits verify 1,417 apertures/segments and explain all 60 TOMO scalar changes. Numerical results are archived with the migration.
- Six baselines now require geometry-v3/tomo-v2; six old scalar files are preserved byte-for-byte. All 106 changed values and 37 previously unfrozen keys are enumerated.
- The actual reference CLI returned 1 with missing formula provenance before migration and 0 after migration: 8 cases, 517 rows, 269 exact rows, no exact/provenance/analysis failures.
- Report refresh and missing-key-versus-null regressions were fixed and tested. Compact reports preserve the strict gate; final report hashes and baseline hashes were checked.
- Headless Python 3.11 suite: 232 passed, 1 skipped, 1 deselected, 39 subtests passed. Formula oracle gate: 12 passed. GUI-only Python 3.14 run: 4 passed; the full run initially hit an intermittent Tcl/Tk initialization error and was retried with explicit local Tcl/Tk library paths.
- Final full Python 3.14 suite with explicit matching Tcl/Tk library paths: **236 passed, 1 skipped, 39 subtests passed**. This resolves the test invocation environment without changing GUI code.
