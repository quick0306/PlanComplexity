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
from halcyon_dual_layer_metrics import calculate_halcyon_dual_layer_metrics_with_warnings
from vcomx_vmat_metrics import (
    calculate_vcomx_supplemental_metrics,
    supplemental_metric_weight_warnings,
)


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


def calculate_core_metrics(plan_dict, *, full_precision=False):
    metrics, _ = calculate_core_metrics_with_warnings(plan_dict, full_precision=full_precision)
    return metrics


def calculate_core_metrics_with_warnings(plan_dict, *, full_precision=False):
    small_aperture_score_obj = SmallApertureScore(full_precision=full_precision)
    modulation_index_score_obj = ModulationIndexScore(full_precision=full_precision)
    warnings = []
    sas_5mm, sas_5mm_warnings = _calculate_with_warnings(
        small_aperture_score_obj, plan_dict, x=5
    )
    sas_10mm, sas_10mm_warnings = _calculate_with_warnings(
        small_aperture_score_obj, plan_dict, x=10
    )
    sas_20mm, sas_20mm_warnings = _calculate_with_warnings(
        small_aperture_score_obj, plan_dict, x=20
    )
    mad, mad_warnings = _calculate_with_warnings(MeanAsymmetryDistance(full_precision=full_precision), plan_dict)
    warnings.extend(sas_5mm_warnings + sas_10mm_warnings + sas_20mm_warnings + mad_warnings)
    metrics = {
        "em": EdgeMetric(full_precision=full_precision).calculate_for_plan(plan_dict),
        "pi": PlanIrregularity(full_precision=full_precision).calculate_for_plan(plan_dict),
        "pm": PlanModulation(full_precision=full_precision).calculate_for_plan(plan_dict),
        "mcsv": ModulationComplexityScore(full_precision=full_precision).calculate_for_plan(plan_dict),
        "sas_5mm": sas_5mm,
        "sas_10mm": sas_10mm,
        "sas_20mm": sas_20mm,
        "pa": MeanFieldArea(full_precision=full_precision).calculate_for_plan(plan_dict),
        "mad": mad,
        "bjar": ApertureAreaRatioJawArea(full_precision=full_precision).calculate_for_plan(plan_dict),
        "asr": ApertureSubRegions(full_precision=full_precision).calculate_for_plan(plan_dict),
        "axjd": ApertureXJaw(full_precision=full_precision).calculate_for_plan(plan_dict),
        "ayjd": ApertureYJaw(full_precision=full_precision).calculate_for_plan(plan_dict),
        "cam": ConvertedApertureMetric(full_precision=full_precision).calculate_for_plan(plan_dict),
        "eam": EdgeAreaMetric(full_precision=full_precision).calculate_for_plan(plan_dict),
        "sport": StationParameterOptimizedRadiationTherapy(full_precision=full_precision).calculate_for_plan(plan_dict),
        "mlc_speed_acc": ProportionMLCSpeedAcceleration(full_precision=full_precision).calculate_for_plan(plan_dict),
        "mi_0_2": modulation_index_score_obj.calculate_for_plan(plan_dict, k=0.2),
        "mi_0_5": modulation_index_score_obj.calculate_for_plan(plan_dict, k=0.5),
        "mi_1_0": modulation_index_score_obj.calculate_for_plan(plan_dict, k=1.0),
        "mi_2_0": modulation_index_score_obj.calculate_for_plan(plan_dict, k=2.0),
    }
    leaf_gap_summary, leaf_gap_warnings = _calculate_with_warnings(LeafGap(full_precision=full_precision), plan_dict)
    warnings.extend(leaf_gap_warnings)
    if isinstance(leaf_gap_summary[0], tuple):
        metrics["alg"] = (leaf_gap_summary[0][0], leaf_gap_summary[1][0])
        metrics["alg_sd"] = (leaf_gap_summary[0][1], leaf_gap_summary[1][1])
    else:
        metrics["alg"], metrics["alg_sd"] = leaf_gap_summary
    metrics.update(calculate_vcomx_supplemental_metrics(plan_dict, full_precision=full_precision))
    warnings.extend(supplemental_metric_weight_warnings(plan_dict))
    halcyon_metrics, halcyon_warnings = calculate_halcyon_dual_layer_metrics_with_warnings(
        plan_dict, full_precision=full_precision
    )
    metrics.update(halcyon_metrics)
    warnings.extend(halcyon_warnings)
    return metrics, list(dict.fromkeys(warnings))


def _calculate_with_warnings(metric, plan_dict, **kwargs):
    warning_aware = getattr(metric, "calculate_for_plan_with_warnings", None)
    if callable(warning_aware):
        return warning_aware(plan_dict, **kwargs)
    return metric.calculate_for_plan(plan_dict, **kwargs), []


def calculate_cyberknife_mlc_metrics(plan_dict, cyberknife_beams=None, *, full_precision=False):
    """Return the six MLC-based CyberKnife metrics reported by Masi et al. (2021)."""
    if cyberknife_beams is not None:
        return calculate_cyberknife_metrics(cyberknife_beams, full_precision=full_precision)

    leaf_gap_summary = LeafGap(full_precision=full_precision).calculate_for_plan(plan_dict)
    lg_value = leaf_gap_summary[0] if isinstance(leaf_gap_summary, tuple) else leaf_gap_summary

    return {
        "mcs": ModulationComplexityScore(full_precision=full_precision).calculate_for_plan(plan_dict),
        "em": EdgeMetric(full_precision=full_precision).calculate_for_plan(plan_dict),
        "pi": PlanIrregularity(full_precision=full_precision).calculate_for_plan(plan_dict),
        "pm": PlanModulation(full_precision=full_precision).calculate_for_plan(plan_dict),
        "lg": lg_value,
        "sas10": SmallApertureScore(full_precision=full_precision).calculate_for_plan(plan_dict, x=10),
    }
