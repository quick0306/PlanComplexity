# Plan_Complexity_Metrics Project Design Summary

> Imported on 2026-08-11 from the legacy unified-workspace snapshot.
> This document records research framing and evidence boundaries; it is not completed clinical evidence.

## Source Evidence

- This repository is the authoritative source for Plan_Complexity_Metrics code, tests, policies, fixtures, and ongoing work; the legacy unified-workspace copy is historical provenance only.
- The authoritative scope includes Python modules for VMAT/IMRT, TOMO, CyberKnife MLC, Aurora SVMAT, Halcyon/Ethos, GUI/CLI entry points, docs, tests, validation framework, `data/`, and `run_reports/`.
- The [project README](../../README.md) documents CLI/GUI entry points, Aurora SVMAT Lab, validation gates, reference-pack artifacts, and clear research-only caveats.

## Current Data or Dependency Boundary

- `data/` and [`run_reports/`](../../run_reports/) are retained in this repository for internal verification and validation evidence.
- The legacy source data/evidence included 238 data files (about 220.54 MB) and 21 run-report files (about 1.33 MB); these counts are retained as historical provenance rather than asserted as the current inventory.
- Generated `output/` remains outside the authoritative repository and is indexed as historical evidence rather than copied into it.

## Required Inputs

- Metric definitions, DICOM RTPLAN/XML/workbook examples, validation manifests, run reports, reference text, and system-specific assumptions.

## Evidence Boundary

- Complexity metrics must remain system-specific across TOMO, Aurora, VMAT/IMRT, CyberKnife, Halcyon, and Ethos.
- Existing validation bundle supports research/publication evidence support; it is not clinical deployment readiness.

## Next Design Decisions

- Define the primary manuscript frame: methods, tool, validation, or QA implementation.
- Choose which metrics and systems are primary versus exploratory.
- Decide which stable code can move to the historically proposed `03_Shared_Code/complexity_metrics` location after independent tests are in place.

## Not Yet Evidence

- This summary does not create universal thresholds, clinical deployment claims, or cross-system metric equivalence.

## Traceability

Use [data and migration provenance](data_and_migration_provenance.md), [validation tests](../../tests/), [`run_reports/`](../../run_reports/), and metric-definition documentation as the source-to-evidence chain.
