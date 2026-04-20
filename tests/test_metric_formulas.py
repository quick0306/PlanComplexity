import unittest

import numpy as np

from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.leaf_gap import LeafGap
from ComplexityMetric.mean_asymmetry_distance import MeanAsymmetryDistance
from ComplexityMetric.small_aperture_score import SmallApertureScore


class MetricFormulaTests(unittest.TestCase):
    def test_mean_asymmetry_distance_matches_ucomx_definition(self):
        aperture = PyAperture(
            leaf_positions=np.array([[-4.0, -2.0], [6.0, 8.0]]),
            leaf_widths=np.array([5.0, 5.0]),
            jaw=[-10.0, 10.0, 10.0, -10.0],
            gantry_angle=0.0,
        )

        value = MeanAsymmetryDistance().calculate_mean_asymmetry_distance(aperture)

        self.assertEqual(value, 5.0)

    def test_leaf_gap_summary_uses_all_active_leaf_pairs(self):
        aperture = PyAperture(
            leaf_positions=np.array([[-5.0, -4.0], [5.0, 8.0]]),
            leaf_widths=np.array([5.0, 5.0]),
            jaw=[-10.0, 10.0, 10.0, -10.0],
            gantry_angle=0.0,
        )

        gaps = LeafGap.get_aperture_leaf_gaps([aperture])
        summary = LeafGap().summarize(gaps)

        self.assertEqual(gaps, [10.0, 12.0])
        self.assertEqual(summary, (11.0, 1.0))

    def test_small_aperture_score_counts_global_fraction(self):
        aperture = PyAperture(
            leaf_positions=np.array([[-1.0, -4.0, -2.0], [1.0, 8.0, 2.5]]),
            leaf_widths=np.array([5.0, 5.0, 5.0]),
            jaw=[-10.0, 10.0, 10.0, -10.0],
            gantry_angle=0.0,
        )

        small_count, total_count = SmallApertureScore.count_aperture_leaf_gaps([aperture], x=5)

        self.assertEqual((small_count, total_count), (2, 3))


if __name__ == "__main__":
    unittest.main()



