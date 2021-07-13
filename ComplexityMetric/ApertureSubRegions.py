from typing import List

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture


class ApertureSubRegions(ComplexityMetric):
    """Maximum number of regions in the aperture

    Reference:
        LAM, Dao, et al. Predicting gamma passing rates for portal dosimetry‐based IMRT QA using machine learning.
        Medical physics, 2019, 46.10: 4666-4675. DOI: https://doi.org/10.1002/mp.13752
    """
    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        """计算aperture中有多少个小子野，MLC interplay"""
        return [aperture.ApertureSubRegions() for aperture in apertures]
