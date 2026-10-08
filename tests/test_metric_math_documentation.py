"""Keep all registered metric families connected to editable math documentation."""
from pathlib import Path
import re
from metric_definition_catalog import build_metric_definition_catalog, export_metric_definitions


def test_every_metric_links_to_existing_math_section():
    from metric_math_links import math_reference_for_record
    root = Path(__file__).resolve().parents[1] / 'docs'
    for record in build_metric_definition_catalog():
        filename, anchor = math_reference_for_record(record)
        text = (root / filename).read_text(encoding='utf-8')
        assert f'## {anchor.replace("-", " ")}' in text.lower(), (record.platform, record.metric_key, filename, anchor)
        assert '$$' in text


def test_generated_definitions_link_every_record_and_complete_index(tmp_path):
    records = export_metric_definitions(csv_path=tmp_path/'definitions.csv', markdown_path=tmp_path/'all.md')
    text = (tmp_path/'all.md').read_text(encoding='utf-8')
    assert text.count('- LaTeX reference:') == len(records)
    index = (tmp_path/'metric_math_index.md').read_text(encoding='utf-8')
    assert index == (Path(__file__).resolve().parents[1]/'docs'/'metric_math_index.md').read_text(encoding='utf-8')
    pairs = re.findall(r'^\| (VMAT_IMRT|TOMO|CYBERKNIFE_MLC|AURORA) \| `([^`]+)` \|', index, re.M)
    assert len(pairs) == len(set(pairs)) == len(records)
    assert set(pairs) == {(r.platform,r.metric_key) for r in records}
    for name in ['vmat_imrt','tomo','cyberknife_mlc','aurora']:
        appendix=(tmp_path/f'metric_definitions_{name}.md').read_text(encoding='utf-8')
        assert appendix.count('- LaTeX reference:') == sum(r.platform == {'vmat_imrt':'VMAT_IMRT','tomo':'TOMO','cyberknife_mlc':'CYBERKNIFE_MLC','aurora':'AURORA'}[name] for r in records)
