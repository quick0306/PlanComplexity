from ucomx_models import AnalysisMode
from ucomx_service import analyze_plan_file, build_export_record
from formula_versions import TOMO_FORMULA_VERSION


def test_invalid_tomo_unit_contract_returns_an_unsupported_versioned_result(monkeypatch):
    monkeypatch.setattr('ucomx_service.detect_mode_from_file', lambda path: AnalysisMode.TOMO)

    def invalid(path):
        raise ValueError('Unsupported TOMO sinogram units')

    monkeypatch.setattr('ucomx_service.parse_tomo_rtplan', invalid)
    result = analyze_plan_file('synthetic.dcm')
    assert result.mode == AnalysisMode.TOMO
    assert not result.supported
    assert not result.metrics
    assert result.warnings == ['Unsupported TOMO sinogram units']
    assert build_export_record(result)['metric_formula_version'] == TOMO_FORMULA_VERSION


def test_unavailable_reference_values_serialize_as_null():
    import numpy as np
    from validation_runtime import _normalize_metric_value
    assert _normalize_metric_value(float('nan')) is None
    assert _normalize_metric_value(np.float64('inf')) is None
    assert _normalize_metric_value(0.0) == 0.0


def test_synthetic_helical_motion_reaches_analysis_and_export(tmp_path):
    import pytest
    from tests.test_tomo_parser import _motion_config, _motion_parse

    plan, _ = _motion_parse(tmp_path, _motion_config(speed=4, pitch=36))
    result = analyze_plan_file(plan.source_path, requested_mode=AnalysisMode.TOMO)
    assert result.supported
    assert result.metrics['couch_translation_mm'] == pytest.approx(4)
    assert result.metrics['couch_speed_mm_s'] == pytest.approx(4)
    assert result.metrics['target_length_mm'] == pytest.approx(2)
    exported = build_export_record(result)
    assert exported['couch_translation_mm'] == pytest.approx(4)
    assert exported['metric_formula_version'] == TOMO_FORMULA_VERSION


def test_missing_motion_stays_unavailable_through_analysis(tmp_path):
    import numpy as np
    from tests.test_tomo_parser import _motion_config, _motion_parse

    plan, _ = _motion_parse(tmp_path, _motion_config())
    result = analyze_plan_file(plan.source_path, requested_mode=AnalysisMode.TOMO)
    assert result.supported
    for key in ('couch_translation_mm', 'couch_speed_mm_s', 'pitch', 'target_length_mm'):
        assert np.isnan(result.metrics[key])
    assert any('unavailable' in warning.lower() and 'motion' in warning.lower() for warning in result.warnings)


def test_fixed_angle_synthetic_file_returns_actionable_unsupported_result(tmp_path):
    import pydicom
    from tests.test_tomo_parser import _motion_config, _motion_parse

    plan, _ = _motion_parse(tmp_path, _motion_config(speed=4, pitch=36))
    ds = pydicom.dcmread(plan.source_path)
    ds.BeamSequence[0][0x300D, 0x10A4].value = b'FIXED_ANGLE'
    for cp in ds.BeamSequence[0].ControlPointSequence:
        cp.GantryAngle = 0
    pydicom.dcmwrite(plan.source_path, ds, enforce_file_format=True)
    result = analyze_plan_file(plan.source_path, requested_mode=AnalysisMode.TOMO)
    assert not result.supported
    assert not result.metrics
    assert any('FIXED_ANGLE' in warning for warning in result.warnings)
    assert build_export_record(result)['metric_formula_version'] == TOMO_FORMULA_VERSION
