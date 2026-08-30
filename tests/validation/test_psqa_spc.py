import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class PsqaSpcTests(unittest.TestCase):
    def test_harmonization_and_spc_classification(self):
        from validation.psqa_spc import calculate_spc_limits, classify_spc_points, harmonize_metric_values

        records = [
            {"plan_id": "p1", "platform": "VMAT_IMRT", "metric_key": "mcs", "metric_value": "1.0"},
            {"plan_id": "p2", "platform": "VMAT_IMRT", "metric_key": "mcs", "metric_value": "2.0"},
            {"plan_id": "p3", "platform": "VMAT_IMRT", "metric_key": "mcs", "metric_value": "3.0"},
        ]

        harmonized = harmonize_metric_values(records, metric_key="mcs")
        limits = calculate_spc_limits([row["z_score"] for row in harmonized])
        points = classify_spc_points([row["z_score"] for row in harmonized], limits)

        self.assertEqual(3, len(harmonized))
        self.assertAlmostEqual(2.0, harmonized[0]["baseline_center"])
        self.assertEqual({"in_control"}, {row["status"] for row in points})

    def test_psqa_spc_tool_writes_artifacts(self):
        from tools.run_psqa_spc_analysis import run_psqa_spc_analysis

        with TemporaryDirectory() as temp_dir:
            input_csv = Path(temp_dir) / "psqa.csv"
            with input_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["plan_id", "platform", "site_id", "machine_id", "metric_key", "metric_value", "gamma_3_3"],
                )
                writer.writeheader()
                writer.writerow({"plan_id": "p1", "platform": "VMAT_IMRT", "site_id": "site_a", "machine_id": "TB1", "metric_key": "mcs", "metric_value": "1.0", "gamma_3_3": "98"})
                writer.writerow({"plan_id": "p2", "platform": "VMAT_IMRT", "site_id": "site_a", "machine_id": "TB1", "metric_key": "mcs", "metric_value": "2.0", "gamma_3_3": "94"})

            report = run_psqa_spc_analysis(input_csv, metric_key="mcs", output_dir=temp_dir)

            self.assertEqual(2, report["summary"]["records_total"])
            self.assertTrue(Path(report["artifacts"]["json"]).exists())
            self.assertTrue(Path(report["artifacts"]["harmonized_csv"]).exists())

    def test_psqa_loader_rejects_records_without_required_columns(self):
        from validation.psqa_spc import validate_psqa_records

        with self.assertRaisesRegex(ValueError, "metric_key"):
            validate_psqa_records([{"plan_id": "p1", "platform": "VMAT_IMRT", "machine_id": "TB1", "metric_value": "1.0"}])


if __name__ == "__main__":
    unittest.main()
