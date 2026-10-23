"""Read-only RTPLAN extraction to a versioned matrix, without Gamma analysis."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from DicomParse.dicom_rt import RTPlan
from halcyon_dual_layer_metrics import _calculate_beam_paper_metrics
from lrt_three_layer import calculate_lrt_beam_metrics
from lrt_metric_schema import EXPORT_KEYS, CANDIDATE_KEYS, REFERENCE_KEYS, SCHEMA_VERSION


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--recomputed-core',type=Path,
                        help='Reuse validated post-change core results instead of recalculating')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    inputs=json.loads(args.manifest.read_text(encoding='utf-8'))
    cached = ({(r['case'],r['beam']):r for r in json.loads(args.recomputed_core.read_text(encoding='utf-8'))}
              if args.recomputed_core else None)
    records=[]; warning_rows=[]
    for row in inputs:
        path=Path(row['path'])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('RTPLAN source hash mismatch')
        if cached is not None:
            result=cached[(row['case'],row['beam'])]
            if result['sha256']!=row['sha256']:
                raise ValueError('Core source hash mismatch')
            values={key:result['values'][key] for key in EXPORT_KEYS}
            warnings=result['warnings']
        else:
            plan=RTPlan(str(path),full_precision=True).to_plan_dict()
            beam=next(b for k,b in plan['beams'].items() if int(k)==int(row['beam']))
            old=_calculate_beam_paper_metrics(beam)
            values,warnings=calculate_lrt_beam_metrics(beam,pr_system=old.values.get('ethos_penumbra_ratio') if old else None)
        record=dict(case=row['case'],beam=row['beam'],**values)
        records.append(record)
        if warnings:
            warning_rows.append(dict(case=row['case'],beam=row['beam'],warnings=warnings))
    def write_csv(filename,keys):
        with (args.output/filename).open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['case','beam',*keys],extrasaction='ignore')
            writer.writeheader();writer.writerows(records)
    write_csv('metric_matrix_51.csv',EXPORT_KEYS)
    write_csv('candidate_matrix_50.csv',CANDIDATE_KEYS)
    write_csv('system_reference.csv',REFERENCE_KEYS)
    metadata=dict(schema=SCHEMA_VERSION, beams=len(records), fields=51, default_candidates=50,
                  families={'Eff':16,'D':16,'P':16,'delivery':2,'system_reference':1},
                  system_source='legacy DICOM report-profile reconstruction; not observed PDF',
                  excluded_historical=['ethos_sas10','ethos_one_minus_mcs'],
                  warnings=warning_rows,
                  missing_per_field={k:sum(r[k] is None for r in records) for k in EXPORT_KEYS})
    (args.output/'schema.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    (args.output/'metrics.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(metadata,ensure_ascii=False)[:1200])


if __name__=='__main__':
    main()
