# PlanComplexity

Utilities for parsing RT Plan DICOM files and calculating plan complexity metrics across
VMAT/IMRT, TOMO, CyberKnife MLC, and Aurora SVMAT plans, with a desktop GUI inspired by UCoMX.

## Requirements

- Python 3.10+
- Packages in `requirements.txt`

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Scripts

Launch the desktop GUI:

```bash
python ucomx.py
```

Analyze a single RT Plan file:

```bash
python main.py --input-file path/to/plan.dcm
```

The main analyzer auto-detects VMAT/IMRT, TOMO, CyberKnife MLC, and Aurora SVMAT RTPLAN files.

Batch export metrics for standard linac plans:

```bash
python metrics_mit.py --input-dir path/to/plans --output-csv eclipse.csv
```

Batch export metrics for Halcyon/Ethos-style plans:

```bash
python complexity_metrics_analysis.py --input-dir path/to/plans --output-csv RTPlan1.csv
```

Halcyon/Ethos dual-layer MLC support includes the paper-specific metrics from Tamura et al. 2020
and Quintero et al. 2021:

- Tamura-style effective 5 mm metrics: `MCS5`, `PA5`, `PI5`, `PM5`, and `EDS`.
- Tamura-style weighted layer metrics: `MCSw`, `PAw`, `PIw`, and `PMw`, with proximal/distal
  component outputs.
- Quintero-style Halcyon-v2 metrics: `MUcp`, `UL`, `MCSUL`, and `NP`.
- Hybrid-v2 physical effective-aperture metrics use the `*_effective` suffix.
- RT Complexity Lens-inspired stacked diagnostics use the `*_stacked` suffix. This geometry is
  deliberately non-physical: it concatenates jaw-evaluated MLCX1 and MLCX2 slots for algorithm
  comparison and must not be interpreted as a transmitted aperture.

VMAT/IMRT and CyberKnife analyses record `metric_formula_version=geometry-v4`; TOMO records
`tomo-v3`. The current [precision and motion migration](docs/precision_motion_validation.md),
[per-metric formula contracts](docs/metric_formula_contracts.md), and
[TOMO input contract](docs/tomo_input_contract.md) describe units, boundaries, and unavailable
results. The [preceding hybrid-v2 contract](docs/hybrid_v2_metrics.md) documents the retained
MU-weighted MAD/LG/SAS definitions, `lt_mean_leaf`, explicit leaf counts, and Halcyon representations.
The project does not provide an `RT_LENS` mode or vendor the upstream implementation; independent
comparisons may call `matteomaspero/rt-complexity-lens` directly.

Validation explicitly requests `analyze_plan_file(..., full_precision=True)`; the default
analysis output retains legacy rounding. The [external benchmark capture](docs/external_benchmarks.md)
records real UCoMX workbook cells and source/config hashes with its provenance and formula limitations.

Use `--recursive` if the input directory contains nested folders.

Use `--verbose` on any script to include debug logging.

Run the full test suite, including independent numerical hand cases:

```bash
python -m pytest tests -q
```

Run the Aurora-focused standalone prototype tests:

```bash
python -m unittest tests.test_aurora_parser tests.test_aurora_metrics tests.test_aurora_export tests.test_aurora_service tests.test_aurora_gui_smoke -v
```

Run the research validation gates:

```bash
python -m unittest tests.validation.test_validation_smoke tests.validation.test_metric_specs tests.validation.test_spec_loaders tests.validation.test_validation_runtime tests.validation.test_reference_manifest tests.validation.test_freeze_reference_outputs tests.validation.test_reference_suite tests.validation.test_tool_comparison tests.validation.test_validation_report -v
```

Rebuild the Phase 1 research validation evidence bundle:

```bash
python tools/run_formula_oracles.py --output-dir run_reports/validation
python tools/build_paper_reproduction_table.py --output-dir run_reports/validation
python tools/run_reference_suite.py --profile research --output-dir run_reports/validation
python tools/run_tool_comparison.py --profile research --output-dir run_reports/validation
python tools/build_comparator_matrix.py --output-dir run_reports/validation
python tools/build_validation_report.py --profile research --output-dir run_reports/validation
python tools/run_clinical_readiness_gate.py --output-dir run_reports/validation
```

These commands produce `reference_case_results.json`, `reference_case_results.csv`,
`comparator_statistics.csv`, `validation_summary.md`, `validation_report.json`,
`formula_oracles.json`, `paper_reproduction_table.json`, `comparator_matrix.json`, `clinical_readiness_gate.json`,
`supplement_tables/`, and `manifest_lock.json` under `run_reports/validation/`.
The full artifact rebuild requires the referenced RTPLAN files under `data/`; when running
from a separate worktree, pass `--source-root path/to/PlanComplexity` to point at the data root.
The validation bundle is research/publication evidence support and is not clinical deployment ready.
The reference command exits nonzero on a failed strict gate, including formula-version or
expected support-state mismatches. Scalar baselines have separate formula-version and SHA256
provenance; see the [reference pack](docs/reference_pack_v1.md) before updating them.

Optional PSQA/SPC and endpoint association scaffolds are available for institution-approved,
de-identified local datasets:

```bash
python tools/run_psqa_spc_analysis.py --input-csv psqa_metrics.csv --metric-key mcs --output-dir run_reports/validation
python tools/run_clinical_endpoint_association.py --input-csv endpoints.csv --metric-key mcs --endpoint-key qa_fail --output-dir run_reports/validation
```

These tools provide harmonization/control-chart and association-only evidence layers. They do not
make clinical deployment claims without approved local QA and endpoint data.

Reference Pack v1 details and open-source packaging constraints are documented in
`docs/reference_pack_v1.md`. Clinical implementation controls are documented in
`docs/clinical_implementation_sop.md` and `docs/deployment_rollback.md`.

Build a standalone Windows GUI executable:

```powershell
.\.venv\Scripts\python.exe -m pip install PyInstaller
.\tools\build_windows_exe.ps1
```

The packaged GUI is created at `dist\PyUCoMX.exe`.

## Aurora SVMAT Lab

`Aurora SVMAT Lab` remains the focused experimental research module for NeuRT Aurora SVMAT RTPLAN analysis.
Aurora plan-level metrics are also available through the main `PyUCoMX` analyzer, GUI, batch CSV export,
and `AUTO` mode alongside VMAT/IMRT, TOMO, and CyberKnife MLC.

Launch the standalone Aurora GUI:

```bash
python aurora_svmat.py
```

Run the standalone Aurora CLI:

```bash
python aurora_svmat_cli.py --input-file path/to/RTPLAN.dcm --verbose
```

Optional Aurora CSV exports:

```bash
python aurora_svmat_cli.py --input-file path/to/RTPLAN.dcm --output-csv aurora_plan.csv --beam-output-csv aurora_beams.csv --trajectory-output-csv aurora_trajectory.csv
```

Aurora prototype scope in the current version:
- Aurora / DeepPlan RTPLAN parsing
- Coupled axial and rotational trajectory reconstruction
- V2 Aurora research metrics centered on paper-style physical quantities:
  - longitudinal travel
  - total rotation and rotations
  - travel per rotation
  - projection pitch mean / variability
  - projection MU-density proxy mean / variability
  - projection aperture-change mean / variability
  - projection leaf-travel mean / variability
  - theta-z, MU-z, and MLC-z coupling variability
- Legacy engineering metrics are still exported for comparison
- Standalone CSV export and desktop GUI

The Aurora prototype is for research use only. Clinical use is strongly forbidden.

## Notes

- The batch scripts now skip unsupported files instead of deleting them.
- Input files are expected to be DICOM RT Plan files readable by `pydicom`.
- `ucomx.py` / `ucomx_gui.py` provide a Python desktop workflow for:
  - VMAT/IMRT analysis using the existing DICOM/aperture metric engine.
  - TOMO analysis using a new sinogram-based metric engine built from the UCoMX/TCoMX references.
  - CyberKnife MLC analysis using the paper-limited six-metric subset (`MCS`, `EM`, `PI`, `PM`, `LG`, `SAS10`).
- The GUI metric panel now uses paper-oriented naming for the two motion metrics discussed below and
  includes a `Metric Notes` pane with short definitions.
- CSV export now writes two files:
  - The requested result table, for example `results.csv`.
  - A companion column dictionary, for example `results_columns.csv`.
- Folder batch analysis now uses light parallelism for independent RT Plan files, and
  beam-level geometry/meterset objects are cached during a single-file analysis pass.
- Code paths have been standardized on `snake_case` module and API naming.
- VMAT/IMRT default formulas use `geometry-v4`, retaining these `hybrid-v2` definitions:
  - `MAD` is the MU-weighted mean absolute aperture-center distance from the beam central axis.
  - `ALG`/`ALG SD` and `SAS` are calculated per control point and then MU weighted; SAS includes
    only jaw-overlapping, strictly positive gaps in its denominator.
  - Legacy dose-weighted `LT` remains unchanged; `LT Mean Leaf` reports raw trajectory travel per
    moving physical leaf.
  - Legacy `NL` remains and equals `NL Pairs`; `NL Leaves` is exactly twice that value.
- `MLC Speed and Acceleration Proportions (Park 2015)` follow:
  - Park JM, et al. Br J Radiol 2015;88(1049):20140698.
  - DOI: `10.1259/bjr.20140698`
  - Speed bins in the program are reported in `mm/s`: `0-4`, `4-8`, `8-12`, `12-16`, `16-20`.
  - Acceleration bins in the program are reported in `mm/s^2`: `0-40`, `40-80`, `80-120`, `120-160`, `160-200`.
  - Each proportion is computed as the mean of per-leaf proportions over valid control-point intervals.
  - These bins require a valid control-point time model. RTPLAN-only exact calculation is
    unavailable when the plan does not provide usable timing inputs, such as nonzero
    dose rate, known machine maximum gantry speed, or delivery timestamps.
  - For the current Elekta Monaco/Oncentra RTPLAN exports, `CumulativeMetersetWeight`
    is present but `DoseRateSet` is absent or zero and the machine is identified only
    by local IDs. In that state the Park speed/acceleration bins are intentionally
    reported as unavailable/`NaN` rather than treated as delivery-accurate values.
  - Elekta Park-style values can be added only as explicitly labeled estimates if a
    site-specific machine profile supplies the missing timing assumptions.
    Delivery-accurate values require treatment delivery logs or another timestamped
    machine record.
- `SPORT Modulation Index (Li and Xing 2013)` follows:
  - Li R, Xing L. Med Phys. 2013;40(5):050701.
  - DOI: `10.1118/1.4802748`
  - The implementation keeps the paper's station-wise `MI(s)` definition and reports the framework's
    aggregated beam/plan summary for GUI and CSV export.
- `CyberKnife MLC` mode follows the MLC-based plan-complexity study:
  - Masi L, et al. Med Phys. 2021.
  - DOI: `10.1002/mp.14667`
  - The current implementation intentionally covers only the paper's MLC-based scope and reports:
    `MCS`, `EM`, `PI`, `PM`, `LG`, and `SAS10`.
  - Fixed-cone and Iris collimator plans are not included because their collimation geometry is not dynamically modulated.
- Some TOMO RTPLAN variants store sinogram data in vendor-specific tags. The parser includes
  standard and private-tag fallbacks, but different Tomo TPS exports may still require
  additional tag mapping.
