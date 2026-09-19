# Aurora SVMAT Lab Metric Definitions

This appendix is generated from the shared metric-definition catalog.

## `longitudinal_travel_mm` - longitudinal_travel_mm

- Group: V2 paper-style physics
- Symbol/short name: longitudinal_travel_mm
- Mathematical definition: sum_i abs(delta z_i)
- Physical meaning: Total absolute longitudinal travel reconstructed from adjacent control-point isocenter z positions.
- Unit: mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `total_rotation_deg` - total_rotation_deg

- Group: V2 paper-style physics
- Symbol/short name: total_rotation_deg
- Mathematical definition: sum_i abs(delta theta_i)
- Physical meaning: Total absolute gantry rotation reconstructed from the observed angle sequence rather than declared direction tags.
- Unit: deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `rotations` - rotations

- Group: V2 paper-style physics
- Symbol/short name: rotations
- Mathematical definition: total rotation / 360
- Physical meaning: Total gantry rotation expressed in full 360-degree turns.
- Unit: turns
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `travel_per_rotation_mm` - travel_per_rotation_mm

- Group: V2 paper-style physics
- Symbol/short name: travel_per_rotation_mm
- Mathematical definition: longitudinal travel / rotations
- Physical meaning: Average longitudinal travel per gantry rotation, derived from total travel and total rotation.
- Unit: mm/rotation
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_pitch_mean` - projection_pitch_mean

- Group: V2 paper-style physics
- Symbol/short name: projection_pitch_mean
- Mathematical definition: mean_i(abs(delta z_i) / abs(delta theta_i))
- Physical meaning: Mean projection pitch, defined as the mean of |delta z| / |delta theta| over valid adjacent control-point intervals.
- Unit: mm/deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_pitch_cv` - projection_pitch_cv

- Group: V2 paper-style physics
- Symbol/short name: projection_pitch_cv
- Mathematical definition: std(projection pitch_i) / mean(projection pitch_i)
- Physical meaning: Coefficient of variation of projection pitch. Lower values mean steadier theta-z coupling.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_mu_density_mean_proxy` - projection_mu_density_mean_proxy

- Group: V2 paper-style physics
- Symbol/short name: projection_mu_density_mean_proxy
- Mathematical definition: mean_i(abs(delta w_i) / abs(delta z_i))
- Physical meaning: Mean projection MU-density proxy, using cumulative meterset-weight change per millimeter of longitudinal travel.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_mu_density_cv_proxy` - projection_mu_density_cv_proxy

- Group: V2 paper-style physics
- Symbol/short name: projection_mu_density_cv_proxy
- Mathematical definition: std(abs(delta w_i) / abs(delta z_i)) / mean(abs(delta w_i) / abs(delta z_i))
- Physical meaning: Coefficient of variation of the projection MU-density proxy across adjacent control-point intervals.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_aperture_change_mean` - projection_aperture_change_mean

- Group: V2 paper-style physics
- Symbol/short name: projection_aperture_change_mean
- Mathematical definition: mean_i(abs(delta W_i) / abs(delta z_i)); W=sum_zip max(MLCX2-MLCX1,0) is an opening-width proxy, not area
- Physical meaning: Mean projection aperture-change rate, defined as absolute aperture-width change per millimeter of longitudinal travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_aperture_change_cv` - projection_aperture_change_cv

- Group: V2 paper-style physics
- Symbol/short name: projection_aperture_change_cv
- Mathematical definition: population_std(abs(delta W_i)/abs(delta z_i))/abs(mean(abs(delta W_i)/abs(delta z_i))); W is opening-width proxy
- Physical meaning: Coefficient of variation of the projection aperture-change rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_leaf_travel_mean` - projection_leaf_travel_mean

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_mean
- Mathematical definition: mean_i(delta L_i / abs(delta z_i)), with delta L_i summed across both MLC layers
- Physical meaning: Mean projection leaf-travel rate, defined as summed leaf travel per millimeter of longitudinal travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_leaf_travel_cv` - projection_leaf_travel_cv

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_cv
- Mathematical definition: std(delta L_i / abs(delta z_i)) / mean(delta L_i / abs(delta z_i))
- Physical meaning: Coefficient of variation of the projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_leaf_travel_mean_mlcx1` - projection_leaf_travel_mean_mlcx1

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_mean_mlcx1
- Mathematical definition: mean_i(delta L_i_MLCX1 / abs(delta z_i))
- Physical meaning: Mean projection leaf-travel rate for the MLCX1 layer only, normalized by longitudinal travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_leaf_travel_cv_mlcx1` - projection_leaf_travel_cv_mlcx1

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_cv_mlcx1
- Mathematical definition: std(delta L_i_MLCX1 / abs(delta z_i)) / mean(delta L_i_MLCX1 / abs(delta z_i))
- Physical meaning: Coefficient of variation of the MLCX1 projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_leaf_travel_mean_mlcx2` - projection_leaf_travel_mean_mlcx2

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_mean_mlcx2
- Mathematical definition: mean_i(delta L_i_MLCX2 / abs(delta z_i))
- Physical meaning: Mean projection leaf-travel rate for the MLCX2 layer only, normalized by longitudinal travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_leaf_travel_cv_mlcx2` - projection_leaf_travel_cv_mlcx2

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_cv_mlcx2
- Mathematical definition: std(delta L_i_MLCX2 / abs(delta z_i)) / mean(delta L_i_MLCX2 / abs(delta z_i))
- Physical meaning: Coefficient of variation of the MLCX2 projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `theta_z_coupling_cv` - theta_z_coupling_cv

- Group: V2 paper-style physics
- Symbol/short name: theta_z_coupling_cv
- Mathematical definition: projection_pitch_cv
- Physical meaning: Theta-z coupling variability, reported here as the same projection-pitch coefficient of variation.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `mu_z_coupling_cv_proxy` - mu_z_coupling_cv_proxy

- Group: V2 paper-style physics
- Symbol/short name: mu_z_coupling_cv_proxy
- Mathematical definition: projection_mu_density_cv_proxy
- Physical meaning: MU-z coupling variability proxy, reported as the coefficient of variation of meterset-weight density over longitudinal travel.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `mlc_z_coupling_cv` - mlc_z_coupling_cv

- Group: V2 paper-style physics
- Symbol/short name: mlc_z_coupling_cv
- Mathematical definition: projection_leaf_travel_cv
- Physical meaning: MLC-z coupling variability, reported here as the coefficient of variation of the projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `mlcx1_z_coupling_cv` - mlcx1_z_coupling_cv

- Group: V2 paper-style physics
- Symbol/short name: mlcx1_z_coupling_cv
- Mathematical definition: projection_leaf_travel_cv_mlcx1
- Physical meaning: MLCX1-z coupling variability, reported as the coefficient of variation of the MLCX1 projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `mlcx2_z_coupling_cv` - mlcx2_z_coupling_cv

- Group: V2 paper-style physics
- Symbol/short name: mlcx2_z_coupling_cv
- Mathematical definition: projection_leaf_travel_cv_mlcx2
- Physical meaning: MLCX2-z coupling variability, reported as the coefficient of variation of the MLCX2 projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `reversal_symmetry_index` - reversal_symmetry_index

- Group: V3 bidirectional symmetry
- Symbol/short name: reversal_symmetry_index
- Mathematical definition: mean over selected burden families of [1 - abs(forward_mean - backward_mean) / (abs(forward_mean) + abs(backward_mean))]
- Physical meaning: Symmetry score comparing forward and backward beam groups across matched modulation summaries. Higher values mean more balanced bidirectional modulation.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `forward_backward_metric_difference` - forward_backward_metric_difference

- Group: V3 bidirectional symmetry
- Symbol/short name: forward_backward_metric_difference
- Mathematical definition: abs(mean_forward(coupled_modulation_index) - mean_backward(coupled_modulation_index))
- Physical meaning: Absolute difference in average modulation burden between forward-moving and backward-moving beam groups.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `beam_pair_balance_index` - beam_pair_balance_index

- Group: V3 bidirectional symmetry
- Symbol/short name: beam_pair_balance_index
- Mathematical definition: 1 - abs(sum_forward(coupled_modulation_index) - sum_backward(coupled_modulation_index)) / (sum_forward + sum_backward)
- Physical meaning: Balance score comparing the total modulation burden assigned to forward and backward beam groups.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `small_opening_fraction` - small_opening_fraction

- Group: V3 small-opening burden
- Symbol/short name: small_opening_fraction
- Mathematical definition: weighted count(gap < 10 mm and gap > 0) / weighted count(gap > 0)
- Physical meaning: Weighted fraction of effective openings smaller than 10 mm.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `near_closed_fraction` - near_closed_fraction

- Group: V3 small-opening burden
- Symbol/short name: near_closed_fraction
- Mathematical definition: weighted count(gap < 2 mm and gap > 0) / weighted count(gap > 0)
- Physical meaning: Weighted fraction of effective openings smaller than 2 mm.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `effective_small_gap_burden` - effective_small_gap_burden

- Group: V3 small-opening burden
- Symbol/short name: effective_small_gap_burden
- Mathematical definition: weighted mean of max(0,1-gap/10 mm) over positive zipped-channel gap proxies; abs(delta CMW) weights, zero increment falls back to 1
- Physical meaning: Weighted severity score for narrow effective openings, with smaller openings contributing more burden.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_pitch_p95` - projection_pitch_p95

- Group: V3 local interval peaks
- Symbol/short name: projection_pitch_p95
- Mathematical definition: nearest-rank 95th percentile of projection_pitch_i
- Physical meaning: 95th percentile of projection pitch, using the nearest-rank interval summary.
- Unit: mm/deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_pitch_max` - projection_pitch_max

- Group: V3 local interval peaks
- Symbol/short name: projection_pitch_max
- Mathematical definition: max(projection_pitch_i)
- Physical meaning: Maximum projection pitch observed across adjacent control-point intervals.
- Unit: mm/deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_pitch_top3_mean` - projection_pitch_top3_mean

- Group: V3 local interval peaks
- Symbol/short name: projection_pitch_top3_mean
- Mathematical definition: mean of the three largest projection_pitch_i values
- Physical meaning: Mean of the three largest projection-pitch intervals, or all intervals if fewer than three exist.
- Unit: mm/deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_mu_density_p95_proxy` - projection_mu_density_p95_proxy

- Group: V3 local interval peaks
- Symbol/short name: projection_mu_density_p95_proxy
- Mathematical definition: nearest-rank 95th percentile of projection_mu_density_proxy_i
- Physical meaning: 95th percentile of the projection MU-density proxy, using cumulative meterset-weight change per millimeter.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_mu_density_max_proxy` - projection_mu_density_max_proxy

- Group: V3 local interval peaks
- Symbol/short name: projection_mu_density_max_proxy
- Mathematical definition: max(projection_mu_density_proxy_i)
- Physical meaning: Maximum projection MU-density proxy observed across adjacent control-point intervals.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_mu_density_top3_mean_proxy` - projection_mu_density_top3_mean_proxy

- Group: V3 local interval peaks
- Symbol/short name: projection_mu_density_top3_mean_proxy
- Mathematical definition: mean of the three largest projection_mu_density_proxy_i values
- Physical meaning: Mean of the three largest projection MU-density proxy values.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_aperture_change_p95` - projection_aperture_change_p95

- Group: V3 local interval peaks
- Symbol/short name: projection_aperture_change_p95
- Mathematical definition: nearest-rank 95th percentile of projection_aperture_change_i
- Physical meaning: 95th percentile of the projection aperture-change rate.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_aperture_change_max` - projection_aperture_change_max

- Group: V3 local interval peaks
- Symbol/short name: projection_aperture_change_max
- Mathematical definition: max(projection_aperture_change_i)
- Physical meaning: Maximum projection aperture-change rate observed across adjacent control-point intervals.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_aperture_change_top3_mean` - projection_aperture_change_top3_mean

- Group: V3 local interval peaks
- Symbol/short name: projection_aperture_change_top3_mean
- Mathematical definition: mean of the three largest projection_aperture_change_i values
- Physical meaning: Mean of the three largest projection aperture-change rates.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_leaf_travel_p95` - projection_leaf_travel_p95

- Group: V3 local interval peaks
- Symbol/short name: projection_leaf_travel_p95
- Mathematical definition: nearest-rank 95th percentile of projection_leaf_travel_i
- Physical meaning: 95th percentile of the projection leaf-travel rate across both layers.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_leaf_travel_max` - projection_leaf_travel_max

- Group: V3 local interval peaks
- Symbol/short name: projection_leaf_travel_max
- Mathematical definition: max(projection_leaf_travel_i)
- Physical meaning: Maximum projection leaf-travel rate across both layers.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `projection_leaf_travel_top3_mean` - projection_leaf_travel_top3_mean

- Group: V3 local interval peaks
- Symbol/short name: projection_leaf_travel_top3_mean
- Mathematical definition: mean of the three largest projection_leaf_travel_i values
- Physical meaning: Mean of the three largest projection leaf-travel rates across both layers.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `head_mu_density_mean_proxy` - head_mu_density_mean_proxy

- Group: V3 axial regions
- Symbol/short name: head_mu_density_mean_proxy
- Mathematical definition: mean(projection_mu_density_proxy_i) over head-third intervals
- Physical meaning: Mean projection MU-density proxy inside the head longitudinal third of the covered z-range.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `head_mu_density_cv_proxy` - head_mu_density_cv_proxy

- Group: V3 axial regions
- Symbol/short name: head_mu_density_cv_proxy
- Mathematical definition: CV(projection_mu_density_proxy_i) over head-third intervals
- Physical meaning: Coefficient of variation of the projection MU-density proxy inside the head longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `head_aperture_change_mean` - head_aperture_change_mean

- Group: V3 axial regions
- Symbol/short name: head_aperture_change_mean
- Mathematical definition: mean(projection_aperture_change_i) over head-third intervals
- Physical meaning: Mean projection aperture-change rate inside the head longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `head_aperture_change_cv` - head_aperture_change_cv

- Group: V3 axial regions
- Symbol/short name: head_aperture_change_cv
- Mathematical definition: CV(projection_aperture_change_i) over head-third intervals
- Physical meaning: Coefficient of variation of the projection aperture-change rate inside the head longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `head_leaf_travel_mean` - head_leaf_travel_mean

- Group: V3 axial regions
- Symbol/short name: head_leaf_travel_mean
- Mathematical definition: mean(projection_leaf_travel_i) over head-third intervals
- Physical meaning: Mean projection leaf-travel rate inside the head longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `head_leaf_travel_cv` - head_leaf_travel_cv

- Group: V3 axial regions
- Symbol/short name: head_leaf_travel_cv
- Mathematical definition: CV(projection_leaf_travel_i) over head-third intervals
- Physical meaning: Coefficient of variation of the projection leaf-travel rate inside the head longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `mid_mu_density_mean_proxy` - mid_mu_density_mean_proxy

- Group: V3 axial regions
- Symbol/short name: mid_mu_density_mean_proxy
- Mathematical definition: mean(projection_mu_density_proxy_i) over mid-third intervals
- Physical meaning: Mean projection MU-density proxy inside the mid longitudinal third of the covered z-range.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `mid_mu_density_cv_proxy` - mid_mu_density_cv_proxy

- Group: V3 axial regions
- Symbol/short name: mid_mu_density_cv_proxy
- Mathematical definition: CV(projection_mu_density_proxy_i) over mid-third intervals
- Physical meaning: Coefficient of variation of the projection MU-density proxy inside the mid longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `mid_aperture_change_mean` - mid_aperture_change_mean

- Group: V3 axial regions
- Symbol/short name: mid_aperture_change_mean
- Mathematical definition: mean(projection_aperture_change_i) over mid-third intervals
- Physical meaning: Mean projection aperture-change rate inside the mid longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `mid_aperture_change_cv` - mid_aperture_change_cv

- Group: V3 axial regions
- Symbol/short name: mid_aperture_change_cv
- Mathematical definition: CV(projection_aperture_change_i) over mid-third intervals
- Physical meaning: Coefficient of variation of the projection aperture-change rate inside the mid longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `mid_leaf_travel_mean` - mid_leaf_travel_mean

- Group: V3 axial regions
- Symbol/short name: mid_leaf_travel_mean
- Mathematical definition: mean(projection_leaf_travel_i) over mid-third intervals
- Physical meaning: Mean projection leaf-travel rate inside the mid longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `mid_leaf_travel_cv` - mid_leaf_travel_cv

- Group: V3 axial regions
- Symbol/short name: mid_leaf_travel_cv
- Mathematical definition: CV(projection_leaf_travel_i) over mid-third intervals
- Physical meaning: Coefficient of variation of the projection leaf-travel rate inside the mid longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `tail_mu_density_mean_proxy` - tail_mu_density_mean_proxy

- Group: V3 axial regions
- Symbol/short name: tail_mu_density_mean_proxy
- Mathematical definition: mean(projection_mu_density_proxy_i) over tail-third intervals
- Physical meaning: Mean projection MU-density proxy inside the tail longitudinal third of the covered z-range.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `tail_mu_density_cv_proxy` - tail_mu_density_cv_proxy

- Group: V3 axial regions
- Symbol/short name: tail_mu_density_cv_proxy
- Mathematical definition: CV(projection_mu_density_proxy_i) over tail-third intervals
- Physical meaning: Coefficient of variation of the projection MU-density proxy inside the tail longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `tail_aperture_change_mean` - tail_aperture_change_mean

- Group: V3 axial regions
- Symbol/short name: tail_aperture_change_mean
- Mathematical definition: mean(projection_aperture_change_i) over tail-third intervals
- Physical meaning: Mean projection aperture-change rate inside the tail longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `tail_aperture_change_cv` - tail_aperture_change_cv

- Group: V3 axial regions
- Symbol/short name: tail_aperture_change_cv
- Mathematical definition: CV(projection_aperture_change_i) over tail-third intervals
- Physical meaning: Coefficient of variation of the projection aperture-change rate inside the tail longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `tail_leaf_travel_mean` - tail_leaf_travel_mean

- Group: V3 axial regions
- Symbol/short name: tail_leaf_travel_mean
- Mathematical definition: mean(projection_leaf_travel_i) over tail-third intervals
- Physical meaning: Mean projection leaf-travel rate inside the tail longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `tail_leaf_travel_cv` - tail_leaf_travel_cv

- Group: V3 axial regions
- Symbol/short name: tail_leaf_travel_cv
- Mathematical definition: CV(projection_leaf_travel_i) over tail-third intervals
- Physical meaning: Coefficient of variation of the projection leaf-travel rate inside the tail longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `layer_imbalance_index` - layer_imbalance_index

- Group: V3 dual-layer coordination
- Symbol/short name: layer_imbalance_index
- Mathematical definition: abs(mean(leaf_travel_i_MLCX1) - mean(leaf_travel_i_MLCX2)) / (abs(mean_MLCX1) + abs(mean_MLCX2))
- Physical meaning: Normalized difference between the mean MLCX1 and MLCX2 leaf-travel rates.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `layer_correlation_index` - layer_correlation_index

- Group: V3 dual-layer coordination
- Symbol/short name: layer_correlation_index
- Mathematical definition: correlation(projection_leaf_travel_i_MLCX1, projection_leaf_travel_i_MLCX2)
- Physical meaning: Correlation between the interval-by-interval MLCX1 and MLCX2 leaf-travel rates.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `x1_x2_aperture_disparity` - x1_x2_aperture_disparity

- Group: V3 dual-layer coordination
- Symbol/short name: x1_x2_aperture_disparity
- Mathematical definition: mean over control points of abs(sum|MLCX1| - sum|MLCX2|) / (sum|MLCX1| + sum|MLCX2|)
- Physical meaning: Surrogate side-opening disparity, computed from the relative difference in MLCX1 and MLCX2 position magnitudes.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `x1_x2_leaf_travel_ratio` - x1_x2_leaf_travel_ratio

- Group: V3 dual-layer coordination
- Symbol/short name: x1_x2_leaf_travel_ratio
- Mathematical definition: mean(projection_leaf_travel_i_MLCX1) / mean(projection_leaf_travel_i_MLCX2)
- Physical meaning: Ratio of mean MLCX1 leaf-travel rate to mean MLCX2 leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

## `axial_travel_mm` - axial_travel_mm

- Group: Legacy engineering
- Symbol/short name: axial_travel_mm
- Mathematical definition: sum_i abs(delta z_i)
- Physical meaning: Legacy engineering metric for total absolute axial travel reconstructed from adjacent control-point isocenter z positions.
- Unit: mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

## `gantry_rotation_deg` - gantry_rotation_deg

- Group: Legacy engineering
- Symbol/short name: gantry_rotation_deg
- Mathematical definition: sum_i abs(delta theta_i)
- Physical meaning: Legacy engineering metric for total absolute gantry rotation reconstructed from the observed angle sequence.
- Unit: deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

## `mm_per_deg` - mm_per_deg

- Group: Legacy engineering
- Symbol/short name: mm_per_deg
- Mathematical definition: axial travel / total rotation
- Physical meaning: Legacy engineering metric for total axial travel divided by total gantry rotation.
- Unit: mm/deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

## `mm_per_rotation` - mm_per_rotation

- Group: Legacy engineering
- Symbol/short name: mm_per_rotation
- Mathematical definition: axial travel / (total rotation / 360)
- Physical meaning: Legacy engineering metric for total axial travel per full 360-degree gantry rotation.
- Unit: mm/rotation
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

## `pitch_consistency` - pitch_consistency

- Group: Legacy engineering
- Symbol/short name: pitch_consistency
- Mathematical definition: std(abs(delta z_i) / abs(delta theta_i)) / mean(abs(delta z_i) / abs(delta theta_i))
- Physical meaning: Legacy engineering pitch variability metric, equivalent to the coefficient of variation of interval pitch.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

## `mu_per_mm` - mu_per_mm

- Group: Legacy engineering
- Symbol/short name: mu_per_mm
- Mathematical definition: MU_total / axial travel
- Physical meaning: Legacy engineering MU density per millimeter of axial travel. Uses explicit total MU when available, otherwise cumulative meterset-weight span as a transparent proxy.
- Unit: MU/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

## `aperture_change_per_mm` - aperture_change_per_mm

- Group: Legacy engineering
- Symbol/short name: aperture_change_per_mm
- Mathematical definition: sum_i abs(delta W_i)/sum_i abs(delta z_i), retaining dz>0; W is summed positive opening width, not area
- Physical meaning: Legacy engineering metric for total absolute aperture-width change normalized by total axial travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

## `leaf_travel_per_mm` - leaf_travel_per_mm

- Group: Legacy engineering
- Symbol/short name: leaf_travel_per_mm
- Mathematical definition: sum_i delta L_i / sum_i abs(delta z_i)
- Physical meaning: Legacy engineering metric for total absolute leaf travel normalized by total axial travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

## `coupled_modulation_index` - coupled_modulation_index

- Group: Legacy engineering
- Symbol/short name: coupled_modulation_index
- Mathematical definition: mean(x/(1+x)) over available aperture-change/mm, leaf-travel/mm, MU-density CV and pitch CV; equal component weights
- Physical meaning: Legacy engineering aggregate of normalized aperture change, leaf travel, MU-density variability, and pitch variability.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.
