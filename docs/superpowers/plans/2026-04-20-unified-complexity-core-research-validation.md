# Unified Complexity Core Research Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a research-grade validation framework that unifies metric specifications, reference cases, comparator mappings, and reproducible validation artifacts across VMAT/IMRT, TOMO, CyberKnife MLC, and Aurora.

**Architecture:** Add a standalone `validation/` layer beside the current runtime analyzers instead of mixing validation rules into the metric-calculation code. Reuse existing runtime entry points from `ucomx_service.py`, `metric_registry.py`, `metric_definition_catalog.py`, and `aurora_svmat_lab/` to normalize outputs into canonical validation records, then compare those records against checked-in reference cases and comparator mappings to produce JSON/CSV/Markdown evidence artifacts.

**Tech Stack:** Python 3.10+, unittest, existing NumPy/Pandas/SciPy/PyDICOM stack, plus `PyYAML`, `jsonschema`, and `Jinja2` for checked-in specs, schema validation, and report templating.

---

## File Map

### New validation package

- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\__init__.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\__init__.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\loaders.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\tolerances.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\statistics.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\comparators.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\serializers.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation_models.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation_runtime.py`

### Checked-in validation specifications

- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\specs\metric_specs.yaml`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\specs\metric_groups.yaml`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\specs\comparator_mapping.yaml`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\specs\validation_profiles.yaml`

### Validation schemas

- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\schemas\metric_spec.schema.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\schemas\reference_case.schema.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\schemas\comparator_mapping.schema.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\schemas\validation_report.schema.json`

### Reference cases

- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\manifest.yaml`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\cases\<case_id>\expected_metrics.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\cases\<case_id>\provenance.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\cases\<case_id>\notes.md`

### Report builders

- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reports\templates\validation_summary.md.j2`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reports\templates\comparison_table.csv.j2`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tools\run_reference_suite.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tools\run_tool_comparison.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tools\build_validation_report.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tools\freeze_reference_outputs.py`

### Existing files to integrate with

- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\requirements.txt`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\metric_registry.py`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\metric_definition_catalog.py`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\README.md`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\.github\workflows\validation.yml`

### New tests

- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\__init__.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_validation_smoke.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_metric_specs.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_spec_loaders.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_validation_runtime.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_reference_manifest.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_reference_suite.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_tool_comparison.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_validation_report.py`

## Task 1: Bootstrap Validation Package And Dependencies

**Files:**
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\requirements.txt`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\__init__.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\__init__.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\__init__.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_validation_smoke.py`

- [ ] **Step 1: Write the failing package-import smoke test**

```python
import unittest


class ValidationSmokeTests(unittest.TestCase):
    def test_validation_modules_import(self):
        import validation  # noqa: F401
        import validation_runtime  # noqa: F401
        import validation_models  # noqa: F401


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the smoke test to verify failure**

Run: `python -m unittest tests.validation.test_validation_smoke -v`
Expected: FAIL with `ModuleNotFoundError` for `validation_runtime` or `validation_models`

- [ ] **Step 3: Add the minimal package skeleton and validation dependencies**

```text
requirements.txt
numpy
pandas
pydicom
scipy
pytest
PyYAML
jsonschema
Jinja2
```

- [ ] **Step 4: Re-run the smoke test to verify the package skeleton passes**

Run: `python -m unittest tests.validation.test_validation_smoke -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add requirements.txt validation/__init__.py validation/utils/__init__.py tests/validation/__init__.py tests/validation/test_validation_smoke.py validation_runtime.py validation_models.py
git commit -m "build: scaffold validation package"
```

## Task 2: Check In Canonical Metric Specs And Profiles

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\specs\metric_specs.yaml`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\specs\metric_groups.yaml`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\specs\validation_profiles.yaml`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\metric_definition_catalog.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_metric_specs.py`

- [ ] **Step 1: Write the failing spec inventory test**

```python
import unittest

from metric_definition_catalog import build_metric_definition_catalog


class MetricSpecInventoryTests(unittest.TestCase):
    def test_checked_in_metric_specs_cover_all_catalog_metrics(self):
        from validation.utils.loaders import load_metric_specs

        catalog_keys = {(record.platform, record.metric_key) for record in build_metric_definition_catalog()}
        spec_keys = {(record.platform, record.metric_key) for record in load_metric_specs()}
        self.assertTrue(catalog_keys.issubset(spec_keys))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the spec inventory test to verify failure**

Run: `python -m unittest tests.validation.test_metric_specs -v`
Expected: FAIL because `load_metric_specs()` and the checked-in YAML files do not exist yet

- [ ] **Step 3: Check in the initial metric spec, metric group, and validation profile files**

```yaml
# validation/specs/validation_profiles.yaml
profiles:
  research:
    exact_abs_default: 1.0e-6
    exact_rel_default: 1.0e-4
    require_reference_exact_green: true
    include_association_only_in_core_gate: false
```

```yaml
# validation/specs/metric_specs.yaml
metrics:
  - platform: VMAT_IMRT
    metric_key: mcsv
    label: MCSv
    unit: dimensionless
    aggregation_scope: plan
    normalization_basis: beam_weighted_mean
    validation_level: Reference-case exact
    comparison_class: exact-equivalent
    default_tolerance_abs: 1.0e-6
    default_tolerance_rel: 1.0e-4
    clinical_readiness: research
```

- [ ] **Step 4: Extend `metric_definition_catalog.py` with a stable export-friendly platform and metric-key accessor if any catalog gaps block the YAML inventory**

```python
def metric_catalog_keys() -> set[tuple[str, str]]:
    return {(record.platform, record.metric_key) for record in build_metric_definition_catalog()}
```

- [ ] **Step 5: Re-run the spec inventory test to verify pass**

Run: `python -m unittest tests.validation.test_metric_specs -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add validation/specs/metric_specs.yaml validation/specs/metric_groups.yaml validation/specs/validation_profiles.yaml metric_definition_catalog.py tests/validation/test_metric_specs.py
git commit -m "feat: add canonical validation metric specs"
```

## Task 3: Add JSON Schemas, Typed Loaders, And Schema Validation

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\schemas\metric_spec.schema.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\schemas\reference_case.schema.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\schemas\comparator_mapping.schema.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\schemas\validation_report.schema.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation_models.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\loaders.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_spec_loaders.py`

- [ ] **Step 1: Write the failing schema-loader test**

```python
import unittest


class ValidationLoaderTests(unittest.TestCase):
    def test_metric_specs_load_as_typed_records(self):
        from validation.utils.loaders import load_metric_specs

        specs = load_metric_specs()
        self.assertGreater(len(specs), 20)
        self.assertTrue(all(hasattr(spec, "metric_key") for spec in specs))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the schema-loader test to verify failure**

Run: `python -m unittest tests.validation.test_spec_loaders -v`
Expected: FAIL because typed loaders and schema validators are missing

- [ ] **Step 3: Implement the validation dataclasses and YAML-plus-schema loaders**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class MetricSpecRecord:
    platform: str
    metric_key: str
    label: str
    unit: str
    aggregation_scope: str
    validation_level: str
    comparison_class: str
```

```python
def load_metric_specs():
    payload = _load_yaml("validation/specs/metric_specs.yaml")
    _validate_schema(payload, "validation/schemas/metric_spec.schema.json")
    return [MetricSpecRecord(**item) for item in payload["metrics"]]
```

- [ ] **Step 4: Re-run the schema-loader test to verify pass**

Run: `python -m unittest tests.validation.test_spec_loaders -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add validation/schemas validation_models.py validation/utils/loaders.py tests/validation/test_spec_loaders.py
git commit -m "feat: add validation schema loaders"
```

## Task 4: Implement Runtime Normalization For All Four Domains

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation_runtime.py`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\metric_registry.py`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\metric_definition_catalog.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_validation_runtime.py`

- [ ] **Step 1: Write the failing runtime-normalization test**

```python
import unittest


class ValidationRuntimeTests(unittest.TestCase):
    def test_runtime_normalization_returns_canonical_metric_records(self):
        from validation_runtime import analyze_validation_case

        record = analyze_validation_case(
            source_path="data/Aurora/RTPLAN_57661.dcm",
            domain="AURORA",
        )
        self.assertEqual(record.domain, "AURORA")
        self.assertIn("projection_pitch_mean", record.metrics)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the runtime-normalization test to verify failure**

Run: `python -m unittest tests.validation.test_validation_runtime -v`
Expected: FAIL because `analyze_validation_case()` does not exist

- [ ] **Step 3: Implement a canonical runtime bridge for VMAT/IMRT, TOMO, CyberKnife MLC, and Aurora**

```python
def analyze_validation_case(source_path: str, domain: str):
    if domain == "AURORA":
        from aurora_svmat_lab.service import analyze_plan_file as analyze_aurora_plan_file

        result = analyze_aurora_plan_file(source_path)
        return _normalize_aurora_result(result)

    from ucomx_service import analyze_plan_file

    result = analyze_plan_file(source_path)
    return _normalize_core_result(result)
```

- [ ] **Step 4: Re-run the runtime-normalization test to verify pass**

Run: `python -m unittest tests.validation.test_validation_runtime -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add validation_runtime.py metric_registry.py metric_definition_catalog.py tests/validation/test_validation_runtime.py
git commit -m "feat: normalize runtime outputs for validation"
```

## Task 5: Check In Reference Cases And Frozen Expected Outputs

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\manifest.yaml`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\cases\vmat_truebeam_canonical\expected_metrics.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\cases\vmat_truebeam_edge\expected_metrics.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\cases\tomo_precision_canonical\expected_metrics.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\cases\tomo_tps_edge\expected_metrics.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\cases\cyberknife_precision_canonical\expected_metrics.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\cases\cyberknife_xml_edge\expected_metrics.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\cases\aurora_canonical\expected_metrics.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reference_cases\cases\aurora_research_edge\expected_metrics.json`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tools\freeze_reference_outputs.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_reference_manifest.py`

- [ ] **Step 1: Write the failing reference-manifest coverage test**

```python
import unittest

from validation.utils.loaders import load_reference_manifest


class ReferenceManifestTests(unittest.TestCase):
    def test_manifest_contains_canonical_and_edge_cases_for_each_domain(self):
        manifest = load_reference_manifest()
        domain_case_types = {(case.domain, case.case_class) for case in manifest}
        self.assertIn(("VMAT_IMRT", "canonical"), domain_case_types)
        self.assertIn(("VMAT_IMRT", "edge"), domain_case_types)
        self.assertIn(("TOMO", "canonical"), domain_case_types)
        self.assertIn(("CYBERKNIFE_MLC", "canonical"), domain_case_types)
        self.assertIn(("AURORA", "canonical"), domain_case_types)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the reference-manifest test to verify failure**

Run: `python -m unittest tests.validation.test_reference_manifest -v`
Expected: FAIL because the manifest and case folders do not exist yet

- [ ] **Step 3: Check in the initial manifest and freeze expected outputs from representative cases**

```yaml
cases:
  - case_id: aurora_canonical
    domain: AURORA
    case_class: canonical
    source_path: data/Aurora/RTPLAN_57661.dcm
    expected_metrics_source: checked_in_json
```

- [ ] **Step 4: Add the baseline-freezing script that regenerates expected outputs from current runtime code with explicit operator confirmation**

```python
def freeze_case(case):
    record = analyze_validation_case(case.source_path, case.domain)
    write_expected_metrics(case.case_id, record.metrics)
```

- [ ] **Step 5: Re-run the reference-manifest test to verify pass**

Run: `python -m unittest tests.validation.test_reference_manifest -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add validation/reference_cases tools/freeze_reference_outputs.py tests/validation/test_reference_manifest.py
git commit -m "feat: add cross-platform reference cases"
```

## Task 6: Implement The Reference Suite And Exact Comparison Engine

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\tolerances.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\serializers.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tools\run_reference_suite.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_reference_suite.py`

- [ ] **Step 1: Write the failing reference-suite test**

```python
import unittest


class ReferenceSuiteTests(unittest.TestCase):
    def test_reference_suite_reports_case_and_metric_level_results(self):
        from tools.run_reference_suite import run_reference_suite

        report = run_reference_suite(profile="research")
        self.assertIn("cases", report)
        self.assertIn("metrics", report)
        self.assertGreater(len(report["cases"]), 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the reference-suite test to verify failure**

Run: `python -m unittest tests.validation.test_reference_suite -v`
Expected: FAIL because the suite runner and tolerance engine are missing

- [ ] **Step 3: Implement exact and tolerance-aware comparisons**

```python
def compare_exact(expected, observed, abs_tol, rel_tol):
    abs_diff = abs(observed - expected)
    rel_diff = 0.0 if expected == 0 else abs_diff / abs(expected)
    return {
        "pass": abs_diff <= abs_tol or rel_diff <= rel_tol,
        "expected": expected,
        "observed": observed,
        "abs_diff": abs_diff,
        "rel_diff": rel_diff,
    }
```

- [ ] **Step 4: Implement the suite runner and JSON/CSV output path**

Run target command to support: `python tools/run_reference_suite.py --profile research --output-dir run_reports/validation`
Expected: writes `reference_case_results.json` and `reference_case_results.csv`

- [ ] **Step 5: Re-run the reference-suite test to verify pass**

Run: `python -m unittest tests.validation.test_reference_suite -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add validation/utils/tolerances.py validation/utils/serializers.py tools/run_reference_suite.py tests/validation/test_reference_suite.py
git commit -m "feat: add reference suite runner"
```

## Task 7: Implement Comparator Mapping And Cross-Tool Comparison

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\specs\comparator_mapping.yaml`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\statistics.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\utils\comparators.py`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tools\run_tool_comparison.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_tool_comparison.py`

- [ ] **Step 1: Write the failing tool-comparison test**

```python
import unittest


class ToolComparisonTests(unittest.TestCase):
    def test_tool_comparison_emits_agreement_statistics(self):
        from tools.run_tool_comparison import run_tool_comparison

        report = run_tool_comparison(profile="research")
        self.assertIn("comparisons", report)
        self.assertTrue(any("mae" in comparison for comparison in report["comparisons"]))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tool-comparison test to verify failure**

Run: `python -m unittest tests.validation.test_tool_comparison -v`
Expected: FAIL because comparator mappings and statistics helpers are missing

- [ ] **Step 3: Check in initial comparator mappings for exact, derived, and non-comparable relationships**

```yaml
mappings:
  - internal_metric: mcsv
    comparator: UCoMX
    comparator_metric: MCSv
    relationship: exact-equivalent
  - internal_metric: projection_pitch_mean
    comparator: AuroraPaper
    comparator_metric: projection_pitch_mean
    relationship: exact-equivalent
```

- [ ] **Step 4: Implement shared agreement statistics and comparison routing**

```python
def summarize_agreement(expected_values, observed_values):
    diffs = [obs - exp for exp, obs in zip(expected_values, observed_values)]
    mae = sum(abs(diff) for diff in diffs) / len(diffs)
    bias = sum(diffs) / len(diffs)
    return {"mae": mae, "bias": bias}
```

- [ ] **Step 5: Re-run the tool-comparison test to verify pass**

Run: `python -m unittest tests.validation.test_tool_comparison -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add validation/specs/comparator_mapping.yaml validation/utils/statistics.py validation/utils/comparators.py tools/run_tool_comparison.py tests/validation/test_tool_comparison.py
git commit -m "feat: add cross-tool comparison pipeline"
```

## Task 8: Build Validation Reports And Publication Artifacts

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reports\templates\validation_summary.md.j2`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\validation\reports\templates\comparison_table.csv.j2`
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tools\build_validation_report.py`
- Test: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\validation\test_validation_report.py`

- [ ] **Step 1: Write the failing validation-report builder test**

```python
import unittest


class ValidationReportTests(unittest.TestCase):
    def test_report_builder_writes_summary_artifacts(self):
        from tools.build_validation_report import build_validation_report

        artifact_paths = build_validation_report(output_dir="run_reports/validation")
        self.assertIn("summary_markdown", artifact_paths)
        self.assertIn("reference_json", artifact_paths)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the report-builder test to verify failure**

Run: `python -m unittest tests.validation.test_validation_report -v`
Expected: FAIL because the templated report builder does not exist

- [ ] **Step 3: Implement the report builder using the suite and comparison outputs**

```python
def build_validation_report(output_dir: str):
    reference_report = run_reference_suite(profile="research", output_dir=output_dir)
    comparison_report = run_tool_comparison(profile="research", output_dir=output_dir)
    return render_validation_artifacts(reference_report, comparison_report, output_dir)
```

- [ ] **Step 4: Re-run the report-builder test to verify pass**

Run: `python -m unittest tests.validation.test_validation_report -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add validation/reports/templates tools/build_validation_report.py tests/validation/test_validation_report.py
git commit -m "feat: add validation report artifacts"
```

## Task 9: Add CI Gates And User-Facing Validation Documentation

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\.github\workflows\validation.yml`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\README.md`

- [ ] **Step 1: Add a failing CI-facing documentation assertion if the validation commands are not discoverable**

```python
import unittest
from pathlib import Path


class ReadmeValidationDocsTests(unittest.TestCase):
    def test_readme_mentions_validation_commands(self):
        readme = Path("README.md").read_text(encoding="utf-8")
        self.assertIn("run_reference_suite.py", readme)
        self.assertIn("build_validation_report.py", readme)
```

- [ ] **Step 2: Run the documentation assertion to verify failure**

Run: `python -m unittest tests.validation.test_validation_report.ReadmeValidationDocsTests -v`
Expected: FAIL because README does not mention the new validation flow yet

- [ ] **Step 3: Add the CI workflow and README validation section**

Workflow command sequence:

```bash
python -m unittest tests.validation.test_metric_specs tests.validation.test_spec_loaders tests.validation.test_validation_runtime tests.validation.test_reference_manifest tests.validation.test_reference_suite tests.validation.test_tool_comparison tests.validation.test_validation_report -v
python tools/run_reference_suite.py --profile research --output-dir run_reports/validation
python tools/build_validation_report.py --profile research --output-dir run_reports/validation
```

- [ ] **Step 4: Re-run the documentation assertion to verify pass**

Run: `python -m unittest tests.validation.test_validation_report.ReadmeValidationDocsTests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/validation.yml README.md
git commit -m "ci: add validation workflow and docs"
```

## Task 10: Run End-To-End Verification And Freeze The First Research Baseline

**Files:**
- Modify only if verification reveals issues in the files above

- [ ] **Step 1: Run the targeted validation test suite**

Run: `python -m unittest tests.validation.test_validation_smoke tests.validation.test_metric_specs tests.validation.test_spec_loaders tests.validation.test_validation_runtime tests.validation.test_reference_manifest tests.validation.test_reference_suite tests.validation.test_tool_comparison tests.validation.test_validation_report -v`
Expected: PASS

- [ ] **Step 2: Run the reference suite against checked-in cases**

Run: `python tools/run_reference_suite.py --profile research --output-dir run_reports/validation`
Expected: writes `reference_case_results.json` and `reference_case_results.csv`

- [ ] **Step 3: Run the comparison and report builders**

Run: `python tools/run_tool_comparison.py --profile research --output-dir run_reports/validation`
Expected: writes `comparator_statistics.csv`

Run: `python tools/build_validation_report.py --profile research --output-dir run_reports/validation`
Expected: writes `validation_summary.md`, `supplement_tables/`, and `manifest_lock.json`

- [ ] **Step 4: Freeze the initial checked-in research baseline**

Run: `python tools/freeze_reference_outputs.py --profile research --case-set canonical`
Expected: updates `validation/reference_cases/cases/*/expected_metrics.json` only for explicitly selected baseline cases

- [ ] **Step 5: Commit**

```bash
git add validation run_reports/validation .github/workflows/validation.yml README.md
git commit -m "chore: freeze initial research validation baseline"
```

## Notes For The Implementer

- Keep validation semantics outside the metric calculators. If a comparison rule changes, the metric implementation should not need to change.
- Do not force Aurora into exact external equivalence when only internal or literature-level evidence exists. Encode that in `comparison_class` and `known_noncomparability`.
- Prefer small, typed records over giant free-form dictionaries in `validation_models.py`.
- Preserve current runtime behavior in `ucomx_service.py` and `aurora_svmat_lab/` unless a normalization gap truly requires a small, targeted export hook.
- Avoid making the report builders depend on private local state. Everything should rebuild from checked-in specs, reference cases, and repository data.
