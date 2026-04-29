from typing import List
import warnings
import numpy as np

from ComplexityMetric.complexity_metric import ComplexityMetric
from ApertureMetric.aperture_geometry import PyAperture


class LeafArea(ComplexityMetric):
    """Calculate mean LeafArea = LeafWidth * LeafGap

    Reference:
        Nauta M, et al. Fractal analysis for assessing the level of modulation of IMRT fields.
        Med Phys 2011; 38: 5385鈥?3. DOI: https://doi.org/10.1118/1.3633912
    """

    aggregation_mode = "mu"

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        return [self.calculate_aperture_leaf_gap_area(aperture) for aperture in apertures]

    def calculate_aperture_leaf_gap_area(self, aperture: PyAperture) -> float:
        """Calculates the mean aperture area of all leaf pairs"""
        areas = np.array(aperture.leaf_pair_areas)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return areas[np.nonzero(areas)].mean()




