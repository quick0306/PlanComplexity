from typing import List

import numpy as np

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture


class ConvertedApertureMetric(ComplexityMetric):
    """计算Converted Aperture Metric

    Reference:
        GÖTSTEDT, et al. Development and evaluation of aperture‐based complexity metrics using film
        and EPID measurements of static MLC openings. Medical physics, 2015, 42.7: 3911-3921.
        DOI: https://doi.org/10.1118/1.4921733
    """
    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        """计算CAM"""
        return [self.CalculateConvertedApertureMetric(aperture) for aperture in apertures]

    def CalculateConvertedApertureMetric(self, aperture: PyAperture) -> float:
        lp_distance_cam = []    # 存储非线性转换后叶片间距，目前只考虑MLC运动方向

        for lp in aperture.LeafPairs:
            if not lp.IsOutsideJaw():
                lp_distance_cam.append(1 - np.exp(-(lp.FieldSize() / 10)))      # convert mm to cm

        lp_distance_cam = np.array(lp_distance_cam)
        area = np.sqrt(aperture.Area())
        area_cam = 1 - np.exp(-(area / 10))
        return 1 - np.mean(lp_distance_cam) * area_cam