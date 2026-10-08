# Deployment And Rollback Procedure

This project is not clinically deployed. This document defines the minimum controls required before any controlled institutional deployment.

## Deployment

- Build only from a reviewed Git commit.
- Run the full validation test suite and validation artifact rebuild.
- Record the commit hash, environment, artifact checksums, and operator.
- Package reports without patient identifiers unless the run is inside an approved protected environment.
- Keep deployment notes with the generated `clinical_readiness_gate.json`.

## Rollback

- Preserve the previous validated executable or source checkout.
- If validation fails after deployment, stop use immediately and revert to the previous locked release.
- Record rollback reason, triggering evidence, operator, timestamp, and input/output hashes.
- Re-run reference-suite and smoke tests after rollback.

## Audit Expectations

- Every analysis and export should be traceable to software version and input hash.
- Every deployment and rollback event should follow `validation/schemas/audit_log.schema.json`.
- Do not claim clinical readiness while `clinical_readiness_gate.json` reports blocking failures.

## Current-version packaging and rollback boundary

Runtime versions are `geometry-v4`, `tomo-v3` and Aurora V4
`aurora-v4-physical-aperture-open-only`. Use [the user guide](user_guide.md) for current
commands. Windows builds use `tools/build_windows_exe.ps1` / `PyUCoMX.spec` and output
`dist/PyUCoMX.exe`; check the build exit status and GUI startup, then record executable SHA256.
Source commits do not automatically update an existing executable, and an executable build
does not publish a GitHub release. Keep protected CSV/DICOM outputs local.

A rollback across Aurora formula versions also changes the meaning of the seven V4 values.
Preserve version labels and recompute a whole research batch with a single intended version;
do not combine unit-height surrogate, initial physical or open-only results. Archived baseline
hashes and historical validation reports are retained, rather than rewritten to imply new validation.
