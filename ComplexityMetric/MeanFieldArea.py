from typing import List

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture


class MeanFieldArea(ComplexityMetric):
    """平均射野面积，子野面积与MU加权平均，Reference 2中PA，BA及AA指标

    Reference 1:
        Crowe SB, et al. Examination of the properties of IMRT and VMAT beams
        and evaluation against pre-treatment quality assurance results. Phys Med Biol 2015; 60(6):2587-2601.
        DOI: http://doi.org/10.1088/0031-9155/60/6/2587.
    Reference 2:
        Du W, et al. Quantification of beam complexity in intensity-modulated radiation therapy treatment plans.
        Med Phys 2014;41:21716. DOI: http://dx.doi.org/10.1118/1.4861821.
    """

    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        """cp Aperture area"""
        return [aperture.Area() for aperture in apertures]
