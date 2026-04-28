# PlanComplexity

Utilities for parsing RT Plan DICOM files and calculating plan complexity metrics, with a
desktop GUI inspired by UCoMX.

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

Batch export metrics for standard linac plans:

```bash
python metrics_mit.py --input-dir path/to/plans --output-csv eclipse.csv
```

Batch export metrics for Halcyon/Ethos-style plans:

```bash
python complexity_metrics_analysis.py --input-dir path/to/plans --output-csv RTPlan1.csv
```

Use `--recursive` if the input directory contains nested folders.

Use `--verbose` on any script to include debug logging.

Run the minimal test suite:

```bash
python -m unittest discover -s tests
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
python tools/run_reference_suite.py --profile research --output-dir run_reports/validation
python tools/run_tool_comparison.py --profile research --output-dir run_reports/validation
python tools/build_validation_report.py --profile research --output-dir run_reports/validation
```

These commands produce `reference_case_results.json`, `reference_case_results.csv`,
`comparator_statistics.csv`, `validation_summary.md`, `validation_report.json`,
`supplement_tables/`, and `manifest_lock.json` under `run_reports/validation/`.
The full artifact rebuild requires the referenced RTPLAN files under `data/`; when running
from a separate worktree, pass `--source-root path/to/PlanComplexity` to point at the data root.
The validation bundle is research/publication evidence support and is not clinical deployment ready.

Build a standalone Windows GUI executable:

```powershell
.\.venv\Scripts\python.exe -m pip install PyInstaller
.\tools\build_windows_exe.ps1
```

The packaged GUI is created at `dist\PyUCoMX.exe`.

## Aurora SVMAT Lab

`Aurora SVMAT Lab` is a standalone experimental research prototype for NeuRT Aurora SVMAT RTPLAN analysis.
It is intentionally separate from the main `PyUCoMX` workflow.

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
- Several VMAT/IMRT metrics were aligned with the UCoMX manual formulas, including:
  - `Leaf Gap` aggregation over all active leaf pairs.
  - `Small Aperture Score` as a whole-plan fraction of active leaf gaps below threshold.
  - `Mean Asymmetry Distance` using the UCoMX Eq. (5) leaf-end distance definition.
- `MLC Speed and Acceleration Proportions (Park 2015)` follow:
  - Park JM, et al. Br J Radiol 2015;88(1049):20140698.
  - DOI: `10.1259/bjr.20140698`
  - Speed bins in the program are reported in `mm/s`: `0-4`, `4-8`, `8-12`, `12-16`, `16-20`.
  - Acceleration bins in the program are reported in `mm/s^2`: `0-40`, `40-80`, `80-120`, `120-160`, `160-200`.
  - Each proportion is computed as the mean of per-leaf proportions over valid control-point intervals.
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
