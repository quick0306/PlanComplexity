from typing import List

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture


class ApertureXJaw(ComplexityMetric):
    """计算X方向Jaw距离

    Reference:
        LI, Jiaqi, et al. Machine Learning for Patient-Specific Quality Assurance of VMAT: Prediction and
        Classification Accuracy. International Journal of Radiation Oncology* Biology* Physics, 2019, 105.4: 893-902.
        DOI: https://doi.org/10.1016/j.ijrobp.2019.07.049
    """
    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        """计算X方向Jaw距离"""
        return [abs(aperture.jaw.Right - aperture.jaw.Left) for aperture in apertures]