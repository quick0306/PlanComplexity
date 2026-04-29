from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jsonschema import Draft202012Validator, FormatChecker

from tools.run_reference_suite import run_reference_suite
from tools.run_tool_comparison import run_tool_comparison
from validation.utils.serializers import write_csv_artifact, write_json_artifact


_TEMPLATE_DIR = ROOT / "validation" / "reports" / "templates"
_VALIDATION_REPORT_SCHEMA = ROOT / "validation" / "schemas" / "validation_report.schema.json"
_ALLOWED_RESULT_STATUSES = {"pass", "fail", "warning", "skipped"}


def build_validation_report(
    profile: str = "research",
    output_dir: Path | str = "run_reports/validation",
    source_root: Path | str | None = None,
) -> dict[str, str]:
    output_root = Path(output_dir)
    reference_report = run_reference_suite(
        profile=profile,
        output_dir=output_root,
        source_root=source_root,
    )
    comparison_report = run_tool_comparison(
        profile=profile,
        output_dir=output_root,
        source_root=source_root,
    )
    return render_validation_artifacts(reference_report, comparison_report, output_root)


def render_validation_artifacts(
    reference_report: dict[str, Any],
    comparison_report: dict[str, Any],
    output_dir: Path | str,
) -> dict[str, str]:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    profile_key = str(reference_report.get("profile") or comparison_report.get("profile") or "research")
    generated_at = _utc_now()
    report_id = _report_id(profile_key, generated_at)

    reference_metrics = _rows(reference_report.get("metrics"))
    comparison_rows = _rows(comparison_report.get("comparisons"))

    artifact_paths: dict[str, Path] = {
        "reference_json": _ensure_json_artifact(
            reference_report,
            "json",
            output_root / "reference_case_results.json",
        ),
        "reference_csv": _ensure_csv_artifact(
            reference_report,
            "csv",
            output_root / "reference_case_results.csv",
            reference_metrics,
            _reference_metric_fieldnames(reference_metrics),
        ),
        "comparison_json": _ensure_json_artifact(
            comparison_report,
            "json",
            output_root / "comparator_statistics.json",
        ),
        "comparison_csv": _ensure_csv_artifact(
            comparison_report,
            "csv",
            output_root / "comparator_statistics.csv",
            comparison_rows,
            _comparison_fieldnames(comparison_rows),
        ),
    }

    validation_report = _build_validation_report_json(
        reference_report,
        profile_key=profile_key,
        generated_at=generated_at,
        report_id=report_id,
    )
    _validate_validation_report(validation_report)
    artifact_paths["validation_report_json"] = write_json_artifact(
        output_root / "validation_report.json",
        validation_report,
    )

    env = _template_environment()
    summary_context = _summary_context(
        profile_key=profile_key,
        generated_at=generated_at,
        report_id=report_id,
        reference_report=reference_report,
        comparison_rows=comparison_rows,
    )
    artifact_paths["summary_markdown"] = _write_text_artifact(
        output_root / "validation_summary.md",
        env.get_template("validation_summary.md.j2").render(summary_context),
    )

    supplement_dir = output_root / "supplement_tables"
    supplement_dir.mkdir(parents=True, exist_ok=True)
    artifact_paths["supplement_comparison_csv"] = _write_text_artifact(
        supplement_dir / "comparison_table.csv",
        env.get_template("comparison_table.csv.j2").render(comparison_rows=comparison_rows),
    )

    manifest_lock = _build_manifest_lock(
        profile_key=profile_key,
        generated_at=generated_at,
        report_id=report_id,
        artifact_paths=artifact_paths,
        output_root=output_root,
    )
    artifact_paths["manifest_lock"] = write_json_artifact(output_root / "manifest_lock.json", manifest_lock)
    return {key: str(path) for key, path in artifact_paths.items()}


def _build_validation_report_json(
    reference_report: dict[str, Any],
    *,
    profile_key: str,
    generated_at: str,
    report_id: str,
) -> dict[str, Any]:
    metrics = _rows(reference_report.get("metrics"))
    exact_rows = [
        row
        for row in metrics
        if row.get("comparison_class") == "exact-equivalent"
    ]
    return {
        "report_id": report_id,
        "generated_at": generated_at,
        "profile_key": profile_key,
        "summary": {
            "total_metrics": len(metrics),
            "exact_passes": sum(1 for row in exact_rows if row.get("status") == "pass"),
            "exact_failures": sum(1 for row in exact_rows if row.get("status") == "fail"),
        },
        "results": [
            {
                "platform": str(row.get("domain") or row.get("platform") or ""),
                "metric_key": str(row.get("metric_key") or ""),
                "comparison_class": str(row.get("comparison_class") or "not-comparable"),
                "status": _report_status(row.get("status")),
            }
            for row in metrics
        ],
    }


def _summary_context(
    *,
    profile_key: str,
    generated_at: str,
    report_id: str,
    reference_report: dict[str, Any],
    comparison_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    cases = _rows(reference_report.get("cases"))
    return {
        "profile_key": profile_key,
        "generated_at": generated_at,
        "report_id": report_id,
        "reference_summary": _reference_summary(reference_report),
        "domain_case_counts": sorted(_count_by(cases, "domain").items()),
        "comparison_rows": comparison_rows,
    }


def _reference_summary(reference_report: dict[str, Any]) -> dict[str, Any]:
    summary = dict(reference_report.get("summary") or {})
    cases = _rows(reference_report.get("cases"))
    metrics = _rows(reference_report.get("metrics"))
    exact_rows = [
        row
        for row in metrics
        if row.get("comparison_class") == "exact-equivalent"
    ]
    summary.setdefault("cases_total", len(cases))
    summary.setdefault("metrics_total", len(metrics))
    summary.setdefault("exact_metrics_total", len(exact_rows))
    summary.setdefault("exact_failures", sum(1 for row in exact_rows if row.get("status") == "fail"))
    summary.setdefault("reference_exact_green", summary["exact_failures"] == 0)
    return summary


def _build_manifest_lock(
    *,
    profile_key: str,
    generated_at: str,
    report_id: str,
    artifact_paths: dict[str, Path],
    output_root: Path,
) -> dict[str, Any]:
    artifacts = []
    for key, path in sorted(artifact_paths.items()):
        artifacts.append(
            {
                "key": key,
                "path": _display_path(path, output_root),
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    return {
        "report_id": report_id,
        "generated_at": generated_at,
        "profile_key": profile_key,
        "artifacts": artifacts,
    }


def _ensure_json_artifact(report: dict[str, Any], artifact_key: str, default_path: Path) -> Path:
    path = _artifact_path(report, artifact_key, default_path)
    if not path.exists():
        write_json_artifact(path, report)
    return path


def _ensure_csv_artifact(
    report: dict[str, Any],
    artifact_key: str,
    default_path: Path,
    rows: list[dict[str, Any]],
    fieldnames: list[str],
) -> Path:
    path = _artifact_path(report, artifact_key, default_path)
    if not path.exists():
        write_csv_artifact(path, rows, fieldnames=fieldnames)
    return path


def _artifact_path(report: dict[str, Any], artifact_key: str, default_path: Path) -> Path:
    artifacts = report.get("artifacts")
    if isinstance(artifacts, dict) and isinstance(artifacts.get(artifact_key), str):
        return Path(artifacts[artifact_key])
    return default_path


def _reference_metric_fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    preferred = [
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
    return _fieldnames(rows, preferred)


def _comparison_fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    preferred = [
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
    return _fieldnames(rows, preferred)


def _fieldnames(rows: list[dict[str, Any]], preferred: list[str]) -> list[str]:
    keys = {key for row in rows for key in row}
    ordered = [key for key in preferred if key in keys or not rows]
    ordered.extend(sorted(keys - set(ordered)))
    return ordered or preferred


def _template_environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
    )
    env.filters["csv_cell"] = _csv_cell
    env.filters["display_value"] = _display_value
    return env


def _csv_cell(value: Any) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="")
    writer.writerow(["" if value is None else value])
    return output.getvalue()


def _display_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _write_text_artifact(path: Path, contents: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")
    return path


def _validate_validation_report(payload: dict[str, Any]) -> None:
    schema = json.loads(_VALIDATION_REPORT_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))
    if errors:
        first_error = errors[0]
        location = ".".join(str(item) for item in first_error.absolute_path) or "<root>"
        raise ValueError(f"Validation report schema failure at {location}: {first_error.message}")


def _rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(row) for row in value if isinstance(row, dict)]


def _count_by(rows: Iterable[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "UNKNOWN")
        counts[value] = counts.get(value, 0) + 1
    return counts


def _report_status(value: Any) -> str:
    status = str(value)
    if status in _ALLOWED_RESULT_STATUSES:
        return status
    return "warning"


def _display_path(path: Path, output_root: Path) -> str:
    try:
        return path.relative_to(output_root).as_posix()
    except ValueError:
        return str(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _report_id(profile_key: str, generated_at: str) -> str:
    safe_timestamp = generated_at.replace(":", "").replace("-", "").replace("Z", "UTC")
    return f"validation-{profile_key}-{safe_timestamp}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build publication-oriented validation evidence artifacts."
    )
    parser.add_argument("--profile", default="research", help="Validation profile key to execute.")
    parser.add_argument(
        "--output-dir",
        default="run_reports/validation",
        help="Directory where validation report artifacts will be written.",
    )
    parser.add_argument(
        "--source-root",
        help="Optional repository root that contains the reference-case source_path inputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    build_validation_report(
        profile=args.profile,
        output_dir=args.output_dir,
        source_root=args.source_root,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
