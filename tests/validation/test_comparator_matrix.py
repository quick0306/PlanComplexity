import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class ComparatorMatrixTests(unittest.TestCase):
    def test_comparator_matrix_summarizes_mapping_coverage(self):
        from validation.comparator_matrix import build_comparator_matrix

        report = build_comparator_matrix()

        self.assertGreater(report["summary"]["metrics_total"], 0)
        self.assertGreaterEqual(report["summary"]["mapped_metrics"], 3)
        platforms = {row["platform"] for row in report["platforms"]}
        self.assertTrue({"VMAT_IMRT", "AURORA"}.issubset(platforms))

    def test_comparator_matrix_tool_writes_platform_and_metric_artifacts(self):
        from tools.build_comparator_matrix import build_comparator_matrix_report

        with TemporaryDirectory() as temp_dir:
            report = build_comparator_matrix_report(output_dir=temp_dir)

            self.assertTrue(Path(report["artifacts"]["json"]).exists())
            self.assertTrue(Path(report["artifacts"]["platform_csv"]).exists())
            self.assertTrue(Path(report["artifacts"]["metric_csv"]).exists())


if __name__ == "__main__":
    unittest.main()
