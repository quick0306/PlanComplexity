from __future__ import annotations

from .metrics import AXIAL_REGIONS


METRIC_NOTES: dict[str, str] = {
    "longitudinal_travel_mm": "Total absolute longitudinal travel reconstructed from adjacent control-point isocenter z positions.",
    "total_rotation_deg": "Total absolute gantry rotation reconstructed from the observed angle sequence rather than declared direction tags.",
    "rotations": "Total gantry rotation expressed in full 360-degree turns.",
    "travel_per_rotation_mm": "Average longitudinal travel per gantry rotation, derived from total travel and total rotation.",
    "projection_pitch_mean": "Mean projection pitch, defined as the mean of |delta z| / |delta theta| over valid adjacent control-point intervals.",
    "projection_pitch_cv": "Coefficient of variation of projection pitch. Lower values mean steadier theta-z coupling.",
    "projection_mu_density_mean_proxy": "Mean projection MU-density proxy, using cumulative meterset-weight change per millimeter of longitudinal travel.",
    "projection_mu_density_cv_proxy": "Coefficient of variation of the projection MU-density proxy across adjacent control-point intervals.",
    "projection_aperture_change_mean": "Mean projection aperture-change rate, defined as absolute aperture-width change per millimeter of longitudinal travel.",
    "projection_aperture_change_cv": "Coefficient of variation of the projection aperture-change rate.",
    "projection_leaf_travel_mean": "Mean projection leaf-travel rate, defined as summed leaf travel per millimeter of longitudinal travel.",
    "projection_leaf_travel_cv": "Coefficient of variation of the projection leaf-travel rate.",
    "projection_leaf_travel_mean_mlcx1": "Mean projection leaf-travel rate for the MLCX1 layer only, normalized by longitudinal travel.",
    "projection_leaf_travel_cv_mlcx1": "Coefficient of variation of the MLCX1 projection leaf-travel rate.",
    "projection_leaf_travel_mean_mlcx2": "Mean projection leaf-travel rate for the MLCX2 layer only, normalized by longitudinal travel.",
    "projection_leaf_travel_cv_mlcx2": "Coefficient of variation of the MLCX2 projection leaf-travel rate.",
    "theta_z_coupling_cv": "Theta-z coupling variability, reported here as the same projection-pitch coefficient of variation.",
    "mu_z_coupling_cv_proxy": "MU-z coupling variability proxy, reported as the coefficient of variation of meterset-weight density over longitudinal travel.",
    "mlc_z_coupling_cv": "MLC-z coupling variability, reported here as the coefficient of variation of the projection leaf-travel rate.",
    "mlcx1_z_coupling_cv": "MLCX1-z coupling variability, reported as the coefficient of variation of the MLCX1 projection leaf-travel rate.",
    "mlcx2_z_coupling_cv": "MLCX2-z coupling variability, reported as the coefficient of variation of the MLCX2 projection leaf-travel rate.",
    "reversal_symmetry_index": "Symmetry score comparing forward and backward beam groups across matched modulation summaries. Higher values mean more balanced bidirectional modulation.",
    "forward_backward_metric_difference": "Absolute difference in average modulation burden between forward-moving and backward-moving beam groups.",
    "beam_pair_balance_index": "Balance score comparing the total modulation burden assigned to forward and backward beam groups.",
    "small_opening_fraction": "Weighted fraction of effective openings smaller than 10 mm.",
    "near_closed_fraction": "Weighted fraction of effective openings smaller than 2 mm.",
    "effective_small_gap_burden": "Weighted severity score for narrow effective openings, with smaller openings contributing more burden.",
    "projection_pitch_p95": "95th percentile of projection pitch, using the nearest-rank interval summary.",
    "projection_pitch_max": "Maximum projection pitch observed across adjacent control-point intervals.",
    "projection_pitch_top3_mean": "Mean of the three largest projection-pitch intervals, or all intervals if fewer than three exist.",
    "projection_mu_density_p95_proxy": "95th percentile of the projection MU-density proxy, using cumulative meterset-weight change per millimeter.",
    "projection_mu_density_max_proxy": "Maximum projection MU-density proxy observed across adjacent control-point intervals.",
    "projection_mu_density_top3_mean_proxy": "Mean of the three largest projection MU-density proxy values.",
    "projection_aperture_change_p95": "95th percentile of the projection aperture-change rate.",
    "projection_aperture_change_max": "Maximum projection aperture-change rate observed across adjacent control-point intervals.",
    "projection_aperture_change_top3_mean": "Mean of the three largest projection aperture-change rates.",
    "projection_leaf_travel_p95": "95th percentile of the projection leaf-travel rate across both layers.",
    "projection_leaf_travel_max": "Maximum projection leaf-travel rate across both layers.",
    "projection_leaf_travel_top3_mean": "Mean of the three largest projection leaf-travel rates across both layers.",
    "layer_imbalance_index": "Normalized difference between the mean MLCX1 and MLCX2 leaf-travel rates.",
    "layer_correlation_index": "Correlation between the interval-by-interval MLCX1 and MLCX2 leaf-travel rates.",
    "x1_x2_aperture_disparity": "Surrogate side-opening disparity, computed from the relative difference in MLCX1 and MLCX2 position magnitudes.",
    "x1_x2_leaf_travel_ratio": "Ratio of mean MLCX1 leaf-travel rate to mean MLCX2 leaf-travel rate.",
    "axial_travel_mm": "Legacy engineering metric for total absolute axial travel reconstructed from adjacent control-point isocenter z positions.",
    "gantry_rotation_deg": "Legacy engineering metric for total absolute gantry rotation reconstructed from the observed angle sequence.",
    "mm_per_deg": "Legacy engineering metric for total axial travel divided by total gantry rotation.",
    "mm_per_rotation": "Legacy engineering metric for total axial travel per full 360-degree gantry rotation.",
    "pitch_consistency": "Legacy engineering pitch variability metric, equivalent to the coefficient of variation of interval pitch.",
    "mu_per_mm": "Legacy engineering MU density per millimeter of axial travel. Uses explicit total MU when available, otherwise cumulative meterset-weight span as a transparent proxy.",
    "aperture_change_per_mm": "Legacy engineering metric for total absolute aperture-width change normalized by total axial travel.",
    "leaf_travel_per_mm": "Legacy engineering metric for total absolute leaf travel normalized by total axial travel.",
    "coupled_modulation_index": "Legacy engineering aggregate of normalized aperture change, leaf travel, MU-density variability, and pitch variability.",
}


for region_name in AXIAL_REGIONS:
    region_title = region_name.capitalize()
    METRIC_NOTES[f"{region_name}_mu_density_mean_proxy"] = (
        f"Mean projection MU-density proxy inside the {region_name} longitudinal third of the covered z-range."
    )
    METRIC_NOTES[f"{region_name}_mu_density_cv_proxy"] = (
        f"Coefficient of variation of the projection MU-density proxy inside the {region_name} longitudinal third."
    )
    METRIC_NOTES[f"{region_name}_aperture_change_mean"] = (
        f"Mean projection aperture-change rate inside the {region_title.lower()} longitudinal third of the covered z-range."
    )
    METRIC_NOTES[f"{region_name}_aperture_change_cv"] = (
        f"Coefficient of variation of the projection aperture-change rate inside the {region_name} longitudinal third."
    )
    METRIC_NOTES[f"{region_name}_leaf_travel_mean"] = (
        f"Mean projection leaf-travel rate inside the {region_name} longitudinal third of the covered z-range."
    )
    METRIC_NOTES[f"{region_name}_leaf_travel_cv"] = (
        f"Coefficient of variation of the projection leaf-travel rate inside the {region_name} longitudinal third."
    )


def get_metric_notes(metric_names: list[str] | tuple[str, ...] | None = None) -> dict[str, str]:
    if metric_names is None:
        return dict(METRIC_NOTES)
    return {metric_name: METRIC_NOTES[metric_name] for metric_name in metric_names if metric_name in METRIC_NOTES}
