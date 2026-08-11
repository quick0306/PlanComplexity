# Data and Migration Provenance

> Imported on 2026-08-12 from the 2026-05-22 legacy unified-workspace snapshot.
> This document preserves migration-time provenance; it does not override current repository policy or describe a current inventory.

## Historical Snapshot

The May 2026 migration copied a source-first snapshot from `C:\Users\hujin\Desktop\Programming\PlanComplexity` to `D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics` as part of the Phase 2 fourth batch on 2026-05-22. The source directory was not modified.

At migration time, the source repository was on branch `main`, ahead of `origin/main` by 17 commits, with modified workflow, source, test, and validation files and multiple untracked validation and documentation files. The snapshot intentionally reflected that working tree at copy time.

The current repository at `C:\Users\hujin\Desktop\Programming\PlanComplexity` is authoritative. The legacy location at `D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics` is historical provenance only. These path strings document where the migration occurred; they are not runtime dependencies and must not be used by executable instructions, tests, scripts, workflows, or runtime configuration.

## Copied Scope

The May 2026 snapshot copied:

- Python source modules for VMAT/IMRT, TOMO, CyberKnife MLC, Aurora SVMAT, and Halcyon/Ethos metrics;
- GUI and CLI entry points;
- `ApertureMetric/`, `ComplexityMetric/`, `DicomParse/`, and `aurora_svmat_lab/`;
- `docs/`, `reference_text/`, `tests/`, `tools/`, and `validation/`;
- the `data/` verification data chain;
- the `run_reports/` validation evidence bundle; and
- requirements, license, README, and the project `.gitignore`.

## Data and Evidence Inventory at Migration Time

The following counts and sizes describe the migration-time source inventory exactly; they are not assertions about the current repository inventory.

| Source path | File count | Size | May 2026 copy decision |
|---|---:|---:|---|
| `data/` | 238 | 220.54 MB | Copied into the legacy snapshot. |
| `run_reports/` | 21 | 1.33 MB | Copied into the legacy snapshot. |
| `output/` | 12 | 0.72 MB | Not copied; retained at the authoritative source location for reference. |

At migration time, `data/` contained RTPLAN, XML, and workbook examples across Aurora, CyberKnife, Halcyon, Monaco/Elekta, Oncentra/Elekta, Precision, RayStation, TOMO, Trilogy, and TrueBeam workflows. `run_reports/` contained prior validation evidence and summary artifacts. `output/` was treated as generated output and indexed rather than copied.

In the current repository, `data/` exists only in the authoritative local working state, is Git-ignored, and must not be committed. `run_reports/` is governed by current repository-hygiene and privacy rules; its inclusion in the historical snapshot does not assert that all current run-report contents are tracked. The migration-time treatment of `output/` does not assert a current tracking status for every output artifact.

## Technical Exclusions

The May 2026 snapshot excluded:

- `.git/`;
- `.venv/`;
- `.worktrees/`;
- `.idea/`;
- `.pytest_cache/`;
- `__pycache__/`;
- `build/`;
- `dist/`;
- `output/`;
- compiled `.exe` files;
- `.pdb` symbol files; and
- Python bytecode files.

The legacy snapshot's migrated `.gitignore` allowed `run_reports/**/*.csv` as an exception to the default `*.csv` ignore rule so copied validation CSV evidence remained traceable there. That migration-specific behavior is not authoritative and does not change current repository hygiene or privacy policy.

## Current Authority

The current repository is the source of truth for code, tests, policies, fixtures, data handling, validation evidence, and ongoing work. The legacy directory was a point-in-time snapshot, not a successor implementation, and contained no later Python implementation absent from the current repository. Nothing should be copied back from the legacy snapshot in a way that replaces current behavior or weakens current privacy controls.

## Decommissioning Note

After consolidation review confirms that the substantive research, migration, and deferred-work records have been preserved in the current repository, the legacy snapshot can be discarded. Its historical paths remain documented here for traceability and do not need to remain accessible at runtime.
