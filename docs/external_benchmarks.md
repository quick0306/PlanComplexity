# External benchmark evidence

The checked-in capture is a numeric excerpt from an existing local UCoMX/VCoMX
workbook. It supplies traceable external observations for one Halcyon reference
input. It is not an authenticated historical execution, an exact-equivalence
baseline, or clinical validation. The three older comparator examples have no
independent external provenance and must not count as verified external evidence.

## Captured artifacts and identity

`validation/external_benchmarks/ucomx_halcyon_historical.json` records ten original
numeric values without rounding or unit conversion. Source identity is fixed by:

| Artifact | SHA256 |
| --- | --- |
| Reference input `vmat_halcyon_edge` | `9813382359503e91d2b1750b706ae98be811ca3bc064cc223f9aa80ddb02b854` |
| Historical workbook | `fa1987065c2a758574b1804c8b397f750d50bafdeceea6e43fd2ca417ef97b10` |
| Saved run CONFIG.in | `5bc25903704c14b767f0c04c369100f0279e4a6297cf632e2ccf3650cfeb402e` |
| Saved run METRICS.in | `993fe6d8fc244aaeff66f38b2bd804ab61e3e782c7f7cb59bf5c55f961241a55` |

The importer finds the local DICOM and workbook by these hashes. It verifies the
reference input checksum and compares local/reference SOPInstanceUID values in
memory. The workbook itself does **not** record that UID or a historical input
hash: its `info!B1` header is `Filename`, and `info!B2` resolves to the local file
whose current bytes match the reference checksum. Metrics use the corresponding
row 2 in the paired export sheets. This is a filename-to-current-input-hash join;
it cannot prove that the historical input bytes were identical at execution time.

No patient name, ID, UID, original input filename, source directory, or full info
sheet is copied into the capture. Original artifacts remain local and unchanged.
Raw workbook hashes permit later verification by someone with authorized access.
The capture's own checksum detects accidental edits; it is not a digital signature.

A second historical workbook, SHA256
`2429c521bc697b36d027d971a1846122db830bb8a725ec2dded7c15d4689fd75`, contains the
same ten values in the same row. It is corroborating storage, not a second
independent input or validation case, and is not included in evidence counts.

## Tool and configuration limits

The saved run configuration selects fluence precision scale 2 (0.5 mm), directory
input, and the metrics stored in the captured METRICS.in. Its raw bytes are hashed;
private path values are not exported. The run's binary hash and tool version are
not recorded in the available workbook/configuration/log. The local GUI currently
labels itself `VCoMX v1.0`; current GUI and entry-point hashes are recorded as
context at capture time. They do not authenticate the historical binary. Version
labels from a later v1.1 distribution must not be retroactively assigned to these
outputs or treated as proof that the local binaries are that distribution.

## Comparison policy

`validation.external_benchmarks.run_external_benchmarks(reference_report)` consumes
raw reference metric rows and returns `summary`, `sources`, `samples`, and
`comparisons`. A pair requires matching case alias, domain, metric key, exact
`source_checksum`, and `numeric_precision="float64"`. Missing or mismatched
provenance prevents pairing; absent/nonfinite values remain unavailable.

| External metric | Workbook cell | Internal candidate | Definition status |
| --- | --- | --- | --- |
| MUs | metrics!A2 | mus | definition_unverified |
| LT | metrics!F2 | lt_stacked | variant_unverified |
| MCSv | metrics!R2 | mcsv_stacked | variant_unverified |
| AAV | metrics!S2 | aav_stacked | variant_unverified |
| LSV | metrics!T2 | lsv_stacked | variant_unverified |
| PI | metrics!Y2 | none | unmapped |
| PA | metrics!AH2 | pa_stacked | variant_unverified |
| EFS | metrics!AM2 | none | unmapped |
| EM | metrics!AR2 | none | unmapped |
| P | metrics!AU2 | none | unmapped |

The stacked candidates are hypotheses, not demonstrated equivalent algorithms.
The remaining metrics have no uniquely justified internal plan aggregate: native
layer values must not be silently collapsed or substituted. Numeric agreement or
disagreement does not change a definition status. Explicitly verified mappings
require documented definition evidence. Even such mappings cannot authenticate
a historical execution, and every historical comparison remains excluded from
the exact reference gate.

With all current raw rows available, this capture offers six actual candidate
pairs, zero definition-eligible pairs, and zero authenticated external runs.
Report counts must distinguish those categories; ten captured cells are not ten
independent validation cases.

## Reproduce the historical capture

From the repository, using its Python environment and authorized local artifacts:

```powershell
.venv/Scripts/python.exe tools/import_external_benchmark.py --source-root <local-ucomx-root>
.venv/Scripts/python.exe tools/import_external_benchmark.py --source-root <local-ucomx-root> --check
```

`--reference-root` can supply the private reference-data root. `--output` changes
the destination capture path; output inside the external source tree is rejected.
`--check` performs read-only reproduction, ignoring only the capture timestamp
and its derived checksum. A missing artifact, changed source hash, ambiguous
identity row, changed current tool snapshot, missing provenance, or modified
capture fails the check. No spreadsheet formulas execute or links refresh.

The reader resolves worksheet relationship IDs rather than assuming sheet order,
checks numeric cells against their headers and identity row, and rejects duplicate
metrics and formula-derived cells. Tests use synthetic OOXML and neutral input
bytes, so the checks do not require or export patient data.

## Bounded live execution attempt

`validation/external_benchmarks/attempts/ucomx_halcyon_live_20260919.json` records
a separate attempt using MATLAB 25.2.0.2998904 (R2025b), the exact same input bytes,
and a complete temporary copy of the local VCoMX tree. The copied CONFIG.in used
one input, an isolated output directory, and precision scale 2; METRICS.in retained
the historical hash. The GUI source documents the zero-argument `VCoMX` entry
point. Execution used that entry point in batch mode with the copied tree on the
MATLAB path. The attempt records all copied tool/configuration file hashes,
timestamps, runtime version, and the sanitized invocation.

The engine failed with `MATLAB:colon:operandsNotRealScalar`, in
`check_leaf_status` through `VCoMX_basis`, `VCoMX_COMPUTE_METRICS`, and `VCoMX`.
It produced no workbook. The surrounding error handler returned process code 0;
the explicit engine failure and zero outputs determine this attempt's failed
status. The failure cause inside opaque P-code remains unresolved. No external
algorithm was changed and original tool files remained unchanged.

This record provides execution evidence for a **failed** attempt only. It neither
adds a successful external run nor authenticates the historical workbooks. Failed
attempts are stored in a subdirectory and excluded from capture loading and
comparison counts.
