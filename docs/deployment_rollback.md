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
