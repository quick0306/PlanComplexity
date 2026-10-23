"""Hand calculations for the V5 migration; no clinical fixtures required."""
from copy import deepcopy
import math

import pytest

from aurora_svmat_lab.models import AuroraBeam, AuroraControlPoint, AuroraAnalysisResult
from aurora_svmat_lab.metrics import calculate_beam_metrics, calculate_plan_metrics
from aurora_svmat_lab.physical_aperture import summarize_apertures, CLOSURE_MM


def physical_beam(gaps=(20.0, 4.0), weights=(0.0, .25, 1.0), mu=100.0):
    # Two distal rows vs one proximal row deliberately have unequal bank counts.
    cps = [AuroraControlPoint(
        control_point_index=i, cumulative_meterset_weight=w, axial_position_mm=10.0*i,
        gantry_angle_deg=30.0*i, jaw_x=(-100.0,100.0), jaw_y=(-10.0,10.0),
        mlc_x1_positions_mm=(-g/2,-g/2,g/2,g/2),
        mlc_x2_positions_mm=(-g/2,g/2),
    ) for i,(g,w) in enumerate(zip((20.0,)+tuple(gaps),weights))]
    return AuroraBeam(control_points=cps, leaf_boundaries_mlcx1=(-10.0,0.0,10.0),
                      leaf_boundaries_mlcx2=(-10.0,10.0),beam_meterset_mu=mu)


def test_physical_area_rate_and_exports_share_the_same_series():
    from aurora_svmat_lab.export import export_projection_rows, export_trajectory_rows
    beam=physical_beam()
    values=calculate_beam_metrics(beam)
    # A=(400,400,80), rates=(0,32), total variation/travel=320/20.
    assert values["projection_aperture_change_mean"] == 16.0
    assert values["aperture_change_per_mm"] == 16.0
    result=AuroraAnalysisResult(beams=[beam])
    rows=export_projection_rows([result])
    assert [r["projection_aperture_change"] for r in rows] == [0.0,32.0]
    assert [r["effective_aperture_area_mm2"] for r in export_trajectory_rows([result])] == [400.,400.,80.]
    assert all(r["aperture_closure_threshold_mm"] == CLOSURE_MM for r in rows)


def test_common_closure_sas_and_exact_mcs_complement():
    beam=physical_beam(gaps=(1.0,4.0))
    v=calculate_beam_metrics(beam)
    assert v["mean_ba"] == 80.0
    assert v["small_opening_fraction"] == v["mean_sas10"] == 1.0
    assert v["mean_sas5"] == 1.0
    assert v["near_closed_fraction"] == 0.0
    assert v["effective_small_gap_burden"] == pytest.approx(.6)
    assert v["mean_ca"] == pytest.approx(.6)
    assert v["mean_bi"] == pytest.approx(7.2/math.pi)
    assert v["mcs_complexity_aurora"] == 1-v["mean_mcs_aurora"] == 0.0


def test_zero_mu_interval_does_not_create_small_gap_weight_or_envelope():
    beam=physical_beam(gaps=(1.5,20.0),weights=(0.0,0.0,1.0))
    v=calculate_beam_metrics(beam)
    assert v["mean_ba"] == 400.0
    assert v["small_opening_fraction"] == v["near_closed_fraction"] == 0.0
    assert v["effective_small_gap_burden"] == 0.0
    assert v["mean_mcs_aurora"] == 1.0


def test_sas_is_cp_fraction_not_equivalent_width_or_pooled_pair_ratio():
    beam=physical_beam(gaps=(20.0,20.0),weights=(0.0,.5,1.0))
    beam.control_points[1].mlc_x1_positions_mm=(0.0,0.0,4.0,20.0)
    beam.control_points[2].mlc_x1_positions_mm=(0.0,0.0,20.0,0.0)
    for cp in beam.control_points:
        cp.mlc_x2_positions_mm=(-50.0,50.0)
    v=calculate_beam_metrics(beam)
    # CP1 has one narrow row among two; CP2 has none among one: .5*.5=.25.
    assert v["mean_sas5"] == v["mean_sas10"] == v["small_opening_fraction"] == .25


def test_native_area_disparity_and_all_aperture_metrics_are_translation_invariant():
    beam=physical_beam(gaps=(20.0,20.0))
    for cp in beam.control_points:
        cp.mlc_x2_positions_mm=(-5.0,5.0)
    before=calculate_beam_metrics(beam)
    assert before["x1_x2_aperture_disparity"] == pytest.approx(1/3)
    for cp in beam.control_points:
        cp.mlc_x1_positions_mm=tuple(x+37 for x in cp.mlc_x1_positions_mm)
        cp.mlc_x2_positions_mm=tuple(x+37 for x in cp.mlc_x2_positions_mm)
        cp.jaw_x=tuple(x+37 for x in cp.jaw_x)
    after=calculate_beam_metrics(beam)
    for key in ["mean_ba","mean_bi","mean_ca","mean_sas5","mean_sas10",
                "mean_mcs_aurora","small_opening_fraction","x1_x2_aperture_disparity",
                "projection_aperture_change_mean"]:
        assert after[key] == pytest.approx(before[key])


def test_open_mu_pool_is_common_across_beams_and_missing_mu_fallback():
    a=physical_beam(gaps=(20.,20.),mu=100.)
    b=physical_beam(gaps=(4.,4.),mu=300.)
    v=calculate_plan_metrics([a,b])
    assert v["small_opening_fraction"] == v["mean_sas10"] == .75
    assert v["mean_sas5"] == .75
    assert v["effective_small_gap_burden"] == pytest.approx(.45)
    a.beam_meterset_mu=None
    v,warnings=summarize_apertures([a,b])
    assert v["small_opening_fraction"] == v["mean_sas10"] == .5
    assert any("RELATIVE_WEIGHTS" in w for w in warnings)


def test_invalid_beam_prevents_partial_geometry_and_mutable_inputs_are_not_cached():
    good=physical_beam()
    first=calculate_beam_metrics(good)
    good.control_points[2].mlc_x2_positions_mm=(-1.5,1.5)
    assert calculate_beam_metrics(good)["mean_ba"] != first["mean_ba"]
    bad=deepcopy(good)
    bad.leaf_boundaries_mlcx2=()
    values=calculate_plan_metrics([good,bad])
    for key in ["mean_ba","small_opening_fraction","projection_aperture_change_mean",
                "head_aperture_change_mean","x1_x2_aperture_disparity",
                "coupled_modulation_index","reversal_symmetry_index"]:
        assert values[key] is None
    assert values["total_rotation_deg"] == 120.0


def test_absolute_mu_density_uses_parser_field_and_never_relative_span():
    beam=physical_beam(mu=200.0)
    assert calculate_beam_metrics(beam)["mu_per_mm"] == 10.0
    beam.beam_meterset_mu=None
    assert calculate_beam_metrics(beam)["mu_per_mm"] is None
    assert calculate_plan_metrics([physical_beam(),beam])["mu_per_mm"] is None


def test_thresholds_and_all_closed_mean_states():
    beam=physical_beam(gaps=(5.,10.))
    v=calculate_beam_metrics(beam)
    assert v["mean_sas5"] == 0.0
    assert v["mean_sas10"] == v["small_opening_fraction"] == .25
    v=calculate_beam_metrics(physical_beam(gaps=(0.,1.)))
    for key in ["mean_ba","mean_ca","mean_mcs_aurora","mcs_complexity_aurora",
                "mean_sas10","small_opening_fraction","near_closed_fraction"]:
        assert v[key] is None
