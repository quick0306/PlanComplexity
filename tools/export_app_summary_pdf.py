"""Regenerate the tracked one-page application overview from current definitions."""
from pathlib import Path
import argparse
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from formula_versions import formula_version_for_mode
from metric_definition_catalog import build_metric_definition_catalog


def export_app_summary_pdf(output_path):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SummaryBody', fontName='Helvetica', fontSize=9,
                              leading=12, spaceAfter=5))
    styles.add(ParagraphStyle(name='SummaryHeading', fontName='Helvetica-Bold', fontSize=11,
                              leading=14, spaceBefore=10, spaceAfter=5,
                              textColor=colors.HexColor('#245576')))
    story = [Paragraph('PlanComplexity / PyUCoMX', styles['Title']),
             Paragraph('Current application summary - research use only', styles['SummaryBody'])]

    def section(title, text):
        story.extend([Paragraph(title, styles['SummaryHeading']),
                      Paragraph(escape(text), styles['SummaryBody'])])

    section('Purpose and workflow',
            'Local RTPLAN complexity analysis for medical-physics research. The Tk desktop GUI '
            'supports single files, folder batches, AUTO or explicit modes, metric notes, warnings '
            'and CSV export. READY means the analysis path is supported; individual metrics may still be unavailable.')
    records = build_metric_definition_catalog()
    rows = [[Paragraph(x, styles['SummaryBody']) for x in ['Mode', 'Catalog keys', 'Current formula version']]]
    for mode in ['VMAT_IMRT', 'TOMO', 'CYBERKNIFE_MLC', 'AURORA']:
        rows.append([Paragraph(escape(x), styles['SummaryBody']) for x in
                     [mode, str(sum(r.platform == mode for r in records)), formula_version_for_mode(mode)]])
    table = Table(rows, colWidths=[37*mm, 25*mm, 111*mm])
    table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#eaf1f6')),
                               ('VALIGN', (0,0), (-1,-1), 'TOP'),
                               ('LINEBELOW', (0,0), (-1,0), .5, colors.HexColor('#245576'))]))
    story.extend([Spacer(1, 2*mm), table])
    section('Metric boundaries',
            'Catalog counts include layer variants and container keys; actual runtime outputs depend on geometry. '
            'Halcyon/Ethos native, effective and nonphysical stacked representations have distinct definitions. '
            'CyberKnife is a six-metric MLC subset. TOMO motion is planned, not measured delivery.')
    section('Aurora: 77 keys and open-only physical aperture metrics',
            'The existing 70 research/proxy keys are retained, plus seven V4 descriptors: mean_ba, mean_bi, '
            'mean_ca, mean_sas5, mean_sas10, mean_mcs_aurora and mcs_complexity_aurora. V4 uses real leaf '
            'boundaries, A/B banks, dual-layer intersection and X/Y jaw clipping. All seven means exclude '
            'area-zero endpoints and renormalize retained MU weights. SAS/LSV exclude closed gaps. '
            'Exclusion count/weight fraction and missing-MU fallback are disclosed in warnings. No open endpoint '
            'makes all seven unavailable. Endpoint sampling is not continuous delivery reconstruction. '
            'The adapted MCS is not classic McNiven MCS; historical V4 versions must not be mixed.')
    section('Run, export and package',
            'Install: python -m pip install -r requirements.txt. GUI: python ucomx.py. '
            'Single-plan console: python main.py --input-file path/to/plan.dcm. Main GUI/service export writes '
            'results.csv and results_columns.csv. The standalone aurora_svmat_cli.py can export separate plan, '
            'beam and trajectory tables. Windows packaging uses tools/build_windows_exe.ps1 and PyUCoMX.spec, '
            'producing dist/PyUCoMX.exe. Rebuilding does not publish a GitHub release.')
    section('Reproducibility and documentation',
            'Keep input identity/hash, source commit, mode, formula version and precision with study results. '
            'Use full_precision=True for VMAT/IMRT and CyberKnife validation. CSV/DICOM clinical data remain local. '
            'Current instructions: docs/user_guide.md and docs/README.md. Full formulas: '
            'docs/metric_formula_contracts.md; Aurora details: docs/aurora_aperture_metrics.md. '
            'Regression results are technical evidence, not clinical validation.')
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=16*mm, bottomMargin=16*mm,
                            title='PlanComplexity current application summary', author='PlanComplexity')
    doc.build(story)
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-path', default=str(ROOT/'output/pdf/plancomplexity_app_summary.pdf'))
    export_app_summary_pdf(parser.parse_args().output_path)
