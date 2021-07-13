from typing import List

import numpy as np

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture


class MeanAsymmetryDistance(ComplexityMetric):
    """叶片对中点与中心轴之间平均距离

    Reference:
        Crowe SB, et al. Examination of the properties of IMRT and VMAT beams and evaluation against pre-treatment
        quality assurance results. Phys Med Biol 2015; 60(6):2587-2601.
        DOI: http://doi.org/10.1088/0031-9155/60/6/2587.
    """
    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        """计算控制点Aperture叶片对中点与中心轴之间平均距离"""
        return [self.CalculateMeanAsymmetryDistance(aperture) for aperture in apertures]

    def CalculateMeanAsymmetryDistance(self, aperture: PyAperture) -> float:
        """ Mean distance from center of each open leaf to the center of MLC using apertures"""
        mid_x = []
        mid_y = []
        for lp in aperture.LeafPairs:
            if not lp.IsOutsideJaw():
                mid_x.append((lp.Left + lp.Right) / 2)
                mid_y.append((lp.Top + lp.Bottom) / 2)

        mid_x = np.array(mid_x)
        mid_y = np.array(mid_y)
        return np.mean(np.sqrt((mid_x * mid_x + mid_y * mid_y)))