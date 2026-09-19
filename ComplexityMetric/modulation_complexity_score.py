from typing import Dict, List, Tuple, Union

from ComplexityMetric.complexity_metric import ComplexityMetric
from ApertureMetric.aperture_geometry import PyAperture
from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from DicomParse.utilities import divide_or_default
from ComplexityMetric.aperture_shape_metrics import (
    maximum_aperture_area, leaf_sequence_variability,
)


class ModulationComplexityScore(ComplexityMetric):
    """MCSv following the AAV/LSV control-point definition described in the UCoMX manual."""

    aggregation_mode = "mu"

    def calculate_for_beam(self, beam: Dict[str, str]) -> Union[Tuple[float, float], float]:
        weights = self.get_control_arc_weights(beam)
        if 'halcyon' in beam['TreatmentMachineName'].lower() or 'ethos' in beam['TreatmentMachineName'].lower():
            apertures = AperturesFromBeamCreator().create(beam)
            mlcx1_values = self.calculate_per_aperture(apertures[0::2])
            mlcx2_values = self.calculate_per_aperture(apertures[1::2])
            return self.weighted_sum(weights, mlcx1_values), self.weighted_sum(weights, mlcx2_values)

        apertures = AperturesFromBeamCreator().create(beam)
        values = self.calculate_per_aperture(apertures)
        return self.weighted_sum(weights, values)

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        if len(apertures) < 2:
            return []

        arc_norm = self._build_arc_aav_normalization(apertures)
        aav_cp = [self._calculate_cp_aav(aperture, arc_norm) for aperture in apertures]
        lsv_cp = [self._calculate_cp_lsv(aperture) for aperture in apertures]
        return [
            ((aav_cp[index] + aav_cp[index + 1]) / 2.0) * ((lsv_cp[index] + lsv_cp[index + 1]) / 2.0)
            for index in range(len(apertures) - 1)
        ]

    @staticmethod
    def _build_arc_aav_normalization(apertures: List[PyAperture]) -> float:
        return maximum_aperture_area(apertures)

    def _calculate_cp_aav(self, aperture: PyAperture, normalization: float) -> float:
        return divide_or_default(aperture.area(), normalization)

    def _calculate_cp_lsv(self, aperture: PyAperture) -> float:
        return leaf_sequence_variability(aperture)

