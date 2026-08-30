import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


class FormulaOracleTests(unittest.TestCase):
    def test_built_in_formula_oracles_are_green(self):
        from validation.formula_oracles import run_formula_oracles

        report = run_formula_oracles()

        self.assertTrue(report["summary"]["formula_oracle_green"])
        self.assertGreaterEqual(report["summary"]["oracles_total"], 5)
        self.assertEqual(set(), {row["status"] for row in report["oracles"]} - {"pass"})

    def test_formula_oracle_tool_writes_artifacts(self):
        from tools.run_formula_oracles import run_formula_oracle_report

        with TemporaryDirectory() as temp_dir:
            report = run_formula_oracle_report(output_dir=temp_dir)

            self.assertTrue(report["summary"]["formula_oracle_green"])
            self.assertTrue(Path(report["artifacts"]["json"]).exists())
            self.assertTrue(Path(report["artifacts"]["csv"]).exists())
            payload = json.loads(Path(report["artifacts"]["json"]).read_text(encoding="utf-8"))
            self.assertIn("oracles", payload)


if __name__ == "__main__":
    unittest.main()
