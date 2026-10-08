# DeepPlan and Aurora RTPLAN compatibility

DeepPlan may export ManufacturerModelName as `WisdomTech`, including Aurora SVMAT plans. The Aurora parser accepts this producing-system identifier. Automatic routing still requires dynamic dual-layer MLC geometry together with an Aurora identity or observed longitudinal isocenter motion; the TPS vendor alone does not select SVMAT.

The generic VMAT/IMRT parser excludes SETUP beams when applying fraction-group dose and MU references. References to missing beams raise an explicit error. Single-layer versus dual-layer metric handling uses declared MLC device geometry, with leaf boundaries read from DICOM. Generic dual-layer metrics describe individual layers; Halcyon/Ethos-specific report metrics retain their existing machine restrictions.

Validation on 2026-10-08:

- Full suite: 369 passed, 1 skipped, 99 subtests passed.
- Three user-supplied Aurora plans: automatic and explicit Aurora analysis both succeed, each returning 70 metric records without program warnings in the executable build environment.
- Synthetic regression coverage includes WisdomTech axial-motion routing, conventional dual-layer plans, SETUP references, missing beam references, and a 30/29-pair area hand calculation.

The Windows executable is built using `tools/build_windows_exe.ps1` and `PyUCoMX.spec`; the output is `dist/PyUCoMX.exe`.
