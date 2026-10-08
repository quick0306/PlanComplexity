import math
import pytest
from aurora_svmat_lab.models import AuroraBeam, AuroraControlPoint
from aurora_svmat_lab.metrics import calculate_beam_metrics, calculate_plan_metrics

KEYS={'mean_ba','mean_bi','mean_ca','mean_sas5','mean_sas10','mean_mcs_aurora','mcs_complexity_aurora'}

def beam(gaps=(20,4), weights=(0,.25,1), mu=100):
    b=AuroraBeam(control_points=[AuroraControlPoint(cumulative_meterset_weight=w,
      jaw_x=(-100,100),jaw_y=(-10,10),
      mlc_x1_positions_mm=(-g/2,-g/2,g/2,g/2),
      mlc_x2_positions_mm=(-g/2,g/2)) for g,w in zip((100,)+gaps,weights)])
    b.leaf_boundaries_mlcx1=(-10,0,10)
    b.leaf_boundaries_mlcx2=(-10,10)
    b.beam_meterset_mu=mu
    return b

def test_v4_hand_calculated_rectangles_and_delivery_weights():
    m=calculate_beam_metrics(beam())
    assert KEYS <= m.keys()
    assert m['mean_ba']==pytest.approx(160)
    assert m['mean_bi']==pytest.approx(6.4/math.pi)
    assert m['mean_ca']==pytest.approx(.5)
    assert m['mean_sas5']==pytest.approx(.75)
    assert m['mean_sas10']==pytest.approx(.75)
    assert m['mean_mcs_aurora']==pytest.approx(.4)
    assert m['mcs_complexity_aurora']==pytest.approx(.6)

def test_v4_plan_uses_absolute_mu_across_beams():
    a=beam(gaps=(20,20),mu=100)
    b=beam(gaps=(4,4),mu=300)
    m=calculate_plan_metrics([a,b])
    assert m['mean_ba']==pytest.approx(160)
    assert m['mean_sas5']==pytest.approx(.75)
    # Each beam has its own maximum aperture normalization.
    assert m['mean_mcs_aurora']==pytest.approx(1)

def test_v4_strict_sas_thresholds_and_missing_geometry():
    m=calculate_beam_metrics(beam(gaps=(5,10)))
    assert m['mean_sas5']==0
    assert m['mean_sas10']==pytest.approx(.25)
    b=beam(); b.leaf_boundaries_mlcx1=()
    m=calculate_beam_metrics(b)
    assert all(m[k] is None for k in KEYS)
    assert len(m)==77

def test_v4_closed_interval_retained_and_zero_mu_interval_excluded():
    m=calculate_beam_metrics(beam(gaps=(20,0)))
    assert m['mean_ba']==100
    assert m['mean_mcs_aurora']==pytest.approx(.25)
    assert m['mean_bi'] is None
    assert m['mean_ca'] is None
    m=calculate_beam_metrics(beam(gaps=(20,0),weights=(0,1,1)))
    assert m['mean_ba']==400
    assert m['mean_mcs_aurora']==1

def test_v4_rejects_malformed_positions_and_nonmonotonic_weights():
    b=beam(); b.control_points[1].mlc_x2_positions_mm=(0,)
    assert all(calculate_beam_metrics(b)[k] is None for k in KEYS)
    b=beam(weights=(0,.8,.7))
    assert all(calculate_beam_metrics(b)[k] is None for k in KEYS)

def test_v4_layer_intersection_and_disconnected_union_perimeter():
    from aurora_svmat_lab.aperture_metrics import _area_perimeter
    # Two disjoint rectangles, each 2x10: A40, P48. Shared Y boundary
    # does not remove an edge because their X intervals do not overlap.
    assert _area_perimeter([(10,0,2),(10,4,6)])==pytest.approx((40,48))
    b=beam(gaps=(20,20))
    for cp in b.control_points:
        cp.mlc_x2_positions_mm=(-2,2)
    m=calculate_beam_metrics(b)
    assert m['mean_ba']==pytest.approx(80)
    assert m['mean_ca']==pytest.approx(.6)
    assert m['mean_sas5']==1
    # Real jaw clipping on both axes.
    for cp in b.control_points:
        cp.jaw_x=(-1,1); cp.jaw_y=(-5,5)
    m=calculate_beam_metrics(b)
    assert m['mean_ba']==20
    assert m['mean_ca']==pytest.approx(1.2)

def test_v4_missing_mu_discloses_fallback_and_incomplete_beam_not_dropped():
    from aurora_svmat_lab.aperture_metrics import calculate_v4_metrics_with_warnings
    a=beam(gaps=(20,20),mu=None); b=beam(gaps=(4,4),mu=300)
    m,warnings=calculate_v4_metrics_with_warnings([a,b])
    assert m['mean_ba']==pytest.approx(240)
    assert any('RELATIVE_WEIGHTS' in message for message in warnings)
    b.leaf_boundaries_mlcx2=()
    m,warnings=calculate_v4_metrics_with_warnings([a,b])
    assert all(m[k] is None for k in KEYS)
    assert any('UNAVAILABLE' in message for message in warnings)

def test_v4_beam_plan_unified_exports_and_version_are_complete(tmp_path):
    import csv
    from aurora_svmat_lab.export import export_plan_rows,export_beam_rows
    from aurora_svmat_lab.models import AuroraAnalysisResult,AuroraPlanMetadata
    from formula_versions import AURORA_FORMULA_VERSION
    from ucomx_service import _adapt_aurora_result,export_results_to_csv
    b=beam();b.metrics=calculate_beam_metrics(b)
    result=AuroraAnalysisResult(beams=[b],supported=True,plan_metrics=calculate_plan_metrics([b]),
      metadata=AuroraPlanMetadata(metric_formula_version=AURORA_FORMULA_VERSION))
    assert KEYS <= export_plan_rows([result])[0].keys()
    assert KEYS <= export_beam_rows([result])[0].keys()
    unified=_adapt_aurora_result(source_path='synthetic.dcm',result=result)
    path=tmp_path/'metrics.csv'
    export_results_to_csv([unified],str(path))
    with path.open(encoding='utf-8-sig',newline='') as f:
        row,=csv.DictReader(f)
    assert KEYS <= row.keys()
    assert row['metric_formula_version']==AURORA_FORMULA_VERSION
    with path.with_name('metrics_columns.csv').open(encoding='utf-8-sig',newline='') as f:
        columns={r['column_name']:r for r in csv.DictReader(f)}
    assert set(columns)==set(unified.metrics)
    assert all(columns[k]['description'] for k in KEYS)

def test_v4_strips_match_independent_polygon_intersection():
    import random
    from shapely.geometry import box
    from shapely.ops import unary_union
    from aurora_svmat_lab.aperture_metrics import _aperture,_area_perimeter
    rng=random.Random(2187)
    e1=(-20,-5,0,20); e2=(-25,-10,10,25)
    grid=sorted(set(e1+e2)-{-25,25})
    for _ in range(30):
        banks=[]; polygons=[]
        for edges in [e1,e2]:
            left=[rng.uniform(-15,5) for _ in range(3)]
            right=[rng.uniform(-5,15) for _ in range(3)]
            banks.append(tuple(left+right))
            polygons.append(unary_union([box(a,lo,b,hi) for a,b,lo,hi in zip(left,right,edges,edges[1:]) if b>a]))
        cp=AuroraControlPoint(mlc_x1_positions_mm=banks[0],mlc_x2_positions_mm=banks[1],
                              jaw_x=(-8,8),jaw_y=(-12,13))
        actual=_area_perimeter(_aperture(cp,e1,e2,grid))
        expected=polygons[0].intersection(polygons[1]).intersection(box(-8,-12,8,13))
        assert actual==pytest.approx((expected.area,expected.length),abs=1e-9)

def test_v4_zero_mu_beam_does_not_invalidate_delivered_beam():
    from aurora_svmat_lab.aperture_metrics import calculate_v4_metrics_with_warnings
    zero=AuroraBeam(beam_meterset_mu=0)
    m,_=calculate_v4_metrics_with_warnings([beam(gaps=(20,20)),zero])
    assert m['mean_ba']==400
