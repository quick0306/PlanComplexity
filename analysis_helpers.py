from ComplexityMetric.aperture_area_ratio_jaw_area import ApertureAreaRatioJawArea
from ComplexityMetric.aperture_sub_regions import ApertureSubRegions
from ComplexityMetric.aperture_x_jaw import ApertureXJaw
from ComplexityMetric.aperture_y_jaw import ApertureYJaw
from ComplexityMetric.converted_aperture_metric import ConvertedApertureMetric
from ComplexityMetric.edge_area_metric import EdgeAreaMetric
from ComplexityMetric.edge_metric import EdgeMetric
from ComplexityMetric.leaf_gap import LeafGap
from ComplexityMetric.mean_asymmetry_distance import MeanAsymmetryDistance
from ComplexityMetric.mean_field_area import MeanFieldArea
from ComplexityMetric.modulation_complexity_score import ModulationComplexityScore
from ComplexityMetric.modulation_index_score import ModulationIndexScore
from ComplexityMetric.plan_irregularity import PlanIrregularity
from ComplexityMetric.plan_modulation import PlanModulation
from ComplexityMetric.proportion_mlc_speed_acceleration import ProportionMLCSpeedAcceleration
from ComplexityMetric.small_aperture_score import SmallApertureScore
from ComplexityMetric.station_parameter_optimized_radiation_therapy import StationParameterOptimizedRadiationTherapy
from cyberknife_metrics import calculate_cyberknife_metrics
from halcyon_dual_layer_metrics import calculate_halcyon_dual_layer_paper_metrics
from vcomx_vmat_metrics import calculate_vcomx_supplemental_metrics


def get_plan_metadata(plan_info, plan_dict):
    treatment_machine_name = ""
    for beam in getattr(plan_info.ds, "BeamSequence", []):
        if str(getattr(beam, "TreatmentDeliveryType", "")).upper() != "SETUP":
            treatment_machine_name = getattr(beam, "TreatmentMachineName", "")
            break

    return {
        "patient_id": plan_dict["patient_id"],
        "patient_name": plan_dict["patient_name"],
        "plan_name": plan_dict["plan_name"],
        "plan_label": plan_dict["label"],
        "manufacturer": getattr(plan_info.ds, "Manufacturer", ""),
        "machine_id": treatment_machine_name,
        "calculation_model": plan_dict["calculation_model"],
        "prescribed_dose": plan_dict["rxdose"],
        "mu": plan_dict["Plan_MU"],
        "beam_type": plan_dict["beam_type"],
        "beam_number": plan_dict["beam_number"],
        "rotation_direction": plan_dict.get("rotation_direction", ""),
    }


def calculate_core_metrics(plan_dict):
    small_aperture_score_obj = SmallApertureScore()
    modulation_index_score_obj = ModulationIndexScore()
    metrics = {
        "em": EdgeMetric().calculate_for_plan(plan_dict),
        "pi": PlanIrregularity().calculate_for_plan(plan_dict),
        "pm": PlanModulation().calculate_for_plan(plan_dict),
        "mcsv": ModulationComplexityScore().calculate_for_plan(plan_dict),
        "sas_5mm": small_aperture_score_obj.calculate_for_plan(plan_dict, x=5),
        "sas_10mm": small_aperture_score_obj.calculate_for_plan(plan_dict, x=10),
        "sas_20mm": small_aperture_score_obj.calculate_for_plan(plan_dict, x=20),
        "pa": MeanFieldArea().calculate_for_plan(plan_dict),
        "mad": MeanAsymmetryDistance().calculate_for_plan(plan_dict),
        "bjar": ApertureAreaRatioJawArea().calculate_for_plan(plan_dict),
        "asr": ApertureSubRegions().calculate_for_plan(plan_dict),
        "axjd": ApertureXJaw().calculate_for_plan(plan_dict),
        "ayjd": ApertureYJaw().calculate_for_plan(plan_dict),
        "cam": ConvertedApertureMetric().calculate_for_plan(plan_dict),
        "eam": EdgeAreaMetric().calculate_for_plan(plan_dict),
        "sport": StationParameterOptimizedRadiationTherapy().calculate_for_plan(plan_dict),
        "mlc_speed_acc": ProportionMLCSpeedAcceleration().calculate_for_plan(plan_dict),
        "mi_0_2": modulation_index_score_obj.calculate_for_plan(plan_dict, k=0.2),
        "mi_0_5": modulation_index_score_obj.calculate_for_plan(plan_dict, k=0.5),
        "mi_1_0": modulation_index_score_obj.calculate_for_plan(plan_dict, k=1.0),
        "mi_2_0": modulation_index_score_obj.calculate_for_plan(plan_dict, k=2.0),
    }
    leaf_gap_summary = LeafGap().calculate_for_plan(plan_dict)
    if isinstance(leaf_gap_summary[0], tuple):
        metrics["alg"] = (leaf_gap_summary[0][0], leaf_gap_summary[1][0])
        metrics["alg_sd"] = (leaf_gap_summary[0][1], leaf_gap_summary[1][1])
    else:
        metrics["alg"], metrics["alg_sd"] = leaf_gap_summary
    metrics.update(calculate_vcomx_supplemental_metrics(plan_dict))
    metrics.update(calculate_halcyon_dual_layer_paper_metrics(plan_dict))
    return metrics


def calculate_cyberknife_mlc_metrics(plan_dict, cyberknife_beams=None):
    """Return the six MLC-based CyberKnife metrics reported by Masi et al. (2021)."""
    if cyberknife_beams is not None:
        return calculate_cyberknife_metrics(cyberknife_beams)

    leaf_gap_summary = LeafGap().calculate_for_plan(plan_dict)
    lg_value = leaf_gap_summary[0] if isinstance(leaf_gap_summary, tuple) else leaf_gap_summary

    return {
        "mcs": ModulationComplexityScore().calculate_for_plan(plan_dict),
        "em": EdgeMetric().calculate_for_plan(plan_dict),
        "pi": PlanIrregularity().calculate_for_plan(plan_dict),
        "pm": PlanModulation().calculate_for_plan(plan_dict),
        "lg": lg_value,
        "sas10": SmallApertureScore().calculate_for_plan(plan_dict, x=10),
    }
