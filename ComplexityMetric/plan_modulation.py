from typing import Dict, List, Tuple, Union

from ApertureMetric.aperture_geometry import PyAperture
from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ComplexityMetric.complexity_metric import ComplexityMetric


class PlanModulation(ComplexityMetric):
    """Plan modulation (PM).

    Reference:
        Du W, et al. Quantification of beam complexity in intensity-modulated radiation therapy
        treatment plans. Medical Physics, 2014.
        DOI: 10.1118/1.4861821
    """

    aggregation_mode = "mu"

    def calculate_for_beam(self, beam: Dict[str, str]) -> Union[Tuple[float, float], float]:
        weights = self.get_weights_beam(beam)
        if "halcyon" in beam["TreatmentMachineName"].lower() or "ethos" in beam["TreatmentMachineName"].lower():
            mlcx1_values, mlcx2_values = self.get_metrics_beam(beam)
            mlcx1_union, mlcx2_union = self.calculate_beam_union_area(beam)
            return (
                self.modulation_weighted_sum(weights, mlcx1_values, mlcx1_union),
                self.modulation_weighted_sum(weights, mlcx2_values, mlcx2_union),
            )

        values = self.get_metrics_beam(beam)
        union_area = self.calculate_beam_union_area(beam)
        return self.modulation_weighted_sum(weights, values, union_area)

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        return [aperture.area() for aperture in apertures]

    def calculate_beam_union_area(self, beam: Dict[str, str]) -> Union[Tuple[float, float], float]:
        if "halcyon" in beam["TreatmentMachineName"].lower() or "ethos" in beam["TreatmentMachineName"].lower():
            apertures = AperturesFromBeamCreator().create(beam)
            return self._max_union_area(apertures[0::2]), self._max_union_area(apertures[1::2])

        apertures = AperturesFromBeamCreator().create(beam)
        return self._max_union_area(apertures)

    def modulation_weighted_sum(self, weights, values, union_area) -> float:
        # PM is computed as 1 - weighted_aperture_area / union_aperture_area in Du et al.
        return 1 - sum(weights[i] * values[i] for i in range(len(values))) / (sum(weights) * union_area)

    def _max_union_area(self, apertures: List[PyAperture]) -> float:
        area_max = {}
        for aperture in apertures:
            for index, leaf_pair in enumerate(aperture.leaf_pairs):
                if leaf_pair.is_outside_jaw():
                    continue
                area_max[index] = max(leaf_pair.field_area(), area_max.get(index, 0.0))
        return sum(area_max.values())




