# Plan Complexity Metrics Shared-Code Extraction

> Imported on 2026-08-12 from the legacy unified-workspace snapshot's `02_Code/extraction_note.md`.
> This document records deferred architecture work; it does not authorize an extraction or create a runtime dependency on the legacy workspace.

## Source Project

`Plan_Complexity_Metrics` is the source project for candidate complexity-metric extraction. Its authoritative continuation is this repository; see the [codebase comparison](codebase_comparison_2026-08-11.md) and [data and migration provenance](data_and_migration_provenance.md) for the consolidation boundary.

## Extraction Boundary

- Candidate shared code belongs in a shared package only after metric definitions, system assumptions, tests, and project-specific analysis dependencies are separated. The legacy proposal named `03_Shared_Code/complexity_metrics` as a possible destination; that historical path is not a current runtime dependency.
- Keep project-specific validation runs, local data paths, reference text, and manuscript logic in this project.
- Stable code must not move to a shared package until project-specific analysis dependencies have been separated from the reusable metric API.

## Required Verification

- Preserve the existing [PlanComplexity test suite](../../tests/).
- Add independent shared-code tests for any extracted metric APIs.
- Confirm units, DICOM requirements, and system-specific interpretation before extraction.
