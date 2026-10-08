import pytest
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian
from DicomParse.dicom_rt import RTPlan
from ucomx_service import detect_mode, detect_mode_from_file, AnalysisMode
from tests.test_aurora_parser import build_fake_aurora_rtplan


def test_setup_reference_is_excluded_but_treatment_mu_preserved():
    ds = Dataset()
    treatment = Dataset()
    treatment.BeamNumber = 2
    treatment.TreatmentDeliveryType = 'TREATMENT'
    setup = Dataset()
    setup.BeamNumber = 101
    setup.TreatmentDeliveryType = 'SETUP'
    ds.BeamSequence = [treatment, setup]
    group = Dataset()
    group.NumberOfFractionsPlanned = 1
    refs = []
    for number, mu in [(2, 100), (101, 0)]:
        ref = Dataset()
        ref.ReferencedBeamNumber = number
        ref.BeamMeterset = mu
        ref.BeamDose = 0
        refs.append(ref)
    group.ReferencedBeamSequence = refs
    ds.FractionGroupSequence = [group]
    plan = object.__new__(RTPlan)
    plan.ds = ds
    beams = plan.get_beams()
    assert set(beams) == {2}
    assert beams[2]['MU'] == 100
    refs[1].ReferencedBeamNumber = 999
    with pytest.raises(ValueError, match='999'):
        plan.get_beams()


@pytest.mark.parametrize('model', ['WisdomTech', 'DeepPlan'])
def test_deepplan_vendor_does_not_imply_aurora(model):
    assert detect_mode({'manufacturer': 'WisdomTech Medical Systems',
                        'manufacturer_model_name': model,
                        'calculation_model': model}) == AnalysisMode.VMAT_IMRT


def test_conventional_dual_layer_deepplan_is_not_svmat(tmp_path):
    ds = build_fake_aurora_rtplan()
    ds.RTPlanLabel = 'TEST'
    ds.RTPlanName = 'TEST'
    for beam in ds.BeamSequence:
        beam.TreatmentMachineName = 'TEST'
        for cp in beam.ControlPointSequence:
            cp.IsocenterPosition = [0, 0, 0]
            for tag in [(0x4001, 0x1004), (0x4001, 0x1005)]:
                if tag in cp:
                    del cp[tag]
    ds.file_meta = FileMetaDataset()
    ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    path = tmp_path / 'test.dcm'
    ds.save_as(path, enforce_file_format=True)
    assert detect_mode_from_file(str(path)) == AnalysisMode.VMAT_IMRT

def test_generic_dual_layer_uses_actual_boundaries():
    from ApertureMetric.aperture_creator import AperturesFromBeamCreator
    from ComplexityMetric.mean_field_area import MeanFieldArea
    devices = []
    positions = []
    for kind, count, width in [('MLCX1', 30, 10), ('MLCX2', 29, 10)]:
        device = Dataset()
        device.RTBeamLimitingDeviceType = kind
        device.NumberOfLeafJawPairs = count
        device.LeafPositionBoundaries = [i * width - count * width / 2 for i in range(count + 1)]
        devices.append(device)
        position = Dataset()
        position.RTBeamLimitingDeviceType = kind
        position.LeafJawPositions = [-10] * count + [10] * count
        positions.append(position)
    cps = []
    for weight in [0, 1]:
        cp = Dataset()
        cp.GantryAngle = 0
        cp.CumulativeMetersetWeight = weight
        cp.BeamLimitingDevicePositionSequence = positions
        cps.append(cp)
    beam = dict(TreatmentMachineName='CVMAT', TreatmentDeliveryType='TREATMENT',
                BeamLimitingDeviceSequence=devices, ControlPointSequence=cps,
                ASYMX=[-20, 20], ASYMY=[-200, 200], GantryAngle=0, MU=100,
                PrimaryDosimeterUnit='MU')
    apertures = AperturesFromBeamCreator().create(beam)
    assert len(apertures) == 4
    assert [ap.area() for ap in apertures] == pytest.approx([6000, 5800, 6000, 5800])
    result = MeanFieldArea(full_precision=True).calculate_for_plan(
        {'machine_id': 'CVMAT', 'beams': {1: beam}})
    assert result == pytest.approx((6000, 5800))

@pytest.mark.parametrize('axial_motion', [True, False])
def test_wisdomtech_model_routes_by_trajectory(tmp_path, axial_motion):
    from ucomx_service import analyze_plan_file
    ds = build_fake_aurora_rtplan(manufacturer_model_name='WisdomTech')
    ds.RTPlanName = 'TEST'
    ds.RTPlanLabel = 'TEST'
    for beam in ds.BeamSequence:
        beam.TreatmentMachineName = 'R0_Clinical Rese'
        if not axial_motion:
            for cp in beam.ControlPointSequence:
                cp.IsocenterPosition = [0, 0, 0]
                for tag in [(0x4001, 0x1004), (0x4001, 0x1005)]:
                    if tag in cp:
                        del cp[tag]
    ds.file_meta = FileMetaDataset()
    ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    path = tmp_path / 'wisdomtech.dcm'
    ds.save_as(path, enforce_file_format=True)
    expected = AnalysisMode.AURORA if axial_motion else AnalysisMode.VMAT_IMRT
    assert detect_mode_from_file(str(path)) == expected
    if axial_motion:
        for mode in [AnalysisMode.AUTO, AnalysisMode.AURORA]:
            result = analyze_plan_file(str(path), requested_mode=mode)
            assert result.supported
            assert result.mode == AnalysisMode.AURORA
            assert 'projection_pitch_mean' in result.metrics
