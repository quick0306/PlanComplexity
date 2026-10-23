"""Recompute a local Aurora cohort under the current version; never alter source plans."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aurora_svmat_lab.metrics import FIRST_PASS_METRIC_ORDER
from aurora_svmat_lab.service import analyze_plan_file
from formula_versions import AURORA_FORMULA_VERSION


def recompute(input_dir, output_dir, baseline_json=None):
    paths = sorted(Path(input_dir).rglob("*.dcm"))
    if not paths:
        raise ValueError("No DICOM plans found.")
    if len({p.stem for p in paths}) != len(paths):
        raise ValueError("Plan filename stems must be unique to align the baseline.")
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=False)
    baseline = json.loads(Path(baseline_json).read_text("utf-8")) if baseline_json else {}
    records, inputs, changed = [], [], {k: 0 for k in FIRST_PASS_METRIC_ORDER}
    missing = {key: 0 for key in FIRST_PASS_METRIC_ORDER}
    for index, path in enumerate(paths, 1):
        result = analyze_plan_file(path)
        if not result.supported:
            raise ValueError(f"Unsupported plan: {path.name}: {result.reason}")
        values = result.plan_metrics
        if set(values) != set(FIRST_PASS_METRIC_ORDER):
            raise ValueError("Incomplete or unexpected metric surface.")
        if values["mean_mcs_aurora"] is not None:
            if values["mcs_complexity_aurora"] != 1-values["mean_mcs_aurora"]:
                raise ValueError("MCS complement invariant failed.")
        if values["small_opening_fraction"] != values["mean_sas10"]:
            raise ValueError("Small-opening/SAS10 invariant failed.")
        if baseline and path.stem not in baseline:
            raise ValueError(f"Missing baseline case: {path.stem}")
        old = baseline.get(path.stem)
        for key, value in values.items():
            missing[key] += int(value is None)
            if old is not None:
                previous = old[key]
                changed[key] += int((value is None) != (previous is None) or
                                   (value is not None and previous is not None and
                                    abs(value-previous) > 1e-10))
        records.append(dict(case=path.stem, metric_formula_version=AURORA_FORMULA_VERSION, **values))
        inputs.append(dict(case=path.stem, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                           warnings=result.warnings))
        if index % 10 == 0:
            print(f"{index}/{len(paths)}", flush=True)
    for filename, content in [
        ("metrics.json", records), ("inputs_and_warnings.json", inputs),
        ("migration_summary.json", dict(formula_version=AURORA_FORMULA_VERSION,
          plans=len(records), metrics=len(FIRST_PASS_METRIC_ORDER),
          changed_plan_count_by_metric=changed if baseline else {},
          missing_plan_count_by_metric=missing,
          closure_threshold_mm=1.0,
          invariants=["small_opening_fraction == mean_sas10",
                      "mcs_complexity_aurora == 1-mean_mcs_aurora"])),
    ]:
        (destination/filename).write_text(json.dumps(content, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    with (destination/"metrics.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--baseline-json", type=Path)
    args = parser.parse_args()
    records = recompute(args.input_dir, args.output_dir, args.baseline_json)
    print(f"Recomputed {len(records)} plans using {AURORA_FORMULA_VERSION}", flush=True)


if __name__ == "__main__":
    main()
