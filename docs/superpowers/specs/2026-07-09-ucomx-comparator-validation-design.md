# UCoMX Comparator Validation Design
> Imported on 2026-08-11 from the legacy unified-workspace snapshot.
> Status: approved historical design for unimplemented future work.

## Goal

Build a checked-in UCoMX comparator evidence layer for `Plan_Complexity_Metrics` so the project can support a multi-system complexity calculation and validation technical report, improve clinical trust for research use, and prepare a safer open-source release pathway.

This phase targets checked-in external comparator evidence, not automatic execution of UCoMX in CI.

## Source Context

The local UCoMX program and historical output evidence are available at:

```text
C:\Users\hujin\Desktop\Programming\ucomx
```

Observed UCoMX assets include:

- `UCoMX.mlapp`, `vcomx/VCoMX.p`, and `tcomx/TCoMX.p`
- UCoMX reference PDFs under `ref/`
- VCoMX extraction outputs under UCoMX `data/`, including `dataset.xlsx`, named dataset workbooks, `CONFIG.in`, `METRICS.in`, `dataset.mat`, and `logfile.txt`
- Output workbooks with `metrics`, `statistics`, and `info` sheets

The `info` sheets contain patient and institution fields, including names, dates, identifiers, and local paths. Raw UCoMX output workbooks must therefore be treated as internal evidence unless explicitly normalized and reviewed for release.

## Evidence Level

Use Evidence Level B: checked-in UCoMX output comparison.

This means:

- UCoMX/VCoMX/TCoMX historical output files are accepted as external golden comparator evidence.
- The project does not require Matlab Runtime or the UCoMX executable in automated tests.
- External comparator values are normalized into public-safe tables before entering routine tests.
- UCoMX program files are not copied into this repository.

## Scope

### In Scope

- UCoMX evidence-pack directory structure
- UCoMX output normalization from Excel workbooks to public-safe CSV
- Manifest-based provenance, checksums, and release safety metadata
- Metric mapping between UCoMX names and internal metric keys
- Exact-equivalent, derived-equivalent, and non-comparable comparison semantics
- Automated tests for normalized UCoMX comparator outputs
- Report artifacts for the technical report
- Clinical and open-source readiness gate updates

### Out Of Scope

- Automatic Matlab or UCoMX execution in CI
- Bundling UCoMX application files into this project
- Publishing raw clinical DICOM, raw UCoMX Excel `info` sheets, or PHI-bearing outputs
- Creating universal complexity thresholds
- Claiming clinical deployment readiness or standalone QA pass/fail capability

## Evidence Pack Layout

Add a controlled external comparator area:

```text
validation/
  external_comparators/
    ucomx/
      manifest.yaml
      mapping.yaml
      raw/
        README.md
      normalized/
        ucomx_metrics.csv
        ucomx_statistics.csv
      reports/
        ucomx_comparison_report.json
        ucomx_comparison_report.csv
        ucomx_comparison_summary.md
```

### `manifest.yaml`

Records comparator provenance and release status.

Required fields should include:

- `comparator`: `UCoMX`
- `comparator_version`
- `source_root`
- `source_workbooks`
- `generated_at`
- `normalized_by`
- `case_id_strategy`
- `deidentification_status`
- `public_release_allowed`
- `checksums`
- `notes`

The manifest may record the local UCoMX source root, but must not require that path for public tests once normalized evidence is checked in.

### `raw/`

Stores internal audit guidance only by default. Raw Excel files should not be copied into the open-source release path unless a separate data-governance decision marks them public safe.

### `normalized/`

Stores release-safe comparator tables. The main table should use a narrow schema:

```text
case_id,source_dataset,source_filename,comparator_metric,comparator_value,unit,comparator_engine,relationship_hint,notes
```

Allowed content:

- pseudonymous case IDs
- normalized source filename labels if needed for traceability
- numeric metric values
- units and metric labels
- method notes

Disallowed content:

- patient names
- birth dates
- MRN or patient ID
- Study/Series/SOP Instance UID
- local PHI-bearing folder names
- institution-specific identifiers not needed for metric comparison

### `mapping.yaml`

Maps external UCoMX fields to internal metric keys and comparison classes.

Initial VMAT/IMRT VCoMX exact-equivalent candidates include:

- `LT` -> `lt`
- `LTMU` -> `ltmu`
- `LTNLMU` -> `ltnlmu`
- `LTNL` -> `ltnl`
- `LNA` -> `lna`
- `MUdeg` -> `mudeg`
- `LTAL` -> `ltal`
- `MCSv` -> `mcsv`
- `AAV` -> `aav`
- `LSV` -> `lsv`
- `SAS5mm` -> `sas_5mm`
- `SAS10mm` -> `sas_10mm`
- `SAS20mm` -> `sas_20mm`
- `MAD` -> `mad`

`LG` should be mapped only if a VMAT/IMRT leaf-gap metric is explicitly present in the internal metric inventory. The current checked inventory contains `lg` for the CyberKnife MLC subset, which is not a VCoMX exact-equivalent claim.

Mappings must record relationship semantics:

- `exact-equivalent`: same definition, unit, case scope, and aggregation
- `derived-equivalent`: same conceptual family but layer flattening, device handling, or aggregation differs
- `not-comparable`: tracked for transparency, but excluded from numeric pass/fail

## Data Flow

```text
UCoMX workbook metrics sheet
  -> normalize UCoMX output
  -> public-safe comparator rows
  -> load PyUCoMX metric output for matched RTPLAN cases
  -> apply mapping and tolerances
  -> emit comparison artifacts
  -> update validation summary and readiness gates
```

The comparator layer should remain separate from the existing reference-case exactness gate. Reference-case validation proves PyUCoMX regression stability. UCoMX comparison proves external agreement for metrics that are truly comparable.

## Test Design

### Unit Tests

Add tests for:

- UCoMX manifest schema loading
- mapping schema loading
- normalized CSV loading
- PHI field rejection for normalized comparator rows
- unknown metric and unknown case rejection
- relationship classification

### Integration Tests

Add tests that:

- load normalized UCoMX comparator rows
- run or load PyUCoMX outputs for matched cases
- compare exact-equivalent metrics within tolerance
- emit JSON, CSV, and Markdown comparison artifacts
- fail when exact-equivalent metrics exceed tolerance

### Readiness Tests

Extend readiness checks with:

- `ucomx_pack_ready`
- `ucomx_comparison_green`
- `no_public_phi`
- `raw_data_is_internal_only`
- `clinical_claims_guard`

## Tolerances

Default tolerance for exact-equivalent UCoMX metrics:

- absolute tolerance: `1e-4`
- relative tolerance: `1e-4`

Metric-specific tolerances may be added when:

- UCoMX rounds exported values
- PyUCoMX preserves higher precision
- a documented unit conversion is required

Any metric-specific tolerance must be visible in `mapping.yaml` or a linked tolerance spec.

## Report Artifacts

The UCoMX comparator runner should produce:

```text
ucomx_comparison_report.json
ucomx_comparison_report.csv
ucomx_comparison_summary.md
```

The main validation report should then include a UCoMX section summarizing:

- number of matched cases
- number of exact-equivalent comparisons
- number of failures
- MAE, bias, and RMSE by metric
- skipped or non-comparable metrics
- known limitations

## Technical Report Structure

Write the technical report as a multi-system tool and validation report, with explicit evidence tiers.

Recommended sections:

1. Intended Use and Scope
2. Supported Delivery Systems
3. Metric Inventory and Definition Sources
4. UCoMX Comparator Evidence
5. Reference Suite Validation
6. Known Non-comparability and System-specific Assumptions
7. Clinical Governance Notes
8. Open-source Release Readiness
9. Reproducibility Appendix

## Claim Boundaries

Allowed claims:

- PyUCoMX calculates a documented multi-system metric inventory.
- Selected VMAT/IMRT metrics are externally compared against checked-in UCoMX/VCoMX output evidence.
- TOMO, CyberKnife MLC, Aurora, and Halcyon/Ethos-specific metrics are validated through reference cases, formula tests, and literature-defined assumptions where applicable.
- The tool can support research, publication evidence, and local clinical physics review.

Disallowed claims:

- Universal complexity thresholds
- Cross-platform metric equivalence without system-specific justification
- Clinical deployment readiness
- Standalone treatment-plan pass/fail decisions
- Replacement of patient-specific QA

## Open-source Release Policy

Open-source release is allowed only when:

- normalized UCoMX comparator files are public safe
- raw UCoMX workbooks and raw DICOM files are absent from the public package
- manifest checksums pass
- exact-equivalent UCoMX comparisons pass
- clinical claims remain research-bound

If raw comparator workbooks are needed for internal audit, store them outside the public release bundle or in a protected internal package.

## Implementation Notes

The first implementation should prioritize:

1. Normalized UCoMX evidence from a small TrueBeam and Halcyon subset
2. Exact-equivalent mapping for core VCoMX VMAT/IMRT metrics
3. Artifact generation and tests
4. Readiness gate integration
5. Technical report draft

This keeps the first milestone useful while leaving room for larger UCoMX/TCoMX evidence expansion later.
