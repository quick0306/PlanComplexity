import csv
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

            manifest_lock = json.loads(Path(artifact_paths["manifest_lock"]).read_text(encoding="utf-8"))
            self.assertEqual("research", manifest_lock["profile_key"])
            locked_keys = {artifact["key"] for artifact in manifest_lock["artifacts"]}
            self.assertTrue((expected_keys - {"manifest_lock"}).issubset(locked_keys))
            for artifact in manifest_lock["artifacts"]:
                self.assertRegex(artifact["sha256"], r"^[0-9a-f]{64}$")


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
