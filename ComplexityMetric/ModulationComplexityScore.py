from typing import List

import numpy as np

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture
from DicomParse.utilities import DivisionOrDefault


class ModulationComplexityScore(ComplexityMetric):
    """ Modulation Complexity Score, MCS

    Reference:
        McNiven AL, et al. A new metric for assessing IMRT modulation complexity and plan deliverability.
        Med Phys 2010;37:505–15. DOI: http://dx.doi.org/10.1118/1.3276775.
    """

    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        posi_max = {}
        for aperture in apertures:
            n_pairs = int(len(aperture.LeafPairs))
            for i, lp in zip(range(n_pairs), aperture.LeafPairs):
                if not lp.IsOutsideJaw():
                    if i in posi_max:
                        "判断当前Leaf Pair位置是否最大，是否替换"
                        posi_max[i][0] = lp.Left if lp.Left < posi_max[i][0] else posi_max[i][0]
                        posi_max[i][1] = lp.Right if lp.Right > posi_max[i][1] else posi_max[i][1]
                    else:
                        posi_max[i] = [lp.Left, lp.Right]

        aav_norm = sum(([abs(posi_max[lp_num][1] - posi_max[lp_num][0]) for lp_num in posi_max]))

        return [self.CalculateApertureMCS(aperture, aav_norm) for aperture in apertures]

    def CalculateApertureMCS(self, aperture, aav_norm) -> float:
        """Calculate LSV and AAV，Aperture MCS"""
        pos = [(lp.Left, lp.Right) for lp in aperture.LeafPairs if not lp.IsOutsideJaw()]
        N = len(pos)
        aperture_mcs = 0
        if N > 0:   # 有叶片打开，有计划控制点叶片全关的情况，如E1706020, A7FDMLCa
            pos_max = np.max(pos, axis=0) - np.min(pos, axis=0)
            a = np.sum(pos_max + np.diff(pos, axis=0), axis=0)
            b = (N * pos_max)
            tmp = np.divide(a, b, out=np.zeros_like(a), where=b != 0)
            LSV = np.prod(tmp)

            num = sum(([lp.FieldSize() for lp in aperture.LeafPairs if not lp.IsOutsideJaw()]))
            AAV = DivisionOrDefault(num, aav_norm)

            aperture_mcs = LSV * AAV

        return aperture_mcs
