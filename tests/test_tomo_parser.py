"""Independent unit and dose cases; all DICOM data here is synthetic."""

import numpy as np
import pydicom
import pytest
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, RTPlanStorage, generate_uid

from tomo_parser import (
    _extract_sinogram_rows,
    _infer_fraction_dose_cgy,
    _infer_projection_time_s,
    parse_tomo_rtplan,
)


def _cp(values, source="standard", creator="TOMO_HA_01", raw=False):
    cp = Dataset()
    if source == "standard":
        if values is not None:
            cp.TomotherapeuticLeafOpenDurations = values
    else:
        if creator is not None:
            cp.add_new((0x300D, 0x0010), "LO", creator)
        if values is not None:
            if raw:
                values = "\\".join(map(str, values)).encode("ascii")
            cp.add_new((0x300D, 0x10A7), "UN" if raw else "DS", values)
    return cp


def _dose_plan(doses=(60.0,), fractions=(30,), beam_doses=()):
    ds = Dataset()
    ds.DoseReferenceSequence = []
    for number, dose in enumerate(doses, 1):
        item = Dataset()
        item.DoseReferenceNumber = number
        item.DoseReferenceType = "TARGET"
        item.TargetPrescriptionDose = dose
        ds.DoseReferenceSequence.append(item)
    ds.FractionGroupSequence = []
    for number, count in enumerate(fractions, 1):
        fg = Dataset()
        fg.FractionGroupNumber = number
        if count is not None:
            fg.NumberOfFractionsPlanned = count
        fg.ReferencedBeamSequence = []
        for beam_number, dose in enumerate(beam_doses, 1):
            ref = Dataset()
            ref.ReferencedBeamNumber = beam_number
            if dose is not None:
                ref.BeamDose = dose
            fg.ReferencedBeamSequence.append(ref)
        ds.FractionGroupSequence.append(fg)
    return ds


def _parse(tmp_path, rows, source="standard", projection_time=0.5, dose_plan=None, configure=None):
    ds = _dose_plan() if dose_plan is None else dose_plan
    ds.SOPClassUID = RTPlanStorage
    ds.SOPInstanceUID = generate_uid()
    ds.file_meta = FileMetaDataset()
    ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    ds.file_meta.MediaStorageSOPClassUID = ds.SOPClassUID
    ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
    beam = Dataset()
    beam.BeamNumber = 1
    beam.ControlPointSequence = [_cp(row, source) for row in rows]
    for index, cp in enumerate(beam.ControlPointSequence):
        cp.GantryAngle = index * 10
    nproj_rot = 36 if len(rows) >= 3 else len(rows)
    if projection_time is not None:
        beam.RevolutionTime = projection_time * nproj_rot
    if configure is not None:
        configure(beam)
    ds.BeamSequence = [beam]
    path = tmp_path / "synthetic_tomo.dcm"
    pydicom.dcmwrite(path, ds, enforce_file_format=True)
    return parse_tomo_rtplan(str(path))


def test_terminal_zero_does_not_change_standard_seconds_to_fractions(tmp_path):
    plan, _ = _parse(tmp_path, [[2, 3], [1, 2], [0, 0]], projection_time=4)
    np.testing.assert_allclose(plan.sinogram, [[0.5, 0.75], [0.25, 0.5]])
    np.testing.assert_allclose(plan.lot_ms, [2000, 3000, 1000, 2000])


def test_standard_subsecond_durations_are_seconds(tmp_path):
    plan, _ = _parse(tmp_path, [[0.1, 0.25], [0.4, 0.2], [0, 0]])
    np.testing.assert_allclose(plan.sinogram, [[0.2, 0.5], [0.8, 0.4]])
    np.testing.assert_allclose(plan.lot_ms, [100, 250, 400, 200])


def test_small_nonzero_final_projection_is_preserved(tmp_path):
    plan, _ = _parse(tmp_path, [[0.1, 0.2], [0.2, 0.3], [1e-10, 0]])
    assert plan.nproj == 3
    assert plan.sinogram[-1, 0] == pytest.approx(2e-10, abs=1e-15)


def test_missing_terminal_standard_row_does_not_remove_closed_projection(tmp_path):
    plan, _ = _parse(tmp_path, [[0.1, 0.2], [0, 0], None])
    assert plan.nproj == 2
    np.testing.assert_array_equal(plan.sinogram[-1], [0, 0])


def test_known_private_fraction_rows_preserve_closed_interior_projection(tmp_path):
    plan, _ = _parse(tmp_path, [[0.5] * 64, None, [0.25] * 64, None], source="private")
    assert plan.sinogram.shape == (3, 64)
    np.testing.assert_allclose(plan.sinogram[:, 0], [0.5, 0, 0.25])
    assert plan.treatment_time_s == pytest.approx(1.5)


def test_known_private_ascii_fractions_have_documented_units():
    rows, fractional = _extract_sinogram_rows([_cp([0.25] * 64, "private", raw=True)])
    assert fractional is True
    assert rows == [[0.25] * 64]


@pytest.mark.parametrize("creator", [None, "UNRECOGNIZED"])
def test_private_units_require_recognized_creator(creator):
    with pytest.raises(ValueError, match="creator|unsupported|Unsupported"):
        _extract_sinogram_rows([_cp([0.5] * 64, "private", creator=creator)])


def test_standard_and_private_rows_cannot_be_mixed():
    with pytest.raises(ValueError, match="[Mm]ixed"):
        _extract_sinogram_rows([_cp([0.5] * 64), _cp([0.5] * 64, "private")])


def test_competing_sources_in_same_control_point_are_rejected():
    cp = _cp([0.5] * 64, "private")
    cp.TomotherapeuticLeafOpenDurations = [0.5] * 64
    with pytest.raises(ValueError, match="[Mm]ixed|[Aa]mbiguous"):
        _extract_sinogram_rows([cp])


@pytest.mark.parametrize("values", [[-0.1, 0.5], [float("nan"), 0.5], [float("inf"), 0.5]])
def test_invalid_standard_duration_values_are_rejected(values):
    with pytest.raises(ValueError, match="finite|negative|invalid"):
        _extract_sinogram_rows([_cp(values)])


def test_standard_rows_must_have_consistent_leaf_counts():
    with pytest.raises(ValueError, match="leaf|ragged|length"):
        _extract_sinogram_rows([_cp([0.1, 0.2]), _cp([0.1, 0.2, 0.3])])


def test_missing_interior_standard_duration_is_not_silently_dropped():
    with pytest.raises(ValueError, match="[Mm]issing|[Ee]mpty"):
        _extract_sinogram_rows([_cp([0.1, 0.2]), _cp(None), _cp([0.2, 0.3])])


def test_private_row_requires_all_64_leaves():
    with pytest.raises(ValueError, match="64|leaf"):
        _extract_sinogram_rows([_cp([0.5] * 63, "private")])


def test_private_fraction_above_one_is_rejected():
    with pytest.raises(ValueError, match="fraction|range"):
        _extract_sinogram_rows([_cp([2.0] * 64, "private")])


@pytest.mark.parametrize("value", [-0.1, float("nan"), float("inf")])
def test_invalid_private_fraction_values_are_rejected(value):
    with pytest.raises(ValueError, match="finite|negative|invalid"):
        _extract_sinogram_rows([_cp([value] * 64, "private", raw=True)])


def test_corrupt_private_ascii_is_not_silently_cleaned():
    cp = _cp([0.5] * 64, "private", raw=True)
    cp[(0x300D, 0x10A7)].value = b"0.\xff5" + b"\\0.5" * 63
    with pytest.raises(ValueError, match="invalid numeric"):
        _extract_sinogram_rows([cp])


def test_standard_duration_longer_than_projection_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="projection|interval|range"):
        _parse(tmp_path, [[0.6, 0.2], [0.2, 0.3], [0, 0]])


def test_standard_durations_need_a_known_projection_time(tmp_path):
    with pytest.raises(ValueError, match="[Pp]rojection time|timing"):
        _parse(tmp_path, [[0.01, 0.005], [0.01, 0.01], [0, 0]], projection_time=None)


def test_documented_private_gantry_period_is_seconds():
    beam = Dataset()
    beam.add_new((0x300D, 0x0010), "LO", "TOMO_HA_01")
    beam.add_new((0x300D, 0x1040), "UN", b"24.0")
    assert _infer_projection_time_s(beam, [Dataset()], 48) == pytest.approx(0.5)


def test_missing_private_timing_keeps_explicit_research_assumption(tmp_path):
    plan, warnings = _parse(tmp_path, [[0.5] * 64, [0.25] * 64, None], source="private", projection_time=None)
    assert plan.projection_time_s == 0.02
    assert any("assumed" in warning and "0.02 s" in warning for warning in warnings)


def test_sixty_gy_thirty_fractions_is_two_hundred_cgy_per_fraction():
    assert _infer_fraction_dose_cgy(_dose_plan()) == pytest.approx(200)


@pytest.mark.parametrize("fractions", [(), (None,), (0,), (-2,), (30, 10)])
def test_missing_invalid_or_ambiguous_fraction_groups_make_dose_unavailable(fractions):
    assert np.isnan(_infer_fraction_dose_cgy(_dose_plan(fractions=fractions)))


def test_multiple_prescription_levels_do_not_choose_arbitrary_maximum():
    assert np.isnan(_infer_fraction_dose_cgy(_dose_plan(doses=(60, 54))))


def test_beam_dose_is_already_per_fraction():
    assert _infer_fraction_dose_cgy(_dose_plan(doses=(), beam_doses=(2.0,))) == pytest.approx(200)


def test_zero_beam_dose_is_unavailable_for_dose_normalization():
    assert np.isnan(_infer_fraction_dose_cgy(_dose_plan(doses=(), beam_doses=(0.0,))))


def test_incomplete_beam_doses_do_not_return_partial_sum():
    assert np.isnan(_infer_fraction_dose_cgy(_dose_plan(doses=(), beam_doses=(1.0, None))))


def test_missing_dose_is_nan_and_warned_by_parser(tmp_path):
    plan, warnings = _parse(tmp_path, [[0.1, 0.2], [0.2, 0.3], [0, 0]], dose_plan=_dose_plan(doses=()))
    assert np.isnan(plan.fraction_dose_cgy)
    assert any("dose" in item.lower() and "unavailable" in item.lower() for item in warnings)


def test_parser_records_formula_version(tmp_path):
    from formula_versions import TOMO_FORMULA_VERSION
    plan, _ = _parse(tmp_path, [[0.1, 0.2], [0.2, 0.3], [0, 0]])
    assert plan.metadata["metric_formula_version"] == TOMO_FORMULA_VERSION


def _motion_config(speed=None, pitch=None, geometry="HELICAL", creator="TOMO_HA_01", width=2.0, positions=None):
    """Independent inputs: 36 projections/rotation and 0.5 seconds/projection."""
    def configure(beam):
        if creator is not None:
            beam.add_new((0x300D, 0x0010), "LO", creator)
        if geometry is not None:
            beam.add_new((0x300D, 0x10A4), "UN", geometry.encode("ascii"))
        for element, value in ((0x1080, speed), (0x1060, pitch)):
            if value is not None:
                beam.add_new((0x300D, element), "UN", str(value).encode("ascii"))
        if width is not None:
            jaws = Dataset()
            jaws.RTBeamLimitingDeviceType = "ASYMY"
            jaws.LeafJawPositions = [-width / 2, width / 2]
            beam.ControlPointSequence[0].BeamLimitingDevicePositionSequence = [jaws]
        if positions is not None:
            for cp, position in zip(beam.ControlPointSequence, positions):
                if position != "inherit":
                    cp.TableTopLongitudinalPosition = position
    return configure


def _motion_parse(tmp_path, configure, rows=None, **kwargs):
    rows = rows if rows is not None else [[0.5] * 64, [0.25] * 64, None]
    return _parse(tmp_path, rows, source="private", configure=configure, **kwargs)


def test_helical_private_speed_times_trimmed_duration_gives_translation(tmp_path):
    plan, _ = _motion_parse(tmp_path, _motion_config(speed=4, pitch=36))
    assert plan.nproj == 2
    assert plan.treatment_time_s == pytest.approx(1)
    assert plan.couch_translation_mm == pytest.approx(4)
    assert plan.couch_speed_mm_s == pytest.approx(4)
    assert plan.pitch == pytest.approx(36)
    assert plan.target_length_mm == pytest.approx(2)
    assert plan.metadata["tomo_plan_geometry"] == "HELICAL"
    assert "10A4" in plan.metadata["tomo_geometry_source"]
    assert "1080" in plan.metadata["couch_speed_source"]
    assert "duration" in plan.metadata["couch_translation_source"]
    assert "1060" in plan.metadata["pitch_source"]


def test_closed_projection_counts_toward_private_couch_travel(tmp_path):
    rows = [[0.5] * 64, None, [0.25] * 64, None]
    plan, _ = _motion_parse(tmp_path, _motion_config(speed=4), rows=rows)
    assert plan.nproj == 3
    assert plan.couch_translation_mm == pytest.approx(6)
    assert plan.target_length_mm == pytest.approx(4)


def test_standard_longitudinal_positions_inherit_and_use_terminal_endpoint(tmp_path):
    rows = [[0.5] * 64, None, [0.25] * 64, None]
    plan, _ = _motion_parse(tmp_path, _motion_config(positions=[10, "inherit", 16, "inherit"]), rows=rows)
    assert plan.couch_translation_mm == pytest.approx(6)
    assert plan.couch_speed_mm_s == pytest.approx(4)
    assert plan.pitch == pytest.approx(36)
    assert "TableTopLongitudinalPosition" in plan.metadata["couch_translation_source"]


def test_standard_explicit_stationary_positions_are_known_zero(tmp_path):
    plan, _ = _motion_parse(tmp_path, _motion_config(positions=[5, "inherit", "inherit"]))
    assert plan.couch_translation_mm == 0
    assert plan.couch_speed_mm_s == 0
    assert plan.pitch == 0
    assert np.isnan(plan.target_length_mm)


def test_private_explicit_zero_motion_is_not_missing(tmp_path):
    plan, _ = _motion_parse(tmp_path, _motion_config(speed=0, pitch=0))
    assert plan.couch_translation_mm == 0
    assert plan.couch_speed_mm_s == 0
    assert plan.pitch == 0
    assert np.isnan(plan.target_length_mm)


def test_missing_couch_and_pitch_information_stays_unavailable(tmp_path):
    plan, warnings = _motion_parse(tmp_path, _motion_config())
    assert np.isnan(plan.couch_translation_mm)
    assert np.isnan(plan.couch_speed_mm_s)
    assert np.isnan(plan.pitch)
    assert np.isnan(plan.target_length_mm)
    assert any("motion" in item.lower() and "unavailable" in item.lower() for item in warnings)


def test_pitch_can_supply_known_helical_travel_without_couch_speed(tmp_path):
    plan, _ = _motion_parse(tmp_path, _motion_config(pitch=36))
    assert plan.couch_translation_mm == pytest.approx(4)
    assert plan.couch_speed_mm_s == pytest.approx(4)
    assert "pitch" in plan.metadata["couch_translation_source"]


def test_missing_pitch_is_derived_only_from_known_helical_motion_and_width(tmp_path):
    plan, _ = _motion_parse(tmp_path, _motion_config(speed=4))
    assert plan.pitch == pytest.approx(36)
    assert "derived" in plan.metadata["pitch_source"]


def test_assumed_field_width_does_not_supply_motion_or_target_length(tmp_path):
    plan, _ = _motion_parse(tmp_path, _motion_config(speed=4, width=None))
    assert plan.couch_translation_mm == pytest.approx(4)
    assert np.isnan(plan.pitch)
    assert np.isnan(plan.target_length_mm)


def test_assumed_projection_time_does_not_supply_private_couch_travel(tmp_path):
    plan, _ = _motion_parse(tmp_path, _motion_config(speed=4), projection_time=None)
    assert plan.couch_speed_mm_s == pytest.approx(4)
    assert np.isnan(plan.couch_translation_mm)
    assert np.isnan(plan.pitch)


@pytest.mark.parametrize("creator", [None, "UNKNOWN_CREATOR"])
def test_unknown_beam_creator_cannot_define_private_motion(tmp_path, creator):
    plan, warnings = _motion_parse(tmp_path, _motion_config(speed=4, pitch=36, creator=creator))
    assert np.isnan(plan.couch_translation_mm)
    assert np.isnan(plan.couch_speed_mm_s)
    assert np.isnan(plan.pitch)
    assert any("creator" in item.lower() for item in warnings)


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf")])
def test_invalid_private_speed_is_unavailable(tmp_path, value):
    plan, warnings = _motion_parse(tmp_path, _motion_config(speed=value))
    assert np.isnan(plan.couch_speed_mm_s)
    assert np.isnan(plan.couch_translation_mm)
    assert any("speed" in item.lower() and "invalid" in item.lower() for item in warnings)


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf")])
def test_invalid_private_pitch_is_unavailable(tmp_path, value):
    plan, warnings = _motion_parse(tmp_path, _motion_config(pitch=value))
    assert np.isnan(plan.pitch)
    assert np.isnan(plan.couch_translation_mm)
    assert any("pitch" in item.lower() and "invalid" in item.lower() for item in warnings)


def test_fixed_angle_plan_is_clearly_unsupported(tmp_path):
    with pytest.raises(ValueError, match="FIXED_ANGLE|fixed.angle"):
        _motion_parse(tmp_path, _motion_config(speed=4, geometry="FIXED_ANGLE"))


def test_unknown_geometry_cannot_trigger_helical_extrapolation(tmp_path):
    plan, warnings = _motion_parse(tmp_path, _motion_config(speed=4, pitch=36, geometry=None))
    assert plan.couch_speed_mm_s == pytest.approx(4)
    assert np.isnan(plan.couch_translation_mm)
    assert np.isnan(plan.pitch)
    assert np.isnan(plan.target_length_mm)
    assert plan.metadata["tomo_plan_geometry"] == "UNKNOWN"
    assert any("geometry" in item.lower() and "unavailable" in item.lower() for item in warnings)


def test_conflicting_standard_and_private_motion_remains_unavailable(tmp_path):
    plan, warnings = _motion_parse(tmp_path, _motion_config(speed=4, positions=[0, 1, 2]))
    assert np.isnan(plan.couch_translation_mm)
    assert np.isnan(plan.couch_speed_mm_s)
    assert np.isnan(plan.pitch)
    assert any("conflict" in item.lower() for item in warnings)


def test_conflicting_private_pitch_and_motion_remains_unavailable(tmp_path):
    plan, warnings = _motion_parse(tmp_path, _motion_config(speed=4, pitch=1))
    assert np.isnan(plan.couch_translation_mm)
    assert np.isnan(plan.couch_speed_mm_s)
    assert np.isnan(plan.pitch)
    assert any("conflict" in item.lower() for item in warnings)


def test_explicit_unknown_standard_position_does_not_inherit(tmp_path):
    plan, _ = _motion_parse(tmp_path, _motion_config(positions=[0, None, "inherit"]))
    assert np.isnan(plan.couch_translation_mm)


def test_standard_reversing_trajectory_is_not_reported_as_zero_travel(tmp_path):
    plan, warnings = _motion_parse(tmp_path, _motion_config(positions=[0, 2, 0]))
    assert np.isnan(plan.couch_translation_mm)
    assert any("monotonic" in item.lower() for item in warnings)


@pytest.mark.parametrize("speed,pitch", [(float("nan"), 36), (4, -1)])
def test_invalid_supplied_motion_is_not_repaired_from_an_alternative(tmp_path, speed, pitch):
    plan, warnings = _motion_parse(tmp_path, _motion_config(speed=speed, pitch=pitch))
    assert np.isnan(plan.couch_translation_mm)
    assert np.isnan(plan.couch_speed_mm_s)
    assert np.isnan(plan.pitch)
    assert any("invalid" in item.lower() for item in warnings)


def test_standard_motion_remains_available_without_private_geometry(tmp_path):
    plan, _ = _motion_parse(tmp_path, _motion_config(geometry=None, positions=[4, "inherit", 0]))
    assert plan.couch_translation_mm == pytest.approx(4)
    assert plan.couch_speed_mm_s == pytest.approx(4)
    assert np.isnan(plan.pitch)
    assert np.isnan(plan.target_length_mm)


def test_agreeing_standard_and_private_motion_keeps_standard_provenance(tmp_path):
    plan, warnings = _motion_parse(tmp_path, _motion_config(speed=4, pitch=36, positions=[0, 2, 4]))
    assert plan.couch_translation_mm == pytest.approx(4)
    assert "TableTopLongitudinalPosition" in plan.metadata["couch_translation_source"]
    assert not any("conflict" in item.lower() for item in warnings)


def test_unknown_geometry_stationary_gantry_does_not_crash_or_invent_rotation(tmp_path):
    configure = _motion_config(geometry=None)
    def stationary(beam):
        configure(beam)
        for cp in beam.ControlPointSequence:
            cp.GantryAngle = 0
    with pytest.raises(ValueError, match="rotation|geometry|helical"):
        _motion_parse(tmp_path, stationary)


def test_missing_native_geometry_can_be_inferred_from_helical_specific_evidence(tmp_path):
    configure = _motion_config(speed=4, pitch=36, geometry=None)
    def native(beam):
        configure(beam)
        beam.add_new((0x300D, 0x1040), "UN", b"18.0")
    plan, warnings = _motion_parse(tmp_path, native)
    assert plan.couch_translation_mm == pytest.approx(4)
    assert plan.pitch == pytest.approx(36)
    assert plan.metadata["tomo_plan_geometry"] == "HELICAL"
    assert plan.metadata["tomo_geometry_source"].startswith("inferred:")
    assert any("inferred" in item.lower() and "geometry" in item.lower() for item in warnings)


def test_explicit_unknown_geometry_is_not_overridden_by_native_tags(tmp_path):
    configure = _motion_config(speed=4, pitch=36, geometry="UNKNOWN")
    def native(beam):
        configure(beam)
        beam.add_new((0x300D, 0x1040), "UN", b"18.0")
    plan, _ = _motion_parse(tmp_path, native)
    assert plan.metadata["tomo_plan_geometry"] == "UNKNOWN"
    assert np.isnan(plan.couch_translation_mm)


def test_reversing_gantry_cannot_establish_inferred_helical_geometry(tmp_path):
    configure = _motion_config(speed=4, pitch=36, geometry=None)
    def native(beam):
        configure(beam)
        beam.add_new((0x300D, 0x1040), "UN", b"18.0")
        beam.ControlPointSequence[-1].GantryAngle = 0
    plan, _ = _motion_parse(tmp_path, native)
    assert plan.metadata["tomo_plan_geometry"] == "UNKNOWN"
    assert np.isnan(plan.couch_translation_mm)


def test_dynamic_jaws_use_maximum_opening_for_private_pitch_closure(tmp_path):
    configure = _motion_config(speed=4, pitch=36, width=1)
    def dynamic(beam):
        configure(beam)
        jaws = Dataset()
        jaws.RTBeamLimitingDeviceType = "ASYMY"
        jaws.LeafJawPositions = [-1, 1]
        beam.ControlPointSequence[1].BeamLimitingDevicePositionSequence = [jaws]
    plan, warnings = _motion_parse(tmp_path, dynamic)
    assert plan.field_width_mm == pytest.approx(2)
    assert plan.couch_translation_mm == pytest.approx(4)
    assert plan.pitch == pytest.approx(36)
    assert plan.target_length_mm == pytest.approx(2)
    assert not any("conflict" in item.lower() for item in warnings)


def test_missing_rotation_samples_cannot_supply_motion_timing(tmp_path):
    configure = _motion_config(speed=4, pitch=36)
    def no_angles(beam):
        configure(beam)
        for cp in beam.ControlPointSequence:
            del cp.GantryAngle
    plan, _ = _motion_parse(tmp_path, no_angles)
    assert plan.couch_speed_mm_s == 4
    assert np.isnan(plan.couch_translation_mm)
    assert np.isnan(plan.target_length_mm)
