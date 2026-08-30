from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.formula_oracles import run_formula_oracles
from validation.utils.serializers import write_csv_artifact, write_json_artifact


def run_formula_oracle_report(output_dir: Path | str | None = None) -> dict[str, object]:
    report = run_formula_oracles()
    report["generated_at"] = _utc_now()
    if output_dir is not None:
        output_root = Path(output_dir)
        report["artifacts"] = {
            "json": str(write_json_artifact(output_root / "formula_oracles.json", report)),
            "csv": str(
                write_csv_artifact(
                    output_root / "formula_oracles.csv",
                    report["oracles"],
                    fieldnames=[
                        "oracle_id",
                        "platform",
                        "metric_key",
                        "status",
                        "expected",
                        "observed",
                        "abs_diff",
                        "abs_tol",
                        "notes",
                    ],
                )
            ),
        }
    return report


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run independent hand-case formula oracles.")
    parser.add_argument(
        "--output-dir",
        default="run_reports/validation",
        help="Directory where formula oracle artifacts will be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = run_formula_oracle_report(output_dir=args.output_dir)
    return 0 if report["summary"]["formula_oracle_green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
