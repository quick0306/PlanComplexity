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

The complete Windows suite passed before integration: 335 passed, 1 skipped,
39 subtests passed, including real GUI creation. It used Python 3.14.3 without
manual Tcl/Tk path overrides. See [precision and motion validation](precision_motion_validation.md)
for reference-gate results and the limits of the external evidence.
