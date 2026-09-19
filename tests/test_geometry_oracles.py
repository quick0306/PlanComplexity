from validation.formula_oracles import run_formula_oracles


def test_formula_gate_includes_independent_geometry_and_dose_answers():
    report = run_formula_oracles()
    rows = {row['oracle_id']: row for row in report['oracles']}
    assert {
        'square_perimeter_40mm', 'square_pi_4_over_pi', 'square_efs_10mm',
        'symmetric_jaws_area_100mm2', 'halcyon_native_edge_100mm2',
        'dynamic_jaw_mcsv_0_6', 'tomo_fraction_dose_200cgy',
    } <= rows.keys()
    assert report['summary']['formula_oracle_green']
