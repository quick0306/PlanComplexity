import json
import argparse
import unittest
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from validation_models import (
    ExpectedRangeRecord,
    MetricSpecRecord,
    ReferenceCaseProvenanceRecord,
    ReferenceCaseRecord,
    ValidationCaseResult,
    ValidationProfileRecord,
)


class ReferenceSuiteTests(unittest.TestCase):
    def test_cli_exits_nonzero_when_strict_reference_gate_fails(self):
        from tools.run_reference_suite import main

        args = argparse.Namespace(profile="research", output_dir="unused", source_root=None)
        with (
            patch("tools.run_reference_suite._parse_args", return_value=args),
            patch("tools.run_reference_suite.run_reference_suite", return_value={
                "summary": {"reference_exact_green": False},
            }),
        ):
            self.assertEqual(1, main())

    def test_cli_succeeds_when_strict_gate_passes_or_is_not_required(self):
        from tools.run_reference_suite import main

        args = argparse.Namespace(profile="research", output_dir="unused", source_root=None)
        for green in (True, None):
            with (
                self.subTest(green=green),
                patch("tools.run_reference_suite._parse_args", return_value=args),
                patch("tools.run_reference_suite.run_reference_suite", return_value={
                    "summary": {"reference_exact_green": green},
                }),
            ):
                self.assertEqual(0, main())

    def test_reference_suite_reports_case_and_metric_level_results(self):
        from tools.run_reference_suite import run_reference_suite

        fake_profile = ValidationProfileRecord(
            profile_key="research",
            description="",
            exact_abs_default=1.0e-6,
            exact_rel_default=1.0e-4,
            require_reference_exact_green=True,
            include_association_only_in_core_gate=False,
            group_keys=("aurora_v2_paper_style_physics",),
        )
        fake_spec = MetricSpecRecord(
            platform="AURORA",
            mode="AURORA",
            group_key="aurora_v2_paper_style_physics",
            metric_key="projection_pitch_mean",
            label="projection_pitch_mean",
            unit="mm/deg",
            aggregation_scope="plan",
            normalization_basis="beam_weighted_mean",
            validation_level="Reference-case exact",
            comparison_class="exact-equivalent",
            default_tolerance_abs=1.0e-4,
            default_tolerance_rel=1.0e-4,
            expected_range=ExpectedRangeRecord(
                kind="nonnegative",
                minimum=0.0,
                maximum=None,
            ),
            clinical_readiness="research",
            known_noncomparability=(),
            comparable_to=(),
            assumptions=(),
            exclusions=(),
        )
        fake_result = ValidationCaseResult(
            source_path="demo.dcm",
            domain="AURORA",
            mode="AURORA",
            supported=True,
            reason="",
            metadata={"plan_name": "Aurora Demo"},
            metrics={
                "projection_pitch_mean": 1.25001,
                "projection_pitch_cv": 0.5,
            },
            warnings=(),
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            source_path = output_dir / "data" / "Aurora" / "demo.dcm"
            source_path.parent.mkdir(parents=True)
            source_path.write_bytes(b"aurora-demo")
            fake_case = ReferenceCaseRecord(
                case_id="aurora_demo",
                source_path="data/Aurora/demo.dcm",
                domain="AURORA",
                device_or_tps="Aurora",
                expected_mode="AURORA",
                case_class="canonical",
                expected_metrics_source="checked_in_json",
                expected_metrics_path=Path("validation/reference_cases/cases/aurora_demo/expected_metrics.json"),
                expected_metrics={
                    "projection_pitch_mean": 1.25,
                    "projection_pitch_cv": 0.5,
                },
                tolerance_overrides={},
                checksum=hashlib.sha256(source_path.read_bytes()).hexdigest(),
                provenance=ReferenceCaseProvenanceRecord(
                    source_kind="synthetic",
                    version="test",
                    notes="",
                ),
                notes="",
            )
            with (
                patch("tools.run_reference_suite.load_reference_manifest", return_value=[fake_case]),
                patch("tools.run_reference_suite.load_validation_profiles", return_value=[fake_profile]),
                patch(
                    "tools.run_reference_suite.load_metric_specs",
                    return_value=[
                        fake_spec,
                        MetricSpecRecord(
                            platform="AURORA",
                            mode="AURORA",
                            group_key="aurora_v2_paper_style_physics",
                            metric_key="projection_pitch_cv",
                            label="projection_pitch_cv",
                            unit="dimensionless",
                            aggregation_scope="plan",
                            normalization_basis="beam_weighted_mean",
                            validation_level="Derived-equivalent",
                            comparison_class="derived-equivalent",
                            default_tolerance_abs=1.0e-4,
                            default_tolerance_rel=1.0e-4,
                            expected_range=ExpectedRangeRecord(
                                kind="nonnegative",
                                minimum=0.0,
                                maximum=None,
                            ),
                            clinical_readiness="research",
                            known_noncomparability=(),
                            comparable_to=(),
                            assumptions=(),
                            exclusions=(),
                        ),
                    ],
                ),
                patch("tools.run_reference_suite.analyze_validation_case", return_value=fake_result),
            ):
                report = run_reference_suite(profile="research", output_dir=output_dir, source_root=output_dir)

            self.assertIn("cases", report)
            self.assertIn("metrics", report)
            self.assertEqual(1, len(report["cases"]))
            self.assertEqual(2, len(report["metrics"]))
            metric_statuses = {row["metric_key"]: row["status"] for row in report["metrics"]}
            self.assertEqual("pass", metric_statuses["projection_pitch_mean"])
            self.assertEqual("skipped", metric_statuses["projection_pitch_cv"])
            self.assertTrue(report["summary"]["reference_exact_green"])
            self.assertTrue((output_dir / "reference_case_results.json").exists())
            self.assertTrue((output_dir / "reference_case_results.csv").exists())

            json_payload = json.loads((output_dir / "reference_case_results.json").read_text(encoding="utf-8"))
            self.assertEqual("research", json_payload["profile"])
            self.assertEqual("aurora_demo", json_payload["cases"][0]["case_id"])

    def test_reference_suite_respects_profile_exact_green_gating_at_case_level(self):
        from tools.run_reference_suite import run_reference_suite

        fake_profile = ValidationProfileRecord(
            profile_key="relaxed",
            description="",
            exact_abs_default=1.0e-6,
            exact_rel_default=1.0e-4,
            require_reference_exact_green=False,
            include_association_only_in_core_gate=False,
            group_keys=("aurora_v2_paper_style_physics",),
        )
        fake_spec = MetricSpecRecord(
            platform="AURORA",
            mode="AURORA",
            group_key="aurora_v2_paper_style_physics",
            metric_key="projection_pitch_mean",
            label="projection_pitch_mean",
            unit="mm/deg",
            aggregation_scope="plan",
            normalization_basis="beam_weighted_mean",
            validation_level="Reference-case exact",
            comparison_class="exact-equivalent",
            default_tolerance_abs=1.0e-4,
            default_tolerance_rel=1.0e-4,
            expected_range=ExpectedRangeRecord(
                kind="nonnegative",
                minimum=0.0,
                maximum=None,
            ),
            clinical_readiness="research",
            known_noncomparability=(),
            comparable_to=(),
            assumptions=(),
            exclusions=(),
        )
        fake_result = ValidationCaseResult(
            source_path="demo.dcm",
            domain="AURORA",
            mode="AURORA",
            supported=True,
            reason="",
            metadata={"plan_name": "Aurora Demo"},
            metrics={"projection_pitch_mean": 1.25},
            warnings=(),
        )

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            source_path = output_dir / "data" / "Aurora" / "demo.dcm"
            source_path.parent.mkdir(parents=True)
            source_path.write_bytes(b"aurora-demo")
            fake_case = ReferenceCaseRecord(
                case_id="aurora_demo",
                source_path="data/Aurora/demo.dcm",
                domain="AURORA",
                device_or_tps="Aurora",
                expected_mode="AURORA",
                case_class="canonical",
                expected_metrics_source="checked_in_json",
                expected_metrics_path=Path("validation/reference_cases/cases/aurora_demo/expected_metrics.json"),
                expected_metrics={"projection_pitch_mean": 1.25},
                tolerance_overrides={},
                checksum=hashlib.sha256(source_path.read_bytes()).hexdigest(),
                provenance=ReferenceCaseProvenanceRecord(
                    source_kind="synthetic",
                    version="test",
                    notes="",
                ),
                notes="",
            )
            with (
                patch("tools.run_reference_suite.load_reference_manifest", return_value=[fake_case]),
                patch("tools.run_reference_suite.load_validation_profiles", return_value=[fake_profile]),
                patch("tools.run_reference_suite.load_metric_specs", return_value=[fake_spec]),
                patch("tools.run_reference_suite.analyze_validation_case", return_value=fake_result),
            ):
                report = run_reference_suite(profile="relaxed", output_dir=output_dir, source_root=output_dir)

            self.assertIsNone(report["summary"]["reference_exact_green"])
            self.assertIsNone(report["cases"][0]["reference_exact_green"])


if __name__ == "__main__":
    unittest.main()
