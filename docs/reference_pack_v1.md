# Reference Pack v1

The reference manifest now points to locally available Aurora files:

- `aurora_canonical`: `data/Aurora/HS-PCI017.dcm`
- `aurora_research_edge`: `data/Aurora/UCC001.dcm`

`tools/run_reference_suite.py` checks source checksums, expected analysis state, scalar values,
and formula provenance. Its strict profile returns exit status 1 when any required gate fails.
Missing inputs or invalid artifact checksums also produce a nonzero process exit.

## Formula-versioned baselines

The six VMAT/IMRT, CyberKnife, and TOMO cases require `geometry-v4` or `tomo-v3` in
`manifest.yaml`. Each retains a flat `expected_metrics.json` and a sibling
`expected_metrics_provenance.json`: formula version, case/domain/mode, source SHA256,
scalar-file SHA256, and generation time. The two unaffected Aurora fixtures remain explicitly
reported as `legacy-unversioned`. The Precision case explicitly expects `supported: false`;
an empty metric mapping alone is insufficient to pass a case.

The pre-migration scalar files are preserved byte-for-byte under
`validation/reference_cases/history/pre-geometry-v3/`. See the
[migration audit](geometry_v3_metrics.md) and machine-readable
`validation/reference_cases/migrations/geometry-v3_tomo-v2.json` for every changed or added value.
Independent hand cases and raw-input audits precede freezing; matching a newly frozen output
does not independently prove a formula.

The subsequent full-precision/motion migration preserves the immediately preceding
files in `history/pre-geometry-v4-tomo-v3/`, including their provenance sidecars.
`migrations/geometry-v4_tomo-v3_audit.json` records unrounded results, every changed/added key,
30 independent numerical checks and the hash of the preceding geometry audit.
See [precision and motion validation](precision_motion_validation.md). Reference result rows
now carry the input checksum and numerical precision, allowing external comparisons to
reject reused case aliases, different input files, or rounded observations.

For an audited migration, select explicit cases and use the relevant override flags:

```bash
python tools/freeze_reference_outputs.py --case-id CASE_ID --yes --allow-formula-version-change
```

Adding or removing metric keys additionally requires `--allow-metric-schema-change`.
These flags do not bypass source checksums, runtime formula requirements, or the expected
analysis state. Changing versions in the manifest without migrating provenance fails the gate.

## Open-Source Packaging Rule

The repository should not publish clinical DICOM data directly. For an open-source release, distribute one of the following:

- A separate approved de-identified reference-data package with matching checksums.
- A synthetic RTPLAN pack whose manifest is frozen independently.
- A clean internal release bundle where `--source-root` points to protected local reference data.

The current code supports this through `--source-root`; the remaining blocker is data governance, not the reference-suite runtime.
