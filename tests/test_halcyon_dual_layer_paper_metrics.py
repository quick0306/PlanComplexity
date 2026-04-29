import unittest
from pathlib import Path

import numpy as np

from ApertureMetric.aperture_geometry import PyAperture
from halcyon_dual_layer_metrics import _layer_contributions
from ucomx_models import AnalysisMode
from ucomx_service import analyze_plan_file, build_metric_reference_rows


class HalcyonDualLayerPaperMetricTests(unittest.TestCase):
    def test_halcyon_result_includes_tamura_and_quintero_metrics(self):
        samples = sorted(Path("data/Halcyon").glob("*.dcm"))
        if not samples:
            self.skipTest("No Halcyon RTPLAN samples are available")

        result = analyze_plan_file(str(samples[0]), requested_mode=AnalysisMode.VMAT_IMRT)
        metrics = result.flattened_metrics

        expected_keys = {
            "mcsv",
            "mcs5",
            "pa5",
            "pi5",
            "pm5",
            "eds",
            "mcsw",
            "paw",
            "piw",
            "pmw",
            "ul",
            "mcsul",
            "np",
            "mucp",
            "proximal_mcs",
            "distal_mcs",
            "proximal_weight_mean",
            "distal_weight_mean",
        }
        self.assertTrue(expected_keys.issubset(metrics), expected_keys - set(metrics))

        self.assertEqual(result.mode, AnalysisMode.VMAT_IMRT)
        self.assertTrue(result.supported)
        self.assertGreater(metrics["mcs5"], 0.0)
        self.assertGreater(metrics["pa5"], 0.0)
        self.assertGreater(metrics["pi5"], 0.0)
        self.assertGreaterEqual(metrics["pm5"], 0.0)
        self.assertLessEqual(metrics["pm5"], 1.0)
        self.assertGreaterEqual(metrics["eds"], 0.0)
        self.assertLessEqual(metrics["eds"], 1.0)
        self.assertGreaterEqual(metrics["ul"], 0.0)
        self.assertLessEqual(metrics["ul"], 1.0)
        self.assertGreaterEqual(metrics["mcsul"], 0.0)
        self.assertLessEqual(metrics["mcsul"], metrics["mcsw"])
        self.assertGreater(metrics["np"], 0.0)
        self.assertAlmostEqual(metrics["proximal_weight_mean"] + metrics["distal_weight_mean"], 1.0, places=6)

    def test_metric_reference_rows_describe_paper_specific_outputs(self):
        samples = sorted(Path("data/Halcyon").glob("*.dcm"))
        if not samples:
            self.skipTest("No Halcyon RTPLAN samples are available")

        result = analyze_plan_file(str(samples[0]), requested_mode=AnalysisMode.VMAT_IMRT)
        reference_text = "\n".join(" | ".join(row) for row in build_metric_reference_rows(result))

        self.assertIn("Tamura", reference_text)
        self.assertIn("effective distal MLC score", reference_text)
        self.assertIn("Quintero", reference_text)
        self.assertIn("uncovered-layer", reference_text)

    def test_uncovered_layer_is_zero_when_dual_layers_are_identical(self):
        # Identical dual layers should not inflate Quintero UL via open-height alone.
        positions = np.array([[-5.0, -4.0], [5.0, 6.0]])
        aperture = PyAperture(
            leaf_positions=positions,
            leaf_widths=np.array([5.0, 5.0]),
            jaw=[-10.0, 10.0, 10.0, -10.0],
            gantry_angle=0.0,
        )

        distal_weight, proximal_weight, distal_ul, proximal_ul = _layer_contributions(
            aperture,
            positions,
            positions,
        )

        self.assertAlmostEqual(0.5, distal_weight)
        self.assertAlmostEqual(0.5, proximal_weight)
        self.assertEqual(0.0, distal_ul)
        self.assertEqual(0.0, proximal_ul)


if __name__ == "__main__":
    unittest.main()
