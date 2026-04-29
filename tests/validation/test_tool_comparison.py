import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch


class ToolComparisonTests(unittest.TestCase):
    def test_tool_comparison_emits_agreement_statistics(self):
        from tools.run_tool_comparison import run_tool_comparison

        fake_reference_report = {
            "metrics": [
                {
                    "case_id": "vmat_truebeam_canonical",
                    "metric_key": "lt",
                    "observed": 117.3,
                    "status": "pass",
                },
                {
                    "case_id": "vmat_halcyon_edge",
                    "metric_key": "lt_mlcx1",
                    "observed": 107.09,
                    "status": "skipped",
                },
                {
                    "case_id": "aurora_canonical",
                    "metric_key": "projection_pitch_mean",
                    "observed": 0.09259232915432099,
                    "status": "skipped",
                },
            ]
        }
        fake_mappings = [
            SimpleNamespace(
                platform="VMAT_IMRT",
                internal_metric="lt",
                comparator="UCoMX",
                comparator_metric="LT",
                relationship="exact-equivalent",
                samples=(SimpleNamespace(case_id="vmat_truebeam_canonical", comparator_value=117.3, notes=""),),
                notes="",
            ),
            SimpleNamespace(
                platform="VMAT_IMRT",
                internal_metric="lt_mlcx1",
                comparator="UCoMX",
                comparator_metric="LT_MLCX1",
                relationship="derived-equivalent",
                samples=(SimpleNamespace(case_id="vmat_halcyon_edge", comparator_value=107.15, notes=""),),
                notes="",
            ),
            SimpleNamespace(
                platform="AURORA",
                internal_metric="projection_pitch_mean",
                comparator="AuroraPaper",
                comparator_metric="projection_pitch_mean",
                relationship="not-comparable",
                samples=(SimpleNamespace(case_id="aurora_canonical", comparator_value=0.09259232915432099, notes=""),),
                notes="",
            ),
        ]

        with TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            with (
                patch("tools.run_tool_comparison.run_reference_suite", return_value=fake_reference_report),
                patch("tools.run_tool_comparison.load_comparator_mappings", return_value=fake_mappings),
            ):
                report = run_tool_comparison(profile="research", output_dir=output_dir)

            self.assertIn("comparisons", report)
            self.assertTrue(any(comparison.get("mae") is not None for comparison in report["comparisons"]))
            statuses = {row["internal_metric"]: row["status"] for row in report["comparisons"]}
            self.assertEqual("skipped", statuses["projection_pitch_mean"])
            self.assertTrue((output_dir / "comparator_statistics.csv").exists())

    def test_comparator_mapping_loader_rejects_unknown_metric_and_case_references(self):
        from validation.utils import loaders

        with TemporaryDirectory() as temp_dir:
            specs_dir = Path(temp_dir)
            self._write_minimal_metric_inventory(specs_dir)
            (specs_dir / "comparator_mapping.yaml").write_text(
                """
                mappings:
                  - platform: AURORA
                    internal_metric: typo_metric
                    comparator: Demo
                    comparator_metric: typo_metric
                    relationship: exact-equivalent
                    samples:
                      - case_id: typo_case
                        comparator_value: 1.0
                """.strip(),
                encoding="utf-8",
            )

            original_specs_dir = loaders._SPECS_DIR
            loaders._SPECS_DIR = specs_dir
            try:
                with self.assertRaisesRegex(ValueError, "unknown metric"):
                    loaders.load_comparator_mappings()
            finally:
                loaders._SPECS_DIR = original_specs_dir

        with TemporaryDirectory() as temp_dir:
            specs_dir = Path(temp_dir)
            self._write_minimal_metric_inventory(specs_dir)
            (specs_dir / "comparator_mapping.yaml").write_text(
                """
                mappings:
                  - platform: AURORA
                    internal_metric: projection_pitch_mean
                    comparator: Demo
                    comparator_metric: projection_pitch_mean
                    relationship: exact-equivalent
                    samples:
                      - case_id: typo_case
                        comparator_value: 1.0
                """.strip(),
                encoding="utf-8",
            )

            original_specs_dir = loaders._SPECS_DIR
            loaders._SPECS_DIR = specs_dir
            try:
                with self.assertRaisesRegex(ValueError, "unknown reference case"):
                    loaders.load_comparator_mappings()
            finally:
                loaders._SPECS_DIR = original_specs_dir

    def test_comparator_mapping_loader_rejects_incompatible_case_references(self):
        from validation.utils import loaders

        with TemporaryDirectory() as temp_dir:
            specs_dir = Path(temp_dir)
            self._write_minimal_metric_inventory(specs_dir)
            (specs_dir / "comparator_mapping.yaml").write_text(
                """
                mappings:
                  - platform: AURORA
                    internal_metric: projection_pitch_mean
                    comparator: Demo
                    comparator_metric: projection_pitch_mean
                    relationship: exact-equivalent
                    samples:
                      - case_id: vmat_truebeam_canonical
                        comparator_value: 1.0
                """.strip(),
                encoding="utf-8",
            )

            original_specs_dir = loaders._SPECS_DIR
            loaders._SPECS_DIR = specs_dir
            try:
                with self.assertRaisesRegex(ValueError, "domain mismatch"):
                    loaders.load_comparator_mappings()
            finally:
                loaders._SPECS_DIR = original_specs_dir

        with TemporaryDirectory() as temp_dir:
            specs_dir = Path(temp_dir)
            self._write_minimal_metric_inventory(specs_dir)
            (specs_dir / "comparator_mapping.yaml").write_text(
                """
                mappings:
                  - platform: AURORA
                    internal_metric: projection_pitch_mean
                    comparator: Demo
                    comparator_metric: projection_pitch_mean
                    relationship: exact-equivalent
                    samples:
                      - case_id: aurora_research_edge
                        comparator_value: 1.0
                """.strip(),
                encoding="utf-8",
            )

            reference_cases = loaders.load_reference_manifest()
            edited_cases = []
            for case in reference_cases:
                if case.case_id == "aurora_research_edge":
                    edited_cases.append(
                        type(case)(
                            case_id=case.case_id,
                            source_path=case.source_path,
                            domain=case.domain,
                            device_or_tps=case.device_or_tps,
                            expected_mode=case.expected_mode,
                            case_class=case.case_class,
                            expected_metrics_source=case.expected_metrics_source,
                            expected_metrics_path=case.expected_metrics_path,
                            expected_metrics={},
                            tolerance_overrides=case.tolerance_overrides,
                            checksum=case.checksum,
                            provenance=case.provenance,
                            notes=case.notes,
                        )
                    )
                else:
                    edited_cases.append(case)

            with patch.object(loaders, "load_reference_manifest", return_value=edited_cases):
                original_specs_dir = loaders._SPECS_DIR
                loaders._SPECS_DIR = specs_dir
                try:
                    with self.assertRaisesRegex(ValueError, "does not include metric"):
                        loaders.load_comparator_mappings()
                finally:
                    loaders._SPECS_DIR = original_specs_dir

    def _write_minimal_metric_inventory(self, specs_dir):
        (specs_dir / "metric_groups.yaml").write_text(
            """
            metric_groups:
              - group_key: aurora_v2_paper_style_physics
                platform: AURORA
                label: Aurora V2 paper-style physics
                description: Minimal comparator mapping test group.
            """.strip(),
            encoding="utf-8",
        )
        (specs_dir / "metric_specs.yaml").write_text(
            """
            metric_specs:
              - platform: AURORA
                mode: AURORA
                group_key: aurora_v2_paper_style_physics
                metric_key: projection_pitch_mean
                label: projection_pitch_mean
                unit: mm/deg
                aggregation_scope: plan
                normalization_basis: beam_weighted_mean
                validation_level: Reference-case exact
                comparison_class: exact-equivalent
                default_tolerance_abs: 1.0e-6
                default_tolerance_rel: 1.0e-4
                expected_range:
                  kind: nonnegative
                  minimum: 0.0
                  maximum: null
                clinical_readiness: research
                known_noncomparability: []
                comparable_to: []
                assumptions: []
                exclusions: []
            """.strip(),
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
