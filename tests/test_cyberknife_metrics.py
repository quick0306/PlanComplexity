import unittest
from types import SimpleNamespace

import numpy as np

import analysis_helpers
from ApertureMetric.aperture_geometry import PyAperture


def make_rectangular_aperture(left: float, right: float, *, pairs: int = 2, width: float = 5.0) -> PyAperture:
    return PyAperture(
        leaf_positions=np.array([[left] * pairs, [right] * pairs], dtype=float),
        leaf_widths=np.array([width] * pairs, dtype=float),
        jaw=[-20.0, 20.0, 20.0, -20.0],
        gantry_angle=0.0,
    )


class CyberKnifeMetricFormulaTests(unittest.TestCase):
    def test_single_rectangular_segment_has_mcs_one_and_pm_zero(self):
        aperture = make_rectangular_aperture(-5.0, 5.0)
        beam = SimpleNamespace(
            beam_id="b1",
            interval_key=(0, 0),
            mu=10.0,
            segments=[SimpleNamespace(aperture=aperture, mu=10.0)],
        )

        metrics = analysis_helpers.calculate_cyberknife_mlc_metrics(
            {"beams": {}},
            cyberknife_beams=[beam],
        )

        self.assertEqual(metrics["mcs"], 1.0)
        self.assertEqual(metrics["pm"], 0.0)
        self.assertEqual(metrics["lg"], 10.0)
        self.assertEqual(metrics["sas10"], 0.0)

    def test_pm_uses_interval_union_across_beams_in_same_group(self):
        small = make_rectangular_aperture(-2.5, 2.5)
        large = make_rectangular_aperture(-5.0, 5.0)
        beams = [
            SimpleNamespace(
                beam_id="b1",
                interval_key=(0, 0),
                mu=10.0,
                segments=[SimpleNamespace(aperture=small, mu=10.0)],
            ),
            SimpleNamespace(
                beam_id="b2",
                interval_key=(0, 0),
                mu=10.0,
                segments=[SimpleNamespace(aperture=large, mu=10.0)],
            ),
        ]

        metrics = analysis_helpers.calculate_cyberknife_mlc_metrics(
            {"beams": {}},
            cyberknife_beams=beams,
        )

        self.assertEqual(metrics["mcs"], 0.75)
        self.assertEqual(metrics["pm"], 0.25)
        self.assertEqual(metrics["lg"], 7.5)
        self.assertEqual(metrics["sas10"], 0.5)


if __name__ == "__main__":
    unittest.main()
