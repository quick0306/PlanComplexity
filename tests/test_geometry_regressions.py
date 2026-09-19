"""Analytic geometry cases; expected answers do not use production geometry helpers."""

import math

import numpy as np
import pytest
from pydicom.dataset import Dataset

from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.edge_metric import EdgeMetric
from ComplexityMetric.plan_irregularity import PlanIrregularity
from ComplexityMetric.modulation_complexity_score import ModulationComplexityScore
from halcyon_dual_layer_metrics import _build_layer_control_points, _mcs_interval_terms
from vcomx_vmat_metrics import _aav_normalization, _aperture_perimeter


def dataset(**attributes):
    result = Dataset()
    for key, value in attributes.items():
        setattr(result, key, value)
    return result


def aperture(left, right, *, jaw=(-100., 100., 100., -100.), widths=None):
    return PyAperture(
        np.asarray([left, right], dtype=float),
        np.asarray(widths if widths is not None else [5.] * len(left)),
        list(jaw), 0.,
    )


def test_square_full_perimeter_pi_efs_and_one_sided_edge_metric():
    square = aperture([-5., -5.], [5., 5.])
    assert square.area() == 100.
    assert _aperture_perimeter(square) == 40.
    assert PlanIrregularity().calculate_aperture_irregularity(square) == pytest.approx(4 / math.pi)
    assert 4 * square.area() / _aperture_perimeter(square) == 10.
    # EM intentionally uses only the horizontal leaf-side boundary, not full P.
    assert EdgeMetric().calculate_aperture_edge_metric(square) == .2


@pytest.mark.parametrize('left,right,expected', [
    ([-5., 0., -5.], [5., 0., 5.], 60.),  # two separate 10x5 rectangles
    ([-10., 0.], [0., 10.], 60.),  # rectangles touching only at one corner
    ([0., 0.], [0., 0.], 0.),
    ([5., 5.], [-5., -5.], 0.),  # crossed leaves cannot form negative area
])
def test_closed_disconnected_and_touching_rows(left, right, expected):
    shape = aperture(left, right)
    assert shape.area() >= 0.
    assert _aperture_perimeter(shape) == expected


def test_completely_closed_y_jaws_have_no_aperture_boundary():
    shape = PyAperture(
        np.array([[-5., -5.], [5., 5.]]), np.array([10., 10.]),
        [-10., -1., 10., -1.], 0., leaf_position_boundaries=[-10., 0., 10.],
    )
    assert shape.area() == 0.
    assert shape.perimeter() == 0.


def standard_beam(jaw_types=('X', 'Y'), *, positions_on_cp=True):
    device = dataset(RTBeamLimitingDeviceType='MLCX', NumberOfLeafJawPairs=2,
                     LeafPositionBoundaries=[-10., 0., 10.])
    positions = [dataset(RTBeamLimitingDeviceType='MLCX', LeafJawPositions=[-10., -10., 10., 10.])]
    if positions_on_cp:
        positions += [dataset(RTBeamLimitingDeviceType=kind, LeafJawPositions=[-5., 5.]) for kind in jaw_types]
    beam = {'TreatmentMachineName': 'GenericLinac', 'GantryAngle': 0.,
            'BeamLimitingDeviceSequence': [device],
            'ControlPointSequence': [dataset(GantryAngle=0., BeamLimitingDevicePositionSequence=positions)]}
    beam.update({kind: [-5., 5.] for kind in jaw_types})
    return beam


@pytest.mark.parametrize('jaw_types', [('X', 'Y'), ('ASYMX', 'ASYMY')])
@pytest.mark.parametrize('positions_on_cp', [True, False])
def test_symmetric_and_asymmetric_jaws_clip_identically(jaw_types, positions_on_cp):
    shape = AperturesFromBeamCreator().create(standard_beam(jaw_types, positions_on_cp=positions_on_cp))[0]
    assert shape.area() == 100.
    assert _aperture_perimeter(shape) == 40.


@pytest.mark.parametrize('dual_layer', [False, True])
def test_omitted_jaws_inherit_the_latest_position_per_axis(dual_layer):
    beam = halcyon_edge_beam() if dual_layer else standard_beam()
    first = beam['ControlPointSequence'][0]
    if dual_layer:
        first.BeamLimitingDevicePositionSequence = [
            dataset(RTBeamLimitingDeviceType=kind, LeafJawPositions=[-10.] * count + [10.] * count)
            for kind, count in [('MLCX1', 28), ('MLCX2', 29)]]
        first.BeamLimitingDevicePositionSequence.extend([
            dataset(RTBeamLimitingDeviceType=kind, LeafJawPositions=[-5., 5.])
            for kind in ('X', 'Y')])
    beam['ControlPointSequence'].extend([
        dataset(GantryAngle=1., BeamLimitingDevicePositionSequence=[
            dataset(RTBeamLimitingDeviceType='Y', LeafJawPositions=[-1., 1.])]),
        dataset(GantryAngle=2., BeamLimitingDevicePositionSequence=[
            dataset(RTBeamLimitingDeviceType='X', LeafJawPositions=[-2., 2.])]),
    ])
    shapes = AperturesFromBeamCreator().create(beam)
    expected = [100., 100., 20., 20., 8., 8.] if dual_layer else [100., 20., 8.]
    assert [shape.area() for shape in shapes] == expected
    if dual_layer:
        snapshots = _build_layer_control_points(beam)
        assert [s.effective_aperture.area() for s in snapshots] == [100., 20., 8.]


def test_absolute_offset_boundaries_are_preserved_in_iec_slot_order():
    beam = standard_beam()
    device = beam['BeamLimitingDeviceSequence'][0]
    device.LeafPositionBoundaries = [10., 15., 25.]
    cp = beam['ControlPointSequence'][0]
    cp.BeamLimitingDevicePositionSequence = [
        dataset(RTBeamLimitingDeviceType='MLCX', LeafJawPositions=[-5., 0., 5., 0.]),
        dataset(RTBeamLimitingDeviceType='ASYMY', LeafJawPositions=[10., 15.]),
    ]
    shape = AperturesFromBeamCreator().create(beam)[0]
    assert [p.top for p in shape.leaf_pairs] == [-10., -15.]
    assert [p.bottom for p in shape.leaf_pairs] == [-15., -25.]
    assert shape.area() == 50.


def halcyon_edge_beam():
    devices = [dataset(RTBeamLimitingDeviceType=kind, NumberOfLeafJawPairs=count,
                       LeafPositionBoundaries=list(range(start, -start + 1, 10)))
               for kind, count, start in [('MLCX1', 28, -140), ('MLCX2', 29, -145)]]
    cp = dataset(GantryAngle=0., BeamLimitingDevicePositionSequence=[
        dataset(RTBeamLimitingDeviceType='MLCX1', LeafJawPositions=[0.] * 56),
        dataset(RTBeamLimitingDeviceType='MLCX2', LeafJawPositions=[0.] * 28 + [-10.] + [0.] * 28 + [10.]),
    ])
    return {'TreatmentMachineName': 'Halcyon', 'GantryAngle': 0.,
            'BeamLimitingDeviceSequence': devices, 'ControlPointSequence': [cp]}


def test_halcyon_native_layers_keep_all_slots_and_edge_half_leaf():
    beam = halcyon_edge_beam()
    distal, proximal = AperturesFromBeamCreator().create(beam)
    assert (len(distal.leaf_pairs), len(proximal.leaf_pairs)) == (28, 29)
    assert (proximal.leaf_pairs[0].top, proximal.leaf_pairs[-1].bottom) == (145., -145.)
    assert proximal.area() == 100.  # 20 mm gap x 5 mm inside the fixed +/-140 jaws
    snapshot = _build_layer_control_points(beam)[0]
    assert snapshot.proximal_aperture.area() == 100.
    assert snapshot.stacked_aperture.area() == 100.
    assert snapshot.effective_aperture.area() == 0.  # distal layer remains closed


def test_mlc_shape_mismatch_is_rejected_instead_of_truncating_leaves():
    beam = standard_beam()
    beam['ControlPointSequence'][0].BeamLimitingDevicePositionSequence[0].LeafJawPositions = [-1.] * 3 + [1.] * 3
    with pytest.raises(ValueError, match='(?i)(shape|boundar|leaf|width)'):
        AperturesFromBeamCreator().create(beam)


def test_dynamic_jaw_aav_and_mcsv_are_bounded_and_order_invariant():
    wide = aperture([-5., -5.], [5., 5.], jaw=(-100., 5., 100., -5.))
    narrow = aperture([-5., -5.], [5., 5.], jaw=(-100., 1., 100., -1.))
    metric = ModulationComplexityScore()
    for series in ([wide, narrow], [narrow, wide]):
        assert _aav_normalization(series) == 100.
        assert metric.calculate_per_aperture(series) == pytest.approx([.6])
        assert _mcs_interval_terms(series) == pytest.approx([.6])


def test_aav_envelope_retains_both_ends_of_a_moving_y_jaw():
    top = aperture([-5., -5.], [5., 5.], jaw=(-100., 5., 100., 3.))
    bottom = aperture([-5., -5.], [5., 5.], jaw=(-100., -3., 100., -5.))
    # Each physical row exposes 2 mm; the two rows together normalize to 40 mm2.
    assert _aav_normalization([top, bottom]) == 40.
    assert _aav_normalization([bottom, top]) == 40.
