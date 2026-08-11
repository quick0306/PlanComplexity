# Plan_Complexity_Metrics Research Question

> Imported on 2026-08-11 from the legacy unified-workspace snapshot.
> This document records research framing and evidence boundaries; it is not completed clinical evidence.

## Source Evidence

- This repository is the authoritative source for Plan_Complexity_Metrics code, tests, policies, fixtures, and ongoing work; the legacy unified-workspace copy is historical provenance only.
- Current repository evidence includes metric code for VMAT/IMRT, TOMO, CyberKnife MLC, Aurora SVMAT, Halcyon/Ethos, GUI/CLI entry points, docs, tests, validation framework, and [`run_reports/`](../../run_reports/) evidence governed by current repository-hygiene and privacy rules; this statement does not assert that all run-report contents are tracked.
- `data/` is retained only in this authoritative repository's local working state. It remains Git-ignored and must not be committed.
- Generated `output/` artifacts remain source-side in this authoritative repository and are indexed rather than copied elsewhere.

## Primary Research Question

For Plan_Complexity_Metrics, which system-specific plan complexity metrics can be computed, validated, and reported reproducibly from the authoritative repository's code, data, and run-report evidence without implying cross-system equivalence?

## Secondary Design Questions

- Which metrics and delivery systems are primary analysis targets versus exploratory examples?
- Which validation gates, fixtures, and run reports are sufficient to support each metric definition?
- Which stable metric components can later be extracted to the historically proposed `03_Shared_Code/complexity_metrics` location with independent tests?

## Answerable With Current Repository Evidence

- The current validation bundle can support metric-definition traceability, system-labeled test coverage, and reproducibility checks for existing data/run reports.
- The repository can document methods/tool evidence and research validation limits for system-specific complexity analysis.

## Requires Future Evidence

- Any manuscript-ready comparison requires locked metric sets, system groupings, statistical summaries, and output-table definitions.
- Clinical QA thresholds or deliverability conclusions require additional independent validation beyond current research evidence.

## Out of Scope

- Do not claim universal complexity thresholds, cross-platform metric equivalence, or clinical deployment readiness from the current validation bundle alone.

## Required Inputs

- Metric definitions, DICOM requirements, validation fixtures, run reports, system labels, and reference-pack assumptions.

## Evidence Boundary

Do not transfer complexity thresholds across TOMO, Aurora, VMAT, IMRT, CyberKnife, Halcyon, or Ethos without system-specific justification.

## Traceability

Link refined questions to [data and migration provenance](data_and_migration_provenance.md), metric definitions, [tests](../../tests/), validation evidence, and output tables.
