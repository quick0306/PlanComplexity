"""Pair current Ethos PDF PR observations with unchanged and new geometry PR.

Input: the original verified batch manifest JSON (manifest + rows). Pairing uses
unique beam MU at PDF precision; plan labels may differ, retained as caveats.
No observed report value is filled from a geometry reconstruction.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from scipy.stats import pearsonr, spearmanr
import pymupdf

from DicomParse.dicom_rt import RTPlan
from halcyon_dual_layer_metrics import _calculate_beam_paper_metrics
from lrt_three_layer import calculate_lrt_beam_metrics


def agreement(observed, calculated):
    """Differences and limits of agreement are in percentage points."""
    x, y = np.asarray(observed, float), np.asarray(calculated, float)
    if x.shape != y.shape or x.ndim != 1 or len(x) < 2 or not np.all(np.isfinite([x,y])):
        raise ValueError('At least two finite paired observations are required')
    diff = y-x
    sd = float(np.std(diff, ddof=1))
    return dict(n=len(x), pearson=float(pearsonr(x,y).statistic),
                spearman=float(spearmanr(x,y).statistic), bias_pp=float(diff.mean()),
                sd_pp=sd, mae_pp=float(np.abs(diff).mean()),
                rmse_pp=float(np.sqrt(np.mean(diff**2))),
                maximum_abs_error_pp=float(np.abs(diff).max()),
                max_relative_error=float(np.max(np.divide(np.abs(diff), np.abs(x),
                                             out=np.zeros_like(x), where=x!=0))),
                loa_lower_pp=float(diff.mean()-1.96*sd), loa_upper_pp=float(diff.mean()+1.96*sd),
                within_display_rounding=int(np.count_nonzero(np.abs(diff)<=.05+1e-9)))


def read_report(path):
    """Extract complete numeric MLC-complexity rows from the current PDF bytes."""
    pattern = re.compile(r'([^\n]+)\n([\d.]+) MU\n([\d.]+) 1/mm\n([\d.]+)\n([\d.]+) %\n([\d.]+) %')
    with pymupdf.open(path) as doc:
        rows = []
        for index, page in enumerate(doc):
            content = page.get_text()
            if 'MLC 复杂度' in content:
                for name,mu,edge,mcs,sas,pr in pattern.findall(content):
                    rows.append(dict(name=name, mu=float(mu), pr_pct=float(pr), page=index+1))
    if not rows:
        raise ValueError(f'No supported complexity table in {path}')
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('batch_manifest', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = json.loads(args.batch_manifest.read_text(encoding='utf-8'))
    records, provenance = [], []
    for item in source['manifest']:
        rp, pdf = Path(item['rp']), Path(item['pdf'])
        for path, key in [(rp,'sha256_rp'), (pdf,'sha256_pdf')]:
            if hashlib.sha256(path.read_bytes()).hexdigest() != item[key]:
                raise ValueError(f'Source bytes differ from verified manifest: {key}')
        pdf_rows = read_report(pdf)
        plan = RTPlan(str(rp), full_precision=True).to_plan_dict()
        beam_records = []
        for key, beam in plan['beams'].items():
            if beam.get('TreatmentDeliveryType') != 'TREATMENT' or beam.get('MU',0)<=0:
                continue
            hits = [r for r in pdf_rows if r['name']!='计划' and abs(r['mu']-beam['MU']) <= .05+1e-8]
            if len(hits)!=1:
                raise ValueError(f'Ambiguous beam/PDF MU pairing: {item["case"]}, beam {key}')
            old = _calculate_beam_paper_metrics(beam)
            new, warnings = calculate_lrt_beam_metrics(beam)
            if old is None or warnings:
                raise ValueError(f'Unsupported PR calculation: {warnings}')
            row = dict(case=item['case'], beam=str(key), mu=float(beam['MU']),
                       PR_original_pct=100*old.values['ethos_penumbra_ratio'],
                       PR_Eff_pct=100*new['PR_Eff'], PR_Ethos_observed_pct=hits[0]['pr_pct'],
                       PR_D_pct=100*new['PR_D'], PR_P_pct=100*new['PR_P'],
                       report_page=hits[0]['page'], report_name=hits[0]['name'])
            row['difference_pp'] = row['PR_Eff_pct']-row['PR_Ethos_observed_pct']
            beam_records.append(row)
            records.append(row)
        summary = [r for r in pdf_rows if r['name']=='计划']
        if len(summary)!=1 or abs(summary[0]['mu']-sum(r['mu'] for r in beam_records))>.05+1e-8:
            raise ValueError('Plan MU pairing failed')
        plan_row = dict(case=item['case'], beam='plan', mu=sum(r['mu'] for r in beam_records),
                        report_page=summary[0]['page'], report_name='计划',
                        PR_Ethos_observed_pct=summary[0]['pr_pct'])
        for column in ['PR_original_pct','PR_Eff_pct','PR_D_pct','PR_P_pct']:
            plan_row[column] = float(np.average([r[column] for r in beam_records], weights=[r['mu'] for r in beam_records]))
        plan_row['difference_pp'] = plan_row['PR_Eff_pct']-plan_row['PR_Ethos_observed_pct']
        records.append(plan_row)
        provenance.append(dict(case=item['case'], sha256_rp=item['sha256_rp'], sha256_pdf=item['sha256_pdf'],
                               rp_label=item['rp_label'], pdf_label=item['pdf_label'],
                               pairing=item['pairing'], report_version=item['report_version']))
    beams = [r for r in records if r['beam']!='plan']
    plans = [r for r in records if r['beam']=='plan']
    metrics = {name:agreement([r['PR_Ethos_observed_pct'] for r in subset], [r['PR_Eff_pct'] for r in subset])
               for name,subset in [('beams',beams), ('plans',plans)]}
    metrics['max_new_vs_original_pp'] = max(abs(r['PR_Eff_pct']-r['PR_original_pct']) for r in records)
    metrics['largest_differences'] = sorted(beams,key=lambda r:abs(r['difference_pp']),reverse=True)[:5]
    (args.output/'agreement.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
    (args.output/'source_provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
    with (args.output/'paired_pr.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family':'Times New Roman','font.size':13})
    x=np.array([r['PR_Ethos_observed_pct'] for r in beams]); y=np.array([r['PR_Eff_pct'] for r in beams])
    fig, axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    axes[0].scatter(x,y,color='#24567a',s=35)
    axes[0].plot([x.min()-1,x.max()+1],[x.min()-1,x.max()+1],color='#555555',ls='--')
    axes[0].set(xlabel='Ethos report PR (%)',ylabel='Recomputed PR-Eff (%)',title=f'A  Paired beams (n={len(x)})')
    diff=y-x; avg=(y+x)/2; m=metrics['beams']
    axes[1].scatter(avg,diff,color='#24567a',s=35)
    for level,style in [(m['bias_pp'],'-'),(m['loa_lower_pp'],'--'),(m['loa_upper_pp'],'--')]:
        axes[1].axhline(level,color='#9a4b30',ls=style)
    axes[1].axhspan(-.05,.05,color='#dde8ee',alpha=.5,zorder=-1)
    axes[1].set(xlabel='Mean PR (%)',ylabel='PR-Eff minus report (percentage points)',title='B  Bland-Altman agreement')
    fig.savefig(args.output/'pr_agreement.png',dpi=220)
    plt.close(fig)
    print(json.dumps(metrics,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
