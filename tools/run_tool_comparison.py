from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.run_reference_suite import run_reference_suite
from validation.utils.comparators import summarize_comparator_mapping
from validation.utils.loaders import load_comparator_mappings
from validation.utils.serializers import write_csv_artifact, write_json_artifact


def run_tool_comparison(
    profile: str,
    output_dir: Path | str | None = None,
    source_root: Path | str | None = None,
) -> dict[str, object]:
    reference_report = run_reference_suite(
        profile=profile,
        output_dir=output_dir,
        source_root=source_root,
    )
    mappings = load_comparator_mappings()
    comparisons = [
        summarize_comparator_mapping(mapping, reference_report["metrics"])
        for mapping in mappings
    ]
    report = {
        "profile": profile,
        "generated_at": _utc_now(),
        "comparisons": comparisons,
    }
    if output_dir is not None:
        output_root = Path(output_dir)
        report["artifacts"] = {
            "json": str(write_json_artifact(output_root / "comparator_statistics.json", report)),
            "csv": str(
                write_csv_artifact(
                    output_root / "comparator_statistics.csv",
                    comparisons,
                    fieldnames=_comparison_fieldnames(),
                )
            ),
        }
    return report


def _comparison_fieldnames() -> list[str]:
    return [
        "platform",
        "internal_metric",
        "comparator",
        "comparator_metric",
        "relationship",
        "status",
        "sample_count",
        "mae",
        "bias",
        "rmse",
        "notes",
    ]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run cross-tool comparator agreement summaries for validation metrics."
    )
    parser.add_argument("--profile", default="research", help="Validation profile key to execute.")
    parser.add_argument(
        "--output-dir",
        default="run_reports/validation",
        help="Directory where comparator statistics artifacts will be written.",
    )
    parser.add_argument(
        "--source-root",
        help="Optional repository root that contains the reference-case source_path inputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    run_tool_comparison(
        profile=args.profile,
        output_dir=args.output_dir,
        source_root=args.source_root,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
