# Aurora V5 unified physical geometry migration

Version: `aurora-v5-unified-physical-closure1mm` (2026-10-23).

The old coordinate proxy zipped complete MLCX1/MLCX2 vectors. Those vectors represent two full MLC layers with their own A/B banks and possibly unequal leaf counts and staggered boundaries. They do not form opposing banks. The current shared kernel reconstructs the physical intersection on real boundaries, clips jaws and closes effective gaps <=1+1e-8 mm. This threshold is an explicit analysis convention, not a measured transmission threshold.

- All aperture changes now use physical intersection area; rate units change from mm/mm to mm^2/mm. Regional, peak, coupled and reversal fields inherit the correction.
- SAS5, SAS10, small-opening, near-closed and severity share the same open-strips mask and open-endpoint delivered-MU weights. small_opening_fraction equals mean_sas10. Zero increments never acquire unit weight.
- Aurora adapted MCS retains its gap-sequence LSV and stripwise maximum-area envelope AAV, using the common mask. It is not classic McNiven MCS. Complexity remains exactly 1-MCS; CA remains P/A in mm^-1.
- Native-layer aperture disparity uses abs(A1-A2)/(A1+A2) on common jaw-clipped coverage, with the same conditional weights.
- mu_per_mm now reads absolute BeamMeterset. Missing/invalid MU is unavailable, not a relative-weight span.
- The 77 metric keys and order remain. Trajectory/projection exports replace aperture_width_mm with explicit physical area fields and record the threshold and formula version.
- Bad geometry in any participating beam invalidates affected plan fields; it does not create a partial plan average. Motion-only fields remain available.

The shared kernel caches only within a calculation and cannot reuse geometry after caller mutation between calls. Hand cases cover unequal layers, strict closure/SAS boundaries, zero intervals, MU pooling, missing MU, translation invariance and CP export parity. Independent polygon comparisons check area and perimeter.

Local cohort reproduction:

```powershell
python -m pytest tests -q
python tools/recompute_aurora_migration.py --input-dir LOCAL_RTPLAN_DIRECTORY --output-dir reports/aurora_v5 --baseline-json LOCAL_BASELINE_JSON
```

The baseline JSON maps case filename stems to the original 77-key metric maps. The tool rejects ambiguous filenames or missing baseline cases, hashes source RTPLAN bytes, records warnings and missing values, and writes current values plus per-key change counts. Input DICOM and per-case outputs remain local; no original clinical files are committed. Prior manuscript statistics have not been rerun or silently replaced.

Historical V4 documentation and evidence remain archived under their original version.

## Verification on 2026-10-23

The full Windows suite passed 432 tests, with 1 skipped and 99 subtests passed. The supplied 81-plan cohort retained all 77 output keys; 49 fields stayed equal to the prior implementation within 1e-10 and 28 fields changed under the documented migration. Both exact aliases hold in every plan. Independent polygon checks passed for 1692 sampled control points (maximum area difference 4.37e-11 mm^2; perimeter difference 1.14e-12 mm). All input RTPLAN hashes match the original ZIP. These checks establish numerical consistency, not a clinical QA threshold.

The two checked-in Aurora reference cases were independently checked, their old 70-key baselines archived under history/pre-aurora-v5, and new 77-key baselines frozen with source and metric checksums plus the V5 formula version. The migration audit is validation/reference_cases/migrations/aurora-v5_unified_geometry_audit.json. No clinical source file is included.
