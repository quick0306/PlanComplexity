from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.clinical_endpoints import associate_binary_endpoint, load_endpoint_records
from validation.utils.serializers import write_json_artifact


def run_clinical_endpoint_association(
    input_csv: Path | str,
    *,
    metric_key: str,
    endpoint_key: str,
    output_dir: Path | str | None = None,
) -> dict[str, object]:
    records = load_endpoint_records(input_csv)
    association = associate_binary_endpoint(records, metric_key=metric_key, endpoint_key=endpoint_key)
    report = {
        "generated_at": _utc_now(),
        "association": association,
        "clinical_status": "association-only; not clinical deployment ready",
    }
    if output_dir is not None:
        report["artifacts"] = {
            "json": str(write_json_artifact(Path(output_dir) / "clinical_endpoint_association.json", report))
        }
    return report


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run metric association against a binary clinical endpoint.")
    parser.add_argument("--input-csv", required=True, help="CSV with metric and binary endpoint columns.")
    parser.add_argument("--metric-key", required=True, help="Column containing the metric value.")
    parser.add_argument("--endpoint-key", required=True, help="Column containing 0/1 endpoint outcome.")
    parser.add_argument("--output-dir", default="run_reports/validation", help="Artifact output directory.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    run_clinical_endpoint_association(
        args.input_csv,
        metric_key=args.metric_key,
        endpoint_key=args.endpoint_key,
        output_dir=args.output_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
