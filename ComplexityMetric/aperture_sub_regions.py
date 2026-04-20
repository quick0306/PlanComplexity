from typing import List

from ComplexityMetric.complexity_metric import ComplexityMetric
from ApertureMetric.aperture_geometry import PyAperture


class ApertureSubRegions(ComplexityMetric):
    """Maximum number of regions in the aperture

    Reference:
        LAM, Dao, et al. Predicting gamma passing rates for portal dosimetry鈥恇ased IMRT QA using machine learning.
        Medical physics, 2019, 46.10: 4666-4675. DOI: https://doi.org/10.1002/mp.13752
    """
    aggregation_mode = "mu"

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        """Count the disconnected open sub-regions in each aperture."""
        return [aperture.aperture_sub_regions() for aperture in apertures]




