# Plan Complexity Research Guardrails

> Imported on 2026-08-11 from legacy project instructions and retained as scientific documentation.

## Scientific Focus

The project preserves plan-complexity-metric research and tooling across TOMO, VMAT/IMRT, Aurora SVMAT, and related validation workflows.

## Data Traceability

- Validation fixtures, reference text, and `run_reports/` evidence retained during the legacy Phase 2 snapshot remain part of the traceability record, governed by current repository-hygiene and privacy rules; this statement does not assert that all run-report contents are tracked.
- Project `data/` retained during the legacy Phase 2 snapshot exists only in this authoritative repository's local working state. It remains Git-ignored and must not be committed.
- Generated `output/` artifacts remain source-side in this authoritative repository unless a later recorded decision establishes why they are needed elsewhere.
- Metric definitions, assumptions, and test evidence are tracked before any code is extracted into a shared package.

## System-specific Boundaries

Complexity thresholds cannot transfer across TOMO, Aurora, VMAT, IMRT, CyberKnife, Halcyon, or Ethos without system-specific justification.

## Shared-code Boundary

Stable code belongs in shared packages only after project-specific analysis dependencies have been separated. This boundary prevents shared-code extraction from obscuring system-specific assumptions or evidence requirements.

## UCoMX Evidence Boundary

UCoMX reference material is contextual evidence unless the deferred `ucomx` decision is revisited; it does not independently establish validation, equivalence, or clinical readiness.
