from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.psqa_spc import (
    calculate_spc_limits,
    classify_spc_points,
    harmonize_metric_values,
    load_psqa_records,
    summarize_psqa,
)
from validation.utils.serializers import write_csv_artifact, write_json_artifact


def run_psqa_spc_analysis(
    input_csv: Path | str,
    *,
    metric_key: str,
    output_dir: Path | str | None = None,
) -> dict[str, object]:
    records = load_psqa_records(input_csv)
    harmonized = harmonize_metric_values(records, metric_key=metric_key)
    z_values = [float(row["z_score"]) for row in harmonized]
    limits = calculate_spc_limits(z_values) if z_values else None
    spc_points = classify_spc_points(z_values, limits) if limits else []
    report = {
        "generated_at": _utc_now(),
        "metric_key": metric_key,
        "summary": {
            "records_total": len(records),
            "harmonized_records": len(harmonized),
            "out_of_control_points": sum(1 for row in spc_points if row["status"] == "out_of_control"),
            "psqa": summarize_psqa(records),
        },
        "limits": limits,
        "harmonized": harmonized,
        "spc_points": spc_points,
    }
    if output_dir is not None:
        output_root = Path(output_dir)
        report["artifacts"] = {
            "json": str(write_json_artifact(output_root / "psqa_spc_report.json", report)),
            "harmonized_csv": str(
                write_csv_artifact(
                    output_root / "psqa_spc_harmonized.csv",
                    harmonized,
                    fieldnames=[
                        "plan_id",
                        "platform",
                        "site_id",
                        "machine_id",
                        "metric_key",
                        "metric_value",
                        "gamma_3_3",
                        "harmonized_metric_key",
                        "harmonization_group",
                        "baseline_center",
                        "baseline_sigma",
                        "z_score",
                    ],
                )
            ),
            "spc_csv": str(
                write_csv_artifact(
                    output_root / "psqa_spc_points.csv",
                    spc_points,
                    fieldnames=["index", "value", "status", "rule"],
                )
            ),
        }
    return report


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PSQA/SPC complexity harmonization analysis.")
    parser.add_argument("--input-csv", required=True, help="CSV with plan_id/platform/machine_id/metric_key/metric_value/gamma_3_3 columns.")
    parser.add_argument("--metric-key", required=True, help="Metric key to harmonize and analyze.")
    parser.add_argument("--output-dir", default="run_reports/validation", help="Artifact output directory.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    run_psqa_spc_analysis(args.input_csv, metric_key=args.metric_key, output_dir=args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
