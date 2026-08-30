# Reference Pack v1

The reference manifest now points to locally available Aurora files:

- `aurora_canonical`: `data/Aurora/HS-PCI017.dcm`
- `aurora_research_edge`: `data/Aurora/UCC001.dcm`

`tools/run_reference_suite.py` passes when the referenced `data/` tree is present and matches the manifest checksums.

## Open-Source Packaging Rule

The repository should not publish clinical DICOM data directly. For an open-source release, distribute one of the following:

- A separate approved de-identified reference-data package with matching checksums.
- A synthetic RTPLAN pack whose manifest is frozen independently.
- A clean internal release bundle where `--source-root` points to protected local reference data.

The current code supports this through `--source-root`; the remaining blocker is data governance, not the reference-suite runtime.
