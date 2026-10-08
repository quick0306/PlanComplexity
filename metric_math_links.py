"""Documentation-only mapping of every catalog family to editable LaTeX notes."""
from pathlib import Path


VMAT_SECTIONS = {
    'Plan prescription': ('vmat_imrt_guide.md', 'plan'),
    'Arc geometry': ('vmat_imrt_guide.md', 'plan'),
    'Leaf travel': ('vmat_imrt_guide.md', 'travel'),
    'Delivery dynamics': ('vmat_imrt_guide.md', 'dynamics'),
    'Motion bins': ('vmat_imrt_guide.md', 'dynamics'),
    'MI family': ('vmat_imrt_guide.md', 'mi'),
    'MI components': ('vmat_imrt_guide.md', 'mi'),
    'McNiven-style modulation': ('vmat_imrt_guide.md', 'modulation'),
    'Shape modulation': ('vmat_imrt_guide.md', 'modulation'),
    'Aperture geometry': ('vmat_imrt_guide.md', 'aperture'),
    'SPORT': ('vmat_imrt_guide.md', 'sport'),
    'Halcyon/Ethos Hybrid v2': ('halcyon_ethos_guide.md', 'representations'),
    'Halcyon/Ethos Tamura 2020': ('halcyon_ethos_guide.md', 'tamura'),
    'Halcyon/Ethos Quintero 2021': ('halcyon_ethos_guide.md', 'quintero'),
    'Varian Ethos/Halcyon dual-layer MLC': ('halcyon_ethos_guide.md', 'report'),
}
TOMO_SECTIONS = {'Delivery':'delivery', 'Leaf open time':'leaf-times',
                 'Sinogram geometry':'sinogram-geometry', 'Sinogram modulation':'modulation'}
AURORA_SECTIONS = {'V2 paper-style physics':'motion', 'Legacy engineering':'motion',
                   'V3 bidirectional symmetry':'research', 'V3 small-opening burden':'research',
                   'V3 local interval peaks':'research', 'V3 axial regions':'research',
                   'V3 dual-layer coordination':'research', 'V4 physical aperture and adapted MCS':'aperture'}


def math_reference_for_record(record):
    if record.platform == 'VMAT_IMRT':
        return VMAT_SECTIONS[record.group]
    if record.platform == 'TOMO':
        return 'tomo_guide.md', TOMO_SECTIONS[record.group]
    if record.platform == 'CYBERKNIFE_MLC':
        if record.group != 'MLC-based subset':
            raise KeyError(record.group)
        return 'cyberknife_guide.md', 'metrics'
    if record.platform == 'AURORA':
        return 'aurora_guide.md', AURORA_SECTIONS[record.group]
    raise KeyError(record.platform)


def math_reference_line(record):
    filename, anchor = math_reference_for_record(record)
    return f'- LaTeX reference: [Readable equations and mode-specific conventions]({filename}#{anchor})'


def write_math_index(records, output_dir):
    lines = ['# 全平台指标与 LaTeX 公式索引', '',
             '由 `python tools/export_metric_definitions.py` 生成。每个已注册记录均指向可直接编辑的 Markdown/LaTeX 章节。', '',
             '公式章节按共享定义归组，原生层、effective、stacked 和容器/标量组件仍是独立记录。章节公式与逐项公式契约共同阅读，不能把共享符号理解为跨平台同一算法。', '',
             '| Platform | Metric key | Display name | Unit | LaTeX chapter |',
             '| --- | --- | --- | --- | --- |']
    for r in records:
        filename, anchor = math_reference_for_record(r)
        lines.append(f'| {r.platform} | `{r.metric_key}` | {r.display_name} | {r.unit} | [{r.group}]({filename}#{anchor}) |')
    Path(output_dir, 'metric_math_index.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
