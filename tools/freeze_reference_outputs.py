from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.utils.loaders import load_reference_manifest
from validation_models import ReferenceCaseRecord
from validation_runtime import analyze_validation_case


def freeze_case(case: ReferenceCaseRecord, *, source_root: Path | str | None = None) -> Path:
    resolved_source_path = _resolve_source_path(case.source_path, source_root=source_root)
    _verify_checksum(case, resolved_source_path)
    record = analyze_validation_case(str(resolved_source_path), case.domain)
    serializable_metrics = {
        key: _json_ready(value)
        for key, value in sorted(record.metrics.items())
    }
    case.expected_metrics_path.parent.mkdir(parents=True, exist_ok=True)
    case.expected_metrics_path.write_text(
        json.dumps(serializable_metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return case.expected_metrics_path


def _resolve_source_path(source_path: str, *, source_root: Path | str | None = None) -> Path:
    relative_path = Path(source_path)
    repo_root = Path(source_root) if source_root is not None else ROOT
    candidate = repo_root / relative_path
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"Could not resolve reference-case source path '{source_path}' under '{repo_root}'."
    )


def _verify_checksum(case: ReferenceCaseRecord, source_path: Path) -> None:
    observed = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if observed.lower() != case.checksum.lower():
        raise ValueError(
            f"Checksum mismatch for '{case.case_id}': expected {case.checksum}, observed {observed}."
        )


def _json_ready(value: object) -> float | int | str | None:
    item_method = getattr(value, "item", None)
    if callable(item_method):
        value = item_method()
    if isinstance(value, bool) or not isinstance(value, (int, float, str)) and value is not None:
        raise TypeError(f"Unsupported metric value for JSON serialization: {value!r}")
    return value


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze checked-in expected metrics for selected validation reference cases."
    )
    parser.add_argument(
        "--case-id",
        action="append",
        dest="case_ids",
        help="Reference case id to refresh. Repeat for multiple cases.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Refresh every checked-in reference case.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm that checked-in expected metrics should be overwritten.",
    )
    parser.add_argument(
        "--source-root",
        help="Optional repository root that contains the manifest source_path inputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if not args.yes:
        raise SystemExit("Refusing to overwrite checked-in expected metrics without --yes.")
    if args.all and args.case_ids:
        raise SystemExit("Use either --all or one or more --case-id values, not both.")
    if not args.all and not args.case_ids:
        raise SystemExit("Select at least one case with --case-id, or pass --all.")

    manifest = load_reference_manifest()
    manifest_by_id = {case.case_id: case for case in manifest}
    selected_ids = sorted(manifest_by_id) if args.all else args.case_ids
    for case_id in selected_ids:
        case = manifest_by_id.get(case_id)
        if case is None:
            raise SystemExit(f"Unknown reference case '{case_id}'.")
        output_path = freeze_case(case, source_root=args.source_root)
        print(f"froze {case.case_id} -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
