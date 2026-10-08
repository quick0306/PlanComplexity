# DeepPlan and Aurora RTPLAN compatibility

DeepPlan may export ManufacturerModelName as `WisdomTech`, including Aurora SVMAT plans. The Aurora parser accepts this producing-system identifier. Automatic routing still requires dynamic dual-layer MLC geometry together with an Aurora identity or observed longitudinal isocenter motion; the TPS vendor alone does not select SVMAT.

The generic VMAT/IMRT parser excludes SETUP beams when applying fraction-group dose and MU references. References to missing beams raise an explicit error. Single-layer versus dual-layer metric handling uses declared MLC device geometry, with leaf boundaries read from DICOM. Generic dual-layer metrics describe individual layers; Halcyon/Ethos-specific report metrics retain their existing machine restrictions.

Historical compatibility-fix validation on 2026-10-08 (before V4 restoration):

- Full suite: 369 passed, 1 skipped, 99 subtests passed.
- Three user-supplied Aurora plans: automatic and explicit Aurora analysis both succeed, each returning 70 metric records without program warnings in the executable build environment at the initial compatibility fix. The subsequent [V4 restoration](aurora_v4_migration.md) expands this to 77 records, and is followed by the open-only update below.
- Synthetic regression coverage includes WisdomTech axial-motion routing, conventional dual-layer plans, SETUP references, missing beam references, and a 30/29-pair area hand calculation.

The Windows executable is built using `tools/build_windows_exe.ps1` and `PyUCoMX.spec`; the output is `dist/PyUCoMX.exe`.

## Current Aurora output

The current runtime exports 77 keys and records `aurora-v4-physical-aperture-open-only`.
The seven physical-aperture means exclude closed endpoints and renormalize retained weights;
closed leaf gaps do not enter SAS/LSV. A closed sample no longer makes plan BI/CA unavailable
when valid open samples remain. Exclusion count and weight fraction appear in warnings.
All-closed plans or invalid physical geometry still have unavailable V4 values.
The prior 70 research/proxy calculations are unchanged. See the [user guide](user_guide.md)
and [current definitions](aurora_aperture_metrics.md). The current-code suite passed
397 tests and 99 subtests with one skip; this is technical verification, not clinical validation.
