from typing import Dict, List, Tuple, Union

import numpy as np

from ComplexityMetric.complexity_metric import ComplexityMetric
from ApertureMetric.aperture_geometry import PyAperture
from ApertureMetric.aperture_creator import AperturesFromBeamCreator


class LeafGap(ComplexityMetric):
    """Average and standard deviation of active leaf gaps over the whole plan."""

    round_digits = 2

    def calculate_for_plan(self, plan: Dict[str, str] = None) -> Union[Tuple[float, float], Tuple[Tuple[float, float], Tuple[float, float]]]:
        if 'halcyon' in plan['machine_id'].lower() or 'ethos' in plan['machine_id'].lower():
            gaps_mlcx1: List[float] = []
            gaps_mlcx2: List[float] = []
            for _, beam in plan['beams'].items():
                if beam['TreatmentDeliveryType'] != 'TREATMENT' or beam['MU'] <= 0.0:
                    continue
                beam_gaps_1, beam_gaps_2 = self.get_beam_leaf_gaps(beam)
                gaps_mlcx1.extend(beam_gaps_1)
                gaps_mlcx2.extend(beam_gaps_2)
            return self.summarize(gaps_mlcx1), self.summarize(gaps_mlcx2)

        gaps: List[float] = []
        for _, beam in plan['beams'].items():
            if beam['TreatmentDeliveryType'] != 'TREATMENT' or beam['MU'] <= 0.0:
                continue
            gaps.extend(self.get_beam_leaf_gaps(beam))
        return self.summarize(gaps)

    def get_beam_leaf_gaps(self, beam: Dict[str, str]) -> Union[List[float], Tuple[List[float], List[float]]]:
        apertures = AperturesFromBeamCreator().create(beam)
        if 'halcyon' in beam['TreatmentMachineName'].lower() or 'ethos' in beam['TreatmentMachineName'].lower():
            return self.get_aperture_leaf_gaps(apertures[0::2]), self.get_aperture_leaf_gaps(apertures[1::2])
        return self.get_aperture_leaf_gaps(apertures)

    @staticmethod
    def get_aperture_leaf_gaps(apertures: List[PyAperture]) -> List[float]:
        gaps = []
        for aperture in apertures:
            for lp in aperture.leaf_pairs:
                if lp.is_outside_jaw():
                    continue
                gap = lp.field_size()
                if gap > 0:
                    gaps.append(gap)
        return gaps

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        return [self.summarize(self.get_aperture_leaf_gaps([aperture]))[0] for aperture in apertures]

    def summarize(self, gaps: List[float]) -> Tuple[float, float]:
        if not gaps:
            return 0.0, 0.0
        values = np.asarray(gaps, dtype=float)
        return round(float(np.mean(values)), self.round_digits), round(float(np.std(values)), self.round_digits)




