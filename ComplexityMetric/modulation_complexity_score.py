from typing import Dict, List, Tuple, Union

import numpy as np

from ComplexityMetric.complexity_metric import ComplexityMetric
from ApertureMetric.aperture_geometry import PyAperture
from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from DicomParse.utilities import divide_or_default


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
        left_min = {}
        right_max = {}
        widths = {}
        for aperture in apertures:
            for idx, lp in enumerate(aperture.leaf_pairs):
                if lp.is_outside_jaw():
                    continue
                left_min[idx] = min(left_min.get(idx, lp.left), lp.left)
                right_max[idx] = max(right_max.get(idx, lp.right), lp.right)
                widths[idx] = lp.open_leaf_width()

        normalization = 0.0
        for idx in left_min:
            normalization += max(right_max[idx] - left_min[idx], 0.0) * widths.get(idx, 0.0)
        return normalization

    def _calculate_cp_aav(self, aperture: PyAperture, normalization: float) -> float:
        return divide_or_default(aperture.area(), normalization)

    def _calculate_cp_lsv(self, aperture: PyAperture) -> float:
        active_leaf_pairs = [lp for lp in aperture.leaf_pairs if not lp.is_outside_jaw() and lp.field_size() > 0]
        if len(active_leaf_pairs) < 2:
            return 1.0 if active_leaf_pairs else 0.0

        left_positions = [lp.left for lp in active_leaf_pairs]
        right_positions = [lp.right for lp in active_leaf_pairs]
        bank_a = self._calculate_bank_lsv(left_positions)
        bank_b = self._calculate_bank_lsv(right_positions)
        return bank_a * bank_b

    @staticmethod
    def _calculate_bank_lsv(positions: List[float]) -> float:
        if len(positions) < 2:
            return 1.0
        pos_range = max(positions) - min(positions)
        if pos_range == 0:
            return 1.0
        variation_sum = sum(pos_range - abs(curr - nxt) for curr, nxt in zip(positions[:-1], positions[1:]))
        return variation_sum / ((len(positions) - 1) * pos_range)




