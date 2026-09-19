import csv
import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


class ValidationReportTests(unittest.TestCase):
    def test_report_builder_writes_summary_artifacts(self):
        from tools.build_validation_report import build_validation_report

        fake_reference_report = {
            "profile": "research",
            "generated_at": "2026-04-28T00:00:00Z",
            "summary": {
                "cases_total": 2,
                "metrics_total": 2,
                "exact_metrics_total": 1,
                "exact_failures": 0,
                "reference_exact_green": True,
            },
            "cases": [
                {
                    "case_id": "vmat_truebeam_canonical",
                    "domain": "VMAT_IMRT",
                    "case_class": "canonical",
                    "device_or_tps": "TrueBeam",
                    "supported": True,
                    "total_metrics": 1,
                    "passes": 1,
                    "failures": 0,
                    "skipped": 0,
                },
                {
                    "case_id": "aurora_canonical",
                    "domain": "AURORA",
                    "case_class": "canonical",
                    "device_or_tps": "Aurora",
                    "supported": True,
                    "total_metrics": 1,
                    "passes": 0,
                    "failures": 0,
                    "skipped": 1,
                },
            ],
            "metrics": [
                {
                    "case_id": "vmat_truebeam_canonical",
                    "domain": "VMAT_IMRT",
                    "metric_key": "lt",
                    "status": "pass",
                    "expected": 117.3,
                    "observed": 117.3,
                    "comparison_class": "exact-equivalent",
                    "validation_level": "Reference-case exact",
                    "group_key": "vmat_aperture",
                    "gate_included": True,
                    "note": "",
                },
                {
                    "case_id": "aurora_canonical",
                    "domain": "AURORA",
                    "metric_key": "projection_pitch_mean",
                    "status": "skipped",
                    "expected": 0.09259232915432099,
                    "observed": 0.09259232915432099,
                    "comparison_class": "not-comparable",
                    "validation_level": "Association-only",
                    "group_key": "aurora_v2_paper_style_physics",
                    "gate_included": False,
                    "note": "Not eligible for exact reference-case comparison.",
                },
            ],
        }
        fake_comparison_report = {
            "profile": "research",
            "generated_at": "2026-04-28T00:00:01Z",
            "comparisons": [
                {
                    "platform": "VMAT_IMRT",
                    "internal_metric": "lt",
                    "comparator": "UCoMX",
                    "comparator_metric": "LT",
                    "relationship": "exact-equivalent",
                    "status": "compared",
                    "sample_count": 1,
                    "mae": 0.0,
                    "bias": 0.0,
                    "rmse": 0.0,
                    "notes": "",
                },
                {
                    "platform": "AURORA",
                    "internal_metric": "projection_pitch_mean",
                    "comparator": "AuroraPaper",
                    "comparator_metric": "projection_pitch_mean",
                    "relationship": "not-comparable",
                    "status": "skipped",
                    "sample_count": 0,
                    "mae": None,
                    "bias": None,
                    "rmse": None,
                    "notes": "Relationship is not-comparable.",
                },
            ],
        }

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            with (
                patch("tools.build_validation_report.run_reference_suite", return_value=fake_reference_report),
                patch("tools.build_validation_report.run_tool_comparison", return_value=fake_comparison_report),
            ):
                artifact_paths = build_validation_report(profile="research", output_dir=output_dir)

            expected_keys = {
                "summary_markdown",
                "reference_json",
                "reference_csv",
                "comparison_json",
                "comparison_csv",
                "supplement_comparison_csv",
                "validation_report_json",
                "manifest_lock",
            }
            self.assertTrue(expected_keys.issubset(artifact_paths))
            for artifact_path in artifact_paths.values():
                self.assertTrue(Path(artifact_path).exists(), artifact_path)

            summary_markdown = Path(artifact_paths["summary_markdown"]).read_text(encoding="utf-8")
            self.assertIn("Research validation profile: research", summary_markdown)
            self.assertIn("not clinical deployment ready", summary_markdown.lower())
            self.assertIn("AURORA", summary_markdown)

            with Path(artifact_paths["supplement_comparison_csv"]).open(encoding="utf-8", newline="") as handle:
                comparison_rows = list(csv.DictReader(handle))
            self.assertEqual("lt", comparison_rows[0]["internal_metric"])

            validation_report = json.loads(Path(artifact_paths["validation_report_json"]).read_text(encoding="utf-8"))
            self.assertEqual(2, validation_report["summary"]["total_metrics"])
            self.assertEqual(1, validation_report["summary"]["exact_passes"])
            self.assertEqual(0, validation_report["summary"]["exact_failures"])
            self.assertTrue(validation_report["summary"]["reference_exact_green"])
            self.assertEqual(0, validation_report["summary"]["analysis_failures"])
            self.assertEqual(0, validation_report["summary"]["provenance_failures"])
            self.assertEqual("legacy-unversioned", validation_report["cases"][0]["formula_version_status"])
            self.assertEqual("vmat_truebeam_canonical", validation_report["results"][0]["case_id"])

            manifest_lock = json.loads(Path(artifact_paths["manifest_lock"]).read_text(encoding="utf-8"))
            self.assertEqual("research", manifest_lock["profile_key"])
            locked_keys = {artifact["key"] for artifact in manifest_lock["artifacts"]}
            self.assertTrue((expected_keys - {"manifest_lock"}).issubset(locked_keys))
            for artifact in manifest_lock["artifacts"]:
                self.assertRegex(artifact["sha256"], r"^[0-9a-f]{64}$")

    def test_compact_report_preserves_failed_case_gates_with_no_metric_rows(self):
        from tools.build_validation_report import render_validation_artifacts

        reference = {
            "profile": "research",
            "summary": {
                "reference_exact_green": False, "analysis_failures": 1,
                "provenance_failures": 1,
            },
            "cases": [{
                "case_id": "synthetic", "domain": "VMAT_IMRT",
                "supported": False, "expected_supported": True,
                "analysis_status": "fail", "analysis_note": "Unexpected unsupported analysis.",
                "required_formula_version": "geometry-v3",
                "expected_formula_version": "geometry-v3",
                "observed_formula_version": "geometry-v2",
                "formula_version_status": "fail", "formula_version_note": "Formula version mismatch.",
                "reference_exact_green": False,
            }],
            "metrics": [],
        }
        with TemporaryDirectory() as temp_dir:
            paths = render_validation_artifacts(reference, {"comparisons": []}, temp_dir)
            report = json.loads(Path(paths["validation_report_json"]).read_text())
            self.assertIs(False, report["summary"]["reference_exact_green"])
            self.assertEqual(1, report["summary"]["analysis_failures"])
            self.assertEqual(1, report["summary"]["provenance_failures"])
            self.assertEqual(0, report["summary"]["exact_failures"])
            self.assertEqual(reference["cases"], report["cases"])
            markdown = Path(paths["summary_markdown"]).read_text()
            self.assertIn("Analysis failures: 1", markdown)
            self.assertIn("Formula provenance failures: 1", markdown)
            self.assertIn("geometry-v3", markdown)
            self.assertIn("geometry-v2", markdown)
            self.assertIn("Reference exact green: False", markdown)

    def test_missing_summary_gate_is_derived_from_case_failures(self):
        from tools.build_validation_report import _build_validation_report_json

        report = _build_validation_report_json(
            {"cases": [{"analysis_status": "fail", "formula_version_status": "fail"}], "metrics": []},
            profile_key="research", generated_at="2026-09-19T10:00:00Z", report_id="synthetic",
        )
        self.assertIs(False, report["summary"]["reference_exact_green"])
        self.assertEqual(1, report["summary"]["analysis_failures"])
        self.assertEqual(1, report["summary"]["provenance_failures"])

    def test_compact_report_preserves_unrequired_gate_as_null(self):
        from tools.build_validation_report import _build_validation_report_json

        report = _build_validation_report_json(
            {"summary": {"reference_exact_green": None}, "metrics": []},
            profile_key="relaxed", generated_at="2026-09-19T10:00:00Z", report_id="synthetic",
        )
        self.assertIsNone(report["summary"]["reference_exact_green"])

    def test_render_overwrites_existing_json_csv_and_locks_fresh_content(self):
        from tools.build_validation_report import render_validation_artifacts

        for explicit_paths in (False, True):
            with self.subTest(explicit_paths=explicit_paths), TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                reference = {
                    "profile": "research", "summary": {"reference_exact_green": False},
                    "cases": [], "metrics": [{
                        "case_id": "synthetic", "domain": "TOMO", "metric_key": "ttdf_s_cgy",
                        "status": "fail", "comparison_class": "exact-equivalent",
                    }],
                }
                comparison = {"comparisons": [{
                    "platform": "TOMO", "internal_metric": "mf", "comparator": "Synthetic",
                    "comparator_metric": "MF", "relationship": "derived-equivalent",
                    "status": "compared", "sample_count": 2, "mae": 0.2, "bias": 0.1,
                    "rmse": 0.3, "notes": "Fresh synthetic comparison.",
                }]}
                names = {
                    "reference_json": "reference_case_results.json",
                    "reference_csv": "reference_case_results.csv",
                    "comparison_json": "comparator_statistics.json",
                    "comparison_csv": "comparator_statistics.csv",
                }
                for name in names.values():
                    (root / name).write_text('{"stale": true}' if name.endswith("json") else "stale\nold\n")
                if explicit_paths:
                    reference["artifacts"] = {suffix: str(root / names[f"reference_{suffix}"]) for suffix in ("json", "csv")}
                    comparison["artifacts"] = {suffix: str(root / names[f"comparison_{suffix}"]) for suffix in ("json", "csv")}

                paths = render_validation_artifacts(reference, comparison, root)
                for key, expected in (("reference_json", reference), ("comparison_json", comparison)):
                    with self.subTest(artifact=key):
                        self.assertEqual(expected, json.loads(Path(paths[key]).read_text()))
                with self.subTest(artifact="reference_csv"):
                    with Path(paths["reference_csv"]).open(newline="") as handle:
                        row = next(csv.DictReader(handle))
                    self.assertIn("metric_key", row)
                    self.assertEqual("ttdf_s_cgy", row["metric_key"])
                    self.assertEqual("fail", row["status"])
                with self.subTest(artifact="comparison_csv"):
                    with Path(paths["comparison_csv"]).open(newline="") as handle:
                        row = next(csv.DictReader(handle))
                    self.assertIn("internal_metric", row)
                    self.assertEqual("mf", row["internal_metric"])
                    self.assertEqual("0.2", row["mae"])
                lock = json.loads(Path(paths["manifest_lock"]).read_text())
                for artifact in lock["artifacts"]:
                    content = Path(paths[artifact["key"]]).read_bytes()
                    self.assertEqual(hashlib.sha256(content).hexdigest(), artifact["sha256"])


class ReadmeValidationDocsTests(unittest.TestCase):
    def test_readme_mentions_validation_commands(self):
        readme = Path("README.md").read_text(encoding="utf-8")
        self.assertIn("run_reference_suite.py", readme)
        self.assertIn("run_formula_oracles.py", readme)
        self.assertIn("build_paper_reproduction_table.py", readme)
        self.assertIn("run_tool_comparison.py", readme)
        self.assertIn("build_comparator_matrix.py", readme)
        self.assertIn("build_validation_report.py", readme)
        self.assertIn("run_psqa_spc_analysis.py", readme)
        self.assertIn("run_clinical_endpoint_association.py", readme)
        self.assertIn("run_clinical_readiness_gate.py", readme)
        self.assertIn("test_freeze_reference_outputs", readme)


if __name__ == "__main__":
    unittest.main()
