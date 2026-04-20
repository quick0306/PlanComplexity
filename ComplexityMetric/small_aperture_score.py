from typing import Dict, List, Tuple, Union

from ApertureMetric.aperture_geometry import PyAperture
from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ComplexityMetric.complexity_metric import ComplexityMetric


class SmallApertureScore(ComplexityMetric):
    """Small aperture score (SASn).

    Reference:
        Crowe SB, et al. Examination of the properties of IMRT and VMAT beams and evaluation
        against pre-treatment quality assurance results. Physics in Medicine & Biology, 2015.
        DOI: 10.1088/0031-9155/60/6/2587
    """

    def calculate_for_plan(self, plan: Dict[str, str] = None, x=5):
        if "halcyon" in plan["machine_id"].lower() or "ethos" in plan["machine_id"].lower():
            mlcx1_small = mlcx1_total = 0
            mlcx2_small = mlcx2_total = 0
            for _, beam in plan["beams"].items():
                if beam["TreatmentDeliveryType"] != "TREATMENT" or beam["MU"] <= 0.0:
                    continue
                (beam_small_1, beam_total_1), (beam_small_2, beam_total_2) = self.count_beam_leaf_gaps(beam, x)
                mlcx1_small += beam_small_1
                mlcx1_total += beam_total_1
                mlcx2_small += beam_small_2
                mlcx2_total += beam_total_2
            return (
                round(mlcx1_small / mlcx1_total, 2) if mlcx1_total else 0.0,
                round(mlcx2_small / mlcx2_total, 2) if mlcx2_total else 0.0,
            )

        small_count = 0
        total_count = 0
        for _, beam in plan["beams"].items():
            if beam["TreatmentDeliveryType"] != "TREATMENT" or beam["MU"] <= 0.0:
                continue
            beam_small_count, beam_total_count = self.count_beam_leaf_gaps(beam, x)
            small_count += beam_small_count
            total_count += beam_total_count

        return round(small_count / total_count, 2) if total_count else 0.0

    def count_beam_leaf_gaps(self, beam: Dict[str, str], x=5) -> Union[Tuple[int, int], Tuple[Tuple[int, int], Tuple[int, int]]]:
        apertures = AperturesFromBeamCreator().create(beam)
        if "halcyon" in beam["TreatmentMachineName"].lower() or "ethos" in beam["TreatmentMachineName"].lower():
            return self.count_aperture_leaf_gaps(apertures[0::2], x), self.count_aperture_leaf_gaps(apertures[1::2], x)
        return self.count_aperture_leaf_gaps(apertures, x)

    @staticmethod
    def count_aperture_leaf_gaps(apertures: List[PyAperture], x=5) -> Tuple[int, int]:
        # SASn is the fraction of active gaps smaller than the threshold n.
        small_count = 0
        total_count = 0
        for aperture in apertures:
            for leaf_pair in aperture.leaf_pairs:
                if leaf_pair.is_outside_jaw():
                    continue
                gap = leaf_pair.field_size()
                if gap <= 0:
                    continue
                total_count += 1
                if gap < x:
                    small_count += 1
        return small_count, total_count




