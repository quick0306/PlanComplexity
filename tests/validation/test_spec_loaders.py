import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory


class ValidationLoaderTests(unittest.TestCase):
    def test_metric_specs_load_as_validation_model_records(self):
        from validation.utils import loaders
        from validation_models import ExpectedRangeRecord, MetricSpecRecord

        specs = loaders.load_metric_specs()
        self.assertGreater(len(specs), 20)
        self.assertTrue(all(isinstance(spec, MetricSpecRecord) for spec in specs))
        self.assertTrue(all(isinstance(spec.expected_range, ExpectedRangeRecord) for spec in specs))

    def test_metric_specs_schema_validation_runs_before_definition_logic(self):
        from validation.utils import loaders

        with TemporaryDirectory() as temp_dir:
            specs_dir = Path(temp_dir)
            (specs_dir / "metric_specs.yaml").write_text(
                """
                metric_specs:
                  - platform: VMAT_IMRT
                    key: alpha
                    mode: VMAT_IMRT
                    group_key: vmat_imrt_aperture_geometry
                    metric_key: alpha
                    unit: dimensionless
                    aggregation_scope: plan
                    normalization_basis: beam_weighted_mean
                    validation_level: Reference-case exact
                    comparison_class: exact-equivalent
                    default_tolerance_abs: 1.0e-6
                    default_tolerance_rel: 1.0e-4
                    expected_range:
                      kind: unit_interval
                      minimum: 0.0
                      maximum: 1.0
                    clinical_readiness: research
                    known_noncomparability: []
                    comparable_to: []
                    assumptions: []
                    exclusions: []
                """.strip(),
                encoding="utf-8",
            )
            (specs_dir / "metric_groups.yaml").write_text(
                """
                metric_groups:
                  - group_key: vmat_imrt_aperture_geometry
                    platform: VMAT_IMRT
                    label: Aperture geometry
                    description: Example VMAT family.
                """.strip(),
                encoding="utf-8",
            )

            original_specs_dir = loaders._SPECS_DIR
            loaders._SPECS_DIR = specs_dir
            try:
                with self.assertRaisesRegex(
                    ValueError,
                    "Schema validation failed for metric_spec.schema.json",
                ):
                    loaders.load_metric_specs()
            finally:
                loaders._SPECS_DIR = original_specs_dir

    def test_future_schema_artifacts_align_with_planned_top_level_keys(self):
        schemas_dir = Path(__file__).resolve().parents[2] / "validation" / "schemas"

        reference_schema = json.loads((schemas_dir / "reference_case.schema.json").read_text(encoding="utf-8"))
        self.assertIn("cases", reference_schema["required"])
        self.assertIn("cases", reference_schema["properties"])

        comparator_schema = json.loads((schemas_dir / "comparator_mapping.schema.json").read_text(encoding="utf-8"))
        self.assertIn("mappings", comparator_schema["required"])
        self.assertIn("mappings", comparator_schema["properties"])
        mapping_properties = comparator_schema["properties"]["mappings"]["items"]["properties"]
        self.assertTrue(
            {"internal_metric", "comparator", "comparator_metric", "relationship"}.issubset(mapping_properties)
        )

        reference_case_item = reference_schema["properties"]["cases"]["items"]["properties"]
        tolerance_override = reference_case_item["tolerance_overrides"]["additionalProperties"]["properties"]
        self.assertTrue({"abs", "rel", "skip", "reason"}.issubset(tolerance_override))
        self.assertIn("source_kind", reference_case_item["provenance"]["required"])

        validation_report_schema = json.loads((schemas_dir / "validation_report.schema.json").read_text(encoding="utf-8"))
        self.assertEqual("date-time", validation_report_schema["properties"]["generated_at"]["format"])
        result_properties = validation_report_schema["properties"]["results"]["items"]["properties"]
        self.assertIn("enum", result_properties["comparison_class"])
        self.assertIn("enum", result_properties["status"])

    def test_schema_loading_failures_are_wrapped_as_value_errors(self):
        from validation.utils import loaders

        with TemporaryDirectory() as temp_dir:
            schemas_dir = Path(temp_dir)
            (schemas_dir / "metric_spec.schema.json").write_text("{not-json", encoding="utf-8")

            original_schemas_dir = loaders._SCHEMAS_DIR
            loaders._SCHEMAS_DIR = schemas_dir
            loaders._load_schema.cache_clear()
            try:
                with self.assertRaisesRegex(ValueError, "Failed to load schema metric_spec.schema.json"):
                    loaders._validate_schema({"metric_specs": []}, "metric_spec.schema.json")
            finally:
                loaders._SCHEMAS_DIR = original_schemas_dir
                loaders._load_schema.cache_clear()

    def test_validation_report_schema_enforces_datetime_format(self):
        from validation.utils import loaders

        invalid_values = (
            "not-a-datetime",
            "2024-01-01",
            "2024-01-01T12:00:00",
            "2024-01-01 12:00:00+00:00",
        )
        for value in invalid_values:
            with self.subTest(generated_at=value):
                bad_payload = {
                    "report_id": "demo",
                    "generated_at": value,
                    "profile_key": "research",
                    "summary": {
                        "total_metrics": 1,
                        "exact_passes": 1,
                        "exact_failures": 0,
                    },
                    "results": [
                        {
                            "platform": "AURORA",
                            "metric_key": "projection_pitch_mean",
                            "comparison_class": "exact-equivalent",
                            "status": "pass",
                        }
                    ],
                }

                with self.assertRaisesRegex(ValueError, "generated_at"):
                    loaders._validate_schema(bad_payload, "validation_report.schema.json")


if __name__ == "__main__":
    unittest.main()
