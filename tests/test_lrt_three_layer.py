"""Independent hand calculations and supported-layout integration tests."""
from copy import deepcopy
import math

import numpy as np
import pytest

from ApertureMetric.aperture_geometry import PyAperture
from ethos_report_metrics import calculate_ethos_beam_metrics
from lrt_metric_schema import EXPORT_KEYS, CANDIDATE_KEYS, select_candidates
from lrt_three_layer import (
    centered_weights, finite_strip_pr, calculate_lrt_beam_metrics, calculate_lrt_plan_metrics,
)
from tests.test_ethos_report_metrics import synthetic_beam


def aperture(left, right, height=5., jaw=None):
    return PyAperture(np.array([left, right], dtype=float), np.full(len(left), height),
                      jaw or [-140., 140., 140., -140.], 0.)


def set_layer(beam, cp_index, kind, left, right):
    for device in beam['ControlPointSequence'][cp_index].BeamLimitingDevicePositionSequence:
        if device.RTBeamLimitingDeviceType == kind:
            n = len(device.LeafJawPositions)//2
            device.LeafJawPositions = [left]*n + [right]*n


def test_rectangle_area_perimeter_pi_and_identical_layers():
    values, warnings = calculate_lrt_beam_metrics(synthetic_beam(gap=20))
    assert not warnings
    # All are clipped to the fixed 280 mm jaw; P has two partial 5 mm edge rows.
    for suffix, height in [('Eff', 280), ('D', 280), ('P', 280)]:
        assert values[f'PA_{suffix}'] == 20*height
        assert values[f'PI_{suffix}'] == pytest.approx((2*(20+height))**2/(4*math.pi*20*height))
        assert values[f'PM_{suffix}'] == 0
        assert values[f'PR_{suffix}'] == pytest.approx(1-(20-5.6)*(height-4.6)/(20*height))
    assert values['PA_Eff'] == values['PA_D']
    assert values['NL_Eff'] == 56 and values['NL_D'] == 28 and values['NL_P'] == 29
    assert len(values) == len(EXPORT_KEYS) == 51


@pytest.mark.parametrize('blocked', ['MLCX1', 'MLCX2'])
def test_closed_layer_and_negative_intersection(blocked):
    beam = synthetic_beam()
    for i in range(2):
        set_layer(beam, i, blocked, 50, 50)
    values, _ = calculate_lrt_beam_metrics(beam)
    assert values['PA_Eff'] == values['PI_Eff'] == values['PM_Eff'] == 0
    assert values['PR_Eff'] is None
    assert values['SAS20_Eff'] is None


def test_offset_and_single_layer_fixed_intersection_changes():
    beam = synthetic_beam(gap=20)
    before, _ = calculate_lrt_beam_metrics(beam)
    for i in range(2):
        set_layer(beam, i, 'MLCX2', 10, 30)
    after, _ = calculate_lrt_beam_metrics(beam)
    assert after['PA_D'] == before['PA_D']
    assert after['PA_P'] == before['PA_P']
    assert after['PA_Eff'] == 10*280
    assert after['PR_Eff'] > before['PR_Eff']


def test_centered_mu_and_manual_two_cp_values():
    weights, intervals = centered_weights([0, 7])
    assert list(weights) == [3.5, 3.5] and list(intervals) == [7]
    beam = synthetic_beam(gap=10)
    for kind in ['MLCX1', 'MLCX2']:
        set_layer(beam, 1, kind, 0, 20)
    result, _ = calculate_lrt_beam_metrics(beam)
    assert result['PA_Eff'] == 15*280
    assert result['PM_Eff'] == pytest.approx(.25)
    assert result['MU_per_CP'] == 50
    assert result['PR_Eff'] == pytest.approx(np.mean([
        1-4.4*275.4/2800, 1-14.4*275.4/5600]))
    w, _ = centered_weights([0, 1, 4])
    assert list(w) == [.5, 2, 1.5]


def test_unequal_mu_three_cp_and_zero_interval():
    beam = synthetic_beam(gap=10)
    beam['ControlPointSequence'].append(deepcopy(beam['ControlPointSequence'][-1]))
    for i, (cmw, gap) in enumerate(zip([0, 1, 4], [10, 20, 30])):
        beam['ControlPointSequence'][i].CumulativeMetersetWeight = cmw
        for kind in ['MLCX1','MLCX2']:
            set_layer(beam, i, kind, 0, gap)
    result, _ = calculate_lrt_beam_metrics(beam)
    assert result['PA_Eff'] == pytest.approx((.5*10+2*20+1.5*30)/4*280)
    assert result['PM_Eff'] == pytest.approx(1-result['PA_Eff']/(30*280))
    beam['ControlPointSequence'][1].CumulativeMetersetWeight = 0
    result, warnings = calculate_lrt_beam_metrics(beam)
    assert not warnings
    assert result['PA_Eff'] == 25*280


def test_pm_is_slot_max_area_modulation_not_motion_or_true_union():
    beam = synthetic_beam(gap=10)
    # A translating constant-width aperture has unchanged legacy PM=0.
    for kind in ['MLCX1', 'MLCX2']:
        set_layer(beam, 1, kind, 20, 30)
    result, _ = calculate_lrt_beam_metrics(beam)
    assert result['PM_Eff'] == 0
    assert result['LT_Eff'] > 0


def test_physical_motion_with_unchanged_effective_shape():
    beam = synthetic_beam(gap=10)
    for i in range(2):
        set_layer(beam, i, 'MLCX2', -10-10*i, 20+10*i)
    result, _ = calculate_lrt_beam_metrics(beam)
    assert result['LT_P'] > 0 and result['LT_Eff'] == 0
    assert result['PM_Eff'] == 0
    assert result['PM_P'] > 0


def test_same_leaf_motion_different_effective_area_modulation():
    a, b = synthetic_beam(gap=20), synthetic_beam(gap=20)
    for beam, pleft in [(a, 0), (b, 15)]:
        for i in range(2):
            set_layer(beam, i, 'MLCX2', pleft, pleft+30)
        set_layer(beam, 1, 'MLCX1', 0, 30)
    av, _ = calculate_lrt_beam_metrics(a)
    bv, _ = calculate_lrt_beam_metrics(b)
    assert av['LT_D'] == bv['LT_D']
    assert av['PM_Eff'] != bv['PM_Eff']


def test_pr_native_and_effective_tessellations_describe_same_rectangle():
    assert finite_strip_pr(aperture([0]*4, [20]*4, 5)) == pytest.approx(
        finite_strip_pr(aperture([0]*2, [20]*2, 10)))
    # Two offset rows: original analytic finite-strip example (not erosion).
    assert finite_strip_pr(aperture([0,10], [20,30])) == pytest.approx(
        1-(2*.4*14.4+2*2.3*7.2)/200)
    assert finite_strip_pr(aperture([0], [2])) == 1
    assert finite_strip_pr(aperture([0], [0])) == 0
    assert finite_strip_pr(aperture([0], [10], 4)) is None


def test_random_effective_pr_matches_unchanged_report_algorithm():
    rng = np.random.default_rng(7)
    for _ in range(20):
        aps = [aperture(rng.uniform(-20,0,8), rng.uniform(0,20,8)) for _ in range(3)]
        old, _ = calculate_ethos_beam_metrics(aps, [0,1,4])
        new = np.average([finite_strip_pr(a) for a in aps], weights=[.5,2,1.5])
        assert new == pytest.approx(old['ethos_penumbra_ratio'], abs=1e-14)


@pytest.mark.parametrize('cmw', [[0,0], [0,-1], [0,float('nan')], [1,2]])
def test_invalid_weights_no_uniform_fallback(cmw):
    beam = synthetic_beam()
    for cp, value in zip(beam['ControlPointSequence'], cmw):
        cp.CumulativeMetersetWeight = value
    values, warnings = calculate_lrt_beam_metrics(beam)
    assert all(x is None for x in values.values()) and warnings


def test_missing_first_layer_and_bad_positions_and_sequence_rejected():
    beam = synthetic_beam()
    beam['ControlPointSequence'][0].BeamLimitingDevicePositionSequence.pop()
    values, warnings = calculate_lrt_beam_metrics(beam)
    assert all(x is None for x in values.values()) and warnings
    beam = synthetic_beam()
    for i, cp in enumerate(beam['ControlPointSequence']):
        cp.ControlPointIndex = 1-i
    values, warnings = calculate_lrt_beam_metrics(beam)
    assert all(x is None for x in values.values()) and 'ControlPointIndex' in warnings[0]
    beam = synthetic_beam()
    beam['ControlPointSequence'][0].BeamLimitingDevicePositionSequence[0].LeafJawPositions = [0,1]
    values, warnings = calculate_lrt_beam_metrics(beam)
    assert all(x is None for x in values.values()) and warnings


def test_omitted_later_positions_inherit_and_repetition_does_not_mutate():
    beam = synthetic_beam()
    beam['ControlPointSequence'][1].BeamLimitingDevicePositionSequence = []
    before = str(beam)
    first, _ = calculate_lrt_beam_metrics(beam)
    second, _ = calculate_lrt_beam_metrics(beam)
    assert first == second and str(beam) == before
    assert first['PA_Eff'] == 2800


def test_system_reference_explicit_no_substitution_and_candidate_exclusion():
    beam = synthetic_beam()
    v, _ = calculate_lrt_beam_metrics(beam, pr_system=.123)
    assert v['PR_System'] == .123 and v['PR_Eff'] != .123
    assert 'PR_System' not in select_candidates(v)
    assert len(CANDIDATE_KEYS) == 50
    assert len(select_candidates(v, include_system_reference=True)) == 51
    del v['SAS20_Eff']
    with pytest.raises(KeyError):
        select_candidates(v)


def test_plan_mu_weighting_and_no_invalid_beam_subset():
    a, b = synthetic_beam(100,10), synthetic_beam(300,20)
    plan = dict(machine_id='Halcyon', beams={1:a,2:b})
    v, _ = calculate_lrt_plan_metrics(plan, pr_system=.789)
    assert v['PA_Eff'] == 17.5*280
    assert v['MU'] == 400 and v['MU_per_CP'] == 100
    assert v['PR_System'] == .789
    b['MU'] = -1
    v, warnings = calculate_lrt_plan_metrics(plan)
    assert all(x is None for x in v.values()) and warnings


def test_registry_catalog_gui_and_export(tmp_path):
    from metric_registry import VMAT_METRIC_SPECS
    from metric_definition_catalog import build_metric_definition_catalog
    from metric_formula_contracts import build_metric_formula_contracts
    assert set(EXPORT_KEYS) <= {s.key for s in VMAT_METRIC_SPECS}
    assert set(EXPORT_KEYS) <= {s.metric_key for s in build_metric_definition_catalog() if s.platform=='VMAT_IMRT'}
    assert set(EXPORT_KEYS) <= {s.metric_key for s in build_metric_formula_contracts() if s.platform=='VMAT_IMRT'}
    from halcyon_dual_layer_metrics import calculate_halcyon_dual_layer_metrics_with_warnings
    from ucomx_service import flatten_metrics
    plan = dict(machine_id='Halcyon', beams={1:synthetic_beam()})
    v, _ = calculate_halcyon_dual_layer_metrics_with_warnings(plan, full_precision=True)
    canonical, _ = calculate_lrt_plan_metrics(plan, pr_system=v['ethos_penumbra_ratio'])
    v.update(canonical)
    flat = flatten_metrics(v)
    assert flat['PR_System'] == v['ethos_penumbra_ratio']
    assert set(EXPORT_KEYS) <= set(flat)
    from ucomx_models import PlanAnalysisResult, AnalysisMode
    from ucomx_service import build_metric_rows
    result = PlanAnalysisResult('synthetic.dcm', AnalysisMode.VMAT_IMRT, {}, v, flat, True, [])
    before = dict(flat)
    for profile, expected in [('LRT Effective',16),('LRT Distal',16),('LRT Proximal',16),
                              ('LRT candidates (50)',50),('LRT system reference',1)]:
        assert len(build_metric_rows(result, profile=profile)) == expected
    assert flat == before


def test_historical_csv_prefix_is_preserved_when_new_columns_append():
    from unittest.mock import patch
    import analysis_exports as exports
    from metric_registry import VMAT_METRIC_SPECS
    metadata=dict(patient_id='synthetic', patient_name='', plan_name='', machine_id='Halcyon',
                  calculation_model='', prescribed_dose=0, mu=100)
    metrics={'sport':.123, 'PR_Eff':.456}
    current_header=list(exports.STANDARD_CSV_HEADER)
    current_row=exports.build_standard_row(metadata,metrics)
    legacy_specs=tuple(s for s in VMAT_METRIC_SPECS if s.key not in EXPORT_KEYS)
    with patch.object(exports, 'VMAT_METRIC_SPECS',legacy_specs):
        legacy_header=exports.BASE_HEADER+exports._metric_columns()
        legacy_row=exports.build_standard_row(metadata,metrics)
    assert current_header[:-51] == legacy_header
    assert current_row[:-51] == legacy_row
    assert current_row[current_header.index('PR_Eff')] == .456
    assert len(current_header) == len(set(current_header))
    assert current_row[current_header.index('MU')] == 100


def test_ordered_indices_and_submillimeter_closed_report_mask():
    beam=synthetic_beam(gap=.5)
    for i,cp in enumerate(beam['ControlPointSequence']):
        cp.ControlPointIndex=i
    values, warnings=calculate_lrt_beam_metrics(beam)
    assert values['PR_Eff'] is None and values['PA_Eff'] == 140
    assert warnings


def test_regression_comparison_fails_on_any_historical_value_change():
    from tools.lrt_compare import compare
    original=[dict(case='SYN',beam=1,sha256='synthetic',values={'pa_effective':12.},warnings=[])]
    changed=deepcopy(original)
    changed[0]['values'].update(PA_Eff=12.,pa_effective=13.)
    result=compare(original,changed)
    assert result['changed_historical_values']==1 and not result['historical_fields_bitwise_equal']


def test_pr_report_agreement_statistics_known_pairs():
    from tools.validate_lrt_pr import agreement
    result=agreement([10,20,30],[10.1,20.1,30.1])
    assert result['bias_pp']==pytest.approx(.1)
    assert result['mae_pp']==pytest.approx(.1)
    assert result['rmse_pp']==pytest.approx(.1)
    assert result['pearson']==pytest.approx(1.)
