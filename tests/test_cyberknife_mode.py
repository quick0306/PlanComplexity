import unittest
from pathlib import Path

from ucomx_models import AnalysisMode
from ucomx_service import analyze_plan_file, detect_mode_from_file


class CyberKnifeModeTests(unittest.TestCase):
    def test_detect_mode_from_real_cyberknife_samples(self):
        sample_dir = Path("data/CyberKnife")
        for path in sorted(sample_dir.glob("*.dcm")):
            with self.subTest(path=path.name):
                self.assertEqual(detect_mode_from_file(str(path)), AnalysisMode.CYBERKNIFE_MLC)

    def test_analyze_real_cyberknife_samples_with_six_metric_subset(self):
        sample_dir = Path("data/CyberKnife")
        for path in sorted(sample_dir.glob("*.dcm")):
            with self.subTest(path=path.name):
                report = analyze_plan_file(str(path), requested_mode=AnalysisMode.AUTO)
                self.assertEqual(report.mode, AnalysisMode.CYBERKNIFE_MLC)
                self.assertTrue(report.supported)
                self.assertEqual(set(report.metrics.keys()), {"mcs", "em", "pi", "pm", "lg", "sas10"})
                self.assertEqual(set(report.flattened_metrics.keys()), {"mcs", "em", "pi", "pm", "lg", "sas10"})
                self.assertGreater(report.metrics["mcs"], 0.0)
                self.assertGreater(report.metrics["em"], 0.0)
                self.assertGreater(report.metrics["pi"], 0.0)
                self.assertGreaterEqual(report.metrics["pm"], 0.0)
                self.assertGreater(report.metrics["lg"], 0.0)
                self.assertGreaterEqual(report.metrics["sas10"], 0.0)


if __name__ == "__main__":
    unittest.main()
