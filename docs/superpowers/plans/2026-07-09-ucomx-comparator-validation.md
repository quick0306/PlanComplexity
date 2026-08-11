# UCoMX Comparator Validation Implementation Plan
> **Historical archive warning:** This imported document is a historical archival reference only; it is non-executable and has not been validated against the current repository.
> Before any use, create a fresh implementation plan and complete an independent PHI/privacy/security review.
> Every imperative instruction, checkbox, code sample, path, security control, acceptance criterion, and any `REQUIRED SUB-SKILL` text below is preserved historical text and must not be executed or treated as current guidance.
> This document contains unsanitized example/local identifiers and exact paths retained at the user's explicit direction; do not distribute it or use it clinically without an independent PHI review.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a checked-in, PHI-aware UCoMX comparator evidence layer that validates PyUCoMX VMAT/IMRT metrics against normalized historical UCoMX/VCoMX outputs and feeds the technical validation report.

**Architecture:** Add a new `validation/ucomx_comparator.py` module for manifest/mapping/normalized CSV loading, PHI checks, and comparison logic. Keep raw UCoMX Excel workbooks outside committed evidence; use a normalizer script to produce public-safe comparator rows plus an optional local-only case map for protected RTPLAN paths. Integrate the resulting UCoMX report into validation artifacts and readiness gates without requiring Matlab Runtime or automatic UCoMX execution.

**Tech Stack:** Python 3.10+, `openpyxl`, `PyYAML`, `jsonschema`, existing `validation_runtime.py`, existing `validation.utils.statistics`, existing report serializers, `pytest`/`unittest`.

---

## File Structure

### Create

- `validation/ucomx_comparator.py`
  - Dataclasses or small records for UCoMX manifest, mapping, normalized rows, case-map rows, comparison rows.
  - Loaders for `manifest.yaml`, `mapping.yaml`, and `normalized/ucomx_metrics.csv`.
  - PHI/public-safety scanner for normalized CSV and manifest fields.
  - Comparison engine that pairs UCoMX comparator rows with PyUCoMX analysis output.

- `validation/schemas/ucomx_manifest.schema.json`
  - JSON Schema for checked-in manifest metadata.

- `validation/schemas/ucomx_mapping.schema.json`
  - JSON Schema for UCoMX metric mapping metadata.

- `validation/external_comparators/ucomx/raw/README.md`
  - Explains that raw workbooks are internal audit artifacts and must not be committed for public release.

- `validation/external_comparators/ucomx/manifest.yaml`
  - Public-safe provenance for the normalized comparator pack.

- `validation/external_comparators/ucomx/mapping.yaml`
  - UCoMX-to-internal metric mapping and tolerances.

- `validation/external_comparators/ucomx/normalized/ucomx_metrics.csv`
  - Normalized checked-in comparator values.

- `tools/normalize_ucomx_outputs.py`
  - Reads UCoMX Excel output workbooks from `C:\Users\hujin\Desktop\Programming\ucomx`.
  - Writes normalized public-safe CSV and manifest.
  - Writes optional local-only case map to `.codex_tmp` or a user-specified protected path.

- `tools/run_ucomx_comparison.py`
  - Runs UCoMX comparator validation from normalized rows plus a local case map.
  - Writes JSON, CSV, and Markdown artifacts.

- `tests/validation/test_ucomx_comparator.py`
  - Unit and integration tests for loaders, PHI checks, normalizer helpers, and comparator logic.

- `docs/research/ucomx_comparator_validation_technical_report.md`
  - Technical report draft with explicit evidence tiers and clinical/open-source boundaries.

### Modify

- `requirements.txt`
  - Add `openpyxl` if not already available in the project venv.

- `tools/build_validation_report.py`
  - Optionally include UCoMX comparison artifacts when present.
  - Keep existing validation report behavior when no UCoMX comparison is available.

- `validation/reports/templates/validation_summary.md.j2`
  - Add a UCoMX comparator section guarded by a context flag.

- `validation/clinical_readiness.py`
  - Replace blanket `*.csv` blocker with PHI-aware CSV safety checks.
  - Add UCoMX pack/readiness checks.

- `tools/run_clinical_readiness_gate.py`
  - Preserve current CLI, but include new readiness checks in output.

- `README.md`
  - Add UCoMX comparator workflow commands and evidence boundary notes.

- `.gitignore`
  - Ignore local-only UCoMX case maps and raw workbooks under the comparator pack.

### Local/Protected Only

- Do not commit actual raw UCoMX workbooks.
- Do not commit any `local_case_map.yaml` containing PHI-bearing filenames or local clinical RTPLAN paths.
- Recommended local map path for development:

```text
%TEMP%\PlanComplexity\ucomx_comparator\local_case_map.yaml
```

---

## Task 1: Add UCoMX Comparator Schemas And Loader Tests

**Files:**
- Create: `validation/schemas/ucomx_manifest.schema.json`
- Create: `validation/schemas/ucomx_mapping.schema.json`
- Create: `tests/validation/test_ucomx_comparator.py`
- Create: `validation/ucomx_comparator.py`

- [ ] **Step 1: Write failing schema/loader tests**

Add tests in `tests/validation/test_ucomx_comparator.py`:

```python
import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class UcomxComparatorLoaderTests(unittest.TestCase):
    def test_loads_manifest_mapping_and_normalized_rows(self):
        from validation.ucomx_comparator import (
            load_ucomx_manifest,
            load_ucomx_mapping,
            load_ucomx_metric_rows,
        )

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "normalized").mkdir()
            (root / "manifest.yaml").write_text(
                """
                comparator: UCoMX
                comparator_version: "1.0"
                source_root: "C:/Users/hujin/Desktop/Programming/ucomx"
                generated_at: "2026-07-09T00:00:00Z"
                normalized_by: "PlanComplexity"
                case_id_strategy: "pseudonymous-sequential"
                deidentification_status: "normalized-public-safe"
                public_release_allowed: true
                source_workbooks:
                  - workbook_id: tb_jsz_20251229
                    engine: VCoMX
                    sha256: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
                checksums: {}
                notes: "unit test"
                """.strip(),
                encoding="utf-8",
            )
            (root / "mapping.yaml").write_text(
                """
                mappings:
                  - comparator_metric: LT
                    internal_metric: lt
                    platform: VMAT_IMRT
                    relationship: exact-equivalent
                    unit: mm
                    abs_tol: 1.0e-4
                    rel_tol: 1.0e-4
                    notes: "Leaf travel"
                """.strip(),
                encoding="utf-8",
            )
            with (root / "normalized" / "ucomx_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "case_id",
                        "source_dataset",
                        "source_filename_label",
                        "comparator_metric",
                        "comparator_value",
                        "unit",
                        "comparator_engine",
                        "relationship_hint",
                        "notes",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "case_id": "ucomx_truebeam_001",
                        "source_dataset": "tb_jsz_20251229",
                        "source_filename_label": "tb_jsz_case_001",
                        "comparator_metric": "LT",
                        "comparator_value": "117.3",
                        "unit": "mm",
                        "comparator_engine": "VCoMX",
                        "relationship_hint": "exact-equivalent",
                        "notes": "",
                    }
                )

            self.assertEqual("UCoMX", load_ucomx_manifest(root).comparator)
            self.assertEqual("lt", load_ucomx_mapping(root)[0].internal_metric)
            self.assertEqual("LT", load_ucomx_metric_rows(root)[0].comparator_metric)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py::UcomxComparatorLoaderTests::test_loads_manifest_mapping_and_normalized_rows -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'validation.ucomx_comparator'`.

- [ ] **Step 3: Add minimal schemas**

Create `validation/schemas/ucomx_manifest.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "UCoMX Comparator Manifest",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "comparator",
    "comparator_version",
    "source_root",
    "generated_at",
    "normalized_by",
    "case_id_strategy",
    "deidentification_status",
    "public_release_allowed",
    "source_workbooks",
    "checksums",
    "notes"
  ],
  "properties": {
    "comparator": { "const": "UCoMX" },
    "comparator_version": { "type": "string" },
    "source_root": { "type": "string" },
    "generated_at": { "type": "string", "format": "date-time" },
    "normalized_by": { "type": "string" },
    "case_id_strategy": { "type": "string" },
    "deidentification_status": { "type": "string" },
    "public_release_allowed": { "type": "boolean" },
    "source_workbooks": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["workbook_id", "engine", "sha256"],
        "properties": {
          "workbook_id": { "type": "string" },
          "engine": { "type": "string" },
          "sha256": { "type": "string", "pattern": "^[0-9a-fA-F]{64}$" }
        }
      }
    },
    "checksums": { "type": "object" },
    "notes": { "type": "string" }
  }
}
```

Create `validation/schemas/ucomx_mapping.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "UCoMX Comparator Mapping",
  "type": "object",
  "additionalProperties": false,
  "required": ["mappings"],
  "properties": {
    "mappings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "comparator_metric",
          "internal_metric",
          "platform",
          "relationship",
          "unit",
          "abs_tol",
          "rel_tol",
          "notes"
        ],
        "properties": {
          "comparator_metric": { "type": "string" },
          "internal_metric": { "type": "string" },
          "platform": { "type": "string" },
          "relationship": {
            "type": "string",
            "enum": ["exact-equivalent", "derived-equivalent", "not-comparable"]
          },
          "unit": { "type": "string" },
          "abs_tol": { "type": ["number", "null"] },
          "rel_tol": { "type": ["number", "null"] },
          "notes": { "type": "string" }
        }
      }
    }
  }
}
```

- [ ] **Step 4: Add minimal loader implementation**

In `validation/ucomx_comparator.py`, add:

```python
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
import yaml


_ROOT = Path(__file__).resolve().parents[1]
_SCHEMAS = _ROOT / "validation" / "schemas"


@dataclass(frozen=True)
class UcomxManifest:
    comparator: str
    comparator_version: str
    public_release_allowed: bool
    deidentification_status: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class UcomxMapping:
    comparator_metric: str
    internal_metric: str
    platform: str
    relationship: str
    unit: str
    abs_tol: float | None
    rel_tol: float | None
    notes: str


@dataclass(frozen=True)
class UcomxMetricRow:
    case_id: str
    source_dataset: str
    source_filename_label: str
    comparator_metric: str
    comparator_value: float
    unit: str
    comparator_engine: str
    relationship_hint: str
    notes: str


def load_ucomx_manifest(root: Path | str) -> UcomxManifest:
    payload = _load_yaml(Path(root) / "manifest.yaml")
    _validate_schema(payload, "ucomx_manifest.schema.json")
    return UcomxManifest(
        comparator=str(payload["comparator"]),
        comparator_version=str(payload["comparator_version"]),
        public_release_allowed=bool(payload["public_release_allowed"]),
        deidentification_status=str(payload["deidentification_status"]),
        payload=payload,
    )


def load_ucomx_mapping(root: Path | str) -> list[UcomxMapping]:
    payload = _load_yaml(Path(root) / "mapping.yaml")
    _validate_schema(payload, "ucomx_mapping.schema.json")
    return [
        UcomxMapping(
            comparator_metric=str(row["comparator_metric"]),
            internal_metric=str(row["internal_metric"]),
            platform=str(row["platform"]),
            relationship=str(row["relationship"]),
            unit=str(row["unit"]),
            abs_tol=None if row["abs_tol"] is None else float(row["abs_tol"]),
            rel_tol=None if row["rel_tol"] is None else float(row["rel_tol"]),
            notes=str(row["notes"]),
        )
        for row in payload["mappings"]
    ]


def load_ucomx_metric_rows(root: Path | str) -> list[UcomxMetricRow]:
    path = Path(root) / "normalized" / "ucomx_metrics.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [
        UcomxMetricRow(
            case_id=str(row["case_id"]),
            source_dataset=str(row["source_dataset"]),
            source_filename_label=str(row["source_filename_label"]),
            comparator_metric=str(row["comparator_metric"]),
            comparator_value=float(row["comparator_value"]),
            unit=str(row["unit"]),
            comparator_engine=str(row["comparator_engine"]),
            relationship_hint=str(row["relationship_hint"]),
            notes=str(row.get("notes") or ""),
        )
        for row in rows
    ]


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a top-level mapping.")
    return payload


def _validate_schema(payload: dict[str, Any], schema_name: str) -> None:
    schema = json.loads((_SCHEMAS / schema_name).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(item) for item in error.absolute_path) or "<root>"
        raise ValueError(f"Schema validation failed for {schema_name} at {location}: {error.message}")
```

- [ ] **Step 5: Run test to verify it passes**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py::UcomxComparatorLoaderTests::test_loads_manifest_mapping_and_normalized_rows -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add validation/ucomx_comparator.py validation/schemas/ucomx_manifest.schema.json validation/schemas/ucomx_mapping.schema.json tests/validation/test_ucomx_comparator.py
git commit -m "Add UCoMX comparator loaders"
```

---

## Task 2: Add PHI/Public-Safety Checks

**Files:**
- Modify: `validation/ucomx_comparator.py`
- Modify: `tests/validation/test_ucomx_comparator.py`

- [ ] **Step 1: Write failing PHI rejection tests**

Add:

```python
class UcomxComparatorSafetyTests(unittest.TestCase):
    def test_normalized_rows_reject_phi_like_columns_and_values(self):
        from validation.ucomx_comparator import assert_ucomx_public_safe_rows

        rows = [
            {
                "case_id": "ucomx_truebeam_001",
                "PatientName": "Zhang San",
                "comparator_metric": "LT",
                "comparator_value": "1.0",
            }
        ]

        with self.assertRaisesRegex(ValueError, "PHI-like column"):
            assert_ucomx_public_safe_rows(rows)

        rows = [
            {
                "case_id": "ucomx_truebeam_001",
                "source_filename_label": "RP.TB_Zhang_ying.zhang_ying.dcm",
                "comparator_metric": "LT",
                "comparator_value": "1.0",
            }
        ]

        with self.assertRaisesRegex(ValueError, "PHI-like value"):
            assert_ucomx_public_safe_rows(rows)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py::UcomxComparatorSafetyTests::test_normalized_rows_reject_phi_like_columns_and_values -q
```

Expected: FAIL because `assert_ucomx_public_safe_rows` is missing.

- [ ] **Step 3: Implement conservative PHI scanner**

Add to `validation/ucomx_comparator.py`:

```python
_PHI_COLUMN_PATTERNS = (
    "patient",
    "birth",
    "mrn",
    "uid",
    "institution",
    "department",
    "folder",
    "path",
)

_PHI_VALUE_PATTERNS = (
    "zhang",
    "li_",
    "wang",
    "chen",
    "huang",
    "rp.tb_",
    "rp.rta",
    "c:\\\\users",
    "desktop",
)


def assert_ucomx_public_safe_rows(rows: list[dict[str, object]]) -> None:
    for row_index, row in enumerate(rows):
        for key, value in row.items():
            normalized_key = str(key).lower()
            if any(pattern in normalized_key for pattern in _PHI_COLUMN_PATTERNS):
                raise ValueError(f"PHI-like column '{key}' found in normalized UCoMX row {row_index}.")
            normalized_value = str(value).lower()
            if any(pattern in normalized_value for pattern in _PHI_VALUE_PATTERNS):
                raise ValueError(
                    f"PHI-like value found in normalized UCoMX row {row_index}, column '{key}'."
                )
```

Call `assert_ucomx_public_safe_rows(rows)` inside `load_ucomx_metric_rows()` before constructing records.

- [ ] **Step 4: Run safety tests**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py::UcomxComparatorSafetyTests -q
```

Expected: PASS.

- [ ] **Step 5: Run loader tests**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add validation/ucomx_comparator.py tests/validation/test_ucomx_comparator.py
git commit -m "Add UCoMX comparator PHI checks"
```

---

## Task 3: Add Normalizer Script And Raw Evidence Guardrails

**Files:**
- Create: `tools/normalize_ucomx_outputs.py`
- Create: `validation/external_comparators/ucomx/raw/README.md`
- Modify: `.gitignore`
- Modify: `tests/validation/test_ucomx_comparator.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Add `openpyxl` dependency if missing**

Check:

```powershell
Select-String -Path requirements.txt -Pattern '^openpyxl$'
```

If missing, add:

```text
openpyxl
```

- [ ] **Step 2: Write failing normalizer helper test**

Add:

```python
class UcomxNormalizerTests(unittest.TestCase):
    def test_build_case_id_and_label_are_public_safe(self):
        from tools.normalize_ucomx_outputs import build_case_id, build_source_filename_label

        self.assertEqual("ucomx_truebeam_001", build_case_id("truebeam", 1))
        self.assertEqual("truebeam_case_001", build_source_filename_label("truebeam", 1))
```

- [ ] **Step 3: Run test to verify it fails**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py::UcomxNormalizerTests::test_build_case_id_and_label_are_public_safe -q
```

Expected: FAIL because `tools.normalize_ucomx_outputs` does not exist.

- [ ] **Step 4: Implement normalizer script**

Create `tools/normalize_ucomx_outputs.py` with:

```python
from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from openpyxl import load_workbook
import yaml


DEFAULT_METRICS = [
    "LT",
    "LTMU",
    "LTNLMU",
    "LTNL",
    "LNA",
    "MUdeg",
    "LTAL",
    "MCSv",
    "AAV",
    "LSV",
    "SAS5mm",
    "SAS10mm",
    "SAS20mm",
    "MAD",
]


def build_case_id(dataset_key: str, one_based_index: int) -> str:
    return f"ucomx_{dataset_key}_{one_based_index:03d}"


def build_source_filename_label(dataset_key: str, one_based_index: int) -> str:
    return f"{dataset_key}_case_{one_based_index:03d}"


def normalize_workbooks(
    workbook_specs: list[tuple[str, Path, str]],
    output_root: Path,
    *,
    metrics: list[str] | None = None,
) -> dict[str, object]:
    selected_metrics = metrics or DEFAULT_METRICS
    metric_rows: list[dict[str, object]] = []
    workbook_entries = []

    for dataset_key, workbook_path, engine in workbook_specs:
        workbook_entries.append(
            {
                "workbook_id": dataset_key,
                "engine": engine,
                "sha256": hashlib.sha256(workbook_path.read_bytes()).hexdigest(),
            }
        )
        workbook = load_workbook(workbook_path, read_only=True, data_only=True)
        sheet = workbook["metrics"]
        header = [str(cell) if cell is not None else "" for cell in next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))]
        metric_indexes = {name: header.index(name) for name in selected_metrics if name in header}
        for row_index, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=1):
            case_id = build_case_id(dataset_key, row_index)
            label = build_source_filename_label(dataset_key, row_index)
            for metric_name, column_index in metric_indexes.items():
                value = row[column_index]
                if value is None:
                    continue
                metric_rows.append(
                    {
                        "case_id": case_id,
                        "source_dataset": dataset_key,
                        "source_filename_label": label,
                        "comparator_metric": metric_name,
                        "comparator_value": value,
                        "unit": "",
                        "comparator_engine": engine,
                        "relationship_hint": "exact-equivalent",
                        "notes": "",
                    }
                )

    normalized_dir = output_root / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = normalized_dir / "ucomx_metrics.csv"
    fieldnames = [
        "case_id",
        "source_dataset",
        "source_filename_label",
        "comparator_metric",
        "comparator_value",
        "unit",
        "comparator_engine",
        "relationship_hint",
        "notes",
    ]
    with metrics_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metric_rows)

    manifest = {
        "comparator": "UCoMX",
        "comparator_version": "1.0",
        "source_root": "C:/Users/hujin/Desktop/Programming/ucomx",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "normalized_by": "PlanComplexity normalize_ucomx_outputs.py",
        "case_id_strategy": "pseudonymous-sequential",
        "deidentification_status": "normalized-public-safe",
        "public_release_allowed": True,
        "source_workbooks": workbook_entries,
        "checksums": {
            "normalized/ucomx_metrics.csv": hashlib.sha256(metrics_path.read_bytes()).hexdigest(),
        },
        "notes": "Raw UCoMX info sheets and DICOM source paths are intentionally excluded.",
    }
    (output_root / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return {"rows": metric_rows, "manifest": manifest}
```

Add argparse support after helper functions:

```python
def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize UCoMX Excel output workbooks.")
    parser.add_argument("--output-root", default="validation/external_comparators/ucomx")
    parser.add_argument(
        "--workbook",
        action="append",
        nargs=3,
        metavar=("DATASET_KEY", "PATH", "ENGINE"),
        required=True,
        help="Dataset key, workbook path, and comparator engine, e.g. truebeam C:/.../TrueBeam.xlsx VCoMX",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    specs = [(dataset, Path(path), engine) for dataset, path, engine in args.workbook]
    normalize_workbooks(specs, Path(args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Add raw README**

Create `validation/external_comparators/ucomx/raw/README.md`:

```markdown
# Raw UCoMX Comparator Evidence

Raw UCoMX workbooks and DICOM-derived output files are internal audit evidence only.

Do not commit raw Excel `info` sheets, DICOM files, `dataset.mat`, or any file containing patient identifiers, local clinical paths, institution names, dates of birth, MRN, or UIDs.

Use `tools/normalize_ucomx_outputs.py` to create public-safe normalized comparator rows.
```

- [ ] **Step 6: Update `.gitignore`**

Add:

```gitignore
# UCoMX comparator local/protected evidence
validation/external_comparators/ucomx/raw/*
!validation/external_comparators/ucomx/raw/README.md
validation/external_comparators/ucomx/local_case_map*.yaml
```

If working from project root rather than workspace root, also add project-local patterns:

```gitignore
validation/external_comparators/ucomx/raw/*
!validation/external_comparators/ucomx/raw/README.md
validation/external_comparators/ucomx/local_case_map*.yaml
```

- [ ] **Step 7: Run tests**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

```powershell
git add requirements.txt tools/normalize_ucomx_outputs.py validation/external_comparators/ucomx/raw/README.md .gitignore tests/validation/test_ucomx_comparator.py
git commit -m "Add UCoMX output normalizer"
```

---

## Task 4: Generate Initial Normalized UCoMX Evidence Pack

**Files:**
- Create: `validation/external_comparators/ucomx/manifest.yaml`
- Create: `validation/external_comparators/ucomx/mapping.yaml`
- Create: `validation/external_comparators/ucomx/normalized/ucomx_metrics.csv`
- Modify: `tests/validation/test_ucomx_comparator.py`

- [ ] **Step 1: Create mapping file**

Create `validation/external_comparators/ucomx/mapping.yaml`:

```yaml
mappings:
  - comparator_metric: LT
    internal_metric: lt
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: mm
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX leaf travel.
  - comparator_metric: LTMU
    internal_metric: ltmu
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: mm/MU
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX leaf travel per MU.
  - comparator_metric: LTNLMU
    internal_metric: ltnlmu
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: mm/(leaf*MU)
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX leaf travel per leaf and MU.
  - comparator_metric: LTNL
    internal_metric: ltnl
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: mm/leaf
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX leaf travel per leaf.
  - comparator_metric: LNA
    internal_metric: lna
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: mm/(leaf*deg)
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX leaf travel normalized by control arc length and leaf count.
  - comparator_metric: MUdeg
    internal_metric: mudeg
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: MU/deg
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX monitor units per gantry degree.
  - comparator_metric: LTAL
    internal_metric: ltal
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: mm/deg
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX leaf travel per arc length.
  - comparator_metric: MCSv
    internal_metric: mcsv
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: dimensionless
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX VMAT modulation complexity score.
  - comparator_metric: AAV
    internal_metric: aav
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: dimensionless
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX aperture area variability.
  - comparator_metric: LSV
    internal_metric: lsv
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: dimensionless
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX leaf sequence variability.
  - comparator_metric: SAS5mm
    internal_metric: sas_5mm
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: dimensionless
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX small aperture score at 5 mm.
  - comparator_metric: SAS10mm
    internal_metric: sas_10mm
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: dimensionless
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX small aperture score at 10 mm.
  - comparator_metric: SAS20mm
    internal_metric: sas_20mm
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: dimensionless
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX small aperture score at 20 mm.
  - comparator_metric: MAD
    internal_metric: mad
    platform: VMAT_IMRT
    relationship: exact-equivalent
    unit: mm
    abs_tol: 1.0e-4
    rel_tol: 1.0e-4
    notes: VCoMX mean asymmetry distance.
```

- [ ] **Step 2: Generate normalized CSV from historical UCoMX workbooks**

Run from the repository root.

```powershell
.venv\Scripts\python.exe tools\normalize_ucomx_outputs.py `
  --output-root validation\external_comparators\ucomx `
  --workbook truebeam_jsz "C:\Users\hujin\Desktop\Programming\ucomx\data\TB_JSZ\1-ExtractionName-20251229202454.303\TB_JSZ_dataset.xlsx" VCoMX `
  --workbook halcyon_jsz "C:\Users\hujin\Desktop\Programming\ucomx\data\Hal_JSZ\1-ExtractionName-20251229202958.09\Hal_JSZ_dataset.xlsx" VCoMX
```

Expected:

- `validation/external_comparators/ucomx/manifest.yaml` exists
- `validation/external_comparators/ucomx/normalized/ucomx_metrics.csv` exists
- no patient names, MRNs, UIDs, local paths, or original filenames appear in the normalized CSV

- [ ] **Step 3: Write failing checked-pack test**

Add:

```python
class UcomxCheckedPackTests(unittest.TestCase):
    def test_checked_in_ucomx_pack_loads_and_is_public_safe(self):
        from validation.ucomx_comparator import (
            load_ucomx_manifest,
            load_ucomx_mapping,
            load_ucomx_metric_rows,
        )

        root = Path("validation/external_comparators/ucomx")
        manifest = load_ucomx_manifest(root)
        mappings = load_ucomx_mapping(root)
        rows = load_ucomx_metric_rows(root)

        self.assertTrue(manifest.public_release_allowed)
        self.assertGreaterEqual(len(mappings), 10)
        self.assertGreater(len(rows), 100)
        self.assertTrue(all(row.case_id.startswith("ucomx_") for row in rows))
```

- [ ] **Step 4: Run checked-pack test**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py::UcomxCheckedPackTests::test_checked_in_ucomx_pack_loads_and_is_public_safe -q
```

Expected: PASS after generated files are present.

- [ ] **Step 5: Inspect normalized CSV for obvious PHI**

Run:

```powershell
Select-String -Path validation\external_comparators\ucomx\normalized\ucomx_metrics.csv -Pattern 'Patient|Birth|UID|C:\\|Desktop|Zhang|Chen|Wang|Huang|RP\.TB_|RP\.RTA'
```

Expected: no matches.

- [ ] **Step 6: Commit**

```powershell
git add validation/external_comparators/ucomx/manifest.yaml validation/external_comparators/ucomx/mapping.yaml validation/external_comparators/ucomx/normalized/ucomx_metrics.csv tests/validation/test_ucomx_comparator.py
git commit -m "Add normalized UCoMX comparator evidence"
```

---

## Task 5: Add UCoMX Comparison Runner

**Files:**
- Create: `tools/run_ucomx_comparison.py`
- Modify: `validation/ucomx_comparator.py`
- Modify: `tests/validation/test_ucomx_comparator.py`

- [ ] **Step 1: Write failing comparison test with mocked PyUCoMX results**

Add:

```python
class UcomxComparisonTests(unittest.TestCase):
    def test_compares_exact_equivalent_rows(self):
        from validation.ucomx_comparator import compare_ucomx_rows

        mappings = [
            type("Mapping", (), {
                "comparator_metric": "LT",
                "internal_metric": "lt",
                "platform": "VMAT_IMRT",
                "relationship": "exact-equivalent",
                "unit": "mm",
                "abs_tol": 1.0e-4,
                "rel_tol": 1.0e-4,
                "notes": "",
            })()
        ]
        rows = [
            type("Row", (), {
                "case_id": "ucomx_truebeam_001",
                "comparator_metric": "LT",
                "comparator_value": 117.3,
                "unit": "mm",
                "source_dataset": "truebeam",
            })()
        ]
        observed_by_case = {"ucomx_truebeam_001": {"lt": 117.30001}}

        report = compare_ucomx_rows(rows, mappings, observed_by_case)

        self.assertEqual(1, report["summary"]["comparisons_total"])
        self.assertEqual(0, report["summary"]["failures"])
        self.assertEqual("pass", report["comparisons"][0]["status"])
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py::UcomxComparisonTests::test_compares_exact_equivalent_rows -q
```

Expected: FAIL because `compare_ucomx_rows` is missing.

- [ ] **Step 3: Implement comparator**

Add to `validation/ucomx_comparator.py`:

```python
def compare_ucomx_rows(
    rows: list[UcomxMetricRow],
    mappings: list[UcomxMapping],
    observed_by_case: dict[str, dict[str, float | int | str | None]],
) -> dict[str, object]:
    mapping_by_metric = {mapping.comparator_metric: mapping for mapping in mappings}
    comparison_rows = []
    failures = 0
    for row in rows:
        mapping = mapping_by_metric.get(row.comparator_metric)
        if mapping is None:
            comparison_rows.append(_comparison_row(row, None, None, "skipped", "No mapping."))
            continue
        if mapping.relationship != "exact-equivalent":
            comparison_rows.append(_comparison_row(row, mapping, None, "skipped", mapping.relationship))
            continue
        observed = observed_by_case.get(row.case_id, {}).get(mapping.internal_metric)
        if not _is_numeric(observed):
            comparison_rows.append(_comparison_row(row, mapping, observed, "fail", "Missing numeric observed value."))
            failures += 1
            continue
        abs_diff = abs(float(observed) - float(row.comparator_value))
        rel_diff = abs_diff / max(abs(float(row.comparator_value)), 1e-12)
        passed = (
            (mapping.abs_tol is not None and abs_diff <= mapping.abs_tol)
            or (mapping.rel_tol is not None and rel_diff <= mapping.rel_tol)
        )
        status = "pass" if passed else "fail"
        if not passed:
            failures += 1
        comparison_rows.append(
            {
                "case_id": row.case_id,
                "source_dataset": row.source_dataset,
                "platform": mapping.platform,
                "comparator_metric": row.comparator_metric,
                "internal_metric": mapping.internal_metric,
                "relationship": mapping.relationship,
                "expected": row.comparator_value,
                "observed": observed,
                "abs_diff": abs_diff,
                "rel_diff": rel_diff,
                "abs_tol": mapping.abs_tol,
                "rel_tol": mapping.rel_tol,
                "status": status,
                "notes": mapping.notes,
            }
        )
    return {
        "summary": {
            "comparisons_total": len(comparison_rows),
            "failures": failures,
            "ucomx_comparison_green": failures == 0,
        },
        "comparisons": comparison_rows,
    }
```

Also add `_comparison_row()` and `_is_numeric()` helpers.

- [ ] **Step 4: Add CLI runner**

Create `tools/run_ucomx_comparison.py`:

```python
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.ucomx_comparator import (
    compare_ucomx_rows,
    load_ucomx_mapping,
    load_ucomx_metric_rows,
)
from validation.utils.serializers import write_csv_artifact, write_json_artifact


def run_ucomx_comparison(
    evidence_root: Path | str = "validation/external_comparators/ucomx",
    *,
    observed_by_case: dict[str, dict[str, float | int | str | None]] | None = None,
    output_dir: Path | str | None = None,
) -> dict[str, object]:
    root = Path(evidence_root)
    rows = load_ucomx_metric_rows(root)
    mappings = load_ucomx_mapping(root)
    report = compare_ucomx_rows(rows, mappings, observed_by_case or {})
    report["generated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if output_dir is not None:
        out = Path(output_dir)
        summary_path = out / "ucomx_comparison_summary.md"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(_render_summary_markdown(report), encoding="utf-8")
        report["artifacts"] = {
            "json": str(write_json_artifact(out / "ucomx_comparison_report.json", report)),
            "csv": str(
                write_csv_artifact(
                    out / "ucomx_comparison_report.csv",
                    report["comparisons"],
                    fieldnames=[
                        "case_id",
                        "source_dataset",
                        "platform",
                        "comparator_metric",
                        "internal_metric",
                        "relationship",
                        "expected",
                        "observed",
                        "abs_diff",
                        "rel_diff",
                        "abs_tol",
                        "rel_tol",
                        "status",
                        "notes",
                    ],
                )
            ),
            "summary_markdown": str(summary_path),
        }
    return report


def _render_summary_markdown(report: dict[str, object]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    comparisons = summary.get("comparisons_total", "")
    failures = summary.get("failures", "")
    green = summary.get("ucomx_comparison_green", "")
    return (
        "# UCoMX Comparator Summary\n\n"
        f"- Comparisons: {comparisons}\n"
        f"- Failures: {failures}\n"
        f"- UCoMX comparison green: {green}\n\n"
        "This artifact uses normalized checked-in UCoMX/VCoMX output evidence and does not execute Matlab or UCoMX.\n"
    )
```

This first CLI can support mocked/report-only comparison. Add protected RTPLAN case-map execution in Task 6.

- [ ] **Step 5: Run comparison tests**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py::UcomxComparisonTests -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add validation/ucomx_comparator.py tools/run_ucomx_comparison.py tests/validation/test_ucomx_comparator.py
git commit -m "Add UCoMX comparison runner"
```

---

## Task 6: Add Protected Case Map Support And Full Local Comparison

**Files:**
- Modify: `validation/ucomx_comparator.py`
- Modify: `tools/run_ucomx_comparison.py`
- Modify: `tests/validation/test_ucomx_comparator.py`

- [ ] **Step 1: Write failing case-map test**

Add:

```python
class UcomxCaseMapTests(unittest.TestCase):
    def test_loads_local_case_map(self):
        from validation.ucomx_comparator import load_ucomx_case_map

        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "local_case_map.yaml"
            path.write_text(
                """
                cases:
                  - case_id: ucomx_truebeam_001
                    domain: VMAT_IMRT
                    source_path: data/TrueBeam/example.dcm
                """.strip(),
                encoding="utf-8",
            )

            case_map = load_ucomx_case_map(path)

        self.assertEqual("data/TrueBeam/example.dcm", case_map["ucomx_truebeam_001"].source_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py::UcomxCaseMapTests::test_loads_local_case_map -q
```

Expected: FAIL because `load_ucomx_case_map` is missing.

- [ ] **Step 3: Implement case map loader**

Add `UcomxCaseMapRecord` and loader:

```python
@dataclass(frozen=True)
class UcomxCaseMapRecord:
    case_id: str
    domain: str
    source_path: str


def load_ucomx_case_map(path: Path | str) -> dict[str, UcomxCaseMapRecord]:
    payload = _load_yaml(Path(path))
    rows = payload.get("cases")
    if not isinstance(rows, list):
        raise ValueError("UCoMX case map must define a cases list.")
    records: dict[str, UcomxCaseMapRecord] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"UCoMX case map row {index} must be a mapping.")
        record = UcomxCaseMapRecord(
            case_id=str(row["case_id"]),
            domain=str(row["domain"]),
            source_path=str(row["source_path"]),
        )
        records[record.case_id] = record
    return records
```

- [ ] **Step 4: Extend runner to analyze local RTPLANs**

In `tools/run_ucomx_comparison.py`, add:

```python
from validation.ucomx_comparator import load_ucomx_case_map
from validation_runtime import analyze_validation_case


def build_observed_by_case(case_map_path: Path | str) -> dict[str, dict[str, float | int | str | None]]:
    case_map = load_ucomx_case_map(case_map_path)
    observed = {}
    for case_id, record in case_map.items():
        result = analyze_validation_case(record.source_path, record.domain)
        observed[case_id] = result.metrics
    return observed
```

Update CLI args:

```python
parser.add_argument("--case-map", help="Protected local YAML mapping case_id to RTPLAN source_path.")
parser.add_argument("--strict", action="store_true", help="Exit non-zero if UCoMX exact comparisons fail.")
```

If `--case-map` is provided, call `build_observed_by_case()`.

- [ ] **Step 5: Create protected local case map outside tracked files**

Create `%TEMP%\PlanComplexity\ucomx_comparator\local_case_map.yaml` with a small subset mapping `ucomx_truebeam_001` etc. to local project RTPLANs. Use the UCoMX workbook `info` sheet to align case order to `data/TrueBeam` and `data/Halcyon`, but do not commit this file.

Example shape:

```yaml
cases:
  - case_id: ucomx_truebeam_jsz_001
    domain: VMAT_IMRT
    source_path: data/TrueBeam/<local-file>.dcm
```

- [ ] **Step 6: Run local full comparison**

Run:

```powershell
.venv\Scripts\python.exe tools\run_ucomx_comparison.py `
  --case-map %TEMP%\PlanComplexity\ucomx_comparator\local_case_map.yaml `
  --output-dir run_reports\validation `
  --strict
```

Expected:

- `run_reports/validation/ucomx_comparison_report.json` exists
- `run_reports/validation/ucomx_comparison_report.csv` exists
- `run_reports/validation/ucomx_comparison_summary.md` exists
- strict mode exits `0` if exact-equivalent rows pass

If failures occur, inspect whether they are formula issues, unit/rounding issues, case-order mismatches, or UCoMX/PyUCoMX scope differences. Do not widen tolerances until the cause is documented.

- [ ] **Step 7: Commit code, not local case map**

```powershell
git add validation/ucomx_comparator.py tools/run_ucomx_comparison.py tests/validation/test_ucomx_comparator.py
git commit -m "Support protected UCoMX case maps"
```

---

## Task 7: Integrate UCoMX Report Into Validation Summary

**Files:**
- Modify: `tools/build_validation_report.py`
- Modify: `validation/reports/templates/validation_summary.md.j2`
- Modify: `tests/validation/test_validation_report.py`

- [ ] **Step 1: Write failing report integration test**

In `tests/validation/test_validation_report.py`, extend `test_report_builder_writes_summary_artifacts` or add a new test with a fake UCoMX report:

```python
def test_summary_includes_ucomx_report_when_available(self):
    from tools.build_validation_report import render_validation_artifacts

    fake_reference_report = {
        "profile": "research",
        "summary": {"cases_total": 1, "metrics_total": 1, "exact_metrics_total": 1, "exact_failures": 0},
        "cases": [{"case_id": "vmat_truebeam_canonical", "domain": "VMAT_IMRT"}],
        "metrics": [{"domain": "VMAT_IMRT", "metric_key": "lt", "status": "pass", "comparison_class": "exact-equivalent"}],
    }
    fake_comparison_report = {"profile": "research", "comparisons": []}
    fake_ucomx_report = {
        "summary": {"comparisons_total": 14, "failures": 0, "ucomx_comparison_green": True},
        "comparisons": [],
    }

    with TemporaryDirectory() as temp_dir:
        paths = render_validation_artifacts(
            fake_reference_report,
            fake_comparison_report,
            Path(temp_dir),
            ucomx_report=fake_ucomx_report,
        )
        summary = Path(paths["summary_markdown"]).read_text(encoding="utf-8")

    self.assertIn("UCoMX Comparator Evidence", summary)
    self.assertIn("comparisons: 14", summary.lower())
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_validation_report.py::ValidationReportTests::test_summary_includes_ucomx_report_when_available -q
```

Expected: FAIL because `render_validation_artifacts()` has no `ucomx_report` parameter.

- [ ] **Step 3: Update report builder**

Modify `render_validation_artifacts()` signature:

```python
def render_validation_artifacts(
    reference_report: dict[str, Any],
    comparison_report: dict[str, Any],
    output_dir: Path | str,
    *,
    ucomx_report: dict[str, Any] | None = None,
) -> dict[str, str]:
```

Pass `ucomx_report` into `_summary_context()`.

Also update `build_validation_report()` so it will include UCoMX evidence when `output_dir/ucomx_comparison_report.json` already exists:

```python
def _load_optional_ucomx_report(output_root: Path) -> dict[str, Any] | None:
    path = output_root / "ucomx_comparison_report.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
```

Call:

```python
ucomx_report = _load_optional_ucomx_report(output_root)
return render_validation_artifacts(reference_report, comparison_report, output_root, ucomx_report=ucomx_report)
```

- [ ] **Step 4: Update template**

In `validation/reports/templates/validation_summary.md.j2`, after Cross-Tool section add:

```jinja2
{% if ucomx_report %}
## UCoMX Comparator Evidence

- Exact/declared comparisons: {{ ucomx_report.summary.comparisons_total }}
- Failures: {{ ucomx_report.summary.failures }}
- UCoMX comparison green: {{ ucomx_report.summary.ucomx_comparison_green }}

This section uses checked-in normalized UCoMX/VCoMX output evidence and does not require automatic Matlab Runtime execution.
{% endif %}
```

Use a dictionary-safe approach if Jinja dot access is awkward:

```jinja2
{{ ucomx_report["summary"]["comparisons_total"] }}
```

- [ ] **Step 5: Run report tests**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_validation_report.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add tools/build_validation_report.py validation/reports/templates/validation_summary.md.j2 tests/validation/test_validation_report.py
git commit -m "Include UCoMX comparator evidence in validation summary"
```

---

## Task 8: Update Clinical/Open-source Readiness Gate

**Files:**
- Modify: `validation/clinical_readiness.py`
- Modify: `tests/validation/test_clinical_readiness.py`
- Modify: `tools/run_clinical_readiness_gate.py` only if CLI wiring needs adjustment

- [ ] **Step 1: Replace blanket tracked CSV expectation test**

Revise `tests/validation/test_clinical_readiness.py` so tracked validation CSV files are not automatically blocking if they pass public-safety checks.

Add:

```python
def test_readiness_allows_public_safe_validation_csv(self):
    from validation.clinical_readiness import run_clinical_readiness_gate

    def fake_git(_root, args):
        if args[:2] == ["ls-files", "*.csv"]:
            return subprocess.CompletedProcess(["git", *args], 0, stdout="validation/external_comparators/ucomx/normalized/ucomx_metrics.csv\n", stderr="")
        if args[:3] == ["log", "--oneline", "--all"]:
            return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")
        return subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")

    with patch("validation.clinical_readiness._git", side_effect=fake_git):
        with patch("validation.clinical_readiness._tracked_csvs_are_public_safe", return_value=(True, "Tracked CSV files are public safe.")):
            report = run_clinical_readiness_gate(Path("."))

    checks = {row["check_id"]: row for row in report["checks"]}
    self.assertEqual("pass", checks["tracked_csv_public_safety"]["status"])
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_clinical_readiness.py::ClinicalReadinessTests::test_readiness_allows_public_safe_validation_csv -q
```

Expected: FAIL because new check function does not exist.

- [ ] **Step 3: Implement readiness checks**

In `validation/clinical_readiness.py`:

- Replace `_check_no_tracked_csv()` with `_check_tracked_csv_public_safety()`.
- Keep `_check_csv_history_clean()` as a blocker for open-source release unless a future clean release repo is used.
- Add `_check_ucomx_pack_ready(root)`.
- Add `_check_ucomx_comparison_artifacts(root)`.

Implementation outline:

```python
def _check_tracked_csv_public_safety(root: Path) -> dict[str, object]:
    result = _git(root, ["ls-files", "*.csv"])
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    safe, message = _tracked_csvs_are_public_safe(root, tracked)
    return _check("tracked_csv_public_safety", "pass" if safe else "fail", message, blocking=True)


def _tracked_csvs_are_public_safe(root: Path, paths: list[str]) -> tuple[bool, str]:
    forbidden = ("Patient", "Birth", "MRN", "UID", "C:\\", "Desktop")
    for relative in paths:
        path = root / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in forbidden:
            if token in text:
                return False, f"Tracked CSV '{relative}' contains forbidden token '{token}'."
    return True, "Tracked CSV files are public safe."
```

For `ucomx_pack_ready`, load manifest, mapping, and rows from `validation/external_comparators/ucomx`.

- [ ] **Step 4: Run readiness tests**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_clinical_readiness.py -q
```

Expected: PASS.

- [ ] **Step 5: Run readiness tool**

Run:

```powershell
.venv\Scripts\python.exe tools\run_clinical_readiness_gate.py --output-dir run_reports\validation
```

Expected:

- UCoMX pack checks appear.
- `clinical_ready` remains `false`.
- `open_source_ready` may remain `false` because existing CSV history is still a blocker; that is acceptable and should be stated in the report.

- [ ] **Step 6: Commit**

```powershell
git add validation/clinical_readiness.py tests/validation/test_clinical_readiness.py tools/run_clinical_readiness_gate.py
git commit -m "Add UCoMX readiness guardrails"
```

---

## Task 9: Draft Technical Report And README Workflow

**Files:**
- Create: `docs/research/ucomx_comparator_validation_technical_report.md`
- Modify: `README.md`
- Modify: `tests/validation/test_validation_report.py` or add a small docs test if desired

- [ ] **Step 1: Draft technical report**

Create `docs/research/ucomx_comparator_validation_technical_report.md` with:

```markdown
# Multi-system Plan Complexity Calculator and UCoMX Comparator Validation Technical Report

## Intended Use and Scope

This tool supports research and publication-oriented plan complexity analysis. It is not a clinical deployment release and must not be used as a standalone patient-specific QA pass/fail tool.

## Supported Delivery Systems

- VMAT/IMRT
- TOMO
- CyberKnife MLC
- Aurora SVMAT
- Halcyon/Ethos dual-layer metrics where DICOM data support those definitions

## Metric Inventory and Definition Sources

Summarize metric families and point to `docs/metric_definitions_*.md`.

## UCoMX Comparator Evidence

Describe normalized checked-in VCoMX output evidence, exact-equivalent metric mapping, tolerance policy, number of compared rows, and limitations.

## Reference Suite Validation

Summarize reference-case suite results and artifact paths.

## Known Non-comparability and System-specific Assumptions

State that Aurora, CyberKnife MLC, TOMO private tag behavior, and Halcyon/Ethos layer-specific metrics are not universal UCoMX equivalence claims.

## Clinical Governance Notes

Complexity metrics may inform plan review and QA risk stratification research. They do not replace patient-specific QA, clinical physicist review, or local governance approval.

## Open-source Release Readiness

Normalized comparator rows are designed for public-safe release. Raw workbooks, DICOM files, local case maps, and PHI-bearing outputs remain internal.

## Reproducibility Appendix

List commands:

```powershell
python tools/normalize_ucomx_outputs.py ...
python tools/run_ucomx_comparison.py ...
python tools/build_validation_report.py ...
python tools/run_clinical_readiness_gate.py ...
```
```

- [ ] **Step 2: Update README**

Add a section:

```markdown
## UCoMX Comparator Validation

The UCoMX comparator layer uses checked-in normalized UCoMX/VCoMX output evidence. It does not require Matlab Runtime or UCoMX execution in CI.

Raw UCoMX Excel workbooks and local RTPLAN case maps are internal evidence only. Do not commit PHI-bearing `info` sheets, raw DICOM files, or local clinical paths.
```

Include command examples for normalizer, comparator, and validation report.

- [ ] **Step 3: Run README docs test**

Run:

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_validation_report.py::ReadmeValidationDocsTests::test_readme_mentions_validation_commands -q
```

Expected: PASS, after updating test if it should check for `run_ucomx_comparison.py`.

- [ ] **Step 4: Commit**

```powershell
git add README.md docs/research/ucomx_comparator_validation_technical_report.md tests/validation/test_validation_report.py
git commit -m "Document UCoMX comparator validation workflow"
```

---

## Task 10: Full Verification And Evidence Rebuild

**Files:**
- Modify generated reports under `run_reports/validation/` only if the project policy keeps them tracked.
- Do not commit local case maps or raw UCoMX workbooks.

- [ ] **Step 1: Run focused UCoMX tests**

```powershell
.venv\Scripts\python.exe -m pytest tests/validation/test_ucomx_comparator.py -q
```

Expected: PASS.

- [ ] **Step 2: Run validation test suite**

```powershell
.venv\Scripts\python.exe -m pytest tests/validation -q
```

Expected: PASS.

- [ ] **Step 3: Run full project tests**

```powershell
.venv\Scripts\python.exe -m pytest -q
```

Expected: all tests pass, allowing existing intentional skips.

- [ ] **Step 4: Rebuild reference and comparator artifacts**

```powershell
.venv\Scripts\python.exe tools\run_reference_suite.py --profile research --output-dir run_reports\validation
.venv\Scripts\python.exe tools\run_tool_comparison.py --profile research --output-dir run_reports\validation
.venv\Scripts\python.exe tools\run_ucomx_comparison.py --case-map %TEMP%\PlanComplexity\ucomx_comparator\local_case_map.yaml --output-dir run_reports\validation
.venv\Scripts\python.exe tools\build_validation_report.py --profile research --output-dir run_reports\validation
.venv\Scripts\python.exe tools\run_clinical_readiness_gate.py --output-dir run_reports\validation
```

Expected:

- reference suite green for exact metrics
- UCoMX comparator green for exact-equivalent rows or documented failures
- readiness gate includes UCoMX pack checks
- `clinical_ready` remains false
- `open_source_ready` reflects data/history governance state

- [ ] **Step 5: Inspect git status**

```powershell
git status --short
```

Expected:

- No raw UCoMX workbooks staged.
- No local case map staged.
- Only intended code, normalized evidence, docs, tests, and optionally tracked report artifacts appear.

- [ ] **Step 6: Commit generated report artifacts if policy requires**

If report artifacts are intentionally tracked:

```powershell
git add run_reports/validation/ucomx_comparison_report.json run_reports/validation/ucomx_comparison_report.csv run_reports/validation/ucomx_comparison_summary.md run_reports/validation/validation_summary.md run_reports/validation/validation_report.json run_reports/validation/manifest_lock.json
git commit -m "Refresh UCoMX validation evidence artifacts"
```

If report artifacts are not intended to change in source control, leave them uncommitted and document their paths in the final handoff.

---

## Final Acceptance Criteria

- `validation/external_comparators/ucomx/normalized/ucomx_metrics.csv` loads and passes PHI/public-safety checks.
- UCoMX mapping covers the initial VMAT/IMRT exact-equivalent candidates from the design spec.
- `tools/run_ucomx_comparison.py` generates JSON, CSV, and Markdown artifacts.
- Full local UCoMX comparison can run from a protected local case map without committing PHI-bearing paths.
- Validation summary includes UCoMX comparator evidence when available.
- Readiness gate reports UCoMX pack status, UCoMX comparison status, public-safety status, and still avoids clinical deployment claims.
- Technical report states evidence tiers and claim boundaries.
- `python -m pytest -q` passes.

## Known Risks

- Historical UCoMX workbooks contain PHI in `info` sheets; never commit raw workbooks.
- Source RTPLAN filenames in local data can include patient-like tokens; keep exact filenames out of normalized CSV and public manifest.
- UCoMX and PyUCoMX may differ for metrics where aggregation or active-leaf handling differs; classify these as derived or non-comparable instead of widening tolerance silently.
- Open-source readiness may remain blocked by existing repository history even after normalized UCoMX evidence is public safe. A clean release repository or approved data package may still be required.
