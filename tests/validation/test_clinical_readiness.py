import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


class ClinicalReadinessTests(unittest.TestCase):
    def test_readiness_gate_flags_csv_history_as_open_source_blocker(self):
        from validation.clinical_readiness import run_clinical_readiness_gate

        def fake_git(_root, args):
            stdout = ""
            if args[:2] == ["ls-files", "*.csv"]:
                stdout = ""
            if args[:3] == ["log", "--oneline", "--all"]:
                stdout = "abc123 historical csv\n"
            return subprocess.CompletedProcess(["git", *args], 0, stdout=stdout, stderr="")

        with patch("validation.clinical_readiness._git", side_effect=fake_git):
            report = run_clinical_readiness_gate(Path("."))

        checks = {row["check_id"]: row for row in report["checks"]}
        self.assertEqual("pass", checks["no_tracked_csv_reports"]["status"])
        self.assertEqual("fail", checks["csv_history_phi_review"]["status"])
        self.assertFalse(report["summary"]["open_source_ready"])
        self.assertFalse(report["summary"]["clinical_ready"])

    def test_clinical_readiness_tool_writes_artifacts(self):
        from tools.run_clinical_readiness_gate import run_clinical_readiness_report

        with TemporaryDirectory() as temp_dir:
            report = run_clinical_readiness_report(output_dir=temp_dir)

            self.assertIn("checks", report)
            self.assertTrue(Path(report["artifacts"]["json"]).exists())
            self.assertTrue(Path(report["artifacts"]["csv"]).exists())


if __name__ == "__main__":
    unittest.main()
