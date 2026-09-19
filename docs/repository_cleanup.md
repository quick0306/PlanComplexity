# Repository cleanup and main-branch integration

The 2026-09-19 integration includes the geometry/unit corrections, TOMO motion
contract, per-metric formulas, full-precision comparisons, versioned baseline
migrations, external benchmark provenance, and their tests.

## Removed from the project source

- Six tracked IDE configuration files under `.idea/`.
- Nine unversioned `run_reports/real_rtplan*.json` diagnostic snapshots. The
  diagnostic/export commands remain available; their generated JSON is now ignored.
  Current scientific evidence remains under `run_reports/validation/`.
- Four unused private bank-LSV forwarding functions, leaving the shared formula
  implementation in `ComplexityMetric/aperture_shape_metrics.py`.
- Two unreferenced DICOM copy/classification routines with hardcoded workstation
  destinations, plus their imports.
- An unused TOMO warning dataclass and unused imports. The parser's actual string
  warnings and their provenance are unchanged.

Repository-wide searches found no calls, tests, documented entry points or formula
contract anchors for the removed helpers. Public metric classes, compatibility
CLIs, inspection tools, original scientific sources and baseline history remain.

`PyUCoMX.spec` is now tracked because the documented Windows build command requires
it. Its workstation-specific search path was removed. Generated executables and
build caches remain ignored; executable packaging was not rerun for this cleanup.

Git line-ending conversion is disabled for baseline JSON and validation reports.
The pre-integration check found that automatic conversion changed archived/report
bytes after staging and invalidated their recorded hashes. A regression test now
performs real Git add/checkout operations with CRLF and LF inputs under all three
`core.autocrlf` settings, verifying the stored and checked-out bytes.

## Local files

Final software-copyright DOCX deliverables are preserved, and their local output
directory is ignored. Attempts to recursively delete obsolete build output and
document-production intermediates were rejected by automatic approval review
(reason supplied: "blocked by policy"). Those ignored directories remain on disk.
Source DICOM data and the Python environment are preserved.

## Verification

The initial Windows full run passed, but a subsequent main-branch run reproduced
an intermittent Tk initialization failure. A controlled comparison used the same
four real GUI tests, Python 3.14.3, test order and environment: default `fd` output
capture failed in two of three runs; `sys` capture and disabled capture each passed
all three runs. `pytest.ini` now defaults to `--capture=sys`; the four tests also
passed with that configuration and no command-line capture override. Product GUI
code, test assertions and test selection are unchanged.

This local evidence supports a Windows Tcl/output-capture interaction. The
[ttkbootstrap project records the same capture workaround](https://github.com/israel-dryer/ttkbootstrap/blob/master/pyproject.toml).
No Tcl/Tk path overrides or retries are needed for the configured test command.

The final complete Windows suite on main passed: **336 passed, 1 skipped,
99 subtests passed**, exit 0 in 113.42 seconds, using
`.venv/Scripts/python.exe -m pytest tests -q --tb=short -rs`.

The main-branch Python 3.11 headless suite passed with 332 tests, 1 skipped,
1 deselected and 99 subtests. The missing Aurora sample accounts for the single
skip. Git-stored contents also passed 29 baseline, archive and report SHA256 checks.
See [precision and motion validation](precision_motion_validation.md) for the
reference-gate results and the limits of the external evidence.
