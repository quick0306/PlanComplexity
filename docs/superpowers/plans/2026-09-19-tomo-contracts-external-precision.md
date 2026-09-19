# TOMO motion, formula contracts, external evidence and precision

> **For agentic workers:** Use superpowers:subagent-driven-development with bounded file ownership and independent review. The user has approved this scope; preserve the current uncommitted geometry/unit fixes.

**Goal:** Correct planned TOMO couch motion, make formula variants explicit, obtain traceable external evidence, and compare unrounded numerical results with independent synthetic tests.

**Architecture:** Read native couch speed/pitch only from the recognized private creator and track source/availability. Keep full precision in computation and round only the existing presentation path. Extend the metric catalog with explicit contracts and qualify external comparisons by source, definition, version and input identity. Archive prior expected outputs before any baseline migration.

**Tech Stack:** Python, pydicom, NumPy/SciPy, pytest, JSON/YAML, existing validation reporting.

- [x] TOMO: add failing synthetic tests for private couch speed/pitch, zero/missing motion, fixed-angle mode, inheritance and terminal projections; implement parser/model changes and source metadata. Files: tomo_parser.py, tomo_metrics.py, tests/test_tomo_parser.py, tests/test_tomo_service.py, docs/tomo_input_contract.md.
- [x] Contracts: inspect every exported scalar against its formula, sampling, active-leaf mask, units, aggregation, missing-value rule and formula version. Register explicit variants and verification status; test catalog coverage and rectangular/range counterexamples. Files: metric_definition_catalog.py, new metric_formula_contracts.py, tests/test_metric_formula_contracts.py, docs/metric_formula_contracts.md.
- [x] External evidence: inspect existing local UCoMX outputs read-only; match inputs and record tool/version/config/output hashes. Add provenance-qualified mapping/import and tests rejecting unverified or mismatched evidence. If actual external outputs are unavailable, retain that state explicitly and use a pinned runnable independent implementation with public synthetic inputs. Never label project-generated expected values as independent truth.
- [x] Precision: remove lossy arithmetic output rounding from the calculation path, retain existing presentation formatting, and ensure validation consumes raw flattened metrics. Test an error hidden by two-decimal rounding and full-precision baseline serialization. Files: calculation modules, ucomx_models.py, ucomx_service.py, validation_runtime.py, tests/test_metric_precision.py.
- [x] Integrate: advance formula versions where numerical semantics change; archive geometry-v3/tomo-v2 outputs and hashes, regenerate only after independent checks, record metric deltas. Expand hand-derived boundary tests, run focused then full tests, execute strict reference validation, refresh reports, and obtain independent spec/code review.

No source DICOM modifications, no public upload of local data, and no commit or push are part of this task. Existing unrelated output/software_copyright files are preserved.

Verification and remaining evidence limits are recorded in docs/precision_motion_validation.md. Core and GUI tests passed in separate runs; mixed-suite Tk initialization remains unstable. Actual historical external values are captured, while formula equivalence and successful live external reproduction remain unestablished. No commit or push was made.
