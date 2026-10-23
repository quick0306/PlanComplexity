"""Freeze all existing core outputs on a fixed RTPLAN/beam manifest."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from DicomParse.dicom_rt import RTPlan
from analysis_helpers import calculate_core_metrics_with_warnings
from ucomx_service import flatten_metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    rows = json.loads(args.manifest.read_text(encoding='utf-8'))
    result = []
    last_path = None
    for index, row in enumerate(rows):
        path = Path(row['path'])
        if str(path) != last_path:
            if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
                raise ValueError('RTPLAN source hash mismatch')
            plan = RTPlan(str(path), full_precision=True).to_plan_dict()
            last_path = str(path)
        key = next(k for k in plan['beams'] if int(k) == int(row['beam']))
        beam = plan['beams'][key]
        selected = dict(plan, beams={key: beam}, Plan_MU=float(beam['MU']), beam_number=1)
        metrics, warnings = calculate_core_metrics_with_warnings(selected, full_precision=True)
        # Only numeric metrics go into this oracle; warnings are retained separately.
        result.append(dict(case=row['case'], beam=row['beam'], sha256=row['sha256'],
                           values=flatten_metrics(metrics), warnings=warnings))
        if (index + 1) % 25 == 0:
            print(f'{index + 1}/{len(rows)}', flush=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Saved {len(result)} beams', flush=True)


if __name__ == '__main__':
    main()
