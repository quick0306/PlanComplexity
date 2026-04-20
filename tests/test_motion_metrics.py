import unittest

import numpy as np

from ApertureMetric.aperture_geometry import PyAperture
from ApertureMetric.mlc_attributes import MLCAttributes
from ComplexityMetric.proportion_mlc_speed_acceleration import ProportionMLCSpeedAcceleration
from ComplexityMetric.station_parameter_optimized_radiation_therapy import (
    StationParameterOptimizedRadiationTherapy,
)


class MotionMetricTests(unittest.TestCase):
    def test_mlc_speed_and_acceleration_use_park_bins(self):
        metric = ProportionMLCSpeedAcceleration()
        speed = np.array(
            [
                [np.nan, np.nan],
                [2.0, 6.0],
                [10.0, 14.0],
                [18.0, 18.0],
            ]
        )
        acceleration = np.array(
            [
                [np.nan, np.nan],
                [np.nan, np.nan],
                [20.0, 60.0],
                [100.0, 180.0],
            ]
        )

        speed_profile = metric.calculate_for_speed_proportion(speed)
        acc_profile = metric.calculate_for_acc_proportion(acceleration)

        self.assertEqual(speed_profile, [1 / 6, 1 / 6, 1 / 6, 1 / 6, 1 / 3])
        self.assertEqual(acc_profile, [1 / 4, 1 / 4, 1 / 4, 0.0, 1 / 4])

    def test_control_point_time_uses_actual_delta_gantry(self):
        apertures = [
            PyAperture(np.array([[-1.0], [1.0]]), np.array([5.0]), [-10.0, 10.0, 10.0, -10.0], 0.0),
            PyAperture(np.array([[-3.0], [3.0]]), np.array([5.0]), [-10.0, 10.0, 10.0, -10.0], 4.0),
            PyAperture(np.array([[-5.0], [5.0]]), np.array([5.0]), [-10.0, 10.0, 10.0, -10.0], 10.0),
        ]

        attributes = MLCAttributes(
            apertures=apertures,
            cumulative_mu=[0.0, 10.0, 20.0],
            treatment_machine_name="TrueBeam",
            dose_rate_set=600.0,
            gantry_rotation_angle=10.0,
        )

        self.assertTrue(np.isnan(attributes.delta_mu_time["time"].iloc[0]))
        self.assertAlmostEqual(attributes.delta_mu_time["time"].iloc[1], 1.0)
        self.assertAlmostEqual(attributes.delta_mu_time["time"].iloc[2], 1.0)

    def test_sport_station_metric_matches_paper_equation(self):
        apertures = [
            PyAperture(np.array([[-1.0], [1.0]]), np.array([5.0]), [-10.0, 10.0, 10.0, -10.0], 358.0),
            PyAperture(np.array([[-2.0], [2.0]]), np.array([5.0]), [-10.0, 10.0, 10.0, -10.0], 0.0),
            PyAperture(np.array([[-4.0], [4.0]]), np.array([5.0]), [-10.0, 10.0, 10.0, -10.0], 2.0),
        ]

        values = StationParameterOptimizedRadiationTherapy().calculate_per_aperture(
            apertures,
            cumulative_mu=[0.0, 10.0, 20.0],
        )

        self.assertEqual(values, [40.0, 30.0, 50.0])


if __name__ == "__main__":
    unittest.main()



