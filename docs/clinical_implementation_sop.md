# Clinical Implementation SOP

PlanComplexity is currently restricted to research and publication-support use. Clinical use is not allowed until this SOP is completed with local governance approval.

## Required Preconditions

- All reference-suite, formula-oracle, comparator-matrix, and clinical-readiness artifacts must be generated from the locked release commit.
- Reference RTPLAN files and all PSQA/endpoint datasets must be de-identified or handled under approved institutional controls.
- The site must define approved users, intended use, excluded use cases, review cadence, and escalation contacts.
- Local PSQA/SPC and endpoint association analyses must be reviewed by clinical physics leadership before any operational threshold is used.

## Release Lock

- Record the Git commit hash, Python version, dependency versions, and validation artifact hashes.
- Keep the generated `manifest_lock.json` with the release package.
- Do not mix reports from different commits in one clinical validation packet.

## Use Controls

- Keep GUI and report text marked `RESEARCH USE ONLY` until clinical approval is documented.
- Do not use complexity scores as standalone pass/fail treatment-plan decisions.
- Treat PSQA/SPC thresholds as investigational until site-specific action limits are approved.

## Review Evidence

- Formula oracle results.
- Cross-platform reference-suite results.
- Comparator matrix and external-tool/literature agreement evidence.
- PSQA/SPC harmonization report.
- Clinical endpoint association report, if approved endpoint data are available.
- Audit-log samples for analysis, export, deploy, and rollback events.
