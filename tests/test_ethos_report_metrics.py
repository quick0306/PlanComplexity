"""Analytic examples distinguish the report profile from generic MCSv/SAS."""
import importlib
import importlib.util

import numpy as np
import pytest

from ApertureMetric.aperture_geometry import PyAperture


def engine():
    assert importlib.util.find_spec("ethos_report_metrics"), "Report profile is missing"
    return importlib.import_module("ethos_report_metrics")


def aperture(left, right, width=5., jaw=None):
    return PyAperture(np.array([left, right], dtype=float),
                      np.full(len(left), width), jaw or [-140., 140., 140., -140.], 0.)


def calculate(aps, cumulative=None):
    return engine().calculate_ethos_beam_metrics(aps, cumulative if cumulative is not None else np.arange(len(aps)))


def test_sas_pools_counts_instead_of_weighting_cp_fractions():
    a = aperture([0, 0, 0], [.5, 5, 10])
    b = aperture([0, 0, 0], [15, 20, 25])
    values, warnings = calculate([a, b, b], [0, 1, 10])
    # Report's boundary is inclusive at 10 mm; tolerate binary roundoff.
    assert values['ethos_sas10'] == pytest.approx(2 / 8)
    assert not warnings


def test_sas_excludes_zero_center_weight_but_keeps_one_sided_delivery():
    small, large = aperture([0], [5]), aperture([0], [20])
    # Centered weights [0,1,1,0,0]: both sides of the delivered interval count.
    values, warnings = calculate([small, large, small, large, small], [0, 0, 2, 2, 2])
    assert values['ethos_sas10'] == pytest.approx(.5)
    assert not warnings
    reference, _ = calculate([large, small], [0, 2])
    for key in ['ethos_one_minus_mcs', 'ethos_penumbra_ratio']:
        assert values[key] == pytest.approx(reference[key])


def test_sas_is_unavailable_if_only_zero_weight_control_points_are_open():
    small, closed = aperture([0], [5]), aperture([0], [0])
    values, warnings = calculate([small, closed, closed, closed], [0, 0, 1, 1])
    assert values['ethos_sas10'] is None
    assert values['ethos_one_minus_mcs'] == 1.
    assert values['ethos_penumbra_ratio'] == 0.
    assert any('SAS10' in w for w in warnings)


def test_mcs_preserves_physical_adjacency_and_excludes_closed_area_and_extrema():
    # Separated rectangular islands have no adjacent variation. Bridging the
    # closed middle slot would invent an offset of 20 mm.
    a = aperture([0, 100, 20], [10, 100.5, 30])
    b = aperture([0, -100, 20], [10, -99.5, 30])
    values, _ = calculate([a, b])
    assert values['ethos_one_minus_mcs'] == pytest.approx(0.)
    assert values['ethos_penumbra_ratio'] == pytest.approx(1 - 4.4 * .4 / 50)


def test_mcs_uses_centered_mean_of_cp_products_not_interval_product_of_means():
    a = aperture([0, 0, 0], [10, 10, 10])
    b = aperture([0, 2, 4], [10, 10, 10])
    c = aperture([0, 0, 0], [20, 20, 20])
    # Envelope 300; CP areas 150,120,300; LSV 1,.5,1; weights .5,2,1.5.
    values, _ = calculate([a, b, c], [0, 1, 4])
    assert values['ethos_one_minus_mcs'] == pytest.approx(1 - (.5*.5 + 2*.2 + 1.5) / 4)


def test_penumbra_rectangle_and_finite_concave_side_strips():
    rectangle = aperture([0]*10, [100]*10)
    values, _ = calculate([rectangle, rectangle])
    assert values['ethos_penumbra_ratio'] == pytest.approx(1 - 94.4*45.4/5000)
    # Two 20x5 rows offset by 10: central core .4*14.4 per row,
    # mutual side cores 2.3*7.2 per row; outer sides have no core.
    step = aperture([0, 10], [20, 30])
    values, _ = calculate([step, step])
    assert values['ethos_penumbra_ratio'] == pytest.approx(1 - (2*.4*14.4 + 2*2.3*7.2)/200)


@pytest.mark.parametrize('cumulative', [[0, 0], [1, 0], [0, float('nan')], [0]])
def test_invalid_mu_does_not_silently_fall_back(cumulative):
    a = aperture([0], [10])
    values, warnings = calculate([a, a], cumulative)
    assert all(v is None for v in values.values())
    assert warnings


def test_closed_beam_is_unavailable_and_partial_jaw_clipping_is_rejected():
    for a in [aperture([0], [.5 + 1e-10]), aperture([0], [10], width=4),
              aperture([0], [10], jaw=[-140, 1, 140, -1])]:
        values, warnings = calculate([a, a])
        assert all(v is None for v in values.values())
        assert warnings


def test_plan_aggregation_does_not_drop_invalid_report_beams():
    from halcyon_dual_layer_metrics import BeamPaperMetrics, _aggregate_beam_results
    values = _aggregate_beam_results([
        BeamPaperMetrics({'ethos_sas10': .3}, 100),
        BeamPaperMetrics({'ethos_sas10': None}, 100)], full_precision=True)
    assert values['ethos_sas10'] is None


def synthetic_beam(mu=100., gap=10.):
    from pydicom.dataset import Dataset
    def ds(**kwargs):
        d = Dataset()
        for k, v in kwargs.items():
            setattr(d, k, v)
        return d
    devices = [ds(RTBeamLimitingDeviceType=kind, NumberOfLeafJawPairs=n,
                  LeafPositionBoundaries=np.arange(start, -start+1, 10).tolist())
               for kind, n, start in [('MLCX1', 28, -140), ('MLCX2', 29, -145)]]
    cps = [ds(CumulativeMetersetWeight=w, GantryAngle=0.,
              BeamLimitingDevicePositionSequence=[
                  ds(RTBeamLimitingDeviceType=kind, LeafJawPositions=[0.]*n+[gap]*n)
                  for kind, n in [('MLCX1', 28), ('MLCX2', 29)]]) for w in [0., 1.]]
    return dict(TreatmentDeliveryType='TREATMENT', MU=mu, PrimaryDosimeterUnit='MU',
                BeamLimitingDeviceSequence=devices, ControlPointSequence=cps)


@pytest.mark.parametrize('machine_id', ['Ethos', 'Halcyon'])
def test_production_aggregation_registry_gui_and_csv(tmp_path, machine_id):
    import csv
    from halcyon_dual_layer_metrics import calculate_halcyon_dual_layer_metrics_with_warnings
    from ucomx_models import PlanAnalysisResult, AnalysisMode
    from ucomx_service import flatten_metrics, build_metric_rows, export_results_to_csv
    from metric_formula_contracts import build_metric_formula_contracts
    from analysis_exports import DUAL_MLC_CSV_HEADER, build_dual_mlc_row
    plan = dict(machine_id=machine_id, beams={1: synthetic_beam(100, 5), 2: synthetic_beam(300, 20)})
    values, warnings = calculate_halcyon_dual_layer_metrics_with_warnings(plan, full_precision=True)
    assert values['ethos_sas10'] == .25
    assert values['ethos_one_minus_mcs'] == 0.
    assert not any('ETHOS_REPORT' in w for w in warnings)
    metadata = dict(patient_id='synthetic', patient_name='', machine_id=machine_id,
                    calculation_model='', prescribed_dose=0, mu=400)
    result = PlanAnalysisResult('synthetic.dcm', AnalysisMode.VMAT_IMRT, metadata,
                                values, flatten_metrics(values), True, warnings)
    gui = dict(build_metric_rows(result))
    assert gui['Varian Dual-layer SAS10'] == '0.25'
    export_results_to_csv([result], str(tmp_path/'results.csv'))
    with (tmp_path/'results.csv').open(encoding='utf-8-sig') as f:
        record = next(csv.DictReader(f))
    assert float(record['ethos_sas10']) == .25
    assert record['ethos_report_formula_version'] == 'ethos-report-v2'
    row = dict(zip(DUAL_MLC_CSV_HEADER, build_dual_mlc_row(metadata, values)))
    assert row['Varian Dual-layer SAS10'] == .25
    contracts = {c.metric_key: c for c in build_metric_formula_contracts() if c.platform=='VMAT_IMRT'}
    assert contracts['ethos_sas10'].formula_version == 'ethos-report-v2'


@pytest.mark.parametrize('problem', ['incomplete', 'unsupported', 'misaligned'])
def test_plan_never_uses_a_subset_of_beams(problem):
    from halcyon_dual_layer_metrics import calculate_halcyon_dual_layer_metrics_with_warnings
    b = synthetic_beam()
    if problem == 'incomplete':
        b['ControlPointSequence'] = b['ControlPointSequence'][:1]
    elif problem == 'unsupported':
        b['BeamLimitingDeviceSequence'][0].LeafPositionBoundaries = list(np.arange(-139.,142.,10))
    else:
        b['ControlPointSequence'][0].BeamLimitingDevicePositionSequence = b['ControlPointSequence'][0].BeamLimitingDevicePositionSequence[:1]
    values, warnings = calculate_halcyon_dual_layer_metrics_with_warnings(
        dict(machine_id='Ethos', beams={1: synthetic_beam(), 2: b}), full_precision=True)
    assert all(values[k] is None for k in engine().ETHOS_REPORT_KEYS)
    assert warnings


@pytest.mark.parametrize('bad_mu', [None, -1., float('nan'), float('inf')])
def test_invalid_treatment_mu_cannot_disappear_from_plan_coverage(bad_mu):
    from halcyon_dual_layer_metrics import calculate_halcyon_dual_layer_metrics_with_warnings
    values, warnings = calculate_halcyon_dual_layer_metrics_with_warnings(
        dict(machine_id='Ethos', beams={1: synthetic_beam(), 2: synthetic_beam(bad_mu)}),
        full_precision=True)
    assert all(values[k] is None for k in engine().ETHOS_REPORT_KEYS)
    assert any('ETHOS_REPORT' in w for w in warnings)


def test_negative_raw_cmw_is_not_repaired_by_dividing_by_negative_final_weight():
    from halcyon_dual_layer_metrics import calculate_halcyon_dual_layer_metrics_with_warnings
    b = synthetic_beam()
    b['ControlPointSequence'][1].CumulativeMetersetWeight = -1.
    values, warnings = calculate_halcyon_dual_layer_metrics_with_warnings(
        dict(machine_id='Ethos', beams={1: b}), full_precision=True)
    assert all(values[k] is None for k in engine().ETHOS_REPORT_KEYS)
    assert any('ETHOS_REPORT' in w for w in warnings)
