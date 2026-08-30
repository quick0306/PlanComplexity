import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class ClinicalEndpointTests(unittest.TestCase):
    def test_binary_endpoint_association_reports_directional_effect(self):
        from validation.clinical_endpoints import associate_binary_endpoint

        rows = [
            {"case_id": "c1", "complexity": "1.0", "qa_fail": "0"},
            {"case_id": "c2", "complexity": "2.0", "qa_fail": "0"},
            {"case_id": "c3", "complexity": "4.0", "qa_fail": "1"},
            {"case_id": "c4", "complexity": "5.0", "qa_fail": "1"},
        ]

        result = associate_binary_endpoint(rows, metric_key="complexity", endpoint_key="qa_fail")

        self.assertEqual(4, result["sample_count"])
        self.assertEqual(2, result["event_count"])
        self.assertGreater(result["mean_difference"], 0.0)
        self.assertGreater(result["point_biserial_r"], 0.0)

    def test_clinical_endpoint_tool_writes_artifact(self):
        from tools.run_clinical_endpoint_association import run_clinical_endpoint_association

        with TemporaryDirectory() as temp_dir:
            input_csv = Path(temp_dir) / "endpoints.csv"
            with input_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["case_id", "complexity", "qa_fail"])
                writer.writeheader()
                writer.writerow({"case_id": "c1", "complexity": "1.0", "qa_fail": "0"})
                writer.writerow({"case_id": "c2", "complexity": "4.0", "qa_fail": "1"})

            report = run_clinical_endpoint_association(
                input_csv,
                metric_key="complexity",
                endpoint_key="qa_fail",
                output_dir=temp_dir,
            )

            self.assertIn("association", report)
            self.assertTrue(Path(report["artifacts"]["json"]).exists())

    def test_endpoint_loader_rejects_records_without_case_id(self):
        from validation.clinical_endpoints import validate_endpoint_records

        with self.assertRaisesRegex(ValueError, "case_id"):
            validate_endpoint_records([{"complexity": "1.0", "qa_fail": "0"}])


if __name__ == "__main__":
    unittest.main()
