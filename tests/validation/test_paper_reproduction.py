import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class PaperReproductionTests(unittest.TestCase):
    def test_paper_reproduction_table_tracks_literature_metric_families(self):
        from validation.paper_reproduction import build_paper_reproduction_table

        report = build_paper_reproduction_table()

        papers = {row["paper"] for row in report["rows"]}
        self.assertIn("Tamura/Park 2020", papers)
        self.assertIn("Quintero/Esposito 2021", papers)
        self.assertGreater(report["summary"]["reference_exact_rows"], 0)

    def test_paper_reproduction_tool_writes_artifacts(self):
        from tools.build_paper_reproduction_table import build_paper_reproduction_report

        with TemporaryDirectory() as temp_dir:
            report = build_paper_reproduction_report(output_dir=temp_dir)

            self.assertTrue(Path(report["artifacts"]["json"]).exists())
            self.assertTrue(Path(report["artifacts"]["csv"]).exists())


if __name__ == "__main__":
    unittest.main()
