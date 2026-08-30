from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.paper_reproduction import build_paper_reproduction_table
from validation.utils.serializers import write_csv_artifact, write_json_artifact


def build_paper_reproduction_report(output_dir: Path | str | None = None) -> dict[str, object]:
    report = build_paper_reproduction_table()
    report["generated_at"] = _utc_now()
    if output_dir is not None:
        output_root = Path(output_dir)
        report["artifacts"] = {
            "json": str(write_json_artifact(output_root / "paper_reproduction_table.json", report)),
            "csv": str(
                write_csv_artifact(
                    output_root / "paper_reproduction_table.csv",
                    report["rows"],
                    fieldnames=[
                        "paper",
                        "platform",
                        "metric_key",
                        "group_key",
                        "validation_level",
                        "comparison_class",
                        "status",
                    ],
                )
            ),
        }
    return report


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build paper metric reproduction coverage table.")
    parser.add_argument("--output-dir", default="run_reports/validation", help="Artifact output directory.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    build_paper_reproduction_report(output_dir=args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
