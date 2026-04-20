import unittest

import numpy as np

from tomo_metrics import TomoPlan, calculate_tomo_metrics


class TomoMetricTests(unittest.TestCase):
    def test_tomo_metrics_basic_statistics(self):
        plan = TomoPlan(
            source_path="plan.dcm",
            sinogram=np.array(
                [
                    [1.0, 0.0, 0.5, 0.0],
                    [0.0, 1.0, 0.5, 0.0],
                ]
            ),
            projection_time_s=0.1,
            projections_per_rotation=2,
            field_width_mm=25.0,
            pitch=0.5,
            couch_translation_mm=25.0,
            fraction_dose_cgy=200.0,
        )

        metrics = calculate_tomo_metrics(plan)

        self.assertAlmostEqual(metrics["mlot"], 75.0)
        self.assertAlmostEqual(metrics["mflot"], 0.75)
        self.assertAlmostEqual(metrics["ta"], 2.5)
        self.assertAlmostEqual(metrics["ncc"], 1.5)
        self.assertAlmostEqual(metrics["fdisc"], 0.5)
        self.assertAlmostEqual(metrics["field_width_mm"], 25.0)
        self.assertAlmostEqual(metrics["projection_time_s"], 0.1)


if __name__ == "__main__":
    unittest.main()
