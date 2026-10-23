from __future__ import annotations

from .metrics import AXIAL_REGIONS


METRIC_NOTES: dict[str, str] = {
    "mean_ba": "Open-aperture conditional delivered-weight mean physical area with the 1 mm closure mask after intersecting both MLC layers and clipping to X/Y jaws using real leaf boundaries; closed endpoints excluded and weights renormalized.",
    "mean_bi": "Open-aperture conditional delivered-weight mean P squared / (4 pi A), using exact physical union perimeter; closed endpoints excluded and weights renormalized; unavailable only when no valid open aperture remains.",
    "mean_ca": "Open-aperture conditional delivered-weight mean P/A in inverse millimeters, not circularity; closed endpoints excluded and weights renormalized.",
    "mean_sas5": "Open-aperture conditional delivered-weight mean fraction of open physical sub-strips (gap > 1+1e-8 mm) with gap strictly below 5 mm; equal sub-strip counts; closed leaves and fully closed endpoints excluded.",
    "mean_sas10": "Open-aperture conditional delivered-weight mean fraction of open physical sub-strips (gap > 1+1e-8 mm) with gap strictly below 10 mm; equal sub-strip counts; closed leaves and fully closed endpoints excluded.",
    "mean_mcs_aurora": "Open-aperture conditional delivered-weight mean AAV times open-gap LSV (gap > 1+1e-8 mm). AAV uses beam maxima of clipped sub-strip areas. Closed endpoints excluded; weights renormalized. Adapted MCS, not exact McNiven MCS.",
    "mcs_complexity_aurora": "One minus the Aurora physical-aperture adapted MCS; larger values indicate greater modulation complexity under this version-specific definition.",
    "longitudinal_travel_mm": "Total absolute longitudinal travel reconstructed from adjacent control-point isocenter z positions.",
    "total_rotation_deg": "Total absolute gantry rotation reconstructed from the observed angle sequence rather than declared direction tags.",
    "rotations": "Total gantry rotation expressed in full 360-degree turns.",
    "travel_per_rotation_mm": "Average longitudinal travel per gantry rotation, derived from total travel and total rotation.",
    "projection_pitch_mean": "Mean projection pitch, defined as the mean of |delta z| / |delta theta| over valid adjacent control-point intervals.",
    "projection_pitch_cv": "Coefficient of variation of projection pitch. Lower values mean steadier theta-z coupling.",
    "projection_mu_density_mean_proxy": "Mean projection MU-density proxy, using cumulative meterset-weight change per millimeter of longitudinal travel.",
    "projection_mu_density_cv_proxy": "Coefficient of variation of the projection MU-density proxy across adjacent control-point intervals.",
    "projection_aperture_change_mean": 'Mean absolute change in physical dual-layer intersection area per millimeter of couch travel, mm^2/mm; the 1 mm closure mask is shared with SAS and MCS.',
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
    "small_opening_fraction": 'Open-aperture delivered-MU mean of the fraction of effective sub-strips with 1+1e-8 < gap < 10 mm; exactly the same value as mean_sas10.',
    "near_closed_fraction": 'Open-aperture delivered-MU mean fraction of effective sub-strips with 1+1e-8 < gap < 2 mm; the same closure mask and denominator as SAS.',
    "effective_small_gap_burden": 'Open-aperture delivered-MU mean of the within-CP average max(0,1-gap/10 mm) over open effective sub-strips; no zero-MU fallback.',
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
    "x1_x2_aperture_disparity": 'Open-aperture delivered-MU mean abs(A1-A2)/(A1+A2); native physical layer areas use the same Y coverage, jaws and 1 mm closure mask.',
    "x1_x2_leaf_travel_ratio": "Ratio of mean MLCX1 leaf-travel rate to mean MLCX2 leaf-travel rate.",
    "axial_travel_mm": "Legacy engineering metric for total absolute axial travel reconstructed from adjacent control-point isocenter z positions.",
    "gantry_rotation_deg": "Legacy engineering metric for total absolute gantry rotation reconstructed from the observed angle sequence.",
    "mm_per_deg": "Legacy engineering metric for total axial travel divided by total gantry rotation.",
    "mm_per_rotation": "Legacy engineering metric for total axial travel per full 360-degree gantry rotation.",
    "pitch_consistency": "Legacy engineering pitch variability metric, equivalent to the coefficient of variation of interval pitch.",
    "mu_per_mm": 'Absolute DICOM BeamMeterset MU summed across beams, divided by total axial travel. Missing or invalid beam MU yields unavailable, never a relative-weight proxy.',
    "aperture_change_per_mm": 'Total absolute effective area change divided by total positive couch travel, mm^2/mm; physical layers are intersected on their boundary grid and clipped to jaws.',
    "leaf_travel_per_mm": "Legacy engineering metric for total absolute leaf travel normalized by total axial travel.",
    "coupled_modulation_index": 'Equal mean of x/(1+x) for area-change rate scaled by 1 mm^2/mm, leaf-travel rate scaled by 1 mm/mm, and the two CVs. Required physical area geometry must be valid.',
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
