# Aurora SVMAT Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Aurora SVMAT research application that parses Aurora RTPLAN files, reconstructs coupled gantry-MLC-axial motion, computes Aurora-specific complexity metrics, and displays or exports the results without depending on the current `PyUCoMX` runtime path.

**Architecture:** Create a new `aurora_svmat_lab` package with its own parser, metric engine, service boundary, export helpers, GUI, CLI, and tests. Use standard RTPLAN control-point fields as the primary source of Aurora motion data, with `WISTECH` private tags as audit and fallback signals, and keep all Aurora logic isolated from `ucomx_service.py` and the existing metric registry.

**Tech Stack:** Python 3.14, `pydicom`, `numpy`, `pandas`, `tkinter`, `unittest`

---

## File Structure

### New Application Code

- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\__init__.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\models.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\parser.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\metrics.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\service.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\export.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\notes.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\gui.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\cli.py`

### New Top-Level Entrypoints

- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_cli.py`

### New Tests

- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_parser.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_metrics.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_export.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_service.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_gui_smoke.py`

### Supporting Documentation

- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\README.md`

### Optional Fixture Work

- If repository policy allows adding the sample plan:
  - Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\data\Aurora\RTPLAN_57661.dcm`
- If not:
  - Keep the regression test synthetic and use the external local file only for manual validation:
    - `D:\Obsidian\Web Clipper\001_inbox\RTPLAN_57661.dcm`

## Task 1: Scaffold The Standalone Aurora Package

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\__init__.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\models.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_cli.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_service.py`

- [ ] **Step 1: Write the failing scaffolding test**

```python
from aurora_svmat_lab import __all__


def test_aurora_package_exports_public_modules():
    assert "models" in __all__
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_service -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'aurora_svmat_lab'`

- [ ] **Step 3: Create the standalone package skeleton**

```python
# aurora_svmat_lab/__init__.py
__all__ = [
    "models",
    "parser",
    "metrics",
    "service",
    "export",
    "notes",
    "gui",
    "cli",
]
```

```python
# aurora_svmat.py
from aurora_svmat_lab.gui import main


if __name__ == "__main__":
    main()
```

```python
# aurora_svmat_cli.py
from aurora_svmat_lab.cli import main


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Add Aurora-specific data models**

Include dataclasses for:
- `AuroraPlanMetadata`
- `AuroraControlPoint`
- `AuroraBeam`
- `AuroraMetricValue`
- `AuroraAnalysisResult`

Keep field names explicit and detached from current `ucomx_models.py`.

- [ ] **Step 5: Run the test again**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_service -v`
Expected: PASS for the package export test

- [ ] **Step 6: Commit**

```bash
git add aurora_svmat_lab/__init__.py aurora_svmat_lab/models.py aurora_svmat.py aurora_svmat_cli.py tests/test_aurora_service.py
git commit -m "feat: scaffold standalone aurora svmat lab package"
```

## Task 2: Build Aurora RTPLAN Identification And Control-Point Parsing

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\parser.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_parser.py`

- [ ] **Step 1: Write a failing parser unit test with a synthetic RTPLAN-like object**

```python
def test_detects_aurora_dual_layer_dynamic_plan():
    dataset = build_fake_aurora_rtplan()
    parsed = parse_aurora_rtplan(dataset)
    assert parsed.metadata.manufacturer == "WisdomTech Medical Systems"
    assert len(parsed.beams) == 1
```

- [ ] **Step 2: Run the parser test**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_parser -v`
Expected: FAIL with `NameError` or missing parser module

- [ ] **Step 3: Implement Aurora plan detection**

Detection should require:
- RT Plan object with `BeamSequence`
- dynamic control points
- dual-layer `MLCX1` and `MLCX2`
- manufacturer/model hints compatible with Aurora / DeepPlan when available

Do **not** import or call `ucomx_service.detect_mode_from_file()`.

- [ ] **Step 4: Implement control-point extraction**

For each control point, parse:
- `gantry_angle_deg`
- `dose_rate_mu_per_min`
- `cumulative_meterset_weight`
- `isocenter_position_mm`
- `axial_position_mm` from `IsocenterPosition[2]`
- `jaw_x` / `jaw_y`
- `mlc_x1_positions_mm`
- `mlc_x2_positions_mm`
- `private_wistech_4001_1004`
- `private_wistech_4001_1005`

- [ ] **Step 5: Implement observed-trajectory reconstruction**

Compute adjacent deltas using the actual angle sequence rather than trusting `GantryRotationDirection`.

Create helper behavior like:

```python
def wrap_angle_delta(current_deg: float, next_deg: float) -> float:
    delta = next_deg - current_deg
    if delta > 180.0:
        delta -= 360.0
    if delta < -180.0:
        delta += 360.0
    return delta
```

- [ ] **Step 6: Add assertions for the real Aurora sample if available locally**

If using the supplied local file:
- beam count is `2`
- control point count is `406` for each beam
- dual-layer MLC is present
- axial motion is non-zero

- [ ] **Step 7: Run the parser tests**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_parser -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add aurora_svmat_lab/parser.py tests/test_aurora_parser.py
git commit -m "feat: parse aurora svmat rtplan control points"
```

## Task 3: Add Trajectory Normalization And Private-Tag Consistency Checks

**Files:**
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\parser.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_parser.py`

- [ ] **Step 1: Write the failing consistency test**

```python
def test_private_axial_track_is_exposed_for_consistency_checks():
    dataset = build_fake_aurora_rtplan(with_private_track=True)
    parsed = parse_aurora_rtplan(dataset)
    assert parsed.beams[0].warnings == []
```

- [ ] **Step 2: Run the specific test**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_parser.AuroraParserTests.test_private_axial_track_is_exposed_for_consistency_checks -v`
Expected: FAIL

- [ ] **Step 3: Implement consistency helpers**

Add parser logic that:
- compares `axial_position_mm` against `private_wistech_4001_1004`
- records a warning when the difference departs from the beam-specific reference offset beyond tolerance
- records a warning when control-point angle metadata direction disagrees with observed angle progression

Recommended tolerance starter:
- `0.5 mm` for axial-vs-private mismatch

- [ ] **Step 4: Store trajectory summaries on each beam**

Include:
- `total_axial_travel_mm`
- `total_gantry_rotation_deg`
- `mm_per_degree`
- `mm_per_rotation`
- `axial_direction_sign`

- [ ] **Step 5: Run parser tests again**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_parser -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add aurora_svmat_lab/parser.py tests/test_aurora_parser.py
git commit -m "feat: add aurora trajectory consistency checks"
```

## Task 4: Implement The Core Aurora Research Metrics

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\metrics.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_metrics.py`

- [ ] **Step 1: Write failing synthetic metric tests**

```python
def test_mm_per_rotation_uses_total_axial_travel_and_total_rotation():
    beam = build_synthetic_beam(total_axial_travel_mm=150.0, total_gantry_rotation_deg=1620.0)
    metrics = calculate_beam_metrics(beam)
    assert metrics["mm_per_rotation"] == 150.0 / (1620.0 / 360.0)
```

```python
def test_mu_per_mm_handles_zero_travel_safely():
    beam = build_synthetic_beam(total_axial_travel_mm=0.0, total_mu=200.0)
    metrics = calculate_beam_metrics(beam)
    assert metrics["mu_per_mm"] is None
```

- [ ] **Step 2: Run the metric tests**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_metrics -v`
Expected: FAIL

- [ ] **Step 3: Implement beam-level metric helpers**

Implement these functions:
- `calculate_axial_travel_mm(beam)`
- `calculate_gantry_rotation_deg(beam)`
- `calculate_mm_per_deg(beam)`
- `calculate_mm_per_rotation(beam)`
- `calculate_pitch_consistency(beam)`
- `calculate_mu_per_mm(beam)`
- `calculate_aperture_change_per_mm(beam)`
- `calculate_leaf_travel_per_mm(beam)`
- `calculate_coupled_modulation_index(beam)`

- [ ] **Step 4: Define the first-pass formulas explicitly in code comments**

Example guidance:
- `pitch_consistency` should summarize the variability of `delta_axial_mm / abs(delta_gantry_deg)` over valid control-point intervals.
- `aperture_change_per_mm` should summarize successive aperture-area or open-width change normalized by `delta_axial_mm`.
- `coupled_modulation_index` should be a transparent weighted or normalized aggregate of:
  - aperture change
  - leaf travel
  - MU density change
  - pitch inconsistency

Do not hide assumptions. Add short comments at the metric definitions.

- [ ] **Step 5: Implement plan-level aggregation**

Plan-level values should be derived from beam-level values using explicit rules, typically:
- sum for travel and rotation totals
- weighted mean for density-style metrics

- [ ] **Step 6: Run metric tests**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_metrics -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add aurora_svmat_lab/metrics.py tests/test_aurora_metrics.py
git commit -m "feat: add aurora svmat research metrics"
```

## Task 5: Add Service-Layer Analysis Results And Unsupported Handling

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\service.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_service.py`

- [ ] **Step 1: Write the failing service test**

```python
def test_service_returns_unsupported_when_axial_track_is_missing():
    dataset = build_fake_aurora_rtplan(with_axial_track=False)
    result = analyze_aurora_dataset(dataset)
    assert result.supported is False
    assert result.reason == "Missing axial trajectory"
```

- [ ] **Step 2: Run the service tests**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_service -v`
Expected: FAIL

- [ ] **Step 3: Implement result orchestration**

Service responsibilities:
- parse file or dataset
- call metric engine
- flatten metadata and metrics
- classify unsupported conditions
- preserve warnings

Result object should include:
- `supported`
- `reason`
- `metadata`
- `beam_results`
- `plan_metrics`
- `warnings`

- [ ] **Step 4: Add file and directory entry points**

Implement:
- `analyze_plan_file(path: Path) -> AuroraAnalysisResult`
- `analyze_directory(path: Path) -> list[AuroraAnalysisResult]`

Keep these self-contained and independent from `analysis_batch.py`.

- [ ] **Step 5: Run service tests**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_service -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add aurora_svmat_lab/service.py tests/test_aurora_service.py
git commit -m "feat: add aurora analysis service"
```

## Task 6: Implement CSV Export And Column Definitions

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\export.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\notes.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_export.py`

- [ ] **Step 1: Write the failing export test**

```python
def test_export_rows_include_reason_and_core_aurora_metrics():
    result = build_fake_analysis_result()
    rows = export_plan_rows([result])
    assert "mm_per_rotation" in rows[0]
    assert "coupled_modulation_index" in rows[0]
    assert "reason" in rows[0]
```

- [ ] **Step 2: Run the export tests**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_export -v`
Expected: FAIL

- [ ] **Step 3: Implement export flattening**

Produce:
- plan-level row export
- optional beam-level export
- optional control-point trajectory export for research debugging

At minimum, the main CSV should include:
- file path
- plan label / plan name
- manufacturer / model
- supported / reason
- warning count
- total beams
- all Aurora plan metrics

- [ ] **Step 4: Implement metric notes**

Add GUI-friendly short notes for:
- axial travel
- gantry rotation
- mm per degree
- mm per rotation
- pitch consistency
- MU per mm
- aperture change per mm
- leaf travel per mm
- coupled modulation index

- [ ] **Step 5: Run export tests**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_export -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add aurora_svmat_lab/export.py aurora_svmat_lab/notes.py tests/test_aurora_export.py
git commit -m "feat: add aurora csv export and metric notes"
```

## Task 7: Add A Minimal Standalone CLI

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\cli.py`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_cli.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_service.py`

- [ ] **Step 1: Write the failing CLI smoke test**

```python
def test_cli_builds_argument_parser():
    parser = build_arg_parser()
    args = parser.parse_args(["--help"])
    assert parser.prog == "aurora_svmat_cli"
```

- [ ] **Step 2: Run the CLI-related test**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_service -v`
Expected: FAIL

- [ ] **Step 3: Implement CLI behaviors**

Support:
- `--input-file`
- `--input-dir`
- `--output-csv`
- `--beam-output-csv`
- `--trajectory-output-csv`
- `--verbose`

Printing rules:
- concise plan summary to console
- non-clinical disclaimer in output text

- [ ] **Step 4: Run a real-file manual validation**

Run:

```powershell
.\.venv\Scripts\python.exe .\aurora_svmat_cli.py --input-file "D:\Obsidian\Web Clipper\001_inbox\RTPLAN_57661.dcm" --verbose
```

Expected:
- no crash
- `supported=True`
- beam count and core metrics displayed

- [ ] **Step 5: Commit**

```bash
git add aurora_svmat_lab/cli.py aurora_svmat_cli.py tests/test_aurora_service.py
git commit -m "feat: add aurora command line entrypoint"
```

## Task 8: Build The Standalone Aurora GUI

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\gui.py`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_gui_smoke.py`

- [ ] **Step 1: Write the failing GUI smoke test**

```python
def test_gui_application_constructs_without_analysis():
    app = AuroraSvmatApp()
    try:
        assert app.title() == "Aurora SVMAT Lab"
    finally:
        app.destroy()
```

- [ ] **Step 2: Run the GUI smoke test**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_gui_smoke -v`
Expected: FAIL

- [ ] **Step 3: Implement a minimal Aurora GUI**

UI should include:
- file chooser
- folder chooser
- run analysis button
- progress text
- result table
- metric notes panel
- warnings panel
- export button
- bottom disclaimer:
  - `RESEARCH USE ONLY. CLINICAL USE IS STRONGLY FORBIDDEN.`

Keep the GUI lightweight and independent. Do not import `ucomx_gui.py`.

- [ ] **Step 4: Run the GUI smoke test**

Run: `.\.venv\Scripts\python.exe -m unittest tests.test_aurora_gui_smoke -v`
Expected: PASS

- [ ] **Step 5: Launch the GUI manually**

Run:

```powershell
.\.venv\Scripts\python.exe .\aurora_svmat.py
```

Expected:
- window opens
- analysis buttons appear
- no dependency on the current `PyUCoMX` window or services

- [ ] **Step 6: Commit**

```bash
git add aurora_svmat_lab/gui.py aurora_svmat.py tests/test_aurora_gui_smoke.py
git commit -m "feat: add standalone aurora svmat gui"
```

## Task 9: Add README Documentation For The Standalone Prototype

**Files:**
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\README.md`

- [ ] **Step 1: Write the README update**

Add a short section covering:
- what Aurora SVMAT Lab is
- that it is standalone and experimental
- supported input expectations
- how to launch GUI
- how to run CLI
- non-clinical disclaimer

- [ ] **Step 2: Verify README formatting**

Run: `Get-Content README.md -TotalCount 260`
Expected: new Aurora section present and readable

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: document aurora svmat lab prototype"
```

## Task 10: End-To-End Validation

**Files:**
- Modify as needed: any Aurora package files above
- Test: all new Aurora tests

- [ ] **Step 1: Run the Aurora-focused test suite**

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest ^
  tests.test_aurora_parser ^
  tests.test_aurora_metrics ^
  tests.test_aurora_export ^
  tests.test_aurora_service ^
  tests.test_aurora_gui_smoke -v
```

Expected: all Aurora tests PASS

- [ ] **Step 2: Run compile verification**

Run:

```powershell
.\.venv\Scripts\python.exe -m compileall aurora_svmat_lab aurora_svmat.py aurora_svmat_cli.py
```

Expected: compile succeeds with no syntax errors

- [ ] **Step 3: Run real-file CLI validation**

Run:

```powershell
.\.venv\Scripts\python.exe .\aurora_svmat_cli.py --input-file "D:\Obsidian\Web Clipper\001_inbox\RTPLAN_57661.dcm" --output-csv .\output\aurora_svmat_sample.csv --verbose
```

Expected:
- CSV is written
- the program reports supported analysis
- trajectory and metric values are non-empty

- [ ] **Step 4: Run manual GUI validation**

Run:

```powershell
.\.venv\Scripts\python.exe .\aurora_svmat.py
```

Expected:
- GUI opens
- sample file can be analyzed
- metrics and warnings render
- export works

- [ ] **Step 5: Final commit**

```bash
git add aurora_svmat_lab aurora_svmat.py aurora_svmat_cli.py tests README.md
git commit -m "feat: ship aurora svmat research prototype"
```

## Notes For Execution

- Keep the Aurora code path fully isolated. Do not import:
  - `ucomx_service.py`
  - `ucomx_gui.py`
  - `metric_registry.py`
  - existing VMAT/TOMO/CyberKnife service wiring
- It is acceptable to borrow small algorithmic ideas from existing geometry code, but only by re-implementing the minimum needed Aurora-specific pieces inside the new package.
- Prefer standard RTPLAN fields over private tags whenever possible.
- Treat `WISTECH (4001,1004)` as audit and fallback data, not as the only source of truth.
- If the supplied real RTPLAN cannot be checked into the repo, keep real-file validation as a manual validation step and keep the automated regression tests synthetic.
