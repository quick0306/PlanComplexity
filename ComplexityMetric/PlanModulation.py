from typing import List, Dict

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture
from ApertureMetric.ApertureCreator import AperturesFromBeamCreator


class PlanModulation(ComplexityMetric):
    """Plan averaged beam modulation (PM)

    Reference :
        Du W, et al. Quantification of beam complexity in intensity-modulated radiation therapy treatment plans.
        Med Phys 2014;41:21716. DOI: http://dx.doi.org/10.1118/1.4861821.
    """
    def CalculateForBeam(self, beam: Dict[str, str]) -> float:
        """Returns the complexity metric of a beam, calculated as the weighted sum of the individual metrics
        for each control point"""
        weights = self.GetWeightsBeam(beam)
        values = self.GetMetricsBeam(beam)
        UAA = self.CalculateBeamUnionArea(beam)
        return self.ModulationWeightedSum(weights, values, UAA)

    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        """cp aperture area"""
        return [aperture.Area() for aperture in apertures]

    def CalculateBeamUnionArea(self, beam: Dict[str, str]) -> float:
        """Calculate beam aperture union area"""
        apertures = AperturesFromBeamCreator().Create(beam)

        area_max = {}
        for aperture in apertures:
            n_pairs = int(len(aperture.LeafPairs))
            for i, lp in zip(range(n_pairs), aperture.LeafPairs):
                if not lp.IsOutsideJaw():
                    if i in area_max:
                        "判断当前Leaf Area是否最大，是否替换"
                        area_max[i] = lp.FieldArea() if lp.FieldArea() > area_max[i] else area_max[i]
                    else:
                        area_max[i] = lp.FieldArea()

        return sum([area_max[i] for i in area_max])

    def ModulationWeightedSum(self, weights, values, UAA) -> float:
        """Returns the weighted sum of the given values and weights"""
        return 1 - sum([weights[i] * values[i] for i in range(len(values))]) / (sum(weights) * UAA)
