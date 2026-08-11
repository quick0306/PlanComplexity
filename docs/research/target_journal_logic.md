# Plan_Complexity_Metrics Target Journal Logic

> Imported on 2026-08-11 from the legacy unified-workspace snapshot.
> This document records research framing and evidence boundaries; it is not completed clinical evidence.

## Source Evidence

- This repository is the authoritative source for system-specific plan complexity metrics; the legacy unified-workspace copy is historical provenance only.
- Current repository evidence includes metric code, validation framework, `data/`, [`run_reports/`](../../run_reports/), docs, tests, and system labels.
- Evidence is strongest for research and tool validation support, not clinical deployment readiness or universal thresholds.

## Candidate Article Types

- Methods or tool paper: strongest if the final article emphasizes metric definitions, implementation reproducibility, and validation gates.
- QA implementation report: plausible if a specific clinical workflow and system subset are selected.
- Broad clinical validation study: only appropriate after independent validation and clinical endpoint assumptions are documented.

## Candidate Journal Logic

- A medical physics methods/tool venue is plausible for system-specific metric definitions and validation evidence.
- JACMP-style framing is plausible if the focus becomes practical QA implementation, reproducibility, and local validation boundaries.
- A high-level clinical journal is not a natural first fit unless future evidence links metrics to clinically meaningful endpoints.

## Current Best Fit

Methods/tool paper or QA implementation report, with claims constrained to system-specific validation evidence.

## Evidence Gates Before Journal Selection

- Select primary metrics and delivery systems versus exploratory examples.
- Lock validation fixtures, run reports, system groupings, output tables, and figure plan.
- Define which parts are project-specific and which can later become shared `complexity_metrics` code.

## Out of Scope Claims

- Do not claim universal complexity thresholds, cross-system metric equivalence, clinical deliverability validation, or deployment readiness.
- Do not treat implementation breadth as validation depth.

## Not a Final Submission Decision

This file records candidate framing logic only. Journal instructions, article types, and formatting limits must be checked on the target journal website when a manuscript version exists.

## Required Inputs

- Target journal scope, validation expectations, metric reporting requirements, figure/table plan, and selected article type.

## Evidence Boundary

Journal framing must not imply universal metric transferability or clinical deliverability validation.

## Traceability

Record journal instructions, date checked, manuscript version, validation evidence, system labels, and matching analysis outputs.
