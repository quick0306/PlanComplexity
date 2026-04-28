from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse

from validation.utils.loaders import (
    load_metric_specs,
    load_reference_manifest,
    load_validation_profiles,
    verify_reference_source_checksum,
)
from validation.utils.serializers import write_csv_artifact, write_json_artifact
from validation.utils.tolerances import compare_exact, resolve_metric_tolerances
from validation_runtime import analyze_validation_case


def run_reference_suite(
    profile: str,
    output_dir: Path | str | None = None,
    source_root: Path | str | None = None,
) -> dict[str, object]:
    profile_record = _load_profile(profile)
    spec_index = {
        (spec.platform, spec.metric_key): spec
        for spec in load_metric_specs()
    }
    cases = load_reference_manifest()

    case_rows: list[dict[str, object]] = []
    metric_rows: list[dict[str, object]] = []
    for case in cases:
        resolved_source_path = verify_reference_source_checksum(case, source_root=source_root)
        observed = analyze_validation_case(str(resolved_source_path), case.domain)
        case_metric_rows = _evaluate_case_metrics(case, observed.metrics, spec_index, profile_record)
        metric_rows.extend(case_metric_rows)
        exact_failures = sum(
            1
            for row in case_metric_rows
            if row["comparison_class"] == "exact-equivalent" and row["status"] == "fail"
        )
        case_rows.append(
            {
                "case_id": case.case_id,
                "domain": case.domain,
                "case_class": case.case_class,
                "device_or_tps": case.device_or_tps,
                "supported": observed.supported,
                "reason": observed.reason,
                "warnings": " | ".join(observed.warnings),
                "total_metrics": len(case_metric_rows),
                "passes": sum(1 for row in case_metric_rows if row["status"] == "pass"),
                "failures": sum(1 for row in case_metric_rows if row["status"] == "fail"),
                "skipped": sum(1 for row in case_metric_rows if row["status"] == "skipped"),
                "reference_exact_green": (
                    exact_failures == 0 if profile_record.require_reference_exact_green else None
                ),
            }
        )

    exact_metric_rows = [
        row
        for row in metric_rows
        if row["comparison_class"] == "exact-equivalent"
    ]
    exact_failures = sum(1 for row in exact_metric_rows if row["status"] == "fail")
    report = {
        "profile": profile_record.profile_key,
        "generated_at": _utc_now(),
        "summary": {
            "cases_total": len(case_rows),
            "metrics_total": len(metric_rows),
            "exact_metrics_total": len(exact_metric_rows),
            "exact_failures": exact_failures,
            "reference_exact_green": (
                exact_failures == 0 if profile_record.require_reference_exact_green else None
            ),
        },
        "cases": case_rows,
        "metrics": metric_rows,
    }
    if output_dir is not None:
        output_root = Path(output_dir)
        report["artifacts"] = {
            "json": str(write_json_artifact(output_root / "reference_case_results.json", report)),
            "csv": str(
                write_csv_artifact(
                    output_root / "reference_case_results.csv",
                    metric_rows,
                    fieldnames=_metric_fieldnames(),
                )
            ),
        }
    return report


def _evaluate_case_metrics(case, observed_metrics, spec_index, profile_record):
    rows: list[dict[str, object]] = []
    for metric_key, expected_value in sorted(case.expected_metrics.items()):
        metric_spec = spec_index.get((case.domain, metric_key))
        if metric_spec is None:
            raise ValueError(
                f"Reference case '{case.case_id}' references unknown metric '{metric_key}' for domain '{case.domain}'."
            )
        if metric_spec.group_key not in profile_record.group_keys:
            continue
        if (
            metric_spec.comparison_class == "association-only"
            and not profile_record.include_association_only_in_core_gate
        ):
            continue
        tolerance = resolve_metric_tolerances(case, metric_spec, profile_record)
        observed_value = observed_metrics.get(metric_key)
        if tolerance["skip"]:
            rows.append(
                {
                    "case_id": case.case_id,
                    "domain": case.domain,
                    "metric_key": metric_key,
                    "status": "skipped",
                    "expected": expected_value,
                    "observed": observed_value,
                    "abs_tol": tolerance["abs_tol"],
                    "rel_tol": tolerance["rel_tol"],
                    "abs_diff": None,
                    "rel_diff": None,
                    "comparison_class": metric_spec.comparison_class,
                    "validation_level": metric_spec.validation_level,
                    "group_key": metric_spec.group_key,
                    "gate_included": False,
                    "note": tolerance["reason"],
                }
            )
            continue
        if metric_spec.comparison_class != "exact-equivalent":
            rows.append(
                {
                    "case_id": case.case_id,
                    "domain": case.domain,
                    "metric_key": metric_key,
                    "status": "skipped",
                    "expected": expected_value,
                    "observed": observed_value,
                    "abs_tol": tolerance["abs_tol"],
                    "rel_tol": tolerance["rel_tol"],
                    "abs_diff": None,
                    "rel_diff": None,
                    "comparison_class": metric_spec.comparison_class,
                    "validation_level": metric_spec.validation_level,
                    "group_key": metric_spec.group_key,
                    "gate_included": False,
                    "note": _comparison_class_skip_reason(metric_spec.comparison_class),
                }
            )
            continue

        comparison = compare_exact(
            expected_value,
            observed_value,
            float(tolerance["abs_tol"]),
            float(tolerance["rel_tol"]),
        )
        rows.append(
            {
                "case_id": case.case_id,
                "domain": case.domain,
                "metric_key": metric_key,
                "status": "pass" if comparison["pass"] else "fail",
                "expected": comparison["expected"],
                "observed": comparison["observed"],
                "abs_tol": tolerance["abs_tol"],
                "rel_tol": tolerance["rel_tol"],
                "abs_diff": comparison["abs_diff"],
                "rel_diff": comparison["rel_diff"],
                "comparison_class": metric_spec.comparison_class,
                "validation_level": metric_spec.validation_level,
                "group_key": metric_spec.group_key,
                "gate_included": True,
                "note": "",
            }
        )
    return rows


def _load_profile(profile_key: str):
    profiles = {profile.profile_key: profile for profile in load_validation_profiles()}
    try:
        return profiles[profile_key]
    except KeyError as exc:
        raise ValueError(f"Unknown validation profile '{profile_key}'.") from exc


def _metric_fieldnames() -> list[str]:
    return [
        "case_id",
        "domain",
        "metric_key",
        "status",
        "expected",
        "observed",
        "abs_tol",
        "rel_tol",
        "abs_diff",
        "rel_diff",
        "comparison_class",
        "validation_level",
        "group_key",
        "gate_included",
        "note",
    ]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _comparison_class_skip_reason(comparison_class: str) -> str:
    return {
        "association-only": "Requires association-oriented downstream evaluation.",
        "derived-equivalent": "Deferred to cross-tool comparison statistics.",
        "not-comparable": "Not eligible for exact reference-case comparison.",
    }.get(comparison_class, "Not evaluated in the exact reference suite.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the validation reference suite against checked-in reference cases."
    )
    parser.add_argument("--profile", default="research", help="Validation profile key to execute.")
    parser.add_argument(
        "--output-dir",
        default="run_reports/validation",
        help="Directory where JSON/CSV reference-suite artifacts will be written.",
    )
    parser.add_argument(
        "--source-root",
        help="Optional repository root that contains the manifest source_path inputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    run_reference_suite(
        profile=args.profile,
        output_dir=args.output_dir,
        source_root=args.source_root,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
