from typing import List

import numpy as np

from ComplexityMetric.complexity_metric import ComplexityMetric
from ApertureMetric.aperture_geometry import PyAperture


class ConvertedApertureMetric(ComplexityMetric):
    """璁＄畻Converted Aperture Metric

    Reference:
        G脰TSTEDT, et al. Development and evaluation of aperture鈥恇ased complexity metrics using film
        and EPID measurements of static MLC openings. Medical physics, 2015, 42.7: 3911-3921.
        DOI: https://doi.org/10.1118/1.4921733
    """
    aggregation_mode = "mu"

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        """璁＄畻CAM"""
        return [self.calculate_converted_aperture_metric(aperture) for aperture in apertures]

    def calculate_converted_aperture_metric(self, aperture: PyAperture) -> float:
        lp_distance_cam = []    # 瀛樺偍闈炵嚎鎬ц浆鎹㈠悗鍙剁墖闂磋窛锛岀洰鍓嶅彧鑰冭檻MLC杩愬姩鏂瑰悜

        for lp in aperture.leaf_pairs:
            if not lp.is_outside_jaw():
                lp_distance_cam.append(1 - np.exp(-(lp.field_size() / 10)))      # convert mm to cm

        lp_distance_cam = np.array(lp_distance_cam)
        area = np.sqrt(aperture.area())
        area_cam = 1 - np.exp(-(area / 10))
        return 1 - np.mean(lp_distance_cam) * area_cam




