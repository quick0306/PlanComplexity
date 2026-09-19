from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.utils.loaders import load_reference_manifest
from validation.utils.loaders import load_expected_metrics_provenance
from validation.utils.loaders import load_validation_profiles
from validation.utils.loaders import verify_reference_source_checksum
from validation_models import ReferenceCaseRecord
from validation_runtime import analyze_validation_case


_CASE_SETS = {"all", "canonical", "edge"}


def freeze_case(
    case: ReferenceCaseRecord,
    *,
    source_root: Path | str | None = None,
    allow_formula_version_change: bool = False,
    allow_metric_schema_change: bool = False,
) -> Path:
    resolved_source_path = verify_reference_source_checksum(case, source_root=source_root)
    previous_provenance = load_expected_metrics_provenance(case)
    if previous_provenance != case.expected_metrics_provenance:
        raise ValueError(f"Baseline provenance changed since loading '{case.case_id}'; reload the manifest.")
    record = analyze_validation_case(str(resolved_source_path), case.domain)
    if record.domain != case.domain or record.mode != case.expected_mode:
        raise ValueError(f"Analysis domain/mode mismatch for reference case '{case.case_id}'.")
    if record.supported != case.expected_supported:
        raise ValueError(f"Analysis supported state mismatch for reference case '{case.case_id}'.")
    formula_version = record.metadata.get("metric_formula_version")
    if formula_version is not None and (
        not isinstance(formula_version, str) or not formula_version.strip()
    ):
        raise ValueError(f"Invalid runtime formula version for '{case.case_id}'.")
    if case.expected_formula_version is not None and formula_version != case.expected_formula_version:
        raise ValueError(
            f"Runtime formula version {formula_version!r} does not match required formula version "
            f"{case.expected_formula_version!r} for '{case.case_id}'."
        )
    previous_version = previous_provenance.formula_version if previous_provenance else None
    if previous_version is not None and formula_version is None:
        raise ValueError(f"Cannot remove formula-version provenance for '{case.case_id}'.")
    if formula_version != previous_version and not allow_formula_version_change:
        raise ValueError(
            f"Refusing formula-version change for '{case.case_id}' from {previous_version!r} to "
            f"{formula_version!r}; audit the migration and use --allow-formula-version-change."
        )
    serializable_metrics = {
        key: _json_ready(value)
        for key, value in sorted(record.metrics.items())
    }
    if case.expected_metrics_path.exists() and set(serializable_metrics) != set(case.expected_metrics):
        if not allow_metric_schema_change:
            added = sorted(set(serializable_metrics) - set(case.expected_metrics))
            removed = sorted(set(case.expected_metrics) - set(serializable_metrics))
            raise ValueError(
                f"Refusing metric schema change for '{case.case_id}': added {added}, removed {removed}; "
                "audit the migration and use --allow-metric-schema-change."
            )
    metrics_bytes = (json.dumps(serializable_metrics, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    provenance_bytes = None
    if formula_version is not None:
        provenance = {
            "schema_version": 1,
            "formula_version": formula_version,
            "case_id": case.case_id,
            "domain": case.domain,
            "mode": case.expected_mode,
            "source_checksum": case.checksum.lower(),
            "expected_metrics_checksum": hashlib.sha256(metrics_bytes).hexdigest(),
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
        provenance_bytes = (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")
    # Complete all validation and serialization before replacing either artifact.
    # Write provenance first: an interrupted first-version migration must never
    # leave changed scalars that still look like an unversioned legacy baseline.
    # A mismatched pair is rejected by the loader rather than accepted as green.
    case.expected_metrics_path.parent.mkdir(parents=True, exist_ok=True)
    if provenance_bytes is not None:
        case.expected_metrics_path.with_name("expected_metrics_provenance.json").write_bytes(provenance_bytes)
    case.expected_metrics_path.write_bytes(metrics_bytes)
    return case.expected_metrics_path


def select_reference_cases(
    manifest: list[ReferenceCaseRecord],
    *,
    case_ids: list[str] | None = None,
    all_cases: bool = False,
    case_set: str | None = None,
) -> list[ReferenceCaseRecord]:
    if case_set is not None and case_set not in _CASE_SETS:
        raise ValueError(f"Unknown case set '{case_set}'. Expected one of: {', '.join(sorted(_CASE_SETS))}.")
    if all_cases and (case_ids or case_set):
        raise ValueError("Use --all, --case-set, or --case-id, not multiple selectors.")
    if case_set and case_ids:
        raise ValueError("Use either --case-set or one or more --case-id values, not both.")
    if not all_cases and not case_set and not case_ids:
        raise ValueError("Select at least one case with --case-id, --case-set, or --all.")

    manifest_by_id = {case.case_id: case for case in manifest}
    if all_cases or case_set == "all":
        return [manifest_by_id[case_id] for case_id in sorted(manifest_by_id)]
    if case_set:
        return [
            case
            for case in sorted(manifest, key=lambda item: item.case_id)
            if case.case_class == case_set
        ]

    selected_cases = []
    for case_id in case_ids or []:
        case = manifest_by_id.get(case_id)
        if case is None:
            raise ValueError(f"Unknown reference case '{case_id}'.")
        selected_cases.append(case)
    return selected_cases


def validate_profile_key(profile_key: str) -> None:
    profiles = {profile.profile_key for profile in load_validation_profiles()}
    if profile_key not in profiles:
        raise ValueError(f"Unknown validation profile '{profile_key}'.")


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
        "--case-set",
        choices=sorted(_CASE_SETS),
        help="Refresh a named case set such as 'canonical' or 'edge'.",
    )
    parser.add_argument(
        "--profile",
        default="research",
        help="Validation profile key used to validate the freeze command context.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm that checked-in expected metrics should be overwritten.",
    )
    parser.add_argument(
        "--allow-formula-version-change",
        action="store_true",
        help="Allow an independently audited formula-version migration, including first versioning.",
    )
    parser.add_argument(
        "--allow-metric-schema-change",
        action="store_true",
        help="Allow an independently audited change to the expected metric key set.",
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

    try:
        validate_profile_key(args.profile)
        selected_cases = select_reference_cases(
            load_reference_manifest(),
            case_ids=args.case_ids,
            all_cases=args.all,
            case_set=args.case_set,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    for case in selected_cases:
        output_path = freeze_case(
            case,
            source_root=args.source_root,
            allow_formula_version_change=args.allow_formula_version_change,
            allow_metric_schema_change=args.allow_metric_schema_change,
        )
        print(f"froze {case.case_id} -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
