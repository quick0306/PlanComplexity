from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.comparator_matrix import build_comparator_matrix
from validation.utils.serializers import write_csv_artifact, write_json_artifact


def build_comparator_matrix_report(output_dir: Path | str | None = None) -> dict[str, object]:
    report = build_comparator_matrix()
    report["generated_at"] = _utc_now()
    if output_dir is not None:
        output_root = Path(output_dir)
        report["artifacts"] = {
            "json": str(write_json_artifact(output_root / "comparator_matrix.json", report)),
            "platform_csv": str(
                write_csv_artifact(
                    output_root / "comparator_matrix_by_platform.csv",
                    report["platforms"],
                    fieldnames=[
                        "platform",
                        "metric_count",
                        "mapped_metrics",
                        "unmapped_metrics",
                        "exact_equivalent_mappings",
                        "derived_equivalent_mappings",
                        "association_only_mappings",
                        "not_comparable_mappings",
                        "sample_count",
                    ],
                )
            ),
            "metric_csv": str(
                write_csv_artifact(
                    output_root / "comparator_matrix_by_metric.csv",
                    report["metrics"],
                    fieldnames=[
                        "platform",
                        "metric_key",
                        "group_key",
                        "validation_level",
                        "comparison_class",
                        "coverage_status",
                        "comparator",
                        "mapping_provenance",
                        "verified_sample_count",
                        "comparator_metric",
                        "relationship",
                        "sample_count",
                    ],
                )
            ),
        }
    return report


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build comparator coverage matrix artifacts.")
    parser.add_argument(
        "--output-dir",
        default="run_reports/validation",
        help="Directory where comparator matrix artifacts will be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    build_comparator_matrix_report(output_dir=args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
