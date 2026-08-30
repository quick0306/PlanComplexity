from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.clinical_readiness import run_clinical_readiness_gate
from validation.utils.serializers import write_csv_artifact, write_json_artifact


def run_clinical_readiness_report(output_dir: Path | str | None = None) -> dict[str, object]:
    report = run_clinical_readiness_gate(ROOT)
    report["generated_at"] = _utc_now()
    if output_dir is not None:
        output_root = Path(output_dir)
        report["artifacts"] = {
            "json": str(write_json_artifact(output_root / "clinical_readiness_gate.json", report)),
            "csv": str(
                write_csv_artifact(
                    output_root / "clinical_readiness_gate.csv",
                    report["checks"],
                    fieldnames=["check_id", "status", "blocking", "message"],
                )
            ),
        }
    return report


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run research/open-source/clinical readiness guardrails.")
    parser.add_argument("--output-dir", default="run_reports/validation", help="Artifact output directory.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when blocking readiness checks fail.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    report = run_clinical_readiness_report(output_dir=args.output_dir)
    if args.strict and report["summary"]["blocking_failures"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
