# Full precision, TOMO motion and external evidence

Active contracts: `geometry-v4` for VMAT/IMRT and CyberKnife, `tomo-v3` for TOMO.
The earlier physical aperture geometry is retained. This revision repairs planned
TOMO couch motion, preserves calculation precision for validation, and makes the
exported metric definitions and external evidence traceable.

## Numerical precision

`analyze_plan_file(path, full_precision=True)` propagates an instance-local option
through DICOM prescription/MU parsing, core metric aggregation, VMAT supplemental
metrics, native CyberKnife segment metrics, and Halcyon paper metrics. Validation
and baseline freezing use this path. Prescription cGy are not truncated to an
integer, and total MU are not rounded before ratios are calculated.

The default API retains the existing two-decimal outputs, four-decimal motion
profiles and six-decimal Halcyon paper outputs. The raw path does not reconstruct
digits from those values. TOMO mode statistics retain their explicit six-decimal
binning rule; that is part of the mode estimator, not output formatting.

NumPy MI triplets now export scalar `mis`, `mia`, `mit` components. Five native
dual-layer metrics use explicit `_mlcx1` / `_mlcx2` names instead of incidental
`_1` / `_2` tuple indices. JA and the formerly missing layer keys are registered.
These are deliberate schema changes recorded in the migration audit.

## TOMO planned motion

Only recognized private fields or complete standard trajectories establish motion.
Native couch speed is mm/s, and translation is speed times the duration of all
retained projections. Nominal width uses the maximum Y opening, including dynamic
jaws. Unknown/invalid/conflicting motion is unavailable; it is not zero. Fixed-angle
delivery is explicitly unsupported by the helical reader. The detailed
[input contract](tomo_input_contract.md) records source precedence and inference limits.

All 24 local native plans omit the explicit helical enum; the reader records its
inference from recognized helical pitch/period and regular rotating control points.
The two reference examples have travel 223.17343239215685 mm and 98.4505202 mm,
and estimated helical target length 198.07343239215686 mm and 73.3505202 mm.
These are planned geometric quantities, not measured delivery or contoured target length.
`validation/reference_cases/migrations/tomo-v3_native_motion_audit.json` records
the 24 input hashes and independent speed/count/period checks. Maximum absolute
travel difference was 1.14e-13 mm; all cases retained explicit inferred-geometry provenance.

## Evidence layers

- [Per-metric contracts](metric_formula_contracts.md) cover formulas, units, sampling,
  masks, normalization, aggregation, unavailable values, versions and source symbols.
  An implementation contract does not establish agreement with every source paper.
- `tests/test_metric_formula_contracts.py` distinguishes bank envelope, max-slot area
  and geometric union; range-normalized LSV; rectangular side-boundary EM; endpoint
  product-of-means MCS; and CP-balanced raw leaf-gap statistics.
- `tests/test_metric_precision.py` checks fractional hand answers, small errors hidden
  by rounding, raw prescription/MU, scalar MI exports and Halcyon aggregation.
- TOMO synthetic tests cover private creator identity, mm/s travel, retained projections,
  position inheritance, true zero, unknown/conflicting inputs, fixed angles and dynamic jaws.
- [External captures](external_benchmarks.md) retain actual workbook values and hashes.
  Unverified formula variants remain visible as differences and do not become exact gates.

## Baseline migration

Previous scalar files and sidecars are preserved byte-for-byte under
`validation/reference_cases/history/pre-geometry-v4-tomo-v3/`, with an archive hash list.
`tools/audit_precision_motion.py` verifies source hashes and compares 20 previously
independently audited unrounded geometry answers plus 10 newly recomputed raw-DICOM
motion answers. Its report is `validation/reference_cases/migrations/geometry-v4_tomo-v3_audit.json`.
Other recorded values are regression snapshots, not independent or external truth.

Baseline freezing requires explicit formula/schema migration flags and retains
case/domain/mode, source hash, scalar hash and generation time. The strict reference
suite checks provenance and expected supported state as well as numerical values.
Reference rows include `source_checksum` and `numeric_precision`; external pairing
requires matching input identity and full precision. Clinical readiness is not inferred
from a green regression suite or numerical agreement on one external case.

## Verification on 2026-09-19

- CI-style core suite: 331 passed, 1 skipped, 1 deselected, 39 subtests passed.
  Command: `python -m pytest tests --ignore=tests/test_aurora_gui_smoke.py --deselect=tests/test_aurora_service.py::AuroraServiceScaffoldingTests::test_aurora_entrypoints_call_real_main_functions -q`.
- Combined Windows suite before integration: 335 passed, 1 skipped, 39 subtests
  passed using Python 3.14.3: `.venv/Scripts/python.exe -m pytest tests -q -x --tb=short`.
  This includes all four real GUI smoke/entrypoint checks. No `TCL_LIBRARY` or
  `TK_LIBRARY` override was set.
- Earlier combined runs with explicit Tcl/Tk path overrides failed during Tk
  initialization despite the referenced files existing. The full run above passed
  without those overrides; the Tcl internal root cause has not been established.
  No product-code change or test exclusion was introduced to hide that failure.
- Strict reference suite: exit 0; 8 cases, 564 rows, 280 required numerical comparisons,
  zero numerical, formula-provenance or analysis-state failures.
- Twelve built-in formula oracles passed. The broader synthetic contracts, precision
  and TOMO tests are included in the core test count above.
- Six current baseline files match the independently checked migration snapshots and
  sidecar hashes. All twelve immediately preceding scalar/sidecar archives retain
  their recorded hashes. Migration: 239 changed values, 47 newly exported scalar keys.
- External capture: 1 historical input, 10 values, 6 candidate pairs, 0 verified
  equivalent definitions; importer integrity check passed. The attempted live opaque
  UCoMX execution failed and produced no workbook; its evidence remains separate.

Independent specification and code-quality reviews covered the precision path and
TOMO behavior. The review-discovered halfway-rounding compatibility regression was
fixed and is covered by a discriminating test. No clinical-readiness claim follows
from these results; the existing clinical-readiness report remains false.
