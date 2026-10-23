"""Compare every historical field; quantify new-to-old mappings separately."""
import argparse
import json
from pathlib import Path
import sys
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lrt_metric_schema import LEGACY_MAP


def compare(before, after):
    old = {(r['case'],r['beam']):r for r in before}
    new = {(r['case'],r['beam']):r for r in after}
    if set(old)!=set(new):
        raise ValueError('Beam identities differ')
    differences, tested = [], 0
    mappings = {key:dict(legacy=legacy, n=0, max_abs_difference=0., nonidentical=0)
                for key,legacy in LEGACY_MAP.items()}
    warning_changes = []
    for identity,a in old.items():
        b = new[identity]
        if a['sha256'] != b['sha256']:
            raise ValueError('Source hash changed')
        if a['warnings']!=b['warnings']:
            warning_changes.append(dict(case=identity[0],beam=identity[1],before=a['warnings'],after=b['warnings']))
        for key, x in a['values'].items():
            tested += 1
            y=b['values'].get(key)
            same = x==y or (isinstance(x,(int,float)) and isinstance(y,(int,float)) and math.isnan(x) and math.isnan(y))
            if not same:
                differences.append(dict(case=identity[0],beam=identity[1],key=key,before=x,after=y))
        for key,item in mappings.items():
            x,y = b['values'].get(key),a['values'].get(item['legacy'])
            if isinstance(x,(float,int)) and isinstance(y,(float,int)):
                d=abs(x-y);item['n']+=1; item['max_abs_difference']=max(item['max_abs_difference'],d)
                item['nonidentical']+=int(d>1e-10)
    return dict(beams=len(old), historical_values_tested=tested,
                changed_historical_values=len(differences),historical_fields_bitwise_equal=not differences,
                differences=differences,warning_changes=warning_changes,
                canonical_to_historical_mapping=mappings)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('before',type=Path);parser.add_argument('after',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    result=compare(json.loads(args.before.read_text(encoding='utf-8')),json.loads(args.after.read_text(encoding='utf-8')))
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='canonical_to_historical_mapping'},ensure_ascii=False)[:1800])
    if result['differences']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
