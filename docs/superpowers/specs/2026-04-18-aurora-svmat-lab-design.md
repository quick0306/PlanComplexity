# Aurora SVMAT Lab Design

## Goal

Build a standalone research prototype for NeuRT Aurora SVMAT plan analysis that does not couple to the existing `PyUCoMX` application or service layer. The prototype will parse Aurora RTPLAN files, recover axial and rotational delivery trajectories, calculate Aurora-specific spiral-coupled complexity metrics, and present results through a lightweight desktop GUI and CSV export.

## Why A Separate Program

This work is exploratory research rather than a stable production extension of the current platform. The existing codebase is already responsible for VMAT/IMRT, TOMO, and CyberKnife workflows. Aurora SVMAT introduces a different delivery model built around coupled gantry rotation, dual-layer MLC modulation, and axial motion. Keeping this effort separate avoids contaminating the existing product with experimental logic, private-tag reverse engineering, and evolving metric definitions.

## Confirmed Input Facts

Based on the inspected sample `RTPLAN_57661.dcm` and the supplied SVMAT papers:

- The plan is a dynamic Aurora SVMAT plan produced by `DeepPlan`.
- The machine uses a dual-layer staggered MLC:
  - `MLCX1`: 30 leaf pairs
  - `MLCX2`: 29 leaf pairs
- Each treatment beam contains `406` control points.
- Standard RTPLAN control points expose:
  - `GantryAngle`
  - `DoseRateSet`
  - `CumulativeMetersetWeight`
  - `IsocenterPosition`
  - `BeamLimitingDevicePositionSequence`
- The axial trajectory is already visible in `IsocenterPosition[2]`.
- Private creator `WISTECH` is present.
- Private tag `(4001,1004)` varies once per control point and is strongly correlated with the axial motion.
- Private tag `(4001,1005)` appears once per beam and behaves like a fixed reference coordinate.

## Scope

### In Scope

- Aurora SVMAT RTPLAN parsing
- Aurora-specific control-point trajectory reconstruction
- Aurora-specific complexity metrics based on coupled gantry, aperture, MU, and axial motion
- Single-file analysis
- Directory batch analysis
- CSV export
- A standalone Tkinter GUI
- Clear research-use disclaimers in the UI and export metadata

### Out Of Scope

- Integration into `PyUCoMX`
- Reuse of `ucomx_service.py` as an application dependency
- RT Dose, RT Structure Set, or CT driven complexity metrics
- Clinical decision support
- Finalized vendor-validated delivery semantics for every private tag
- Packaging into the current production executable during the first pass

## High-Level Architecture

The new program will live in a dedicated package directory:

```text
aurora_svmat_lab/
  __init__.py
  models.py
  parser.py
  metrics.py
  service.py
  gui.py
  cli.py
  export.py
  notes.py
```

### Module Responsibilities

#### `models.py`

Defines small, explicit data structures for:

- plan metadata
- beam summary
- control point trajectory sample
- aperture state
- metric value records
- analysis results

These models are specific to Aurora SVMAT and avoid importing the existing project result models.

#### `parser.py`

Reads RTPLAN and constructs Aurora-specific internal models.

Responsibilities:

- identify Aurora / DeepPlan plans
- extract standard beam and control-point fields
- extract dual-layer leaf positions from `MLCX1` and `MLCX2`
- extract axial position from `IsocenterPosition[2]`
- extract private `WISTECH` tags for audit and optional fallback
- reconstruct beam trajectories in delivery order
- expose derived per-control-point values such as:
  - delta gantry angle
  - delta axial position
  - delta MU weight
  - axial travel per degree

`IsocenterPosition[2]` is the primary axial source. `(4001,1004)` is stored for consistency checks and fallback handling.

#### `metrics.py`

Implements the first-pass Aurora research metrics.

Planned metrics:

- `axial_travel_mm`
  - total longitudinal travel over the analyzed delivery
- `gantry_rotation_deg`
  - total gantry rotation accumulated from adjacent control-point differences
- `mm_per_deg`
  - axial travel normalized by gantry rotation
- `mm_per_rotation`
  - axial travel normalized by 360 degrees
- `pitch_consistency`
  - variability of axial advancement per degree
- `mu_per_mm`
  - meterset modulation density along the longitudinal axis
- `aperture_change_per_mm`
  - change in aperture geometry normalized by axial motion
- `leaf_travel_per_mm`
  - cumulative leaf motion normalized by axial travel
- `coupled_modulation_index`
  - a research composite derived from concurrent variation in aperture, MU, and axial progression

This first version intentionally favors interpretable sub-metrics over a single opaque score.

#### `service.py`

Coordinates:

- parsing
- metric calculation
- warnings
- unsupported status
- batch execution
- export-ready flattening

This module is the internal application boundary for the standalone Aurora program.

#### `export.py`

Produces:

- per-plan CSV rows
- optional beam-level CSV rows
- optional control-point trajectory CSV rows for research debugging

#### `notes.py`

Defines short GUI-facing descriptions for the Aurora metrics and trajectory fields.

#### `gui.py`

Builds a small standalone Tkinter desktop interface for:

- file selection
- directory selection
- running analysis in the background
- viewing plan metadata
- viewing beam trajectory summary
- viewing metric notes
- exporting CSV

The GUI should follow the same research disclaimer style already used in the existing project, but remain completely independent from the old interface code.

#### `cli.py`

Provides a scriptable entry point for:

- single-file analysis
- directory analysis
- CSV export
- optional verbose trajectory summary

## Data Flow

1. User selects one RTPLAN or a directory of RTPLAN files.
2. `parser.py` loads DICOM and validates Aurora-specific prerequisites.
3. The parser reconstructs beam-level control-point trajectories.
4. `metrics.py` calculates per-beam and per-plan research metrics.
5. `service.py` assembles a normalized analysis result.
6. `gui.py` or `cli.py` renders or exports the result.

## Unsupported And Warning Rules

The program must fail clearly and safely instead of silently producing misleading values.

Unsupported conditions include:

- missing `BeamSequence`
- missing dynamic control-point sequence
- missing both standard axial trajectory and usable private fallback
- missing dual-layer MLC geometry
- non-Aurora RTPLAN mistakenly given to the tool

Warnings include:

- private trajectory differs materially from standard `IsocenterPosition[2]`
- beam direction metadata disagrees with observed angle progression
- incomplete control-point geometry
- non-monotonic axial progression within a beam

## Metric Philosophy

The first version is intended to answer a research question:

> How strongly does the plan couple longitudinal motion, gantry rotation, MLC modulation, and MU delivery?

That means the prototype should not merely reuse VMAT aperture metrics with a new label. Instead, it should normalize change against axial progression or against coupled angular-axial travel where appropriate.

## Testing Strategy

The Aurora prototype will include dedicated tests that do not depend on the existing `tests/` application contract.

Planned test layers:

- parser unit tests for control-point extraction
- regression test using the supplied Aurora sample RTPLAN
- metric tests on small synthetic trajectories
- export tests for CSV column stability
- GUI smoke test limited to object construction where practical

## Deliverables For The First Implementation Pass

- standalone Aurora package directory
- CLI entry point
- Tkinter GUI entry point
- RTPLAN parser
- first set of Aurora-specific metrics
- CSV export
- tests for parser, metrics, and export
- README section or dedicated prototype note describing scope and non-clinical status

## Risks And Mitigations

### Risk: private-tag meaning is not fully vendor-documented

Mitigation:

- prefer standard DICOM fields whenever available
- treat private tags as supporting evidence and fallback
- expose warnings rather than hiding ambiguity

### Risk: early metric definitions are too heuristic

Mitigation:

- keep metrics interpretable and decomposed
- avoid compressing everything into one score in v1
- document formulas and assumptions next to the code

### Risk: accidental coupling back into the existing app

Mitigation:

- place all code in a dedicated package
- avoid importing `ucomx_service.py`, `ucomx_gui.py`, and current application models
- keep independent tests and entry points

## Success Criteria

The first-pass prototype is successful if it can:

- open the supplied Aurora RTPLAN
- reconstruct coupled axial and rotational motion from RTPLAN
- compute a stable set of Aurora research metrics
- export results to CSV
- show the results in a small standalone GUI
- remain fully independent from the existing `PyUCoMX` runtime path
