from typing import Dict, List, Tuple, Union

from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.complexity_metric import ComplexityMetric


class LeafTravel(ComplexityMetric):
    """Leaf travel between adjacent control points."""

    aggregation_mode = "mu"

    def calculate_for_beam(self, beam: Dict[str, str]) -> Union[Tuple[float, float], float]:
        if "halcyon" in beam["TreatmentMachineName"].lower() or "ethos" in beam["TreatmentMachineName"].lower():
            apertures = AperturesFromBeamCreator().create(beam)
            mlcx1_values = self.calculate_per_aperture(apertures[0::2])
            mlcx2_values = self.calculate_per_aperture(apertures[1::2])
            weights = self.get_control_arc_weights(beam)
            return self.weighted_sum(weights, mlcx1_values), self.weighted_sum(weights, mlcx2_values)

        apertures = AperturesFromBeamCreator().create(beam)
        values = self.calculate_per_aperture(apertures)
        weights = self.get_control_arc_weights(beam)
        return self.weighted_sum(weights, values)

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        if len(apertures) < 2:
            return []
        return [self._leaf_motion_distance(first, second) for first, second in zip(apertures[:-1], apertures[1:])]

    @staticmethod
    def _leaf_motion_distance(first: PyAperture, second: PyAperture) -> float:
        total = 0.0
        for first_leaf_pair, second_leaf_pair in zip(first.leaf_pairs, second.leaf_pairs):
            if first_leaf_pair.is_outside_jaw() and second_leaf_pair.is_outside_jaw():
                continue
            total += abs(first_leaf_pair.left - second_leaf_pair.left)
            total += abs(first_leaf_pair.right - second_leaf_pair.right)
        return total
