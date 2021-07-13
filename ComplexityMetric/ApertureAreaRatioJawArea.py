from typing import List

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture


class ApertureAreaRatioJawArea(ComplexityMetric):
    """Ratio of the average area of an aperture over the area defined by jaws

    Reference:
        LAM, Dao, et al. Predicting gamma passing rates for portal dosimetry‐based IMRT QA using machine learning.
        Medical physics, 2019, 46.10: 4666-4675. DOI: https://doi.org/10.1002/mp.13752
    """
    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        """计算控制点Aperture面积与Jaw面积比值"""
        return [self.CalculateApertureAreaRatioJawArea(aperture) for aperture in apertures]

    def CalculateApertureAreaRatioJawArea(self, aperture: PyAperture) -> float:
        AA = aperture.Area()
        jaws = aperture.Jaw
        JA = abs(jaws.Right - jaws.Left) * abs(jaws.Top - jaws.Bottom)
        return AA / JA