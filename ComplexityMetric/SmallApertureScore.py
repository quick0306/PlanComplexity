from typing import List, Dict

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture
from ApertureMetric.ApertureCreator import AperturesFromBeamCreator


class SmallApertureScore(ComplexityMetric):
    """计划小野评分，计算小于给定阈值距离（x）的开放叶片对的比例

    Reference:
        Crowe SB, et al. Examination of the properties of IMRT and VMAT beams and evaluation against
        pre-treatment quality assurance results. Phys Med Biol 2015; 60(6):2587-2601.
        DOI: https://doi.org/10.1088/0031-9155/60/6/2587
    """
    def CalculateForPlan(self, plan: Dict[str, str] = None, x=5):
        """Returns the complexity metric of a plan, calculated as the weighted sum of the individual metrics
        for each beam"""
        weights = self.GetWeightsPlan(plan)
        metrics = self.GetMetricsPlan(plan, x)

        return round(self.WeightedSum(weights, metrics), 2)

    def GetMetricsPlan(self, plan: Dict[str, str], x=5) -> List[float]:
        """Returns the unweighted metrics of a plan's beams"""
        values = []
        for k, beam in plan['beams'].items():
            # check if treatment beam
            if beam['TreatmentDeliveryType'] == 'TREATMENT':
                if beam['MU'] > 0.:
                    v = self.CalculateForBeam(beam, x)
                    values.append(v)
        return values

    def CalculateForBeam(self, beam: Dict[str, str], x=5) -> float:
        """Returns the complexity metric of a beam, calculated as the weighted sum of the individual metrics
        for each control point"""
        weights = self.GetWeightsBeam(beam)
        values = self.GetMetricsBeam(beam, x)

        return self.WeightedSum(weights, values)

    def GetMetricsBeam(self, beam: Dict[str, str], x=5) -> List[float]:
        """Returns the unweighted metrics of a beam's control points"""
        apertures = AperturesFromBeamCreator().Create(beam)
        return self.CalculatePerAperture(apertures, x)

    def CalculatePerAperture(self, apertures: List[PyAperture], x=5) -> List[float]:
        """计算控制点Aperture小于给定阈值距离（x）开放叶片对的比例"""
        return [self.CalculateSmallApertureScore(aperture, x) for aperture in apertures]

    def CalculateSmallApertureScore(self, aperture: PyAperture, x=5) -> float:
        lp_fs = [lp.FieldSize() for lp in aperture.LeafPairs if not lp.IsOutsideJaw()]
        lp_fs_x = [fs for fs in lp_fs if fs < x]
        return len(lp_fs_x) / len(lp_fs)